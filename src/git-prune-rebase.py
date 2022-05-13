#!/usr/bin/env python3
#
# Author: Albert Esteve <aesteve@redhat.com>
#
# This file is licensed under the GNU General Public License.
# Please see the LICENSE file

import click


@click.group()
def cli():
    """
    Prune local and remote branches that have been merged, even if it
    has been merged by rebasing. Currently supported only for GitHub projects.
    """
    print("This is the main")


@click.command()
def config():
    """
    Setup the configuration file to use.
    """
    print("Setup configuration")


@click.command()
def lsbr():
    """
    List all branches (local or remote) that have been merged.
    """
    print("List all branches")


@click.command()
def prune():
    """
    Prune all branches (local or remote) that have been merged.
    """
    print("Prune all branches")


cli.add_command(config)
cli.add_command(lsbr)
cli.add_command(prune)

if __name__ == '__main__':
    cli()
