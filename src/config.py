# SPDX-FileCopyrightText: 2022 Albert Esteve <aesteve@redhat.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Configuration file stored at project's root .git folder.
The file stores information required to interact with GH Rest API.
"""

from pathlib import Path
from typing import Optional

import yaml

from . import log

DEFAULT_CFG_PATH = Path(Path.cwd(), '.git/.gitpruneconf')


def create_config(
        path: Path,
        token: Optional[str],
        user: Optional[str],
        repo: Optional[str]) -> None:
    # pylint: disable=unused-argument
    """
    Create configuration file for GitHub.
    """
    config = {key: value for key, value in locals().items()
              if value and key != 'path'}
    if path.is_file():
        log.warning("A configuration file already exists at '%s'", path)
        log.info("If you continue the configuration will be overwritten.")
        while True:
            answer = input("    Are you sure? [Y/n] ")
            if not answer or any(char in answer for char in ['y', 'Y']):
                break
            if any(char in answer for char in ['n', 'N']):
                return

    with open(path, 'w', encoding='utf-8') as conf_file:
        yaml.dump(config, conf_file)
