"""FlakeRanker CLI tool module."""

import os
import click

from src.flakeranker import labeler, analyzer, ranker


@click.group(invoke_without_command=False)
@click.pass_context
def cli(ctx):
    """FlakeRanker CLI tool."""
    if not ctx.invoked_subcommand:
        print("FlakeRanker Hello World!")
    else:
        pass


@cli.command()
@click.argument(
    "input_file", type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
)
def run(input_file: str, output_dir: str):
    rank.callback(
        analyze.callback(label.callback(input_file, output_dir), output_dir), output_dir
    )


@cli.command()
@click.argument(
    "input_file", type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
)
def label(input_file: str, output_dir: str):
    """Label an INPUT_FILE .csv dataset of build jobs having required columns:
    `id`, `name`, `status`, `failure_reason`, `commit`, `created_at`, `finished_at`, `duration`, `logs`, `project`
    """
    click.echo("Labeling...")
    input_file_base_name = os.path.basename(input_file)
    output_file_path = os.path.join(output_dir, f"labeled_{input_file_base_name}")
    labeler.label(input_file, output_file_path)
    return output_file_path


@cli.command()
@click.argument(
    "input_file", type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
)
def analyze(input_file: str, output_dir: str):
    """Analyze an INPUT_FILE labeled dataset of build jobs, the output from the label sub-command.

    Outputs the RFM dataset of the categories.
    """
    click.echo("Analyzing...")
    output_file_path = os.path.join(output_dir, "rfm_dataset.csv")
    analyzer.analyze(input_file, output_file_path)
    click.echo(click.style("Analysis successfully finished! ", fg="green"))
    return output_file_path


@cli.command()
@click.argument(
    "input_file", type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
)
def rank(input_file: str, output_dir: str):
    """Rank flaky job failure categories using an INPUT_FILE rfm dataset, the output of the analyze sub-command"""
    click.echo("Ranking...")
    output_file_path = os.path.join(output_dir, "ranked_rfm_dataset.csv")
    ranker.rank(input_file, output_file_path)
    click.echo(click.style("Ranking successfully finished! ", fg="green"))


if __name__ == "__main__":
    cli()
