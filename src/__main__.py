# SPDX-FileCopyrightText: 2022 Albert Esteve <aesteve@redhat.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Main entry point to the prune-rebase CLI."""

from .main import cli

if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
