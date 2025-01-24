import configparser
import math
import re
import subprocess
from datetime import timedelta
from os.path import exists as check_file
from pathlib import Path
from typing import Tuple

import tomllib
from dateutil.parser import parse
from github import Github, Repository

from cyaudit.constants import REPORT_FOLDER
from cyaudit.logging import logger

# Define file paths
SOURCE_PATH = f"./{REPORT_FOLDER}/source/"
OUTPUT_PATH = f"./{REPORT_FOLDER}/output/"
WORKING_PATH = f"./{REPORT_FOLDER}/working/"
TEMPLATE_PATH = f"./{REPORT_FOLDER}/templates/"
LEAD_AUDITORS = f"./{REPORT_FOLDER}/source/lead_auditors.md"
ASSISTING_AUDITORS = f"./{REPORT_FOLDER}/source/assisting_auditors.md"
SEVERITY_COUNTS = SOURCE_PATH + "severity_counts.toml"
SUMMARY_TEX = f"./{REPORT_FOLDER}/templates/summary.tex"
SUMMARY_INFORMATION = SOURCE_PATH + "summary_information.toml"
SOURCE_REPORT = SOURCE_PATH + "report.md"
OUTPUT_SOLODIT = OUTPUT_PATH + "solodit_report.md"
MITIGATION_TABLE = OUTPUT_PATH + "mitigation_table.csv"

# Possible severity labels from github issues
SEVERITY_LABELS = [
    "Severity: Critical Risk",
    "Severity: High Risk",
    "Severity: Medium Risk",
    "Severity: Low Risk",
    "Severity: Informational",
    "Severity: Gas Optimization",
]

# Possible status labels from github issues
STATUS_LABELS = [
    "Report Status: Open",
    "Report Status: Acknowledged",
    "Report Status: Resolved",
    "Report Status: Closed",
]


# Little helper to get issues with a certain label
def get_issue_count(dict, label):
    try:
        count = len(dict[label])
    except Exception:
        count = 0
    finally:
        return count


def title_to_link(title):
    """
    title_to_link converts an issue title to an internal link

    see https://stackoverflow.com/questions/2822089/how-to-link-to-part-of-the-same-document-in-markdown
    """
    # all non-alphanumeric characters should be removed, and spaces replaced with hyphens
    pattern = re.compile("[^a-zA-Z0-9 ]")
    link_anchor = re.sub(pattern, "", title.lower()).replace(" ", "-")
    full_link = f"[*{title}*](#{link_anchor})"
    return full_link


def replace_internal_links(issues, issues_by_number) -> dict:
    """
    replace_internal_links Replaces github's issue links (#xx) with internal document links
    """
    for label in issues:
        for issue in issues[label]:
            # Find every occurrence of ' #' followed by a number of up to 4 digits
            p = re.findall(" #\d{1,4}", issue)
            if p:
                for match in p:
                    # Extract the issue number to link to
                    number = int(match[2:])
                    # Create the internal link to the issue
                    try:
                        # The space below is needed, because the regexp match includes the space. Otherwise it would be lost.
                        target = " " + title_to_link(issues_by_number[number])
                    except KeyError as e:
                        # Common error occurs when there is a '#' in the issue description i.e "Fix implemented in #2"
                        print(
                            f"Issue '{issue}' references issue #{number} but there is no such issue. KeyError {e}. Make sure there aren't any `#`s written in the Issue description."
                        )
                        exit(1)
                    # Replace with link
                    index = issues[label].index(issue)
                    new_issue = issues[label][index].replace(match, target)
                    issues[label][index] = new_issue
                    issue = new_issue
    return issues


def markdown_heading_to_latex_hypertarget(heading):
    # Use Pandoc to generate LaTeX with a table of contents
    markdown = f"# Table of Contents\n\n{heading}"
    latex = subprocess.check_output(
        ["pandoc", "-f", "markdown", "-t", "latex"], input=markdown.encode()
    ).decode()

    # Extract the hypertarget from the LaTeX
    hypertarget = ""
    for line in latex.split("\n"):
        if "\\hypertarget{table-of-contents}" in line:
            continue
        elif "\\hypertarget{" in line:
            hypertarget = line.strip()
            break

    hypertarget = re.sub(
        r"^\\hypertarget{(.*)}{%", r"\1", hypertarget
    )  # Remove the leading "\\hypertarget{" and trailing "}{%"

    return hypertarget


def format_inline_code(text):
    # Find sections within backticks and wrap them with \texttt{} while also escaping underscores
    return re.sub(
        r"`([^`]+)`", lambda m: "\\texttt{" + m.group(1).replace("_", "\\_") + "}", text
    )


