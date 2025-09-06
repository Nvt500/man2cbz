import os
import json
import logging
import click
from flask import Flask, render_template

from src import constants


@click.command()
@click.help_option("-h", "--help")
@click.argument("name")
@click.option("-v", "--verbose", "verbose", default=False, is_flag=True, help="Show more information.")
def host(name: str, verbose: bool) -> None:
    """Host a series' folder locally

        NAME: the name of the folder to host

        This works ONLY for compiled as html
    """

    man_path = os.path.join(constants.get_root_dir(), name)
    if not os.path.exists(man_path):
        click.echo(f"{name} does not exist at {man_path}.", err=True)
        return

    app = Flask(__name__, template_folder=man_path, static_folder=man_path)

    @app.route("/")
    def index():
        return paths("index.html")

    @app.route("/<path:path>")
    def paths(path: str):
        if path.endswith(".json"):
            images = json.loads(render_template(path))
            for i, image in enumerate(images["images"]):
                images["images"][i] = os.path.join(name, image)
            return json.dumps(images)
        return render_template(path)

    if not verbose:
        click.echo("Serving http://localhost:8080 CTRL+C to quit")
        log = logging.getLogger("werkzeug")
        log.disabled = True

    app.run(host="localhost", port=8080)
