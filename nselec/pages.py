from flask import (
    Blueprint, render_template, abort
)
from jinja2.exceptions import TemplateNotFound

bp = Blueprint("pages", __name__)

@bp.route("/<name>")
def page(name):
    if name == "_base":
        abort(404)
    try:
        return render_template("pages/{}.html".format(name))
    except TemplateNotFound:
        abort(404)
