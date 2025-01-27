"""Rank Command."""

import os
import click

from src.flakeranker import ranker


@click.command()
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
    """Rank an INPUT_FILE rfm dataset of flaky job failure categories, i.e. the output of the `analyze` command"""
    click.echo("Ranking...")
    output_file_path = os.path.join(output_dir, "ranked_rfm_dataset.csv")
    ranker.rank(input_file, output_file_path)
    click.echo(click.style("Ranking successfully finished! ", fg="green"))
