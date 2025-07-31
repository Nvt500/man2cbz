import importlib
import os
import pathlib
import click

from src import constants
from src.providers.asura import AsuraDownloader
from src.providers.mgeko import MangaGekkoDownloader
from src.providers.general import GeneralDownloader


@click.command()
@click.help_option("-h", "--help")
@click.argument("url")
@click.option("-p", "--provider", "provider", is_flag=False, flag_value="", type=click.STRING, default=None, help="Name of the provider (website) of the manwha/manga.", metavar="PROVIDER")
def download(url: str, provider: str | None) -> None:
    """Downloads a manwha/manga from a url

        URL: the url to the homepage of the series to download.

        If the --provider flag is not given, the provider will be automatically detected,
        ie if url starts with https://asuracomic the AsuraDownloader will be used.

        Use --provider as a flag to pick from a list of available providers.
    """

    if provider is None:
        if url.startswith("https://asuracomic"):
            AsuraDownloader(url).download()
        elif url.startswith("https://www.mgeko.cc"):
            MangaGekkoDownloader(url).download()
        else:
            GeneralDownloader(url).download()
        return
    if provider == "":
        provider = get_provider()

    provider_dict = importlib.import_module("src.providers." + provider).__dict__
    downloader = list(provider_dict.values())[-1]
    downloader(url).download()

def get_provider() -> str:
    """Gets user selected provider from list of available providers"""

    click.clear()
    file_num = 1
    providers = []
    for file_name in [key for key in importlib.import_module("src.providers").__dict__.keys() if not key.startswith("__")]:
        provider_dict = importlib.import_module("src.providers." + file_name).__dict__
        downloader_class = list(provider_dict.values())[-1]
        click.echo(f"{file_num}. {downloader_class.__doc__ or downloader_class.__name__} ({file_name})")
        providers.append(file_name)

        file_num += 1

    click.echo("Enter the name of the provider (the name in the last set of parentheses):")
    while True:
        provider = click.get_text_stream("stdin").readline().strip()
        for prov in providers:
            if provider == prov:
                click.clear()
                return provider

        click.echo("\nEnter a valid provider:")
