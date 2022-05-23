# Author: Albert Esteve <aesteve@redhat.com>
#
# This file is licensed under the GNU General Public License.
# Please see the LICENSE file

from pathlib import Path
from typing import Optional

import click

from . import log, add_file_handler
from .config import DEFAULT_CFG_PATH
from .config import create_config
from .list import list_branches
from .list import _get_github_merged_prs
from .prune import prune_local
from .prune import prune_remote


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--debug', '-d', is_flag=True,
              help='Log debug messages into a file.', default=False)
def cli(debug: bool):
    """
    Prune local and remote branches that have been merged, even if it
    has been merged by rebasing. Currently supported only for GitHub projects.
    """
    if debug:
        add_file_handler()


@click.command()
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
        exit(1)
    create_config(path, token, user, repo)


@click.command()
@click.option('--config', '-c', type=click.Path(dir_okay=False, exists=True),
              default=DEFAULT_CFG_PATH, help='Path to the config file.')
def ls(config: Path) -> None:
    # pylint: disable=invalid-name
    """
    List branches that will be deleted in a prune.
    """
    list_branches(config)


@click.command()
@click.option('--config', '-c', type=click.Path(dir_okay=False, exists=True),
              default=DEFAULT_CFG_PATH, help='Path to the config file.')
@click.option('--local/--remote', '-l/-r', is_flag=True, default=True)
@click.option('--all', is_flag=True, default=False,
              help='Prune both remote and local branches.')
@click.option('--yes', is_flag=True, default=False, help='Do not ask for confirmation.')
def pr(config: Path, local: bool, all: bool, yes: bool) -> None:
    # pylint: disable=invalid-name
    """
    Prune all branches (local or remote) that have been merged.
    Branches are deleted based on the SHA1 of the HEAD of the branch
    and the status of the Pull Request in GitHub.
    """
    if all:
        gh_pr = _get_github_merged_prs(config)
        prune_remote(config, yes, gh_pr)
        prune_local(config, yes, gh_pr)
    elif local:
        prune_local(config, yes)
    else:
        prune_remote(config, yes)


cli.add_command(config)
cli.add_command(ls)
cli.add_command(pr)