def calculate_period(review_timeline):
    # Extract start and end dates from the review timeline
    # `dateutil.parser.parse` is used here to parse date strings with ordinal suffixes
    dates = [parse(date.strip()) for date in review_timeline.split(" - ")]
    start_date = dates[0]
    end_date = dates[1]

    # Calculate the number of workdays
    workdays = 0
    current_date = start_date

    while current_date <= end_date:
        # Check if the current date is a weekday (Monday to Friday)
        if current_date.weekday() < 5:
            workdays += 1
        current_date += timedelta(days=1)

    return workdays


def generate_markdown_from_issues(issue_dict, summary_of_findings):
    logger.info("Generating markdown from issues...")
    # Dictionary for count by severity
    count_by_severity: dict[str, int] = {}

    with open(SOURCE_REPORT, "w") as report:
        for label in SEVERITY_LABELS:
            # Do nothing if there are no issues with this label
            if get_issue_count(issue_dict, label) == 0:
                continue

            report.write(f"## {label[10:]}\n")
            for content in issue_dict[label]:
                report.write(content.replace("\r\n", "\n"))
            report.write("\n\\clearpage\n")

    total_count = 0
    with open(SEVERITY_COUNTS, "w") as counts_file:
        counts_file.write("[counts]" + "\n")
        for label in SEVERITY_LABELS:
            variable_name = (
                label[10:].lower().replace(" risk", "").replace(" ", "_") + " = "
            )
            count = get_issue_count(issue_dict, label)
            counts_file.write(variable_name + str(count) + "\n")
            count_by_severity[label] = count
            total_count += count
        counts_file.write("total = " + str(total_count) + "\n")

    with open(SUMMARY_TEX, "r") as summary_file:
        summary_tex_content = summary_file.read()

    summary_findings_table = ""
    mitigation_table = f"Name,Status,{get_summary_information()['team_name']},Cyfrin\n"
    for label in SEVERITY_LABELS:
        # Do nothing if there are no issues with this label
        if get_issue_count(issue_dict, label) == 0:
            continue

        fill = math.ceil(math.log10(count_by_severity[label]))
        prefix = f"{label[10:11]}-"

        mitigation_table += f"{label.split()[1].upper()},,,\n"

        # Iterate through all findings for the current severity
        for counter, (issue_title, status_label) in enumerate(
            summary_of_findings[label], start=1
        ):
            linted_title = replace_ampersand_in_findings_headings(issue_title)
            latex_hypertarget = markdown_heading_to_latex_hypertarget(
                "### " + linted_title
            )
            prefixed_title = f"\hyperlink{{{latex_hypertarget}}}{{[{prefix}{str(counter).zfill(fill)}] {format_inline_code(linted_title)}}}"
            status_label = status_label.replace("Report Status: ", "")
            summary_findings_table += f"{prefixed_title} & {status_label} \\\\\n\hline"
            mitigation_table += f'"{linted_title}",{status_label},,\n'

    # Replace the placeholder in the SUMMARY_TEX file
    placeholder_start = "% __PLACEHOLDER__SUMMARY_OF_FINDINGS_START"
    placeholder_end = "% __PLACEHOLDER__SUMMARY_OF_FINDINGS_END"

    if (
        placeholder_start in summary_tex_content
        and placeholder_end in summary_tex_content
    ):
        # Find the position of the start and end placeholders
        start_position = summary_tex_content.index(placeholder_start)
        end_position = summary_tex_content.index(placeholder_end) + len(placeholder_end)

        # Construct the new content with the updated table
        new_content = (
            summary_tex_content[:start_position]
            + placeholder_start
            + "\n\hline"
            + summary_findings_table
            + "\n"
            + placeholder_end
            + summary_tex_content[end_position:]
        )

        # Replace the table section with the new content in the summary_tex_content
        updated_summary_tex_content = new_content
    else:
        print(
            "Table placeholder not found in summary.tex. Make sure the placeholders are present."
        )
        exit(1)

    with open(SUMMARY_TEX, "w") as summary_file:
        summary_file.write(updated_summary_tex_content)

    with open(MITIGATION_TABLE, "w") as mitigation_file:
        mitigation_file.write(mitigation_table)

    return total_count


