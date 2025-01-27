"""FlakeRanker CLI tool module."""

import click

from src.flakeranker.cli.utils.ordered_group import OrderedGroup
from src.flakeranker.cli.commands import label, analyze, rank, run


@click.group(invoke_without_command=False, cls=OrderedGroup)
@click.pass_context
def cli(ctx):
    """FlakeRanker CLI tool."""
    if not ctx.invoked_subcommand:
        print("FlakeRanker Hello World!")
    else:
        pass


cli.add_command(run)
cli.add_command(label)
cli.add_command(analyze)
cli.add_command(rank)


if __name__ == "__main__":
    cli()
