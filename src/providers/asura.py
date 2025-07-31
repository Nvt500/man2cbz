import requests
import re
import urllib.parse

from src.downloader import Downloader


class AsuraDownloader(Downloader):
    """Asura Scans Downloader"""

    def __init__(self, base_url: str) -> None:
        """Constructor

            base_url: url of homepage to get the first chapter's url
        """

        response = requests.get(base_url)
        try:
            first_url = re.search(r'<a.+href=["\']([^"\']+)["\'][^>]*>(?=.*first chapter).*?</a>', response.text, re.IGNORECASE).group(1)
        except AttributeError:
            raise Exception(f"AsuraDownloader cannot get the first chapter's url from: {base_url}.")

        super().__init__(urllib.parse.urljoin(base_url, first_url), None)

    def get_image_urls(self, response: requests.Response) -> list[str]:
        """Gets images urls"""

        urls = re.findall(r'{\\"order\\":[0-9]*,\\"url\\":\\["\']([^"\']*)\\["\']', response.text)
        self.remove_duplicates(urls)
        return urls

    def get_next_url(self, response: requests.Response) -> str | None:
        """Gets next url"""

        url = re.findall(r'<a.+href=["\']([^"\']+)["\'][^>]*>(?!.*prev).*?</a>', response.text, re.IGNORECASE)
        if not url:
            return None
        return urllib.parse.urljoin(response.url, url[0])
