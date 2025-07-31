import requests
import re
import urllib.parse

from src.downloader import Downloader


class MangaGekkoDownloader(Downloader):
    """Manga Gekko Downloader (mgeko.cc)"""

    def __init__(self, base_url: str) -> None:
        """Constructor

            base_url: url of homepage to get the first chapter's url
        """

        response = requests.get(base_url)
        try:
            first_url = re.search(r'<a.+href=["\']([^"\']+)["\'][^>]*>(?=.*chapter 1).*?</a>', response.text,
                                  re.IGNORECASE | re.DOTALL).group(1)
        except AttributeError:
            raise Exception(f"MangaGekkoDownloader cannot get the first chapter's url from: {base_url}.")

        super().__init__(urllib.parse.urljoin(base_url, first_url), None)

    def get_image_urls(self, response: requests.Response) -> list[str]:
        """Gets images urls"""

        urls = re.findall(r'<img.*src=["\']([^"\']*)["\']', response.text)

        for index in range(len(urls)-1, -1, -1):
            if not urls[index].startswith("http"):
                urls.pop(index)

        return urls

    def get_next_url(self, response: requests.Response) -> str | None:
        """Gets next url"""

        url = re.findall(r'<a(?!.*disabled).*?href=["\']([^"\']+)["\'][^>]*>(?=.*next).*?</a>', response.text, re.IGNORECASE)

        if not url:
            return None
        return urllib.parse.urljoin(response.url, url[0])
