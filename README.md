<!--
SPDX-FileCopyrightText: 2022 Albert Esteve <aesteve@redhat.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# git-prune-merged

Git plugin to help you keep repository clean from the command line, by
pruning local and remote branches that have been integrated in GitHub.

## Installation

The package is available through PyPI.

    pip install git-prune-merged

## Basic usage

First you need to configure GitHub connection. The recommended way to authenticate
is to use a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
Also, the name of the repository where you are going to create your
Pull Requests is required. Usually, this is the repository in
which you are currently working, but in forked repositories this needs
to be the upstream repository name.

    git prune-merged config -- token <token_id> -- repo 'repo/name'

Print the help to get a glimpse of all the commands, arguments and flags:

    git prune-merged -h

List all branches that would be pruned. Make sure to have fetched your remote
before running 'prune-merged' if you have recently integrated a branch that
you expect to be pruned.

    $ git prune-merged ls
    [I] There are 5 local branches that can be pruned:
    [I]     dev-branch1
    [I]     dev-branch2
    [I]     dev-branch3
    [I]     dev-branch4
    [I]     dev-branch5
    [I] There are 4 remote branches that can be pruned:
    [I]     origin/dev-branch1
    [I]     origin/dev-branch2
    [I]     origin/dev-branch3
    [I]     origin/dev-branch4

List branches older than 3 months:
    
    $ git prune-merged ls --months 3
    [I] No local branches to prune.
    [I] No remote branches to prune.


Prune all remote branches:

    $ git prune-merged -r
    [I] Going to remove origin/dev-branch1
        Are you sure? [Y/n]
    [I] [deleted] .... origin/dev-branch1
    [I] Going to remove origin/dev-branch2
        Are you sure? [Y/n] y
    [I] [deleted] .... origin/dev-branch2
    [I] Going to remove origin/dev-branch3
        Are you sure? [Y/n] n
    [I] Skipping origin/dev-branch3
    [I] Going to remove origin/dev-branch4
        Are you sure? [Y/n] n
    [I] Skipping origin/dev-branch4
    [I] All (2) remote branches pruned.

Do a dry-run simulation for prunning all branches (local and remote), and do not ask for confirmation:

    $ git prune-merged --all --yes --dry-run
    [I] [deleted] .... origin/dev-branch3
    [I] [deleted] .... origin/dev-branch4
    [I] All (2) remote branches pruned.
    [I] [deleted] .... dev-branch1
    [I] [deleted] .... dev-branch2
    [I] [deleted] .... dev-branch3
    [I] [deleted] .... dev-branch4
    [I] [deleted] .... dev-branch5
    [I] All (5) local branches pruned.

## How it works

A branch that has been integrated by rebasing in GitHub
[will update the SHAs of the commits](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges#rebase-and-merge-your-pull-request-commits),
making it difficult to track whether
a branch has been merged, since the SHAs will differ.

Although branches can be [automatically deleted after merge](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-the-automatic-deletion-of-branches), making it easier to manage
these cases (e.g., git garbage collector), it is not always posible or
desirable to change the configuration of a project.

Currently, this plugin works only in GitHub-hosted repositories. The plugin
discerns whether a branch has been merged by exploring the user's GitHub
pull requests (PR). By looping through all the 'closed and merged' PRs for the
user, and comparing the HEAD SHA against the local and remote HEAD SHAs, it
is able to discern which branches can be safely pruned. Using SHAs is a secure
way to do this, since SHA is unique. Using branch name could lead to
wrongfully pruned branches.

## Safety measures

- Never remove a branch without a confirmation or the `--yes` flag.
- Posibility to print all branches that will be pruned before running the command.
- Dry-run option to safely pre-verify what would be removed.
- Using SHAs to ensure that the branches that will be pruned are the ones that were
integrated.
- Allow to prune only older branches to month granularity.

## Support

Please report any bugs, issues or suggestions you may have.

Like this plugin? Support it with a star!