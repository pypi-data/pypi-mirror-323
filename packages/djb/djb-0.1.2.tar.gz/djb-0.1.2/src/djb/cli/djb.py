import os
from pathlib import Path

import click

from djb.cli.create import create
from djb.cli.ctx import DjbContext
from djb.cli.djbrc import djbrc
from djb.cli.install import install
from djb.cli.up import up


class OrderedGroup(click.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command_order = []

    def add_command(self, cmd, name=None):
        super().add_command(cmd, name)
        self.command_order.append(name or cmd.name)

    def list_commands(self, ctx):
        return self.command_order


@click.group(cls=OrderedGroup)
@click.option(
    "--project",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
    default=os.getenv("DJB_PROJECT_DIR", "."),
    envvar="DJB_PROJECT_DIR",
    show_default=True,
    show_envvar=True,
    help="Path to djb project directory.",
    metavar="DIR",
)
@click.option("--debug", is_flag=True, help="Enable debug output.")
@click.option("--verbose", is_flag=True, help="Enable verbose output.")
@click.pass_context
def djb(
    ctx,
    project,
    debug,
    verbose,
):
    """
    djb (dj_bun): playin' dev and deploy since 1984 🎶
    """
    ctx.ensure_object(DjbContext)
    ctx.obj.project = Path(project).resolve()
    ctx.obj.debug = debug
    ctx.obj.verbose = verbose


djb.add_command(create)
djb.add_command(up)
djb.add_command(djbrc)
djb.add_command(install)


def main():
    djb(max_content_width=100)


if __name__ == "__main__":
    main()
