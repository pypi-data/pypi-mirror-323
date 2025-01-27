"""Utilities functions."""

from datetime import datetime


def compute_job_deltas(row):
    """Returns the list of time gaps in seconds between jobs' finition and creation timestamps."""
    deltas = []
    for i in range(1, len(row["created_at"])):
        # delta diagnosis and fix time between the last finished job and this job creation.
        start_date = row["finished_at"][i - 1]
        end_date = row["created_at"][i]
        delta = (end_date - start_date).total_seconds()
        deltas.append(delta)  # add delta minus in seconds

    return deltas


def compute_time_deltas(date_times: list[datetime]):
    """Return time gaps from an array of timestamps."""
    date_times.sort()
    deltas = []
    for i in range(1, len(date_times)):
        delta = (date_times[i] - date_times[i - 1]).total_seconds()
        deltas.append(delta)

    return deltas


def seconds_to_human_readable(seconds: int):
    """Convert seconds to human readable string."""
    intervals = (
        ("years", 60 * 60 * 24 * 365),  # 60 * 60 * 24 * 365
        ("months", 60 * 60 * 24 * 30),  # 60 * 60 * 24 * 30
        ("weeks", 60 * 60 * 24 * 7),  # 60 * 60 * 24 * 7
        ("days", 60 * 60 * 24),  # 60 * 60 * 24
        ("hours", 3600),  # 60 * 60
        ("minutes", 60),
        ("seconds", 1),
    )
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds %= count
            if value == 1:
                name = name.rstrip("s")  # singular form if value is 1
            result.append(f"{value} {name}")

    return ", ".join(result)
