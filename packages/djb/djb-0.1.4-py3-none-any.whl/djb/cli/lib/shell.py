import subprocess
import traceback
from typing import List, Optional

import click

from djb.cli.lib.constants import ERR, NXT, SUC


def run_cmd(
    ctx: click.Context,
    cmd: str | List[str],
    what: Optional[str] = None,
    success: Optional[str] = None,
    error: str = None,
):
    assert error, "Error message must be provided."

    if what:
        click.echo(f"{NXT} {what.rstrip('.')}...")
    if ctx.obj.verbose:
        if isinstance(cmd, list):
            click.echo(f"  {NXT} Executing {cmd}...")
        else:
            click.echo(f"  {NXT} Executing '{cmd}'...")
    try:
        subprocess.run(cmd, check=True, shell=isinstance(cmd, str))
        if success:
            click.echo(f"{SUC} {success}")
    except subprocess.CalledProcessError as e:
        click.echo(f"{ERR}: {error}")
        click.echo(f"Error: {e}")
        if ctx.obj.debug:
            traceback.print_exception()
        ctx.exit(1)
