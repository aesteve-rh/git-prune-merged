# SPDX-FileCopyrightText: 2022 Albert Esteve <aesteve@redhat.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""git-prune-merged package setup."""

from setuptools import setup, find_packages
import src

with open("README.md", "r", encoding="utf8") as readme_file:
    readme = readme_file.read()

requirements = ["Click", "gitpython>3.1", "pygithub>=1.55", "pyyaml>=6.0", "python-dateutil"]

setup(
    name="git-prune-merged",
    version=src.__version__,
    author="Albert Esteve",
    author_email="aesteve@redhat.com",
    description="A git plugin to prune local and remote branches",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/aesteve-rh/git-prune-merged",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'git-prune-merged=src.main:cli',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
