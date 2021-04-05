import functools

from werkzeug.security import check_password_hash, generate_password_hash
from flask import (
    Blueprint, request, session, redirect, url_for, render_template, flash,
    current_app
)

from itsdangerous import TimestampSigner, SignatureExpired, BadSignature

from tinydb import Query

from nselec.db import get_db

def get_user(username):
    # utility function for other stuff to use
    db = get_db()
    usertab = db.table("users")
    u = usertab.get(Query().username == username)
    return u

def set_password(username, password):
    pwh = generate_password_hash(password)
    del password # i have no idea if that will do anything but we can try i guess
    usertab = get_db().table("users")
    u = usertab.get(Query().username == username)
    if u == None:
        return False
    else:
        usertab.update({"password":pwh}, Query().username == username)

def check_user():
    if "user" not in session:
        # not even logged in
        return False, "You need to be logged in"
    db = get_db()
    User = Query()
    if not db.table("users").contains(User.username == session['user']):
        # that user doesn't exist!
        # it shouldn't be possible for somebody to tamper with the session, this
        # is mainly to log people out if the user gets deleted.
        return False, "The user you are logged in as does not exist (any more)"
    return True, "seems ok to me"

def login_required(view):
    # decorator for views/pages for which the user needs to be logged in
    # view is the view function we're decorating
    @functools.wraps(view)
    def wrapped(**kwargs):
        ok, msg = check_user()
        if not ok:
            flash(msg, "error")
            return redirect(url_for('auth.login'))
        else:
            return view(**kwargs)
    return wrapped

def role_required(role):
    # decorator for views that need a role value in the db greater than or equal
    # to the value passed to the db.
    # currently we have 0 (user) and 1 (admin) but this may change in future.
    def inner(view):
        view = login_required(view)
        @functools.wraps(view)
        def wrapped(**kwargs):
            db = get_db()
            # we know the user exists, because login_required should check that for us
            User = Query()
            u = db.table("users").get(User.username == session['user'])
            if u['role'] >= role:
                return view(**kwargs)
            else:
                flash("You do not have permissions to do that.", "error")
                return redirect(url_for("admin.index"))
        return wrapped
    return inner # that's a lot of nested functions but I think it makes sense


bp = Blueprint("auth", __name__)

def gen_signup_token(username):
    return TimestampSigner(current_app.secret_key).sign(username.encode("utf-8")).decode("utf-8")

@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        error = None
        token = request.form['token']
        ts = TimestampSigner(current_app.secret_key)
        try:
            username = ts.unsign(token, 60*5).decode("utf-8") # 2 minutes
        except SignatureExpired:
            error = "Token has expired"
        except BadSignature:
            error = "Invalid token"
        else:
            db = get_db()
            users = db.table("users")
            if users.contains(Query().username == username):
                error = "That user already exists"
            else:
                users.insert({"username":username,"role":0,"password":generate_password_hash(request.form['password'])})
        if error is None:
            session.clear()
            flash("Successfully created user! You can now login.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash(error, "error")
    return render_template("auth/signup.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        usertab = db.table("users")
        User = Query()
        entry = usertab.get(User.username == username)
        if entry == None or not check_password_hash(entry.get('password', None), password):
            flash("Invalid username or password!", "error")
        else:
            # valid login, hooray!
            session.clear()
            session['user'] = username
            flash("Login successful!", "success")
            return redirect(url_for('admin.index'))
    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    session.clear()
    flash("Successfully logged out!", "success")
    return redirect(url_for("index"))
