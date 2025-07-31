import json
import os
import pathlib
import shutil
import click
import cbz
from cbz.constants import PageType, Format, YesNo, Manga, AgeRating

from src import constants


@click.command("compile")
@click.help_option("-h", "--help")
@click.argument("name")
@click.option("-f", "--format", "compile_format", default="cbz", type=click.STRING, show_default=True, help="What to compile to.", metavar="FORMAT")
@click.option("-v", "--verbose", "verbose", default=False, is_flag=True, help="Show more information.")
def compile_images(name: str, compile_format: str, verbose: bool) -> None:
    """Compile to cbz or html

        Valid formats: "cbz", "html"
    """

    match compile_format:
        case "cbz":
            compile_cbz(name, verbose)
        case "html":
            compile_html(name, verbose)
        case _:
            raise click.BadParameter(f"Unknown format: {compile_format}.")

def compile_html(name: str, verbose: bool) -> None:
    """Compile to a folder with html files to view the manwha in"""

    directory = os.path.join(constants.get_root_dir(), name)
    if os.path.exists(directory):
        raise Exception(f"{name} folder already exists at {directory}.")
    os.mkdir(directory)

    images_json = {}
    for file in pathlib.Path(constants.get_temp_images_dir()).iterdir():
        chapter = file.name.split("Image")[0]

        if not os.path.exists(os.path.join(directory, chapter)):
            os.mkdir(os.path.join(directory, chapter))

        shutil.copy(file, os.path.join(directory, chapter, file.name))

        if verbose:
            click.echo(f"Copied {file.name} to {os.path.join(directory, chapter, file.name)}.")

        images_json.setdefault(chapter, {})
        images_json[chapter].setdefault("images", [])
        images_json[chapter]["images"].append(file.name)

    all_dirs = list(pathlib.Path(directory).iterdir())
    all_dirs = [d for d in all_dirs if d.is_dir()]

    for index, chapter_dir in enumerate(all_dirs):
        if index == 0:
            images_json[chapter_dir.name].setdefault("previous", None)
        else:
            images_json[chapter_dir.name].setdefault("previous", all_dirs[index - 1].name)

        if index == len(all_dirs) - 1:
            images_json[chapter_dir.name].setdefault("next", None)
        else:
            images_json[chapter_dir.name].setdefault("next", all_dirs[index + 1].name)

        with open(os.path.join(chapter_dir.absolute(), "images.json"), "w") as file:
            file.write(json.dumps(images_json[chapter_dir.name], indent=4))
            file.close()

        if verbose:
            click.echo(f"Created {os.path.join(chapter_dir.absolute(), "images.json")}.")

    with open(os.path.join(directory, "index.html"), "w") as file:
        file.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    <ul>
        {chapters}
    </ul>
</body>
</html>""".format(title=name, chapters="\n\t\t".join(
            ["<li><a href=\"chapter.html?chapter={chapter}\">Chapter {i}</a></li>".format(chapter=chapter, i=i+1) for i, chapter in enumerate(images_json.keys())]
        )))
        file.close()
    if verbose:
        click.echo(f"Created {os.path.join(directory, "index.html")}.")

    with open(os.path.join(directory, "chapter.html"), "w") as file:
        file.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title></title>
</head>
<style>
    body, div {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    a {
        margin: 50px;
        font-size: 24px;
    }
    #top, #bottom {
        flex-direction: row;
    }
</style>
<script>
    function getChapter()
    {
        const params = new URLSearchParams(window.location.search);
        document.title = params.get("chapter");
        fetch(params.get("chapter") + "/images.json")
            .then((res) => res.json())
            .then((json) => {
                const title = document.createElement("h1");
                title.textContent = params.get("chapter");
                document.body.prepend(title);
                const container = document.querySelector("#images_container");
                for (const image of json.images)
                {
                    const img = document.createElement("img");
                    img.alt = "Loading " + image + "...";
                    img.src = params.get("chapter") + "/" + image;
                    container.appendChild(img);
                }
                const top = document.querySelector("#top");
                const bottom = document.querySelector("#bottom");
                if (json.previous !== null)
                {
                    const prev = document.createElement("a");
                    prev.href = "chapter.html?chapter=" + json.previous;
                    prev.textContent = "Previous Chapter";
                    top.appendChild(prev);
                    bottom.appendChild(prev.cloneNode(true))
                }
                if (json.next !== null)
                {
                    const next = document.createElement("a");
                    next.href = "chapter.html?chapter=" + json.next;
                    next.textContent = "Next Chapter";
                    top.appendChild(next);
                    bottom.appendChild(next.cloneNode(true))
                }
            })
            .catch((e) => console.error(e));
    }

</script>
<body onload="getChapter()">
    <h1><a href="index.html">Home</a></h1>
    <div id="top"></div>
    <div id="images_container"></div>
    <div id="bottom"></div>
</body>
</html>""")
        file.close()
    if verbose:
        click.echo(f"Created {os.path.join(directory, "chapter.html")}.")

def compile_cbz(name: str, verbose: bool) -> None:
    """Compile as cbz"""

    paths = list(pathlib.Path(constants.get_temp_images_dir()).iterdir())

    pages = []
    for i, path in enumerate(paths):
        if verbose:
            click.echo(f"Compiling {path}.")
        pages.append(cbz.PageInfo.load(
            path=path,
            type=PageType.FRONT_COVER if i == 0 else PageType.BACK_COVER if i == len(paths) - 1 else PageType.STORY,
        ))

    comic = cbz.ComicInfo.from_pages(
        pages,
        title=name,
        series=name,
        number=1,
        language_iso="en",
        format=Format.WEB_COMIC,
        black_white=YesNo.NO,
        manga=Manga.NO,
        age_rating=AgeRating.PENDING
    )
    cbz_content = comic.pack()
    cbz_path = pathlib.Path(os.path.join(constants.get_root_dir(), name + ".cbz"))
    if os.path.exists(cbz_path):
        raise Exception(f"{name} already exists at: {cbz_path}.")
    cbz_path.write_bytes(cbz_content)
    if verbose:
        click.echo(f"Created {cbz_path}.")
