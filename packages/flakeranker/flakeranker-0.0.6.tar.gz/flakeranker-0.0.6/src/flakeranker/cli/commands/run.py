"""Run Command."""

from datetime import date
import click

from src.flakeranker.cli.commands import label, analyze, rank
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
def run(
    input_file: str,
    output_dir: str,
    cost_infra_pricing_rate: float,
    cost_dev_hourly_rate: float,
    recency_reference_date: date,
    recency_n_last: int,
):
    """Run the complete prioritization pipeline. label => analyze => rank."""
    rank.callback(
        analyze.callback(
            input_file=label.callback(input_file, output_dir),
            output_dir=output_dir,
            cost_infra_pricing_rate=cost_infra_pricing_rate,
            cost_dev_hourly_rate=cost_dev_hourly_rate,
            recency_reference_date=recency_reference_date,
            recency_n_last=recency_n_last,
        ),
        output_dir,
    )
