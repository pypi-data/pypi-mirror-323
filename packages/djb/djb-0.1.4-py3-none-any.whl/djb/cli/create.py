import os
import re
import readline  # noqa
import subprocess
import sys
from pathlib import Path

import click

from djb.cli.lib.constants import ERR, FAI, NXT, OBS, SUC, TEMPLATE_REPO
from djb.cli.up import up

# RFC 1123 regex to validate that a project name is compatible with k8s.
RFC_1123_REGEX = r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))*$"

PROJECT_NAME_REQUIREMENTS = """\b
For the project name to be compatible with a wide range of tools, it must
follow the DNS label standard as defined by RFC 1123:
\b
- contain at most 63 characters
- contain only lowercase alphanumeric characters or '-'
- start with an alphanumeric character
- end with an alphanumeric character
"""

PROJECT_DOCSTRING = f"""
Create a new djb project.

Prompts you for a project name, unless given via --name.

The project is created as a subdirectory of --directory.

{PROJECT_NAME_REQUIREMENTS}
"""


def validate_project_name(name):
    """
    Validate input against RFC 1123 hostname rules.
    """
    if not re.match(RFC_1123_REGEX, name):
        raise click.BadParameter(
            f"'{name}' is not a valid project name.\n{PROJECT_NAME_REQUIREMENTS}"
        )
    return name


def readline_prompt(prompt, validator, max_retries=3):
    for _ in range(max_retries):
        print(prompt, file=sys.stderr, end=":\n", flush=True)
        user_input = input("> ")
        try:
            return validator(user_input)
        except click.BadParameter as e:
            print(f"{ERR} {e}", file=sys.stderr)
    raise click.ClickException(f"{FAI} Maximum retries exceeded.")


@click.command(help=PROJECT_DOCSTRING)
@click.option("--name", help="Project name.")
@click.option(
    "--directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
    default=".",
    show_default=True,
    help="The new project is created relative to this directory.",
    metavar="DIR",
)
@click.option(
    "--template-repo",
    default=TEMPLATE_REPO,
    show_default=True,
    help="Git repository URL for the djb project template.",
)
@click.option(
    "--project-dir-file",
    type=click.File("w"),
    help="Write project directory path into this file.",
    metavar="FILE",
)
@click.pass_context
def create(ctx, name, directory, template_repo, project_dir_file):
    parent_path = Path(directory).resolve()

    # Welcome!
    click.echo("Welcome to djb!\n")
    click.echo("This script will create a new djb project.\n")
    click.echo("Let's get started!\n")

    # Prompt for project_name if it is not provided.
    if name:
        validate_project_name(name)
    else:
        name = readline_prompt("Please enter your project name", validate_project_name)

    # Create project directory.
    project = parent_path / name
    if project.exists():
        click.echo(
            f"{OBS} The directory '{project}' already exists. Using the existing directory..."
        )
    else:
        project.mkdir(parents=True)
        click.echo(f"{SUC} Created project directory.")

    # Clone djb project template.
    try:
        click.echo(
            f"{NXT} Cloning repository from '{template_repo}' into '{project}'..."
        )
        subprocess.run(["git", "clone", template_repo, project], check=True)
        click.echo(f"{SUC} Repository cloned.")
    except Exception as e:
        click.echo(f"{ERR} Failed to clone repository. {e}")

    # Configure project and install dependencies.
    ctx.obj.project = project
    ctx.invoke(up)

    # If given a file, write the project path to it.
    if project_dir_file:
        project_dir_file.write(str(project))


if __name__ == "__main__":
    create()
