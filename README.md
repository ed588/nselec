#important 
This software is no longer maintained by me. It is made available for historical purposes and in the hope
that it may be useful to people. I cannot however offer support for it, or maintain it into the future.

This repository contains the latest version of the software at the time that it was archived. Earlier commits
are not included in this repository for various reasons. If you need an old version for some specific reason,
contact me.

Below is the original README file:

# nselec
An election-running web app for your NationStates region.

# Features
- Supports for/against and fully-ranked elections
- Automatically opens and closes elections at a given date and time
- Verifies the voter's nation name with the NationStates verification API
- Easy-to-use admin interface for managing elections
- User management system with permissions and logins
- Looks nice :)

# Installation and Usage
You will need:
- Python 3.5+ (with pip)
- Any web server that supports wsgi.

1. (Optional) Create a venv: `python3 -m venv venv`, and activate it: `source venv/bin/activate`
2. Install nselec: `pip install nselec` (this will install requirements)
3. Set things up:
    1. Setup the environment: `export FLASK_APP=nselec`
    2. Create the instance: `flask initialise`
    3. Make yourself an admin user: `flask new_admin yourusername` and enter the password when prompted
    4. Edit the config file. The path will be given to you when you did the initialisation command; it is normally at
    `venv/var/nselec-instance/config.py`. See the section "Config File" below for information on what you should put
    in that.
4. (Optional) See if it works: `flask run` then visit the address it shows you. Do whatever you want, check
    it all works, then come back here.
5. Connect it to your production WSGI server. This really depends on what server you're using, so you should read the 
    [flask docs on deploying](http://flask.pocoo.org/docs/1.0/deploying/) for instructions. But normally you should just be able to put this 
    ```python
    from nselec import create_app
    application = create_app()
    ```
    in your `wsgi.py`, and then do whatever you need to do. But I'm not a WSGI expert, go read the flask docs.
6. Visit the website, log in using the credentials you supplied in step 3.3, make elections, add some more users, profit! Or maybe not, who knows...

## The Config File
- The first required field for this is `GET_VOTERS`, which should be a function that returns a dict of voters, which should look like this: `{"honk_donk": "Honk Donk", ...}`.
If you're using [my `ns-rc-checker` script](https://github.com/ed588/ns-rc-checker), then it'll look like this

```python
import pickle
def GET_VOTERS():
    with open("/path/to/your/memstates.pkl", "rb") as fp:
        data = pickle.load(fp)
    return data['example']
```
- Another required (well, not technically, but you definitely need to on production otherwise people could bypass all the security) field is `SECRET_KEY`. Check out the [flask docs](http://flask.pocoo.org/docs/1.0/config/#SECRET_KEY) for what you should set this to.
- Another required field is `USER_AGENT` which is the user agent to use when making requests to the NationStates API for verifying nation identities. NationStates requires that you use a descriptive user agent when accessing their API; putting the name of your region and/or nation here is probably sufficient.
- The three other required fields are `TITLE_MAINPAGE`, `TITLE_LONG`, and `TITLE_SHORT`.
  These string values control the title of the site, as displayed in different places. 
  - `TITLE_MAINPAGE` is the big title on the main election listing page.
  - `TITLE_SHORT` is displayed in the page titles and as the first entry
  in breadcrumbs, linking back to the main page.
  - `TITLE_LONG` is displayed at the top of the footer of each page.

  These all have sensible (albeit fairly generic) defaults, so it's not 
critical if you forget to set these.

- Another field you can set is `DATABASE` which should be the filename of the database to use. It defaults 
to `"nselec.db"` in the instance folder, which should be fine for most people, but you can change it here if you really want.

- The `FAVICON` field controls the url of the favicon used by the site. It defaults to `favicon.ico` in the application root.

# Note on css
The CSS file (`nselec/static/site.min.css`) is [bulma](https://bulma.io) with some small customisations. The SCSS
file containing those customisations can be found [here](https://gist.github.com/ed588/9d87ba2bca0b6580fca6b691b5edcfc9).

# History
[Conifer](https://nationstates.net/region=conifer) is a region in the game NationStates.
Like many other regions, we have democratic elections for things such as legislation and regional officials.
There didn't seem to be any existing solution for elections with large numbers of people which we didn't have to pay
for, so Honk Donk (aka ed588) made a quick app in Flask that just about solved the problem. This version of nselec
is so bad that Honk Donk has refused to release it anywhere.

A little later, when we realised that the existing app didn't support necessary things such as ranked elections, and 
that the admin interface was impossible to use, (as well as the fact that all the code that wasn't in the templates
was in a single python file that was impossible to maintain or do anything with), Honk Donk rewrote the entire thing.
It now looked nicer (using the css library bulma for the frontend), supported ranked elections, and had a usable
interface for adding new elections. Additionally, it was split into separate files, so that Honk Donk could actually
maintain it and add new features in the future.
