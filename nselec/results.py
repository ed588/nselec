from flask import (
    Blueprint, abort, redirect, url_for, render_template
)

from nselec.db import get_db
from nselec.utils import time_type
from nselec.ns_inter import get_allowed_voters
from nselec.irvote import compute_winner

bp = Blueprint('results', __name__)

@bp.route('/<int:el_id>')
def results(el_id):
    db = get_db()
    el = db.get(doc_id=el_id)
    if el is None:
        abort(404)
    tt = time_type(el['times']['start'], el['times']['end'])
    if tt == "present":
        return redirect(url_for("vote.election", el_id=el_id))
    elif tt != "past":
        abort(404)
    if el['type'] == "yesno":
        results = process_votes_yesno(el['votes'])
        voters = process_voters(el['voters'])
        return render_template("results/yesno.html", processed_results=results, results=el['votes'], voters=voters, el=el)
    elif el['type'] == "ranked":
        winner, results = process_votes_ranked(list(el['votes']), el)
        voters = process_voters(el['voters'])
        return render_template("results/ranked.html", winner=winner, processed_results=results, results=el['votes'], voters=voters, el=el)
    else:
        return render_template("base.html", content="Oops, that election type is not supported")

def process_votes_yesno(votes):
    # votes will be a dict with `for` and `against`
    if votes['for'] == votes['against']:
        return "draw"
    return "for" if votes['for'] > votes['against'] else "against"

def process_votes_ranked(votes, el):
    # votes will be a list of :-terminated strings
    avotes = [ v.split(":") for v in votes ]
    winner = compute_winner(avotes)
    nvotes = []
    for vote in avotes:
        t = []
        for entry in vote:
            t.append(el['options'][int(entry)])
        nvotes.append(t)
    return winner, sorted(nvotes)

def process_voters(voters):
    # voters is a list of internal nation names
    allowed = get_allowed_voters()
    return sorted([allowed.get(name, name) for name in voters])