def fetch_issues(repository: Repository, github: Github) -> Tuple[dict, dict]:
    """
    fetches issues from the github.

    Returns a dictionary with issues by severity and a dictionary with summary of findings.
    """
    repository_url = re.sub(
        r"^https://github.com/(.*?)(\.git)?$", r"\1", repository.clone_url
    )  # Remove the leading "https://github.com/" and trailing ".git"

    # The dictionary where the issues will be stored, by severity.
    issue_dict: dict[str, list[str]] = {}

    # Dictionary for issues by github number, to replace #xx links
    issues_by_number: dict[int, str] = {}

    # Dictionary for summary of findings
    summary_of_findings: dict[str, list[tuple[str, str]]] = {}

    # TODO catch get_repo() 404 errors and produce a gentle suggestion on what's wrong.
    # "GitHub's REST API v3 considers every pull request an issue"--need to filter them out.
    issues_list = list(github.get_repo(repository_url).get_issues())
    for i in range(len(issues_list) - 1, -1, -1):
        issue = issues_list[i]
        if issue.state == "open" and issue.pull_request is None:
            # get issue number and title for replacing links
            issues_by_number[issue.number] = issue.title

            # filter issue labels for only severity labels
            severity_labels_in_issue = [
                label.name for label in issue.labels if label.name in SEVERITY_LABELS
            ]

            # filter issue labels for only status labels
            status_labels_in_issue = [
                label.name for label in issue.labels if label.name in STATUS_LABELS
            ]

            assert (
                len(severity_labels_in_issue) == 1
            ), f"Issue {issue.html_url} has more than one (or no) severity label."
            assert (
                len(status_labels_in_issue) == 1
            ), f"Issue {issue.html_url} has more than one (or no) status label."

            severity_label = severity_labels_in_issue[0]
            if severity_label not in issue_dict:
                issue_dict[severity_label] = []
            issue_dict[severity_label].append(
                f"\n\n### {issue.title}\n\n{issue.body}\n"
            )

            status_label = status_labels_in_issue[0]
            # Append issue title and status to summary of findings dictionary
            if severity_label not in summary_of_findings:
                summary_of_findings[severity_label] = []
            summary_of_findings[severity_label].append((issue.title, status_label))

    issues_dict = replace_internal_links(issue_dict, issues_by_number)
    return issues_dict, summary_of_findings


def get_file_contents(filename: Path | str):
    """
    get_file_contents Reads the contents of a file and returns a list where every element is a line in the file. Newlines are stripped.

    :param filename: Name of the file to read
    :return: List of all lines in the file, with the newline character removed.
    """

    if not Path(filename).exists():
        print(
            "I can't find the requested file: '"
            + str(filename)
            + "'. Make sure it exists."
        )
        exit(1)

    with open(filename) as file:
        lines = [line.rstrip() for line in file]

    return lines


def save_file_contents(filename, contents):
    """
    save_file_contents Saves a list to disk, one element per line

    :param filename: Name of the file to write to
    :param contents: List containing the information to save
    """

    with open(filename, "w") as file:
        file.write("\n".join(contents))


def replace_in_file_content(file_content, replacement):
    """
    replace_in_file_content Finds text in every element of a list and replaces it as required.

    :param file_content: List containing the string elements to be replaced
    :param replacement: A list of two-element lists containing text to replace, and what to replace it with.
    :return: Input with text replaced.
    """

    lines = []
    for line in file_content:
        if line.find("__PLACEHOLDER__") >= 0:
            for r in replacement:
                line = line.replace(r[0], str(r[1]))
        lines.append(line)

    return lines


def get_summary_information():
    """
    get_summary_information Retrieves all strings needed to fill summary.tex and title.tex

    :return: A dictionary with all strings needed to replace in the tex files.
    """
    SUMMARY_INFORMATION = Path(REPORT_FOLDER) / "source" / "summary_information.toml"

    if not Path(SUMMARY_INFORMATION).exists():
        print(
            "I can't find summary_information.toml. Make sure it is in the source folder."
        )
        exit(1)

    try:
        with open(SUMMARY_INFORMATION, "rb") as f:
            config = tomllib.load(f)

        # If your TOML has a [summary] section like the conf file did:
        return config.get("summary", {})

        # Or if your TOML is flat without sections:
        # return config

    except tomllib.TOMLDecodeError as e:
        print(f"Error parsing TOML file: {e}")
        exit(1)


def get_severity_counts():
    """
    get_severity_counts Retrieves all information needed to fill the amount of findings in summary.tex

    :return: A dictionary with all severity counts.
    """

    if not check_file(SEVERITY_COUNTS):
        print(
            "I can't find severity_counts.conf. Make sure it is in the source folder."
        )
        exit(1)

    config = configparser.ConfigParser()
    config.read(SEVERITY_COUNTS)

    counts: dict[str, int] = {}

    for key, value in config["counts"].items():
        counts[key] = value

    # If integers are needed instead of strings:
    # for key, value in config['counts'].items():
    #    try:
    #        counts[key] = int(value)
    #    except ValueError:
    #        counts[key] = 0

    return counts


