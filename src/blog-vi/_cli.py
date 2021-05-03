import os

import click
from .__main__ import generate_blog

@click.command()
@click.option("--url", envvar="BLOGVI_URL", type=click.STRING, required=True)
# @click.option("--source", envvar="FUNCTION_SOURCE", type=click.Path(), default=None)
#
# @click.option("--host", envvar="HOST", type=click.STRING, default="0.0.0.0")
# @click.option("--port", envvar="PORT", type=click.INT, default=8080)
# @click.option("--debug", envvar="DEBUG", is_flag=True)
# @click.option("--dry-run", envvar="DRY_RUN", is_flag=True)


def _cli():
    generate_blog()