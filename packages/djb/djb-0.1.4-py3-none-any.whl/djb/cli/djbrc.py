import os
from pathlib import Path

import click

from djb.cli.lib.constants import ERR, SUC


@click.command()
@click.pass_context
def djbrc(ctx):
    """
    Update `.djbrc` script based on the project's current state.

    Tip: It's best to run `djb djbrc` as `djb djbrc && source .djbrc` to ensure
    that your shell environment reflects any changes.
    """
    project = ctx.obj.project
    djbrc_file_path = project / ".djbrc"

    click.echo(f"→ Updating '{djbrc_file_path}'...")

    # Update `.djbrc`
    djbrc_content = f"""\
# .djbrc

# Ensure .djbrc can only be sourced.
# This works because return only works inside a function or a sourced script.
( return 0 2>/dev/null ) || {{
    echo "$(basename "$0") must be sourced. Use: \\`. "$0"\\`" >&2
    exit 1
}}

# Wrapper around venv deactivate.
djb-deactivate() {{
    # Deactivate virtual environment.
    # We piggy-back on deactivate to restore our own changes to PATH and PS1.
    if command -v deactivate >/dev/null 2>&1; then
        deactivate
    fi

    if [ -n "${{DJB_CLEAN_PS1:-}}" ]; then
        unset DJB_CLEAN_PS1
    fi

    unset DJB_PROJECT_DIR

    if [ "${{1:-}}" != "spare_deactivate_function" ]; then
        unset djb-deactivate
    fi
}}

# Deactivate any previously activated djb application.
djb-deactivate "spare_deactivate_function"

source .venv/bin/activate

# Exports.
export DJB_PROJECT_DIR={project}
"""
    try:
        with djbrc_file_path.open("w") as file:
            file.write(djbrc_content)
        click.echo(f"{SUC} Updated '{djbrc_file_path}'.")
    except Exception as e:
        click.echo(f"{ERR} Failed to update '{djbrc_file_path}': {e}", err=True)
