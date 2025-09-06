import os
import pathlib
import click

from src import constants
from src.download import download
from src.compile import compile_images
from src.host import host
from src.convert import convert
from src.ui import ui


@click.group()
@click.help_option("-h", "--help")
@click.version_option("0.2.0", "-v", "--version", message="%(prog)s %(version)s", prog_name="man2cbz")
def cli() -> None:
    """A cli to download manga/manwha as cbz files."""
    pass


@cli.command()
def clear() -> None:
    """Clear temp_images"""

    for file in pathlib.Path(constants.get_temp_images_dir()).iterdir():
        click.echo(f"Deleting {file.absolute()}.")
        os.remove(file.absolute())


cli.add_command(download)
cli.add_command(compile_images)
cli.add_command(host)
cli.add_command(convert)
cli.add_command(ui)

if __name__ == "__main__":
    cli()
