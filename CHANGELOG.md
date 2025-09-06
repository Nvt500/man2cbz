# man2cbz changelog

## 0.2.0 - 9-6-2025 - 3 New Commands

- Added the `host` command which allows hosting html files locally without any external tools
- Added the `ui` command which allows for reading cbz files locally without any external tools
- Added the `convert` command which allows for converting series between each format (cbz and html)

## 0.1.1 - 8-1-2025 - Bugfix

- Remove `image_len_offset` variable from `downloader.py` and remove svg images from `image_urls` before
  adding them to `images` as it led to this error:
  - `FileNotFoundError: [WinError 2] The system cannot find the file specified: 
    './man2cbz/temp_images/Chapter1Image001.jpg' -> 
    './man2cbz/temp_images/Chapter001Image001.jpg'`
- Caught exceptions with try except to remove long error messages. However, those can still be used by
  raising `constants.ProgError` in order to see where in the code whatever went wrong
  - Example: 
    ```text
      File "./man2cbz/src/download.py", line 44, in download
        raise constants.ProgError(e)
    src.constants.ProgError: Either first_url or urls must be defined.
    ```

## 0.1.0 - 7-31-2025 - man2cbz Created

- man2cbz was created with commands:
  - download
  - compile
  - clear
- Providers implemented:
  - General: websites that host a single series like https://www.solo-levelingmanhwa.com/ or
  https://w14.fffclass-trashero.com/
  - Asura Scans: https://asuracomic.net/
  - Manga Gekko (I think that's the name): https://www.mgeko.cc/