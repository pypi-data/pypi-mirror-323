# FlakeRanker

FlakeRanker is a CLI tool associated to the paper [On the Diagnosis of Flaky Job Failures: Understanding and Prioritizing Failure Categories](https://arxiv.org/abs/2501.04976) accepted at the 47th International Conference on Software Engineering ICSE SEIP 2025.

This CLI tool enables automated labeling of flaky job failures with failure categories and prioritization of the categories using RFM modeling.

[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/devopsirc/telus-flaky-job-failures-prioritization)

## ⚙️ Installation with Docker (recommended)

Clone the GitHub repository

```bash
git clone https://github.com/devopsirc/telus-flaky-job-failures-prioritization.git
```

Build the Docker image

```bash
docker build --tag flakeranker --file docker/Dockerfile .
```

## 🚀 Quickstart Example

For demonstration purpose, we provide in the `example/data/` directory, a .csv dataset of 57,350 build jobs collected from the open-source project [Veloren](https://gitlab.com/veloren/veloren) hosted on GitLab. In the following example steps, all the outputs of the flakeranker commands are saved in the `example/results/` directory specified with the option `-o` (or `--output-dir`).

### Step 0. Unzip the Dataset

```bash
unzip example/data/veloren.zip example/data/
```

It outputs inside the `example/data/veloren/` directory, the `jobs.csv` and `labeled_jobs.csv` files.

Overview of the input `jobs.csv` dataset

| **id**     | **name**    | **status** | **created_at**             | **finished_at**            | **duration** | **failure_reason** | **commit**                               | **project** | **logs** |
|------------|-------------|------------|----------------------------|----------------------------|--------------|--------------------|------------------------------------------|-------------|----------|
| 8169884262 | security    | success    | 2024-10-23 21:21:41.701+00 | 2024-10-23 21:38:33.728+00 | 329.987579   |                    | 71ef5d084bb13c8b1e73aabce8a559e50536fc11 | 10174980    |          |
| 8169738883 | translation | failed    | 2024-10-23 21:00:18.592+00 | 2024-10-23 21:01:13.11+00  | 50.088166    |                    | 4a3d0b76f01117aabbff24b6a7717144b1780f60 | 10174980    |   [logs]       |
| ... | ...    | ...    | ... | ... | ...   |     ...               | ... | ...    |...          |
| 8158010241 | benchmarks  | success    | 2024-10-22 21:00:08.719+00 | 2024-10-22 21:21:42.926+00 | 1292.721363  |                    | 4a3d0b76f01117aabbff24b6a7717144b1780f60 | 10174980    |          |
| 8158010236 | translation | failed    | 2024-10-22 21:00:08.703+00 | 2024-10-22 21:01:25.105+00 | 74.982538    |     script_failure               | 4a3d0b76f01117aabbff24b6a7717144b1780f60 | 10174980    |    [logs]         |
| 8153907558 | pages       | success    | 2024-10-22 13:50:48.752+00 | 2024-10-22 14:38:16.103+00 | 494.913378   |                    | 4a3d0b76f01117aabbff24b6a7717144b1780f60 | 10174980    |          |

**NOTE.** If only interested in running the complete prioritization pipeline in one command, please skip to the section `No Step` at the bottom of this page.

### Step 1. Label Dataset with FlakeRanker

Using the Docker Image

```sh
docker run \
-v ./example/data/veloren/jobs.csv:/opt/flakeranker/jobs.csv \
-v ./example/results/:/opt/flakeranker/ \
flakeranker label /opt/flakeranker/jobs.csv -o /opt/flakeranker/
```

Using the Python Package

```bash
flakeranker label example/data/veloren/jobs.csv -o example/results/ 
```

The `flakeranker label` command outputs the `labeled_jobs.csv` file containing 2 additional columns:

- `flaky` (bool): Whether the job is flaky.
- `category` (str): The category label for flaky job failures.

### Step 2. Analyze Labeled Dataset

Using the Docker Image

```bash
docker run \
-v ./example/results/labeled_jobs.csv:/opt/flakeranker/labeled_jobs.csv \
-v ./example/results/:/opt/flakeranker/ \
flakeranker analyze /opt/flakeranker/labeled_jobs.csv -o /opt/flakeranker/
```

Using the Python Package

```bash
flakeranker analyze example/results/labeled_jobs.csv -o example/results/
```

The `flakeranker analyze` command outputs the `rfm_dataset.csv` file containing the following columns:

- `category` (str): The flaky job failure category
- `recency` (int): Recency value of the category calculated as described in RQ3-4.
- `frequency` (int): Frequency value of the category as descibed in RQ1.
- `cost` (float): Monetary cost value of the category as calculated in RQ2.
- `machine_cost` (float): Machine cost component as calculated in RQ2.
- `diagnosis_cost` (float): Diagnosis cost component as calculated in RQ2.

### Step 3. Rank Categories using the RFM Dataset

Using the Docker Image

```bash
docker run \
-v ./example/results/rfm_dataset.csv:/opt/flakeranker/rfm_dataset.csv \
-v ./example/results/:/opt/flakeranker/ \
flakeranker rank /opt/flakeranker/rfm_dataset.csv -o /opt/flakeranker/
```

Using the Python Package

```bash
flakeranker rank example/results/rfm_dataset.csv -o example/results/
```

The `flakeranker rank` command outputs the sorted `ranked_rfm_dataset.csv` file containing the following columns:

- `category` (str): The flaky job failure category
- `recency` (int): Recency value of the category calculated as described in RQ3-4.
- `frequency` (int): Frequency value of the category as descibed in RQ1.
- `cost` (int): Monetary cost value of the category as calculated in RQ2.
- `R` (int): R score based on the quintile method
- `F` (int): F score based on the quintile method
- `M` (int): M score based on the quintile method
- `cluster` (int): Cluster ID of the category. Similar categories found have the same cluster ID. An of -1 is assigned to identified outliers.
- `pattern` (str): The RFM pattern serving as ranking of the category. From `R+F+M+` for high priority categories a the top, to `R-F-M-` for irrelevant categories at the bottom.

### No Step. Run the Complete RFM Prioritization Pipeline

Using the Docker Image

```sh
docker run \
-v ./example/data/veloren/jobs.csv:/opt/flakeranker/jobs.csv \
-v ./example/results/:/opt/flakeranker/ \
flakeranker run /opt/flakeranker/jobs.csv -o /opt/flakeranker/
```

Using the Python Package

```sh
flakeranker run ./example/data/veloren/jobs.csv -o ./example/results/
```

The `flakeranker run` command outputs the  `labeled_jobs.csv`,  `rfm_dataset.csv`, and  `ranked_rfm_dataset.csv` files as described above in each step.

## 🗒️ Help

Display the help information available for the CLI. Help is also available for each specific flakeranker command.

Using the Docker Image

```sh
docker run flakeranker --help
```

Using the Python Package

```sh
flakeranker --help
```