def edit_report_md():
    with (
        open(Path.cwd() / LEAD_AUDITORS, "r") as lead_auditors,
        open(Path.cwd() / ASSISTING_AUDITORS, "r") as assisting_auditors,
        open(Path.cwd() / SOURCE_REPORT, "r") as source_report,
        open(Path.cwd() / OUTPUT_SOLODIT, "w") as solodit_report,
    ):
        solodit_report.write("**Lead Auditors**\n\n")
        for line in lead_auditors:
            solodit_report.write(line)
        solodit_report.write("\n**Assisting Auditors**\n\n")
        for line in assisting_auditors:
            solodit_report.write(line)
        solodit_report.write("\n\n---\n\n# Findings\n")
        for line in source_report:
            solodit_report.write(line)


def replace_org_in_link(
    line, internal_org, internal_repo_name, source_org, source_repo_name
):
    # Identify all links
    links = re.findall('https?://[^\s<>"]+|[^\s<>"]+\.[^\s<>"]+', line)

    for link in links:
        if re.search(internal_org, link, re.IGNORECASE):
            # Replace internal organization with source organization
            new_link = re.sub(internal_org, source_org, link, flags=re.IGNORECASE)

            # Replace internal repository name with source repository name, if different
            if source_repo_name != internal_repo_name:
                new_link = re.sub(
                    internal_repo_name, source_repo_name, new_link, flags=re.IGNORECASE
                )

            line = line.replace(link, new_link)

    return line


def replace_ampersand_in_findings_headings(line):
    # If the line is a finding markdown heading and contains '&', replace '&' with 'and'
    if line.strip().startswith("###") and "&" in line:
        line = line.replace("&", "and")

    return line


def lint(
    report, team_name, source_org, source_repo_name, internal_org, internal_repo_name
):
    for line in report:
        new_line = line

        # Replace any internal organization repo links
        new_line = replace_org_in_link(
            new_line, internal_org, internal_repo_name, source_org, source_repo_name
        )

        # Replace any '&' in finding headings with 'and'
        new_line = replace_ampersand_in_findings_headings(new_line)

        # Replace any double backslashes with single backslashes (GitHub MathJax to LaTeX)
        new_line = new_line.replace("\\\\", "\\")

        report[report.index(line)] = new_line

    # Check for link structures ( format [something](url) ) that don't start with http
    for line in report:
        pos = line.find("](")
        while pos != -1:
            # Check if the first 4 characters after the open-paren are "http"
            if line[pos + 2 : pos + 6] != "http" and line[pos + 2] != "#":
                position = report.index(line)
                print(f"Possible broken link at report.md line {position}: ")
                print(f"\t{line}")
            pos = line.find("](", pos + 1)

    # Check for raw links ("http" string not immediately preceded by a link structure)
    for line in report:
        pos = line.find("http")
        while pos != -1:
            # Check if the character to the left of "http" is an open-paren preceded by a close-bracket
            if line[pos - 2 : pos] != "](":
                position = report.index(line)
                print(f"Possible raw link at report.md line {position}: ")
                print(f"\t{line}")
            pos = line.find("http", pos + 1)

    # Check for descriptions not starting in the same line as the headers
    lineNumber = 0
    for line in report:
        # If there's a newline, merge the next line with the current one
        if (
            (
                line.startswith("**Description:**")
                and len(line) < len("**Description:**") + 5
            )
            or (line.startswith("**Impact:**") and len(line) < len("**Impact:**") + 5)
            or (
                line.startswith("**Proof of Concept:**")
                and len(line) < len("**Proof of Concept:**") + 5
            )
            or (
                line.startswith("**Recommended Mitigation:**")
                and len(line) < len("**Recommended Mitigation:**") + 5
            )
            or (
                line.startswith("**" + internal_org + ":**")
                and len(line) < len("**" + internal_org + ":**") + 5
            )
            or (
                line.startswith("**" + team_name + ":**")
                and len(line) < len("**" + team_name + ":**") + 5
            )
        ):
            # There might be more than one empty lines following the header, remove them
            while lineNumber + 1 < len(report) and report[lineNumber + 1] == "":
                del report[lineNumber + 1]

            if lineNumber + 1 < len(report):
                nextLine = report[lineNumber + 1]
                # If it's a list, code or quote, don't merge
                if (
                    not nextLine.lstrip().startswith("-")
                    and not nextLine.lstrip().startswith("1.")
                    and not nextLine.lstrip().startswith("```")
                    and not nextLine.lstrip().startswith("#")
                    and not nextLine.lstrip().startswith(">")
                ):
                    report[lineNumber] = line + " " + nextLine.lstrip()
                    del report[lineNumber + 1]

        lineNumber = lineNumber + 1

    return report
