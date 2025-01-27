"""Module for ranking flaky job failure categories based on RFM measures, i.e. Output of Analyzer."""

import sys
import pandas as pd

from src.flakeranker.ranker import utils as ranker_utils


def rank(input_file_path: str, output_file_path: str):
    # Read input data
    rfm = pd.read_csv(input_file_path)[["category", "recency", "frequency", "cost"]]
    outliers, rfm_scores = ranker_utils.preprocess(rfm)
    outliers = ranker_utils.process_outliers(outliers, rfm)

    # Run clustering and get the model
    y = rfm_scores["category"]
    X = rfm_scores[["R", "F", "M"]].astype(int)
    model = ranker_utils.create_clustering_model(X)

    # create results dataset
    results = pd.DataFrame(X).astype(int)
    results["cluster"] = model.labels_
    results["category"] = y
    results["recency"] = rfm["recency"]
    results["frequency"] = rfm["frequency"]
    results["cost"] = rfm["cost"]
    results = results[
        ["category", "R", "F", "M", "recency", "frequency", "cost", "cluster"]
    ]

    cluster_stats = ranker_utils.compute_cluster_statistics(results)[
        ["cluster", "pattern"]
    ]
    results = results.join(
        cluster_stats.set_index("cluster"), on="cluster", validate="m:1"
    )
    results = pd.concat([results, outliers], sort=False)

    results["rfm_sum"] = results[["R", "F", "M"]].sum(axis=1)
    results.sort_values(
        by=["pattern", "rfm_sum"], ascending=[True, False], inplace=True
    )

    # remove internal information
    results.drop(columns="rfm_sum", inplace=True)
    for k in ["R", "F", "M"]:
        results.loc[results["cluster"] == -1, k] = None

    # export results
    results.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    input = sys.argv[1]
    output = sys.argv[2]
    rank(input, output)
