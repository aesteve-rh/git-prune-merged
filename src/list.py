# Author: Albert Esteve <aesteve@redhat.com>
#
# This file is licensed under the GNU General Public License.
# Please see the LICENSE file

import getpass
from pathlib import Path
from typing import List

import yaml
from git import Repo
from gitdb.exc import BadName
from github import Github

from . import log


def _get_github_merged_prs(config: Path) -> List['github.PullRequest']:
    with open(config, 'r', encoding='utf-8') as conf_file:
        loaded_conf = yaml.safe_load(conf_file)

    if token := loaded_conf.get('token'):
        gh = Github(token)
    else:
        username = loaded_conf.get('user')
        assert username is not None
        pword = getpass.getpass(prompt=f"{username}'s password: ")
        gh = Github(username, pword)
        del pword

    issues = [pr.as_pull_request() for pr in gh.search_issues('', state='closed',
              author=gh.get_user().login, repo=loaded_conf.get('repo'), type='pr')]
    return [pr for pr in issues if pr.merged]


def list_branches(config: Path) -> None:
    gh_merged = _get_github_merged_prs(config)
    repo = Repo()
    log.info('Local branches that will be pruned:')
    for head in repo.heads:
        if any(head.commit.hexsha == gh_pr.head.sha for gh_pr in gh_merged):
            log.info("\t%s", head.name)

    log.info('Remote branches that will be pruned:')
    for gh_pr in gh_merged:
        remote_name = f'origin/{gh_pr.head.ref}'
        try:
            sha = repo.rev_parse(remote_name)
        except BadName:
            continue

        if str(sha) == gh_pr.head.sha:
            log.info("\t%s", remote_name)
