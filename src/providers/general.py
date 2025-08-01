import requests
import re

from src import constants
from src.downloader import Downloader


class GeneralDownloader(Downloader):
    """General Downloader"""

    def __init__(self, base_url: str) -> None:
        """Constructor

            base_url: url of homepage to get the urls of all the chapters
        """

        response = requests.get(base_url)

        urls = re.findall(f'<a href=["\']({base_url}[^"\']*)["\']>.*chapter.*<',
                          response.text, re.IGNORECASE)

        if not urls:
            raise Exception(f"GeneralDownloader cannot get urls from: {base_url}.")

        self.remove_duplicates(urls)
        urls = urls[::-1]

        super().__init__(None, urls)

    def get_image_urls(self, response: requests.Response) -> list[str]:
        """Gets images urls"""

        return re.findall(r'<img.*src=["\']([^"\']*)["\']', response.text)

    def get_next_url(self, response: requests.Response) -> str | None:
        """Gets next url"""

        raise constants.ProgError("Not implemented.")
