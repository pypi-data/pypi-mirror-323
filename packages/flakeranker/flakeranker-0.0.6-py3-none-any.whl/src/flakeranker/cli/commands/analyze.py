"""Analyze Command."""

import os
import click
from datetime import date

from src.flakeranker import analyzer
from src.flakeranker.core.config import settings


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
@click.option(
    "-c",
    "--cost-infra-pricing-rate",
    type=float,
    default=settings.COST_INFRA_PRICING_RATE,
    show_default=True,
    required=False,
    help="CI Infrastructure per minute pricing rate. Defaults to $0.14 per min."
)
@click.option(
    "-d",
    "--cost-dev-hourly-rate",
    type=float,
    default=settings.COST_DEV_HOURLY_RATE,
    show_default=True,
    required=False,
    help="Hourly developer salary for cost estimation. Defaults to $36 per hour."
)
@click.option(
    "-r",
    "--recency-reference-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(settings.RECENCY_REFERENCE_DATE),
    show_default=True,
    required=False,
    help="Reference date for calcutating the recency."
)
@click.option(
    "-n",
    "--recency-n-last",
    type=int,
    default=str(settings.RECENCY_N_LAST),
    show_default=True,
    required=False,
    help="Number of last date points considered for calculating the recency."
)
def analyze(
    input_file: str,
    output_dir: str,
    cost_infra_pricing_rate: float,
    cost_dev_hourly_rate: float,
    recency_reference_date: date,
    recency_n_last: int,
):
    """Analyze an INPUT_FILE labeled dataset of build jobs, i.e. the output from the `label` command.

    Outputs the RFM dataset of the categories.
    """
    click.echo("Analyzing...")
    output_file_path = os.path.join(output_dir, "rfm_dataset.csv")
    analyzer.analyze(
        input_file_path=input_file,
        output_file_path=output_file_path,
        cost_infra_pricing_rate=cost_infra_pricing_rate,
        cost_dev_hourly_rate=cost_dev_hourly_rate,
        recency_reference_date=recency_reference_date,
        recency_n_last=recency_n_last,
    )
    click.echo(click.style("Analysis successfully finished! ", fg="green"))
    return output_file_path
