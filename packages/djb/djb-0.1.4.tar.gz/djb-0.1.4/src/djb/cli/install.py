import os
import re
import shutil
from pathlib import Path
from typing import List

import click

from djb.cli.lib.constants import DJB_REPO, ERR, NXT, OBS, SUC, TIP, WRN
from djb.cli.lib.ctx import DjbInstallContext
from djb.cli.lib.shell import run_cmd


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
                    f"{WRN} `{name}` update requested but `{name}` is not installed yet"
                )
            click.echo(f"{TIP} Use `djb up && source .djbrc` to install `{name}`")
        else:
            click.echo(f"{NXT} `{name}` updating")
            for cmd in up_cmds:
                run_cmd(ctx, cmd, error=f"Failed to execute update command: {cmd}")
            if missing_binaries_ := missing_binaries(binaries):
                click.echo(
                    f"{WRN} `{name}` updated without errors, but the following binaries are now missing: {' '.join(missing_binaries_)}"
                )
            else:
                click.echo(f"{SUC} `{name}` updated")

    else:
        if not missing_binaries(binaries):
            click.echo(f"{SUC} `{name}` is already installed")
            return

        click.echo(f"{NXT} `{name}` installing")
        for cmd in in_cmds:
            run_cmd(ctx, cmd, error=f"Failed to execute install command: {cmd}")
        if missing_binaries_ := missing_binaries(binaries):
            click.echo(
                f"{WRN} `{name}` installed without errors, but the following binaries are still missing: {' '.join(missing_binaries_)}"
            )
        else:
            click.echo(f"{SUC} `{name}` installed")


@click.group(chain=True, invoke_without_command=True)
@click.option(
    "--update",
    is_flag=True,
    help="Update installed development dependencies",
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
        click.echo(f"{NXT} Verifying and installing dependencies")
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
        click.echo(f"{ERR} `uv` is not installed or not in PATH")
        click.echo(
            f"{TIP} `uv` and djb's other development dependencies are installed using `djb up && source .djbrc`"
        )
        ctx.exit(1)


@install.command()
@click.pass_context
def venv(ctx):
    ensure_uv(ctx)

    project = ctx.obj.project

    run_cmd(
        ctx,
        ["uv", "sync", "--project", str(project), "--directory", str(project)],
        f"Installing python packages for '{project}'",
        "Python packages installed",
        "Failed to install python packages",
    )


def shortest_path(root: Path, other: Path) -> Path:
    """
    Returns a relative path from root to other if other is relative to root.
    Returns other otherwise.
    """
    if other.is_relative_to(root):
        return other.relative_to(root)
    else:
        return other


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
    default=".djb",
    show_default=True,
    help="Path to the directory where djb is checked out.",
    metavar="DIR",
)
@click.option(
    "--revert",
    is_flag=True,
    help="Revert back to using the most recently released djb.",
)
@click.option(
    "--no-gitexclude",
    is_flag=True,
    help="""
    Skip adding the project-relative --djb-dir to the project's
    .git/info/exclude.
    """,
)
@click.pass_context
def editable_djb(ctx, djb_repo, djb_dir, revert, no_gitexclude):
    """
    Optional; checkout and install djb as an editable dependency.

    Note: By default, --djb-dir is added to the project's .git/info/exclude,
    unless `--no-gitexclude` is set or `--djb-dir` is outside the project
    directory.
    """
    ensure_uv(ctx)

    project = ctx.obj.project
    update = ctx.obj.update
    djb_path = Path(djb_dir).resolve()

    if djb_path.exists():
        if update:
            run_cmd(
                ctx,
                ["git", "-C", str(djb_path), "pull"],
                f"Updating djb repository in '{djb_path}'",
                "Editable djb repository updated",
                "Failed to update djb repository",
            )
        else:
            click.echo(f"{OBS} djb repository is already present at '{djb_path}'")
    else:
        if update:
            click.echo(
                f"{WRN} `editable-djb` update requested but an editable djb repository is not installed in '{djb_path}' yet"
            )
            click.echo(
                f"{TIP} Use `djb install editable-djb` to install djb in editable mode"
            )
            ctx.exit(1)

        run_cmd(
            ctx,
            ["git", "clone", djb_repo, str(djb_path)],
            f"Cloning djb repository from '{djb_repo}' into '{djb_path}'",
            "djb repository cloned",
            "Failed to clone djb repository",
        )

    if revert:
        run_cmd(
            ctx,
            ["uv", "add", "djb", "--reinstall-package", "djb"],
            "Uninstalling djb editable mode",
            "djb editable mode uninstalled",
            "Failed to uninstall djb editable mode",
        )
    else:
        run_cmd(
            ctx,
            [
                "uv",
                "pip",
                "install",
                "--project",
                str(project),
                "--editable",
                str(djb_path),
                "--reinstall-package",
                "djb",
            ],
            f"Installing djb in editable mode from '{djb_path}'",
            "djb installed in editable mode",
            f"Failed to install djb in editable mode from '{djb_path}'",
        )

        # Add project-relative djb lib path to .git/info/exclude if it's inside the
        # project, and not added alraedy.
        if not no_gitexclude and djb_path.is_relative_to(project):
            dot_git_file_path = project / ".git"
            if not dot_git_file_path.exists():
                click.echo(
                    f"{WRN} Skipping adding '{djb_path}' to .git/info/exclude because '{project}' is not a git repository"
                )
            
            gitexclude_path = project / ".git/info/exclude"

            # Check if .git is a file (when this is a submodule) and follow the
            # gitdir: <path> to the actual .git directory.
            if not dot_git_file_path.is_dir():
                dot_git_file_content = dot_git_file_path.read_text()
                gitdir_path_re = re.compile(r"^gitdir: (.+)$")
                gitdir_path_match = gitdir_path_re.search(dot_git_file_content)
                if gitdir_path_match:
                    gitexclude_path = Path(gitdir_path_match.group(1)) / "info/exclude"
                else:
                    click.echo(
                        f"{WRN} Skipping adding '{djb_path}' to .git/info/exclude because .git file does not contain a gitdir line"
                    )

            if gitexclude_path.exists():
                with open(gitexclude_path, "r") as f:
                    gitexclude_content = f.read()
            else:
                gitexclude_content = ""

            djb_lib_rel_path = f"/{shortest_path(project, djb_path).as_posix()}/"
            if not re.search(
                rf"^{re.escape(djb_lib_rel_path)}$", gitexclude_content, re.MULTILINE
            ):
                with open(gitexclude_path, "a") as f:
                    f.write(f"# Added by `djb install editable-djb`.\n")
                    f.write(f"{str(djb_lib_rel_path)}\n")
                click.echo(f"{NXT} Added '{djb_lib_rel_path}' to '{gitexclude_path}'")
            else:
                if ctx.obj.verbose:
                    click.echo(f"{OBS} {djb_lib_rel_path} is already in '{gitexclude_path}'")


DEFAULT_INSTALLERS = [homebrew, uv, venv]
