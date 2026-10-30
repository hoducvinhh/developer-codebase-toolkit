"""Environment Checker (envcheck) CLI implementation."""

from typing import List
import click


class DefaultGroup(click.Group):
    """Click group that defaults to 'audit' command when no recognized command is given."""
    def parse_args(self, ctx: click.Context, args: List[str]) -> List[str]:
        if not args:
            args = ["audit"]
        elif args[0] not in self.commands and args[0] not in ("--help", "-h", "--version"):
            args = ["audit"] + args
        return super().parse_args(ctx, args)


@click.group(cls=DefaultGroup)
@click.version_option(version="0.1.0", prog_name="envcheck")
def main() -> None:
    """Environment configuration validator and secret auditor."""
    pass
