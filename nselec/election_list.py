# blueprint containing the main election list
from flask import (
    Blueprint, render_template
)
from nselec.db import get_db
from nselec.utils import time_type

import datetime as dt

bp = Blueprint('election_list', __name__)

@bp.route('/')
def election_list():
    db = get_db()
    elections = db.all()
    # we need to sort these into "past", "present" and "future"
    categories = {'past':[],'present':[],'future':[]}
    for el in elections:
        tt = time_type(el['times']['start'], el['times']['end'])
        categories[tt].append(el)
    
    threshold = dt.datetime.now() - dt.timedelta(days=7*2) # 2 weeks ago
    print(threshold)
    for e in categories['past']:
        print(e['times']['end'], e['times']['end'] < threshold)
    categories['past'] = [e for e in categories['past'] if e['times']['end'] > threshold]

    return render_template("election_list/election_list.html", **categories)
