import os
import pathlib
import shutil
import click
from cbz import ComicInfo

from src import constants
from src.compile import compile_cbz, compile_html


@click.command()
@click.help_option("-h", "--help")
@click.argument("name")
@click.option("-v", "--verbose", "verbose", default=False, is_flag=True, help="Show more information.")
def convert(name: str, verbose: bool) -> None:
    """Converts series to and from each format

        If it's a cbz file it will be converted to html and vice versa

        It will not delete the original file(s) or anything in temp_images
    """

    path = os.path.join(constants.get_root_dir(), name)
    if not os.path.exists(path):
        click.echo(f"{name} does not exist at {path}.", err=True)
        return

    if name.endswith(".cbz"):
        if os.path.exists(constants.get_temp_images_dir(create=False)):
            os.rename(constants.get_temp_images_dir(), constants.get_temp_images_dir() + "_backup")

        extract_cbz(path, verbose)
        compile_html(name.rstrip(".cbz"), verbose)
    elif os.path.isdir(name):
        if os.path.exists(constants.get_temp_images_dir(create=False)):
            os.rename(constants.get_temp_images_dir(), constants.get_temp_images_dir() + "_backup")

        extract_html(path, verbose)
        compile_cbz(name, verbose)
    else:
        click.echo(f"{path} is not a cbz file or directory.", err=True)
        return

    shutil.rmtree(constants.get_temp_images_dir(create=False))
    os.rename(constants.get_temp_images_dir(create=False) + "_backup", constants.get_temp_images_dir(create=False))


def extract_cbz(path: str, verbose: bool) -> None:
    """Extracts image files and places them into temp_images"""

    comic = ComicInfo.from_cbz(path)
    for page in comic.pages:
        if verbose:
            click.echo(f"Extracting {page.key} to temp_images from {path}.")
        page.save(os.path.join(constants.get_temp_images_dir(), page.key))


def extract_html(path: str, verbose: bool) -> None:
    """Extracts image files and places them into temp_images"""

    for folder in pathlib.Path(path).iterdir():
        if os.path.isdir(folder):
            for file in folder.iterdir():
                if not file.suffix == ".json":
                    if verbose:
                        click.echo(f"Extracting {file.name} to temp_images from {path}.")
                    shutil.copy(file.absolute(), os.path.join(constants.get_temp_images_dir(), file.name))