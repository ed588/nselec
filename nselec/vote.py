from flask import (
    Blueprint, render_template, abort, request, redirect, url_for, flash
)
from nselec.db import get_db, list_append, inc_result
from nselec.utils import time_type
from nselec.ns_inter import get_allowed_voters, verify_code

bp = Blueprint('vote', __name__)

@bp.route("/<int:el_id>")
def election(el_id):
    db = get_db()
    el = db.get(doc_id=el_id)
    if el is None:
        abort(404)
    else:
        tt = time_type(el['times']['start'], el['times']['end'])
        if tt == "past":
            return redirect(url_for("results.results", el_id=el_id))
        elif tt == "present":
            voters = get_allowed_voters()
            if el['type'] == "yesno":
                return render_template("vote/yesno.html", el=el, el_id=el_id, voters=voters)
            elif el['type'] == "ranked":
                return render_template("vote/ranked.html", el=el, el_id=el_id, voters=voters)
            else:
                return render_template("base.html", content="Oops, that election type is not supported")
        else:
            abort(404)

@bp.route("/<int:el_id>/submit", methods=["GET","POST"])
def submit(el_id):
    if request.method == "GET":
        return redirect(url_for("vote.election",el_id=el_id))
    nation = request.form.get("nation", None)
    try:
        nation_name = get_allowed_voters()[nation]
    except KeyError:
        nation_name = None
    code = request.form.get("verify", None)
    vote = request.form.get("vote", None)
    ok, err = check_vote(el_id, nation, code, vote)
    if not ok:
        flash("{}'s vote was not registered: {}".format(nation_name or "(unknown)", err), "error")
        return redirect(url_for('vote.election',el_id=el_id))
    else:
        register_vote(el_id, nation, vote)
        flash("{}'s vote was registered successfully!".format(nation_name), "success")
        return redirect(url_for('index'))

def check_vote(el_id, nation, code, vote):
    if nation is None or code is None or vote is None:
        return False, "the nation, verification code, or vote was not specified"
    voters = get_allowed_voters()
    if nation not in voters:
        return False, "that nation is not allowed to vote"
    if not verify_code(nation, code):
        return False, "the verification code was invalid or has expired"
    db = get_db()
    el = db.get(doc_id=el_id)
    if el is None:
        return False, "that election does not exist"
    if nation in el['voters']:
        return False, "you have already voted on this election"
    if el['type'] == "yesno":
        if vote not in ['for','against']:
            return False, "invalid vote (must be for or against)"
    elif el['type'] == "ranked":
        opts = vote.split(":")
        for o in opts:
            if not o.isdigit():
                return False, "invalid option string, please contact your administrator. (some non-digits) (debug: {})".format(vote)
        seq = all(val == idx for idx, val in enumerate(sorted((int(o) for o in opts))))
        if not seq:
            return False, "invalid option string, please contact your administrator. (non-consecutive options) (debug: {})".format(vote)

    return True, "ok"

def register_vote(el_id, nation, vote):
    db = get_db()
    el = db.get(doc_id=el_id)
    if el['type'] == "yesno":
        register_vote_yesno(el_id, nation, vote)
    elif el['type'] == "ranked":
        register_vote_ranked(el_id, nation, vote)

def register_vote_yesno(el_id, nation, vote):
    db = get_db()
    db.update(list_append("voters", nation), doc_ids=[el_id])
    db.update(inc_result(vote), doc_ids=[el_id])

def register_vote_ranked(el_id, nation, vote):
    db = get_db()
    db.update(list_append("voters", nation), doc_ids=[el_id])
    db.update(list_append("votes", vote), doc_ids=[el_id])
