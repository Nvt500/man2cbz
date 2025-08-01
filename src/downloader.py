import os
import pathlib
import click
import requests
from concurrent.futures import ThreadPoolExecutor

from src import constants


class Downloader:
    """Downloader Template

        In a derived Downloader class:
            __init__ MUST have one argument. It should be the series homepage, although
                you can get away with making it the first chapter's url, but that will
                not be shown in the help message for the download command.
            Get either the first chapter's url or all chapter's urls and pass through to
                super().__init__.
            Implement the get_image_urls method to get the images of a chapter's page.
            If passing the first chapter's url, you will also need to implement get_next_url
                which gets the next chapter's url or None if it's the last chapter.
        These conditions need to be fulfilled and then the download method can be used.
    """

    def __init__(self, first_url: str | None, urls: list[str] | None) -> None:
        """Constructor

            first_url: url of first chapter, can be None if all urls can be accessed on homepage
            urls: urls of chapters, can be None if it isn't possible to get all urls on homepage
        """
        if first_url is None and urls is None:
            raise constants.ProgError("Either first_url or urls must be defined.")
        self.first_url = first_url or None
        self.urls = urls or None

    def download(self) -> None:
        """Downloads all images of all chapters"""

        num_files = 0
        for _ in pathlib.Path(constants.get_temp_images_dir()).iterdir():
            num_files += 1
        if num_files > 0:
            if click.confirm(f"temp_images has {num_files} files. Do you want to delete them to continue?"):
                for file in pathlib.Path(constants.get_temp_images_dir()).iterdir():
                    click.echo(f"Deleting {file.absolute()}.")
                    os.remove(file.absolute())
            else:
                click.echo("Exiting.")
                return

        if self.urls is not None:
            chapter_max_zeros = len(str(len(self.urls)))

            for chapter, url in enumerate(self.urls):
                response = requests.get(url)

                if response.status_code != 200:
                    click.echo(f"{url} failed with status code {response.status_code}.", err=True)
                    continue

                image_urls = self.get_image_urls(response)

                if len(image_urls) == 0:
                    click.echo(f"Couldn't find any images at {url}.", err=True)
                    continue

                image_max_zeros = len(str(len(image_urls)))

                images = []
                for i, image_url in enumerate(image_urls):
                    path = pathlib.Path(image_url)
                    if path.suffix == ".svg":
                        continue
                    images.append({
                        "url": image_url,
                        "filename": f"Chapter{str(chapter + 1).zfill(chapter_max_zeros)}Image{str(i + 1).zfill(image_max_zeros)}{path.suffix}",
                    })

                click.echo(f"Downloading {len(image_urls)} images from {url} ({chapter + 1}/{len(self.urls)})")

                with ThreadPoolExecutor() as executor:
                    executor.map(self.download_image, images)
        else:
            url = self.first_url
            image_amounts = []
            chapter = 1

            while url is not None:
                response = requests.get(url)

                if response.status_code != 200:
                    click.echo(f"{url} failed with status code {response.status_code}.", err=True)
                    return

                image_urls = self.get_image_urls(response)

                if len(image_urls) == 0:
                    click.echo(f"Couldn't find any images at {url}.", err=True)
                    return

                for index in range(len(image_urls)-1, -1, -1):
                    path = pathlib.Path(image_urls[index])
                    if path.suffix == ".svg":
                        image_urls.pop(index)

                image_amounts.append([])
                image_max_zeros = len(str(len(image_urls)))

                images = []
                for i, image_url in enumerate(image_urls):
                    path = pathlib.Path(image_url)
                    image_amounts[chapter-1].append(path.suffix)
                    images.append({
                        "url": image_url,
                        "filename": f"Chapter{chapter}Image{str(len(images)+1).zfill(image_max_zeros)}{path.suffix}",
                    })

                click.echo(f"Downloading {len(images)} images from {url} ({chapter}/???)")

                with ThreadPoolExecutor() as executor:
                    executor.map(self.download_image, images)

                chapter += 1
                url = self.get_next_url(response)

            if chapter <= 10:
                return

            chapter_max_zeros = len(str(len(image_amounts)))
            for chapter, images in enumerate(image_amounts):
                image_max_zeros = len(str(len(images)))
                for image, ext in enumerate(images):
                    os.rename(
                        os.path.join(constants.get_temp_images_dir(), f"Chapter{chapter+1}Image{str(image+1).zfill(image_max_zeros)}{ext}"),
                        os.path.join(constants.get_temp_images_dir(), f"Chapter{str(chapter+1).zfill(chapter_max_zeros)}Image{str(image+1).zfill(image_max_zeros)}{ext}")
                    )

    def get_image_urls(self, response: requests.Response) -> list[str]:
        """Gets images urls"""

        raise constants.ProgError("To be implemented.")

    def get_next_url(self, response: requests.Response) -> str | None:
        """Gets next url"""

        raise constants.ProgError("To be implemented.")

    @staticmethod
    def download_image(image: {str, str}) -> None:
        """Downloads an image

            image: {
                url: str,
                filename: str,
            }
        """

        file = requests.get(image["url"])
        file_path = os.path.join(constants.get_temp_images_dir(), image["filename"])
        with open(file_path, "wb") as f:
            f.write(file.content)

    @staticmethod
    def remove_duplicates(array: list[str]) -> None:
        """Removes duplicate from list"""

        # Find all indices of urls that are repeated before
        indices = []
        for i, url in enumerate(array):
            if array[:i].count(url) != 0:
                indices.append(i)
        # Remove the indices from urls but update the other indices
        for index in indices:
            array.pop(index)
            for i in range(len(indices)):
                indices[i] -= 1
