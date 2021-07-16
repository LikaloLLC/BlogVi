import os
from pathlib import Path

import click

from .__main__ import generate_blog
from ._config import SETTINGS_FILENAME, AUTHORS_FILENAME

# List of filenames, that must exists in the directory
MANDATORY_FILENAMES = [SETTINGS_FILENAME]


@click.command()
@click.argument(
    "directory",
    envvar="BLOGVI_DIRECTORY",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True
)
def _cli(directory):
    # TODO: Checks for `templates_dir`
    workdir = Path(directory)

    for filename in MANDATORY_FILENAMES:
        if not workdir.joinpath(filename).exists():
            click.echo('Could not find `{}` in directory `{}`.'.format(filename, directory))

            return

    generate_blog(workdir)
