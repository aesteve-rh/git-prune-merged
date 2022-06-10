# Author: Albert Esteve <aesteve@redhat.com>
#
# This file is licensed under the GNU General Public License.
# Please see the LICENSE file

"""
Offers utility functions to obtain and log local and remote branches
that can be potentially pruned.
"""

import getpass
from datetime import datetime
from pathlib import Path
from typing import List

import yaml
from git import Repo
from gitdb.exc import BadName
from github import Github

from . import log


def months_old(date: datetime) -> int:
    """
    Returns how old a date is compared to now at month granularity.
    """
    now = datetime.now()
    return (now.year - date.year) * 12 + now.month - date.month


def _get_github_merged_prs(config: Path, months: int) -> List['github.PullRequest']:
    with open(config, 'r', encoding='utf-8') as conf_file:
        loaded_conf = yaml.safe_load(conf_file)

    if token := loaded_conf.get('token'):
        gh = Github(token)  # pylint: disable=invalid-name
    else:
        username = loaded_conf.get('user')
        assert username is not None
        pword = getpass.getpass(prompt=f"{username}'s password: ")
        gh = Github(username, pword)  # pylint: disable=invalid-name
        del pword

    # Get PRs (issues of type PR) that pertain to the GitHub user, for this
    # specific repo. Select those that are closed and merged.
    issues = [pr.as_pull_request() for pr in gh.search_issues('', state='closed',
              author=gh.get_user().login, repo=loaded_conf.get('repo'), type='pr')]
    if months:
        return [pr for pr in issues
                if pr.merged and
                (pr.closed_at is None or months_old(pr.closed_at) >= months)]

    return [pr for pr in issues if pr.merged]


def log_branch_list(branch_loc: str, branches: List[str]) -> None:
    """
    Log string elements in a list that represent branch names.
    Locations stands for private or remote, that will be logged in the output.
    """
    if len(branches) > 0:
        log.info(
            'There are %s %s branches that can be pruned:',
            len(branches),
            branch_loc)
        for branch_name in branches:
            log.info("\t%s", branch_name)
    else:
        log.info('No %s branches to prune.', branch_loc)


def list_branches(config: Path, months: int) -> None:
    """
    Obtain and log all local and remote branches that are older than months.
    """
    gh_merged = _get_github_merged_prs(config, months)
    repo = Repo()
    # Loop through local head commits and compare its SHA against GitHub head SHA.
    local_branches = []
    for head in repo.heads:
        if any(head.commit.hexsha == gh_pr.head.sha for gh_pr in gh_merged):
            local_branches.append(head.name)
    # Log local branches found.
    log_branch_list("local", local_branches)

    # Loop through GitHub PRs and rev_parse the remote branch name to be able
    # to compare the SHAs.
    remote_branches = []
    for gh_pr in gh_merged:
        remote_name = f'origin/{gh_pr.head.ref}'
        try:
            sha = repo.rev_parse(remote_name)
        except BadName:
            continue

        if str(sha) == gh_pr.head.sha:
            remote_branches.append(remote_name)
    # Log remote branches found.
    log_branch_list("remote", remote_branches)
