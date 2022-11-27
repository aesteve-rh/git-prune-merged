# SPDX-FileCopyrightText: 2022 Albert Esteve <aesteve@redhat.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Handle the actual prune of all local and remote branches.
"""

from typing import List

from git import Reference, Repo
from gitdb.exc import BadName

from . import log


def _prompt_confirmation(branch_name: str) -> bool:
    while True:
        log.info("Going to remove %s", branch_name)
        answer = input("    Are you sure? [Y/n] ")
        if not answer or any(char in answer for char in ['y', 'Y']):
            return True
        if any(char in answer for char in ['n', 'N']):
            return False


def prune_remote(yes: bool, dry_run: bool, gh_pr: List['github.PullRequest']):
    """
    Prune remote branches based on its SHA.
    """
    deleted = 0
    repo = Repo()
    for preq in gh_pr:
        remote_name = f'origin/{preq.head.ref}'
        try:
            sha = repo.rev_parse(remote_name)
        except BadName:
            continue

        if str(sha) == preq.head.sha:
            answer = True
            if not yes:
                answer = _prompt_confirmation(remote_name)
            if answer:
                log.debug("Removing %s...", remote_name)
                if not dry_run:
                    repo.remote().push(refspec=(f":{preq.head.ref}"))
                deleted += 1
                log.info("[deleted] .... %s", remote_name)
            else:
                log.info("Skipping %s", remote_name)

    log.info("All (%s) remote branches pruned.", deleted)


def prune_local(yes: bool, dry_run: bool, gh_pr: List['github.PullRequest']):
    """
    Prune local branches based on its SHA.
    """
    deleted = 0
    repo = Repo()
    for head in repo.heads:
        if any(head.commit.hexsha == preq.head.sha for preq in gh_pr):
            answer = True
            if not yes:
                answer = _prompt_confirmation(head.name)
            if answer:
                try:
                    if not dry_run:
                        Reference.delete(repo, head.path)
                    deleted += 1
                    log.info("[deleted] .... %s", head.name)
                except OSError:
                    log.error("%s", head, exc_info=True)
            else:
                log.info("Skipping %s", head.name)

    log.info("All (%s) local branches pruned.", deleted)
