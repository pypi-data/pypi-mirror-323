import itertools
import os
import re
import shutil
import subprocess
import traceback
from pathlib import Path
from typing import List

import click

from djb.cli.constants import DJB_REPO, ERR, NXT, OBS, SUC, TIP, WRN
from djb.cli.ctx import DjbInstallContext


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def missing_binaries(binaries: List[str]):
    missing_binaries = []
    for binary in binaries:
        if not command_exists(binary):
            missing_binaries.append(binary)
    return missing_binaries


def install_or_update_tool(
    ctx: click.Context,
    name: str,
    binaries: str | List[str],
    in_cmds: str | List[str],
    up_cmds: str | List[str],
):
    update = ctx.obj.update
    binaries = binaries if isinstance(binaries, list) else [binaries]
    in_cmds = in_cmds if isinstance(in_cmds, list) else [in_cmds]
    up_cmds = up_cmds if isinstance(up_cmds, list) else [up_cmds]

    if update:
        if missing_binaries_ := missing_binaries(binaries):
            if len(missing_binaries_) < len(binaries):
                click.echo(
                    f"{WRN} `{name}` update requested but `{name}` is not fully installed yet. The following binaries are missing: {' '.join(missing_binaries_)}"
                )
            else:
                click.echo(
                    f"{WRN} `{name}` update requested but `{name}` is not installed yet."
                )
            click.echo(f"{TIP} Use `djb up && source .djbrc` to install `{name}`.")
        else:
            click.echo(f"{NXT} `{name}` updating...")
            try:
                for cmd in up_cmds:
                    if ctx.obj.verbose:
                        click.echo(f"{NXT} Executing `{cmd}`...")
                    subprocess.run(cmd, shell=True, check=True)
                if missing_binaries_ := missing_binaries(binaries):
                    click.echo(
                        f"{WRN} `{name}` updated without errors, but the following binaries are now missing: {' '.join(missing_binaries_)}"
                    )
                else:
                    click.echo(f"{SUC} `{name}` updated.")
            except subprocess.CalledProcessError as e:
                click.echo(
                    f"{ERR} `{name}` failed to execute update command `{cmd}`: {e}",
                    err=True,
                )
                if ctx.obj.debug:
                    traceback.print_exc()

    else:
        if not missing_binaries(binaries):
            click.echo(f"{SUC} `{name}` is already installed.")
            return

        click.echo(f"{NXT} `{name}` installing...")
        try:
            for cmd in in_cmds:
                if ctx.obj.verbose:
                    click.echo(f"{NXT} Executing `{cmd}`...")
                subprocess.run(cmd, shell=True, check=True)
            if missing_binaries_ := missing_binaries(binaries):
                click.echo(
                    f"{WRN} `{name}` installed without errors, but the following binaries are still missing: {' '.join(missing_binaries_)}"
                )
            else:
                click.echo(f"{SUC} `{name}` installed.")
        except subprocess.CalledProcessError as e:
            click.echo(
                f"{ERR} `{name}` failed to execute install command `{cmd}`: {e}",
                err=True,
            )
            if ctx.obj.debug:
                traceback.print_exc()


@click.group(chain=True, invoke_without_command=True)
@click.option(
    "--update",
    is_flag=True,
    help="Update installed development dependencies.",
)
@click.pass_context
def install(ctx: click.Context, update):
    """
    Install development dependencies.
    """
    parent_context = ctx.obj
    ctx.ensure_object(DjbInstallContext)
    ctx.obj.__dict__.update(parent_context.__dict__)
    ctx.obj.update = update

    if not ctx.invoked_subcommand:
        click.echo(f"{NXT} Verifying and installing dependencies...")
        for installer in DEFAULT_INSTALLERS:
            ctx.invoke(installer)


@install.command()
@click.pass_context
def homebrew(ctx):
    """Install homebrew."""
    install_or_update_tool(
        ctx,
        name="homebrew",
        binaries="brew",
        in_cmds='/bin/bash -c "$(curl -LsSf https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        up_cmds="brew update",
    )


@install.command()
@click.pass_context
def uv(ctx):
    """Install uv."""
    install_or_update_tool(
        ctx,
        name="uv",
        binaries="uv",
        in_cmds="curl -LsSf https://astral.sh/uv/install.sh | sh",
        up_cmds="uv self update",
    )


def ensure_uv(ctx):
    if not command_exists("uv"):
        click.echo(f"{ERR} `uv` is not installed or not in PATH.")
        click.echo(
            f"{TIP} `uv` and djb's other development dependencies are installed using `djb up && source .djbrc`."
        )
        ctx.exit(1)


