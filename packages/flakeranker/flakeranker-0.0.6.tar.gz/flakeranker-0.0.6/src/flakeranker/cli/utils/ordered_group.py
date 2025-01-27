"""Utility to display CLI commands help in a defined order."""

import click
import collections
from typing import Mapping, Optional


class OrderedGroup(click.Group):

    def __init__(
        self,
        name: Optional[str] = None,
        commands: Optional[Mapping[str, click.Command]] = None,
        **kwargs
    ):
        super(OrderedGroup, self).__init__(name, commands, **kwargs)
        #: the registered subcommands by their exported names.
        self.commands = commands or collections.OrderedDict()

    def list_commands(self, ctx: click.Context) -> Mapping[str, click.Command]:
        return self.commands
