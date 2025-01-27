"""Label Command."""

import os
import click

from src.flakeranker import labeler


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
def label(input_file: str, output_dir: str):
    """Label an INPUT_FILE .csv dataset of build jobs having required columns:
    `id`, `name`, `status`, `failure_reason`, `commit`, `created_at`, `finished_at`, `duration`, `logs`, `project`
    """
    click.echo("Labeling...")
    input_file_base_name = os.path.basename(input_file)
    output_file_path = os.path.join(output_dir, f"labeled_{input_file_base_name}")
    labeler.label(input_file, output_file_path)
    return output_file_path
