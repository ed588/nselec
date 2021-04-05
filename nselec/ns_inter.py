# nationstates integration
from flask import current_app

def get_allowed_voters():
    return current_app.config['GET_VOTERS']()

def verify_code(nation, code, check_voters=True):
    if check_voters:
        voters = get_allowed_voters()
        if nation not in voters:
            return False
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
    url = "https://www.nationstates.net/cgi-bin/api.cgi"
    data = {
        "a":"verify",
        "v":9,
        "nation":nation,
        "checksum":code,
    }
    full_url = url + "?" + urlencode(data)
    req = Request(full_url, headers={"User-Agent":current_app.config["USER_AGENT"]})
    res = urlopen(req).read()
    return res == b"1\n"
