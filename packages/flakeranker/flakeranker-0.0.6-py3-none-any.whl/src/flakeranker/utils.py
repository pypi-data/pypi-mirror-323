"""Utilities for FlakeRanker."""

import pandas as pd


def join_dfs(df1: pd.DataFrame, df2: pd.DataFrame, key: str = "category"):
    """Join two dataframes on a shared column key, defaults to `category.`"""
    return df1.set_index(key).join(df2.set_index(key)).reset_index()


def list_flaky_rerun_suites(jobs: pd.DataFrame):
    """Returns the list of rerun suites that contains at least one success and one failed jobs.

    Each result row is a rerun suite with a column id containing the ordered of rerun suite's jobs.
    """
    grouped_jobs = (
        jobs[jobs["status"].isin(["success", "failed"])]
        .sort_values(by=["created_at"], ascending=True)
        .groupby(["project", "commit", "name"])
        .aggregate(
            {
                "id": list,
                "status": list,
                "created_at": list,
                "finished_at": list,
            }
        )
    ).reset_index()
    flaky_reruns = grouped_jobs[
        grouped_jobs["status"].map(lambda x: set(["success", "failed"]).issubset(x))
    ].reset_index(drop=True)
    return flaky_reruns
