"""Utilities for FlakeRanker Analyzer."""

import numpy as np
import pandas as pd
from datetime import date

from src.flakeranker import utils


def first_failure_finition_date(row):
    for i, status in enumerate(row["status"]):
        if status == "failed":
            return row["finished_at"][i]


def last_job_finition_date(row):
    return max(row["finished_at"])


def first_failure_category(row, labeled_flaky_jobs: pd.DataFrame):
    indexed_labeled_flaky_jobs = labeled_flaky_jobs.copy(deep=True).set_index("id")
    for i, status in enumerate(row["status"]):
        if status == "failed":
            job_id = row["id"][i]
            if job_id in list(indexed_labeled_flaky_jobs.index.values):
                return indexed_labeled_flaky_jobs.loc[job_id, "category"]
            return None


def recency(creation_dates, recency_reference_date, recency_n_last):
    dates = [x.to_pydatetime().date() for x in creation_dates]
    dates.sort()
    last_n_dates = dates[-recency_n_last:]
    reference_date = pd.to_datetime(recency_reference_date).normalize().date()
    recencies = [(reference_date - d).days for d in last_n_dates]
    return round(np.mean(recencies))


def compute_diagnosis_time_delays(
    flaky_reruns: pd.DataFrame, labeled_flaky_jobs: pd.DataFrame
):
    """Returns for each rerun suite the flaky failure category and time delay required for diagnosis."""
    # Set category of each rerun suite based on the category of the initial failure (if labeled).
    flaky_reruns["category"] = flaky_reruns.apply(
        lambda row: first_failure_category(row, labeled_flaky_jobs), axis=1
    )
    flaky_reruns = flaky_reruns[~flaky_reruns["category"].isnull()]

    # Calculate each diagnosis delay component
    flaky_reruns["first_failure_finished_at"] = flaky_reruns.apply(
        first_failure_finition_date, axis=1
    )
    flaky_reruns["last_job_finished_at"] = flaky_reruns.apply(
        last_job_finition_date, axis=1
    )
    flaky_reruns["delay"] = (
        flaky_reruns["last_job_finished_at"] - flaky_reruns["first_failure_finished_at"]
    )
    return flaky_reruns[["category", "delay"]]


def compute_categories_machine_costs(
    labeled_flaky_jobs: pd.DataFrame, cost_infra_pricing_rate: float
):
    """Compute infrastructure cost per category."""
    results = (
        labeled_flaky_jobs[["category", "duration"]]
        .groupby("category")
        .agg("sum")
        .reset_index()
    )
    results.columns = ["category", "duration"]
    results["machine_cost"] = results["duration"].apply(
        lambda duration: round(duration / 60 * cost_infra_pricing_rate, 2)
    )  # by default duration is in seconds and the rate in minutes
    return results[["category", "machine_cost"]]


def compute_categories_diagnosis_costs(
    jobs: pd.DataFrame, labeled_flaky_jobs: pd.DataFrame, cost_dev_hourly_rate: float
):
    """Compute diagnosis time cost per category."""
    # Get all rerun suites' categores and diagnosis times.
    flaky_reruns = utils.list_flaky_rerun_suites(jobs)
    flaky_reruns = compute_diagnosis_time_delays(flaky_reruns, labeled_flaky_jobs)

    # Compute results dataframe by apply formula
    results = flaky_reruns.groupby("category").sum().reset_index()
    results["diagnosis_cost"] = results["delay"].apply(
        lambda delay: round(delay.total_seconds() / 60 * cost_dev_hourly_rate / 60, 2)
    )
    results["diagnosis_cost"] = results["diagnosis_cost"].fillna(0)
    return results[["category", "diagnosis_cost"]]


def compute_categories_recencies(
    labeled_flaky_jobs: pd.DataFrame,
    recency_reference_date: date,
    recency_n_last: float,
):
    results = (
        labeled_flaky_jobs.groupby("category")
        .agg(
            {
                "created_at": lambda creation_dates: recency(
                    creation_dates, recency_reference_date, recency_n_last
                )
            }
        )
        .reset_index()
    )
    results.columns = ["category", "recency"]
    return results
