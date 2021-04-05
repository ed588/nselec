from datetime import datetime

from nselec.db import get_db

from flask import Blueprint, render_template
from tinydb import Query


bp = Blueprint("archive", __name__)


@bp.route("/")
def archive():
    db = get_db()
    Election = Query()
    els = sorted(
        db.search(Election.times.end < datetime.now()),
        key=lambda n: n["times"]["end"],
        reverse=True,
    )
    return render_template("archive/archive.html", els=els)
