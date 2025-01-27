"""Utilities for FlakeRanker Ranker."""

import click
import numpy as np
import pandas as pd
from tqdm import trange
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest


def find_outliers(rfm: pd.DataFrame):
    """Identify outliers in the RFM dataset using IsolationForest."""
    IF = IsolationForest(n_estimators=500, contamination=0.1)
    IF.fit(rfm[["recency", "frequency", "cost"]])
    IF_anomalies = IF.predict(rfm[["recency", "frequency", "cost"]])
    outliers = rfm[IF_anomalies == -1]
    return outliers


def preprocess(rfm: pd.DataFrame) -> pd.DataFrame:
    """Preprocess RFM dataset. Find and remove outliers, and perform RFM scoring."""
    outliers = find_outliers(rfm)

    # remove outliers
    rfm = rfm[~rfm["category"].isin(outliers["category"])]

    # RFM Scoring
    rfm["R"] = pd.qcut(rfm["recency"], q=5, labels=list(range(5, 0, -1)))
    rfm["F"] = pd.qcut(rfm["frequency"], q=5, labels=list(range(1, 6)))
    rfm["M"] = pd.qcut(rfm["cost"], q=5, labels=list(range(1, 6)))
    return outliers, rfm


def create_clustering_model(rfm_scores: pd.DataFrame):
    """Create and return the clustering results."""
    inertias = []
    models = []
    for _ in trange(500, desc="Fitting clustering models"):
        kmeans = KMeans(n_clusters=8, init="k-means++")
        kmeans.fit(rfm_scores)
        models.append(kmeans)
        inertias.append(kmeans.inertia_)

    i = np.argmin(inertias)
    click.echo(f"Lowest clustering inertia: {min(inertias)}")
    return models[i]


def cluster_rfm_pattern(row, cluster_stats):
    """Derive RFM pattern from cluster statistics results."""
    r_mean = cluster_stats["R"].mean()
    f_mean = cluster_stats["F"].mean()
    m_mean = cluster_stats["M"].mean()

    pattern = ""
    pattern += "R+" if row["R"] > r_mean else "R-"
    pattern += "F+" if row["F"] > f_mean else "F-"
    pattern += "M+" if row["M"] > m_mean else "M-"
    return pattern


def outlier_rfm_pattern(row, rfm_dataset):
    """Return RFM pattern corresponding to an outliers based on the values."""
    r_mean = rfm_dataset["recency"].mean()
    f_mean = rfm_dataset["frequency"].mean()
    m_mean = rfm_dataset["cost"].mean()

    pattern = ""
    pattern += "R+" if row["recency"] < r_mean else "R-"
    pattern += "F+" if row["frequency"] > f_mean else "F-"
    pattern += "M+" if row["cost"] > m_mean else "M-"
    return pattern


def compute_cluster_statistics(results: pd.DataFrame):
    """Compute cluster statistics. Calculate mean RFM scores and assign pattern."""
    cluster_stats = (
        results.drop(columns=["category"])
        .groupby("cluster")
        .agg(["count", "mean"])
        .reset_index()
        .round(2)
    )
    cluster_stats.columns = [
        "cluster",
        "#",
        "R",
        "a",
        "F",
        "a",
        "M",
        "a",
        "recency",
        "a",
        "frequency",
        "a",
        "cost",
    ]
    cluster_stats = cluster_stats[
        ["cluster", "#", "R", "F", "M", "recency", "frequency", "cost"]
    ]
    cluster_stats["pattern"] = cluster_stats.apply(
        lambda row: cluster_rfm_pattern(row, cluster_stats), axis=1
    )
    return cluster_stats


def process_outliers(outliers: pd.DataFrame, rfm: pd.DataFrame):
    """Process ranking of outliers."""
    outliers["cluster"] = -1
    outliers["pattern"] = outliers.apply(
        lambda row: outlier_rfm_pattern(row, rfm), axis=1
    )
    # Set RFM values for outliers
    for k in ["R", "F", "M"]:
        outliers[k] = outliers.apply(
            lambda row: (1 - 1 if f"{k}-" in row["pattern"] else 5 + 1),
            axis=1,
        )
    return outliers
