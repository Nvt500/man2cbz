
# mancbz

A cli to download manga/manwha as cbz files.

The goal is to download series to read offline easily and is done using requests and regex to scrape 
webpages.

# Installation

Either download the executable from the releases or build it yourself with something like 
```pyinstaller```.

Simply

```text
> pyinstaller src/man2cbz.py --onefile --console
```

Or use ```--onedir``` to reduce start up time

```text
> pyinstaller src/man2cbz.py --onedir --console
```

To isolate the build files into a single directory where ```executable``` is the directory 
name.

```text
> pyinstaller src/man2cbz.py --onefile --console --distpath executable --workpath executable --specpath executable
```

Or use ```--onedir``` to reduce start up time

```text
> pyinstaller src/man2cbz.py --onedir --console --distpath executable --workpath executable/build --specpath executable
```

# Usage

## Download

```text
Usage: man2cbz download [OPTIONS] URL

  Downloads a manwha/manga from a url

  URL: the url to the homepage of the series to download.

  If the --provider flag is not given, the provider will be automatically
  detected, ie if url starts with https://asuracomic the AsuraDownloader will
  be used.

  Use --provider as a flag to pick from a list of available providers.

Options:
  -h, --help               Show this message and exit.
  -p, --provider PROVIDER  Name of the provider (website) of the manwha/manga.
```

### Providers

Providers are websites where the manwha are stored like https://asuracomic.net/.
Providers are listed in the providers folder in their own python file. To add one create a class and
extend the `Downloader` superclass in `downloader.py`.

Requirements of subclass:
- `__init__(self, base_url: str)` should take in one argument, the url of the homepage of the series and
  call `super().__init__` and pass either a list of each chapter's url or the first chapter's url if
  getting every chapter's url is impossible. It can also take in the first chapter's url and pass it
  directly to `super().__init__` but that should be specified in the doc string
-  `get_image_urls(self, response: requests.Response) -> list[str]` this method must be implemented and 
  should return a list of the urls of each image to download from the given page
- `get_next_url(self, response: requests.Response) -> str | None` this method must be implemented only if 
  first chapter's url was passed to `super().__init__`. It should return the next chapter's url or None 
  if it is the last chapter
- This is optional, but if there is a doc string for the class, it will be shown when listing available 
  providers and can give the user additional information like mentioned above
- THE CLASS EXTENDING `Downloader` MUST BE THE LAST THING IN THE FILE

After following these requirements, simply call the `download()` method of the superclass to download everything.

List of implemented providers:
- General: websites that host a single series like https://www.solo-levelingmanhwa.com/ or
  https://w14.fffclass-trashero.com/
- Asura Scans: https://asuracomic.net/
- Manga Gekko (I think that's the name): https://www.mgeko.cc/

## Compile

```text
Usage: man2cbz compile [OPTIONS] NAME

  Compile to cbz or html

  Valid formats: "cbz", "html"

Options:
  -h, --help           Show this message and exit.
  -f, --format FORMAT  What to compile to.  [default: cbz]
  -v, --verbose        Show more information.
```

Takes all the images stored in `temp_images` downloaded from the `download` command and compile them into
a cbz file or into a folder with html files to read how you would on the actual website. I recommend the 
[Panels](https://apps.apple.com/us/app/panels-comic-reader/id1236567663) app for cbz file if reading on 
your phone as it has vertical scrolling. If compiling to html, it uses javascript's fetch api to get local 
files stored on the computer so it doesn't work in normal browsers, but on the phone the 
[Koder](https://apps.apple.com/us/app/koder-code-editor/id1447489375) app allows for 'hosting' the html 
files locally in a built-in browser, so I recommend that.