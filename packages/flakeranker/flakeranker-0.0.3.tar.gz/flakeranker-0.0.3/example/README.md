# FlakeRanker

FlakeRanker is a CLI tool associated to the paper [On the Diagnosis of Flaky Job Failures: Understanding and Prioritizing Failure Categories](https://arxiv.org/abs/2501.04976) accepted at the 47th International Conference on Software Engineering ICSE SEIP 2025.

Here is the [GitHub Repository](https://github.com/devopsirc/telus-flaky-job-failures-prioritization).

## Example Usage of FlakeRanker

For demonstration purpose, we provide an example `data/` directory including a .csv dataset of 57,350 build jobs collected from the open-source project [Veloren](https://gitlab.com/veloren/veloren) hosted on GitLab.

### Step 0. Unzip Dataset

```bash
unzip data/jobs.zip data/
```

This command outputs the `data/jobs.csv` file.

Overview of the input jobs dataset

| **id**     | **name**    | **status** | **created_at**             | **finished_at**            | **duration** | **failure_reason** | **commit**                               | **project** | **logs** |
|------------|-------------|------------|----------------------------|----------------------------|--------------|--------------------|------------------------------------------|-------------|----------|
| 8169884262 | security    | success    | 2024-10-23 21:21:41.701+00 | 2024-10-23 21:38:33.728+00 | 329.987579   |                    | 71ef5d084bb13c8b1e73aabce8a559e50536fc11 | 10174980    |          |
| 8169738883 | translation | failed    | 2024-10-23 21:00:18.592+00 | 2024-10-23 21:01:13.11+00  | 50.088166    |                    | 4a3d0b76f01117aabbff24b6a7717144b1780f60 | 10174980    |   [logs]       |
| ... | ...    | ...    | ... | ... | ...   |     ...               | ... | ...    |...          |
| 8158010241 | benchmarks  | success    | 2024-10-22 21:00:08.719+00 | 2024-10-22 21:21:42.926+00 | 1292.721363  |                    | 4a3d0b76f01117aabbff24b6a7717144b1780f60 | 10174980    |          |
| 8158010236 | translation | failed    | 2024-10-22 21:00:08.703+00 | 2024-10-22 21:01:25.105+00 | 74.982538    |     script_failure               | 4a3d0b76f01117aabbff24b6a7717144b1780f60 | 10174980    |    [logs]         |
| 8153907558 | pages       | success    | 2024-10-22 13:50:48.752+00 | 2024-10-22 14:38:16.103+00 | 494.913378   |                    | 4a3d0b76f01117aabbff24b6a7717144b1780f60 | 10174980    |          |

### Step 1. Label Dataset with FlakeRanker

```bash
flakeranker label ./data/jobs.csv -o ./results/ 
```

This command outputs the `./results/labeled_jobs.csv` file containing 2 additional columns:

- `flaky` (bool): Whether the job is flaky.
- `category` (str): The category label for flaky job failures.

### Step 2. Analyze Labeled Dataset

```bash
flakeranker analyze ./results/labeled_jobs.csv -o ./results/
```

This command outputs the `./results/rfm_dataset.csv` file containing the following columns:

- `category` (str): The flaky job failure category
- `recency` (int): Recency value of the category calculated as described in RQ3-4.
- `frequency` (int): Frequency value of the category as descibed in RQ1.
- `cost` (float): Monetary cost value of the category as calculated in RQ2.
- `machine_cost` (float): Machine cost component as calculated in RQ2.
- `diagnosis_cost` (float): Diagnosis cost component as calculated in RQ2.

### Step 3. Rank Categories using RFM Dataset

```bash
flakeranker rank ./results/rfm_dataset.csv --output=./results/
```

This command outputs the sorted `results/ranked_rfm_dataset.csv` file containing the following columns:

- `category` (str): The flaky job failure category
- `recency` (int): Recency value of the category calculated as described in RQ3-4.
- `frequency` (int): Frequency value of the category as descibed in RQ1.
- `cost` (int): Monetary cost value of the category as calculated in RQ2.
- `R` (int): R score based on the quintile method
- `F` (int): F score based on the quintile method
- `M` (int): M score based on the quintile method
- `cluster` (int): Cluster ID of the category. Similar categories found have the same cluster ID. An of -1 is assigned to identified outliers.
- `pattern` (str): The RFM pattern serving as ranking of the category. E.g., R+F+M+ for a high priority category.
