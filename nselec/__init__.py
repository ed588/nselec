import os
import importlib
import random

__version__ = "2.2.1"

from flask import Flask


def noconf_voters_example_data():
    # you should put a function called GET_VOTERS in the config file
    # this function is the backup
    return {"testlandia": "Testlandia"}


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "nselec.db"),
        GET_VOTERS=noconf_voters_example_data,
        TITLE_MAINPAGE = "An Elections Website",
        TITLE_SHORT = "Elections",
        TITLE_LONG = "Election Site",
        FAVICON = app.config['APPLICATION_ROOT']+"favicon.ico",
    )

    app.config.from_pyfile("config.py", silent=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # fmt: off
    plugins = (
        "db",
        "cli",
        "errors"
    )
    for plugname in plugins:
        plug = importlib.import_module("nselec." + plugname)
        plug.init_app(app)

    from . import election_list
    app.register_blueprint(election_list.bp)

    modules = (
        "vote",
        "results",
        "auth",
        "admin",
        "pages",
        "archive",
    )
    for modname in modules:
        mod = importlib.import_module("nselec." + modname)
        bp = mod.bp
        app.register_blueprint(bp, url_prefix="/" + modname)
    # fmt: on
    app.add_url_rule("/", endpoint="index")

    @app.context_processor
    def _version_context():
        return {"version": __version__}

    @app.template_filter("shuffleopts")
    def _shuffleopts_filter(s):
        # s will be a list of option names
        try:
            result = list(enumerate(s))
            random.shuffle(result)
            return result
        except:
            return s

    @app.template_filter("human_dt")
    def _human_dt(s):
        from ago import human
        return human(s)
    
    @app.template_filter("iso_dt")
    def _iso_dt(s):
        return s.isoformat(" ")

    return app
