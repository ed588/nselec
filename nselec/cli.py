import click
import os
import json
from getpass import getpass
from werkzeug.security import generate_password_hash

from nselec.db import get_db


def init_app(app):
    @app.cli.command()
    def initialise():
        """Creates the instance directory, and creates an empty database file
        and config file if one doesn't exist already."""
        # nb: create_app creates the instance dir so we don't need to actually do that here
        if not os.path.isfile(app.config["DATABASE"]):
            with open(app.config["DATABASE"], "w") as f:
                json.dump({"_default": {}, "users": {}}, f)
                click.echo(
                    "Created an empty database at {}.".format(app.config["DATABASE"])
                )
        confpath = os.path.join(app.instance_path, "config.py")
        if not os.path.isfile(confpath):
            with open(confpath, "w") as f:
                f.write("")
                click.echo("Created an empty config file at {}.".format(confpath))

    @app.cli.command()
    @click.argument("username")
    def new_admin(username):
        """Creates a new administrator user. Useful if you've forgotten the password, or
        if you've just installed this (if so, do initialise first)"""
        password = getpass("Password for the new user: ")
        db = get_db()
        usertab = db.table("users")
        data = {
            "username": username,
            "password": generate_password_hash(password),
            "role": 1,
        }
        usertab.insert(data)
        click.echo("User {} created and given admin permissions successfully.")

