from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf8") as readme_file:
    readme = readme_file.read()

requirements = ["click>=8"]

setup(
    name="git-prune-rebase",
    version="0.0.1",
    author="Albert Esteve",
    author_email="aesteve@redhat.com",
    description="A git plugin to prune local and remote branches",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/aesteve-rh/git-prune-rebase",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)