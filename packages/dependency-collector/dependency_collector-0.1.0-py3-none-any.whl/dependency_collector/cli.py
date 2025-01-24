import click
import subprocess
import sys
import logging
from pathlib import Path


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


@click.command()
@click.option(
    "--package",
    "package",
    required=True,
    type=str,
    help="Package path",
)
@click.option(
    "-d",
    "--dest",
    "dest",
    required=True,
    type=str,
    help="Download packages into <dir>.",
)
@click.option(
    "--python-version",
    "python_version",
    type=str,
    help="The Python interpreter version to use for wheel and Requires-Python compatibility checks.",
)
@click.option(
    "--extra-index-url",
    "extra_index",
    type=str,
    help="Extra URLs of package indexes to use in addition to default index.",
)
def collect(package, dest, python_version, extra_index):
    """Collect package dependencies for offline installation."""

    package = Path(package).resolve()
    dest = Path(dest).resolve()

    parameters = [sys.executable, "-m", "pip", "download", package.as_posix(), "-d", dest.as_posix(), "--only-binary=:all:"]
    if python_version is not None:
        parameters += ["--python-version", python_version]
    if extra_index is not None:
        parameters += ["--extra-index-url", extra_index]

    logging.info("Running pip download with arguments :")
    logging.info(parameters)

    subprocess.check_call(parameters)
