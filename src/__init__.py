# SPDX-FileCopyrightText: 2022 Albert Esteve <aesteve@redhat.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Placeholder for centralized package logging and version control."""

import logging


__version__ = '0.4.6'


class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter with colors.
    """
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: f'[{grey}%(levelname).1s{reset}] %(message)s',
        logging.INFO: f'[{grey}%(levelname).1s{reset}] %(message)s',
        logging.WARNING: f'[{yellow}%(levelname).1s{reset}] %(message)s',
        logging.ERROR: f'[{red}%(levelname).1s{reset}] %(message)s',
        logging.CRITICAL: f'[{bold_red}%(levelname).1s{reset}] %(message)s'
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        return logging.Formatter(log_fmt).format(record)


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

ch.setFormatter(CustomFormatter())
# add the handlers to the logger
log.addHandler(ch)


def add_file_handler():
    """
    Create and add a FileHandler to log debug messages into a file.
    """
    # create file handler which logs even debug messages
    fhandler = logging.FileHandler('.prune-merged.log')
    fhandler.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    fhandler.setFormatter(
        logging.Formatter('%(levelname)s - %(message)s (%(filename)s:%(lineno)d)'))
    log.addHandler(fhandler)