@install.command()
@click.pass_context
def venv(ctx):
    ensure_uv(ctx)

    project = ctx.obj.project
    venv_path = project / ".venv"

    click.echo(f"{NXT} Creating virtual environment in '{venv_path}'...")
    try:
        cmd = [
            "uv",
            "venv",
            "--allow-existing",
            "--project",
            str(project),
            "--directory",
            str(project),
            "--prompt",
            project.name,
            str(venv_path),
        ]
        click.echo(f"{OBS} Executing {cmd}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(
            f"{ERR} Failed to create virtual environment in '{venv_path}': {e}",
            err=True,
        )
        if ctx.obj.debug:
            traceback.print_exc()
        ctx.exit(1)
    click.echo(f"{SUC} Created virtual environment in '{venv_path}'.")

    click.echo(f"{NXT} Install python packages in '{venv_path}'...")
    try:
        cmd = [
            "uv",
            "pip",
            "install",
            str(project),
            "--directory",
            str(project),
            "--prerelease",
            "allow",
        ]
        click.echo(f"{OBS} Executing {cmd}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(
            f"{ERR} Failed to install python packages in '{project}': {e}",
            err=True,
        )
        if ctx.obj.debug:
            traceback.print_exc()
        ctx.exit(1)
    click.echo(f"{SUC} Installed python packages in '{venv_path}'.")


@install.command()
@click.option(
    "--djb-repo",
    default=DJB_REPO,
    show_default=True,
    help="Git repository URL for djb.",
)
@click.option(
    "--djb-dir",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    default="./editable-djb",
    show_default=True,
    help="Path to the directory where djb is checked out.",
    metavar="DIR",
)
@click.option(
    "--no-gitignore",
    is_flag=True,
    help="Skip adding the project-relative --djb-dir to the project's .gitignore.",
)
@click.pass_context
def editable_djb(ctx, djb_repo, djb_dir, no_gitignore):
    """
    Optional; checkout and install djb as an editable dependency.

    Note: By default, djb projects come with `/editable-djb/` included in their
    .gitignore. When you use a custom `--djb-dir`, that custom directory is
    also added to the project's .gitignore, unless `--no-gitignore` is set or
    `--djb-dir` is outside the project directory.
    """
    ensure_uv(ctx)

    project = ctx.obj.project
    update = ctx.obj.update
    djb_path = Path(djb_dir).resolve()

    # Ensure project directory exists and switch to it.
    if not project.exists():
        click.echo(f"{ERR} Project directory {project} does not exist.")
        ctx.exit(1)
    os.chdir(project)

    if djb_path.exists():
        if update:
            click.echo(f"{NXT} Updating djb in '{djb_path}'...")
            try:
                subprocess.run(["git", "-C", str(djb_path), "pull"], check=True)
                click.echo(f"{SUC} djb updated.")
            except subprocess.CalledProcessError as e:
                click.echo(
                    f"{ERR} Failed to update djb repository in {djb_path}: {e}",
                    err=True,
                )
                if ctx.obj.debug:
                    traceback.print_exc()
                ctx.exit(1)
        else:
            click.echo(f"{OBS} djb repository is already present at '{djb_path}'.")
    else:
        if update:
            click.echo(
                f"{WRN} `editable-djb` update requested but an editable djb repository is not installed in '{djb_path}' yet."
            )
            click.echo(
                f"{TIP} Use `djb install editable-djb` to install djb in editable mode."
            )
            ctx.exit(1)

        click.echo(f"{NXT} Cloning djb repository from {djb_repo} into {djb_path}...")
        try:
            subprocess.run(["git", "clone", djb_repo, str(djb_path)], check=True)
            click.echo(f"{SUC} djb repository cloned.")
        except subprocess.CalledProcessError as e:
            click.echo(
                f"{ERR} Failed to clone djb repository from {djb_repo}: {e}",
                err=True,
            )
            if ctx.obj.debug:
                traceback.print_exc()
            ctx.exit(1)

    # Install djb in editable mode
    click.echo(f"{NXT} Installing djb in editable mode from '{djb_path}'...")
    try:
        cmd = [
            "uv",
            "pip",
            "install",
            "--project",
            str(project),
            "--editable",
            str(djb_path),
            "--reinstall-package",
            "djb",
        ]
        if ctx.obj.verbose:
            click.echo(f"Running `uv pip install` command: {cmd}")
        subprocess.run(cmd, check=True)
        click.echo(f"{SUC} djb installed in editable mode.")
    except subprocess.CalledProcessError as e:
        click.echo(
            f"{ERR} Failed to install djb in editable mode from {djb_path}: {e}",
            err=True,
        )
        if ctx.obj.debug:
            traceback.print_exc()
        ctx.exit(1)

    # Add project-relative djb lib path to .gitignore if it's inside the
    # project, and not added alraedy.
    if not no_gitignore and djb_path.is_relative_to(project):
        djb_lib_rel_path = f"/{djb_path.relative_to(project).as_posix()}/"
        gitignore_path = project / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                gitignore_content = f.read()
        else:
            gitignore_content = ""
        if not re.search(
            rf"^{re.escape(djb_lib_rel_path)}$", gitignore_content, re.MULTILINE
        ):
            with open(gitignore_path, "a") as f:
                f.write(f"# Added by `djb install editable-djb`.\n")
                f.write(f"{str(djb_lib_rel_path)}\n")
            click.echo(f"{NXT} Added '{djb_lib_rel_path}' to .gitignore.")
        else:
            if ctx.obj.verbose:
                click.echo(f"{OBS} {djb_lib_rel_path} is already in .gitignore.")


DEFAULT_INSTALLERS = [homebrew, uv, venv]
