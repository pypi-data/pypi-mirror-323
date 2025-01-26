import os

import click

from djb.cli.djbrc import djbrc
from djb.cli.install import editable_djb, install


@click.command()
@click.pass_context
def up(ctx):
    """
    Install development dependencies and configure project env.

    Shorthand for `djb install && djb djbrc`

    This command verifies and installs project dependencies, then updates
    the project's `.djbrc` script based on the current project state.

    Tip: It's best to run `djb up` as `djb up && source .djbrc` to ensure that
    your shell environment reflects any changes.
    """
    ctx.invoke(install)
    ctx.invoke(djbrc)
