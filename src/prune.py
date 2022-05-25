# Author: Albert Esteve <aesteve@redhat.com>
#
# This file is licensed under the GNU General Public License.
# Please see the LICENSE file

from pathlib import Path
from typing import List, Optional

from git import Reference, Repo
from gitdb.exc import BadName

from . import log
from .list import _get_github_merged_prs


def _prompt_confirmation(branch_name: str) -> bool:
    while True:
        log.info("Going to remove %s", branch_name)
        answer = input("    Are you sure? [Y/n] ")
        if not answer or any(char in answer for char in ['y', 'Y']):
            return True
        if any(char in answer for char in ['n', 'N']):
            return False


def prune_remote(config: Path, yes: bool, dry_run: bool,
                 gh_pr: Optional[List['github.PullRequest']] = None):
    if gh_pr is None:
        gh_pr = _get_github_merged_prs(config)

    deleted = 0
    repo = Repo()
    for gh_pr in gh_pr:
        remote_name = f'origin/{gh_pr.head.ref}'
        try:
            sha = repo.rev_parse(remote_name)
        except BadName:
            continue

        if str(sha) == gh_pr.head.sha:
            answer = True
            if not yes:
                answer = _prompt_confirmation(remote_name)
            if answer:
                log.debug("Removing %s...", remote_name)
                if not dry_run:
                    repo.remote().push(refspec=(f":{gh_pr.head.ref}"))
                deleted += 1
                log.info("[deleted] .... %s", remote_name)
            else:
                log.info("Skipping %s", remote_name)

    log.info("All (%s) remote branches pruned.", deleted)


def prune_local(config: Path, yes: bool, dry_run: bool,
                gh_pr: Optional[List['github.PullRequest']] = None):
    if gh_pr is None:
        gh_pr = _get_github_merged_prs(config)

    deleted = 0
    repo = Repo()
    for head in repo.heads:
        if any(head.commit.hexsha == gh_pr.head.sha for gh_pr in gh_pr):
            answer = True
            if not yes:
                answer = _prompt_confirmation(head.name)
            if answer:
                try:
                    if not dry_run:
                        Reference.delete(repo, head.path)
                    deleted += 1
                    log.info("[deleted] .... %s", head.name)
                except Exception:
                    log.error("%s", head, exc_info=True)
            else:
                log.info("Skipping %s", head.name)

    log.info("All (%s) local branches pruned.", deleted)
