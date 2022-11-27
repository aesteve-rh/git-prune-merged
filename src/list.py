# SPDX-FileCopyrightText: 2022 Albert Esteve <aesteve@redhat.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Offers utility functions to obtain and log local and remote branches
that can be potentially pruned.
"""

import getpass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import yaml
from git import Repo
from gitdb.exc import BadName
from github import Github

from . import log


class Branches:

    def __init__(self, config: Path, months: int) -> None:
        self._config = config
        self._months = months
        self._repo: str = ''


class GithubBranches(Branches):

    def __init__(self, config: Path, months: int) -> None:
        super().__init__(config, months)
        self._gh: Optional[Github] = None
        self._create_github()

    def _create_github(self) -> Github:
        with open(self._config, 'r', encoding='utf-8') as conf_file:
            loaded_conf = yaml.safe_load(conf_file)

        self._repo = loaded_conf.get('repo')
        if token := loaded_conf.get('token'):
            self._gh = Github(token)  # pylint: disable=invalid-name
        else:
            username = loaded_conf.get('user')
            assert username is not None
            pword = getpass.getpass(prompt=f"{username}'s password: ")
            self._gh = Github(username, pword)  # pylint: disable=invalid-name
            del pword

    @property
    def branches(self):
        assert self._gh is not None
        # Get PRs (issues of type PR) that pertain to the GitHub user, for this
        # specific repo. Select those that are closed and merged.
        qualifiers = {
            'state': 'closed',
            'is': 'merged',
            'author': self._gh.get_user().login,
            'repo': self._repo,
            'type': 'pr'
        }
        issues = [pr.as_pull_request() for pr in self._gh.search_issues('', **qualifiers)]
        if self._months:
            return [pr for pr in issues
                    if pr.merged
                    and (pr.closed_at is None or months_old(pr.closed_at) >= self._months)]

        return [pr for pr in issues if pr.merged]


def months_old(date: datetime) -> int:
    """
    Returns how old a date is compared to now at month granularity.
    """
    now = datetime.now()
    return (now.year - date.year) * 12 + now.month - date.month


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
    gh_merged = GithubBranches(config, months).branches
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
