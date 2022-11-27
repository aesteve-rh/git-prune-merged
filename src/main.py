# SPDX-FileCopyrightText: 2022 Albert Esteve <aesteve@redhat.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Main aplication CLI.
"""

import sys
from pathlib import Path
from typing import Optional

import click

from . import __version__, add_file_handler, log
from .config import DEFAULT_CFG_PATH, create_config
from .exceptions import exception_handler
from .list import list_branches, GithubBranches
from .prune import prune_local, prune_remote

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def print_version(ctx, param, value):
    # pylint: disable=unused-argument
    """
    Print version and exit.
    """
    if not value or ctx.resilient_parsing:
        return
    click.echo(f'git-prune-merged version: {__version__}')
    ctx.exit()


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.pass_context
@exception_handler
@click.option('--debug', '-d', is_flag=True,
              help='Log debug messages into a file.', default=False)
@click.option('--version', '-v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Print version and exit.')
@click.option('--config', '-c', 'configuration', type=click.Path(dir_okay=False, exists=True),
              default=DEFAULT_CFG_PATH, help='Path to the config file.')
@click.option('--local/--remote', '-l/-r', is_flag=True, default=True, show_default=True,
              help='Select to prune only local or remote merged branches.')
@click.option('--all', 'all_branches', is_flag=True, default=False,
              help='Prune both remote and local merged branches.')
@click.option('--months', type=int, default=0,
              help='Select PRs older than specified months.')
@click.option('--yes', is_flag=True, default=False, help='Do not ask for confirmation.')
@click.option('--dry-run', is_flag=True, default=False,
              help='Simulated run, do not delete branches.')
def cli(ctx, debug: bool, configuration: Path, local: bool,
        all_branches: bool, months: int, yes: bool, dry_run: bool) -> None:
    # pylint: disable=too-many-arguments, unused-argument
    """
    Prune local and remote branches that have been merged, even if it
    has been merged by rebasing.

    Currently supported only for GitHub projects.

    Branches are deleted based on the SHA1 of the HEAD of the branch
    and the status of the Pull Request in GitHub.
    """
    if debug:
        add_file_handler()
    if ctx.invoked_subcommand is None:
        # With no subcommmand, we prune the branches
        gh_pr = GithubBranches(configuration, months).branches
        if local or all_branches:
            prune_local(yes, dry_run, gh_pr)
        if not local or all_branches:
            prune_remote(yes, dry_run, gh_pr)


@cli.command()
@exception_handler
@click.option('--path', '-p', type=click.Path(dir_okay=False),
              default=DEFAULT_CFG_PATH, help='Path to the config file.')
@click.option('--token', '-t', type=str,
              help='Specify token for GitHub login [recommended].')
@click.option('--user', '-u', type=str,
              help='Specify user for GitHub login.')
@click.option('--repo', '-r', type=str, required=True)
def config(
        path: Path,
        token: Optional[str],
        user: Optional[str],
        repo: Optional[str]) -> None:
    """
    Setup the configuration file to use.
    """
    if not token and not user:
        log.error('Need at least the token or the user to login.')
        sys.exit(1)
    create_config(path, token, user, repo)


@cli.command()
@exception_handler
@click.option('--config', '-c', 'configuration', type=click.Path(dir_okay=False, exists=True),
              default=DEFAULT_CFG_PATH, help='Path to the config file.')
@click.option('--months', type=int, default=0,
              help='Select PRs older than specified months.')
def ls(configuration: Path, months: int) -> None:
    # pylint: disable=invalid-name
    """
    List branches that will be deleted in a prune.
    """
    list_branches(configuration, months)
