from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    abort,
    session,
)

from nselec.auth import login_required, role_required, get_user, gen_signup_token, set_password
from nselec.db import get_db
from nselec.utils import time_type

from tinydb import Query

bp = Blueprint("admin", __name__)


@bp.route("/")
@login_required
def index():
    return render_template("admin/index.html", user=get_user(session["user"]))


@bp.route("/users")
@role_required(1)
def users():
    db = get_db()
    users = db.table("users").all()
    return render_template("admin/users.html", users=users)


@bp.route("/users/new", methods=["GET", "POST"])
@role_required(1)
def new_user():
    tok = None
    if request.method == "POST":
        username = request.form["username"]
        tok = gen_signup_token(username)
    return render_template("admin/new_user.html", tok=tok)


@bp.route("/users/delete/<username>", methods=["GET", "POST"])
@role_required(1)
def delete_user(username):
    db = get_db()
    user = db.table("users").get(Query().username == username)
    if user is None:
        abort(404)
    if request.method == "POST":
        db.table("users").remove(Query().username == username)
        flash("User removed successfully", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/delete_user.html", username=username)


@bp.route("/users/edit/<username>", methods=["GET", "POST"])
@role_required(1)
def edit_user(username):
    db = get_db()
    usertab = db.table("users")
    user = usertab.get(Query().username == username)
    if user is None:
        abort(404)
    if request.method == "POST":
        err = None
        pw = request.form["password"]
        role = request.form['role']
        if not (0 <= int(role) <= 1):
            err = "Role must be an integer between 0 and 1"
        else:
            if pw != "":
                set_password(username, pw)
            usertab.update({"role":int(role)}, Query().username == username)
        if err is None:
            flash("User updated successfully!", "success")
            return redirect(url_for("admin.users"))
        else:
            flash(err, "error")
    return render_template("admin/edit_user.html", user=user)
            

@bp.route("/elections")
@login_required
def elections():
    db = get_db()
    els = db.all()
    categories = {"past": [], "present": [], "future": []}
    for el in els:
        tt = time_type(el["times"]["start"], el["times"]["end"])
        categories[tt].append(el)

    return render_template("admin/elections.html", **categories)


@bp.route("/elections/delete/<int:el_id>", methods=["GET", "POST"])
@login_required
def delete_election(el_id):
    db = get_db()
    el = db.get(doc_id=el_id)
    if el is None:
        abort(404)
    tt = time_type(el["times"]["start"], el["times"]["end"])
    if tt != "future":
        abort(404)
    if request.method == "POST":
        db.remove(doc_ids=[el_id])
        flash("Election removed successfully", "success")
        return redirect(url_for("admin.elections"))
    return render_template("admin/delete_election.html", el=el)


@bp.route("/elections/edit/<int:el_id>", methods=["GET", "POST"])
@login_required
def edit_election(el_id):
    db = get_db()
    el = db.get(doc_id=el_id)
    if el is None:
        abort(404)
    tt = time_type(el["times"]["start"], el["times"]["end"])
    if tt != "future":
        abort(404)
    if request.method == "POST":
        if el["type"] == "ranked":
            succ, data = get_data_ranked()
            if succ:
                db.remove(doc_ids=[el_id])
                db.insert(data)
                flash("Election updated successfully!", "success")
                return redirect(url_for("admin.elections"))
            else:
                flash(data, "error")
        elif el["type"] == "yesno":
            succ, data = get_data_yesno()
            if succ:
                db.remove(doc_ids=[el_id])
                db.insert(data)
                flash("Election updated successfully!", "success")
                return redirect(url_for("admin.elections"))
            else:
                flash(data, "error")
    else:
        if el["type"] == "ranked":
            return render_template("admin/edit_ranked.html", el=el)
        elif el["type"] == "yesno":
            return render_template("admin/edit_yesno.html", el=el)


@bp.route("/elections/new/yesno", methods=["GET", "POST"])
@login_required
def new_yesno():
    if request.method == "POST":
        succ, data = get_data_yesno()
        if succ:
            db = get_db()
            db.insert(data)
            flash("Successfully added new election!", "success")
            return redirect(url_for("admin.elections"))
        else:
            flash(data, "error")
    return render_template("admin/new_yesno.html")


@bp.route("/elections/new/ranked", methods=["GET", "POST"])
@login_required
def new_ranked():
    if request.method == "POST":
        succ, data = get_data_ranked()
        if succ:
            db = get_db()
            db.insert(data)
            flash("Successfully added election!", "success")
            return redirect(url_for("admin.elections"))
        else:
            flash(data, "error")
    return render_template("admin/new_ranked.html")


def get_data_yesno():
    lastchanged = session['user']
    name = request.form["name"]
    desc = request.form["desc"]
    start = request.form["start_date"] + " " + request.form["start_time"]
    end = request.form["end_date"] + " " + request.form["end_time"]
    fstr = "%Y-%m-%d %H:%M"
    start_f = datetime.strptime(start, fstr)
    end_f = datetime.strptime(end, fstr)
    return (
        True,
        {
            "name": name,
            "desc": desc,
            "times": {"start": start_f, "end": end_f},
            "type": "yesno",
            "voters": [],
            "votes": {"for": 0, "against": 0},
            "lastchanged": lastchanged,
        },
    )


def get_data_ranked():
    lastchanged = session['user']
    name = request.form["name"]
    desc = request.form["desc"]
    start = request.form["start_date"] + " " + request.form["start_time"]
    end = request.form["end_date"] + " " + request.form["end_time"]
    fstr = "%Y-%m-%d %H:%M"
    start_f = datetime.strptime(start, fstr)
    end_f = datetime.strptime(end, fstr)
    options = request.form.getlist("opt")
    if len(options) < 2:
        return False, "You need at least 2 options"
    return (
        True,
        {
            "name": name,
            "desc": desc,
            "type": "ranked",
            "times": {"start": start_f, "end": end_f},
            "voters": [],
            "votes": [],
            "options": options,
            "lastchanged": lastchanged,
        },
    )

