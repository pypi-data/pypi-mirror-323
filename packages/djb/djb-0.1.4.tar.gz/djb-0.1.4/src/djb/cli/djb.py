import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import click

from djb.cli.create import create
from djb.cli.djbrc import djbrc
from djb.cli.install import install
from djb.cli.lib.constants import ERR
from djb.cli.lib.ctx import DjbContext
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


def get_version():
    try:
        # Replace 'my-app' with the name of your project in pyproject.toml
        return version("djb")
    except PackageNotFoundError:
        return "unknown"


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
@click.version_option(version=get_version(), prog_name="djb")
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

    # Ensure project directory exits.
    if not ctx.obj.project.exists():
        if project == os.getenv("DJB_PROJECT_DIR"):
            click.echo(
                f"{ERR} Project directory {project} (from $DJB_PROJECT_DIR) does not exist."
            )
        else:
            click.echo(f"{ERR} Project directory {project} does not exist.")
        ctx.exit(1)

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
