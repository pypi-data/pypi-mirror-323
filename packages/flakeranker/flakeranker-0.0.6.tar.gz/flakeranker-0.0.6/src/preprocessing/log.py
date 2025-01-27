"""Pre-processing build log."""

import os
import re
from cleantext import clean
from src.utils import constants


def filter_logs(line: str):
    """File log lines to identify failure statements."""
    included_contains_keywords = ["fail", "error", "remote"]
    included_startswith_keywords = ["error", "fatal", "fail", "invalid", "exception"]
    excluded_contains_keywords = [
        "$ " "echo ",
        "section_start",
        "section_end",
        "error: no files to upload",  # false positive error displayed on artifacts files not generated
    ]
    excluded_startswith_keywords = [
        "$"  # cmd line
        "note:",
    ]
    line = line.lower().strip()
    first_word = line.lower().split(" ")[0]
    return (
        any(el in line for el in included_contains_keywords)
        or any(line.startswith(el) for el in included_startswith_keywords)
    ) and not (
        any(el in line for el in excluded_contains_keywords)
        or any(line.startswith(el) for el in excluded_startswith_keywords)
        or first_word[-3:] == "ing"  # cleaning, preparing, uploading, downloading, etc.
    )


def clean_logs(line: str):
    regexes = [
        r"[\t\n\r\f\v]",
        r"\x1b[^m]*m",  # ansi escape sequences
        r"([0-9]\|)?\\?\\r\\?\\n",  # useless return carriage
        r"\+?0x[0-9a-f]+",  # hexadecimal numbers
    ]
    for reg in regexes:
        line = re.sub(reg, "", line, flags=re.IGNORECASE)
    # replace multiple spaces with single space
    line = re.sub(r"\s+", " ", line)
    line = line.strip()
    return line


def read_logs_bottom(project_id: int, job_id: int, max_lines: int = 15):
    """Read max_lines at the bottom of log file for a given job in a project and process it."""
    root = "/home/henri/Documents/ETS/telus-flaky-build/"
    filepath = os.path.join(
        str(root), "data", "logs", str(project_id), f"{project_id}_{job_id}.log"
    )
    log_lines = None
    with open(filepath, "r") as f:
        log_lines = f.read().splitlines()

    if log_lines is not None:
        log_lines = log_lines[-max_lines:] if len(log_lines) > max_lines else log_lines
    return log_lines


def replace_numbers(text, replace_with="<NUMBER>"):
    """
    Replace all numbers in ``text`` str with ``replace_with`` str.
    """
    return constants.NUMBERS_REGEX.sub(replace_with, text)


def replace_urls(text, regexes, replace_with="<URL>"):
    for regx in regexes:
        text = re.sub(regx, replace_with, text)
    return text


def preprocess(project_id: int, job_id: int, max_lines: int = 0):
    """Retrieve log lines that indicate the failure reason(s)."""
    log_lines = read_logs_bottom(project_id, job_id, max_lines)
    if log_lines is None:
        return None

    log_lines = [clean_logs(line) for line in log_lines]
    log_lines = list(filter(filter_logs, log_lines))
    log_lines = [
        clean(
            line,
            lower=False,
            fix_unicode=True,
            no_urls=True,
            strip_lines=True,
            no_line_breaks=True,
            replace_with_url="<URL>",
            lang="en",
        )
        for line in log_lines
    ]

    URL_REGEX = [
        constants.URL_REGEX.pattern,
        r"[a-z]*:\/(\/[a-zA-Z0-9-\.:?=%&]*)+",
        r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
    ]
    errors_with_code = ["exit code", "exit status"]

    log_lines = [clean_logs(line) for line in log_lines]
    log_lines = list(filter(filter_logs, log_lines))
    log_lines = [replace_urls(line, URL_REGEX) for line in log_lines]
    log_lines = [re.sub(r"(\/.*?\.[\w:]+)", "<FILEPATH>", line) for line in log_lines]
    log_lines = [re.sub(r"(\/(\w|-)*)+", "<DIRPATH>", line) for line in log_lines]
    log_lines = [
        re.sub(r"[^a-zA-Z0-9<>]+\s*", " ", line) for line in log_lines
    ]  # remove punctuations
    # remove numbers but keep status codes
    log_lines = [
        (
            line.strip()
            if any(error in line.lower() for error in errors_with_code)
            else replace_numbers(line, "")
        )
        for line in log_lines
    ]
    log_lines = [re.sub(r"((\d+)?[\w]+\d+[\w\d]*)", "<ID>", line) for line in log_lines]

    log_lines = list(set(log_lines))
    return log_lines
