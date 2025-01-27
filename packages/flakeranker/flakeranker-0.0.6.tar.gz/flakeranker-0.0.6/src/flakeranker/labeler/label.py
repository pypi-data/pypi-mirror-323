import re
import os
import sys
from typing import Optional
import click
import itertools
import pandas as pd
from tqdm import tqdm

from src.flakeranker import utils


tqdm.pandas()
pd.options.mode.chained_assignment = None  # default='warn'
CURRENT_DIRNAME = os.path.dirname(__file__)


def find_category(job, patterns) -> Optional[str]:
    """Infer job category based on manual patterns."""
    if job["category"] is not None:
        return job["category"]
    if job["failure_reason"] == "stuck_or_timeout_failure":
        return job["failure_reason"]
    if not job["logs"]:
        return None
    for _, pattern in patterns.iterrows():
        try:
            if (
                re.search(pattern["regex"], job["logs"], flags=re.IGNORECASE)
                is not None
            ):
                return pattern["category"]
        except MemoryError:
            continue
    return None


def label(input_file_path: str, output_file_path: str):
    """Automatically label (add label columns described below to) a dataset of build jobs.

    Returns
    -------
        The input `.csv` dataset with the following additional columns.
        `flaky` (bool): Indicating whether the job is flaky or not.
        `category` (str): Category of flaky job failure, available only for flaky failed jobs successfully identified by the regexes.
    """
    df = pd.read_csv(input_file_path)
    click.echo(click.style(f"Job data loaded. {df.shape[0]} jobs found.", fg="green"))

    # label flakiness
    click.echo("Adding column `flaky`...")
    flaky_reruns = utils.list_flaky_rerun_suites(df)
    flaky_job_ids = list(itertools.chain(*flaky_reruns["id"].to_list()))
    df["flaky"] = df.progress_apply(lambda job: job["id"] in flaky_job_ids, axis=1)

    # label on flaky job failure with categories
    click.echo("Adding column `category`...")

    patterns = pd.read_csv(os.path.join(CURRENT_DIRNAME, "patterns.csv"))
    click.echo(
        click.style(f"Patterns loaded. {patterns.shape[0]} patterns.", fg="green")
    )

    flaky_job_failures = df[df["flaky"] & (df["status"] == "failed")]
    click.echo(
        click.style(
            f"Labeling {flaky_job_failures.shape[0]} identified flaky job failures.",
            bold=True,
        )
    )

    if "category" not in flaky_job_failures.columns:
        flaky_job_failures["category"] = None
    flaky_job_failures["logs"] = flaky_job_failures["logs"].astype(str)
    flaky_job_failures["category"] = flaky_job_failures.progress_apply(
        lambda job: find_category(job, patterns), axis=1
    )

    # Join labeled job to the full dataset
    df = utils.join_dfs(
        df.drop(columns="category"), flaky_job_failures[["id", "category"]], key="id"
    )
    labeled_df = df[~df["category"].isna()]

    # Export
    df.to_csv(output_file_path, index=False)

    # Display the obtained coverage
    n_labeled = labeled_df.shape[0]
    recall = round(float(n_labeled / flaky_job_failures.shape[0]) * 100, 2)
    click.echo(
        click.style(f"{recall}% of the flaky job failures are labeled.", fg="green")
    )
    return recall


if __name__ == "__main__":
    input = sys.argv[1]
    output = sys.argv[2]
    label(input, output)
