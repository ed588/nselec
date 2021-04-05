from datetime import datetime, timezone
from tinydb import TinyDB
from tinydb_serialization import Serializer, SerializationMiddleware
from flask import g, current_app


# Serialization
sz = SerializationMiddleware()


class DatetimeSerializer(Serializer):
    OBJ_CLASS = datetime

    def encode(self, obj):
        return str(obj.timestamp())

    def decode(self, s):
        return datetime.fromtimestamp(float(s))


sz.register_serializer(DatetimeSerializer(), "timestamp")

# Operations
def list_append(field, item):
    def transform(doc):
        doc[field].append(item)

    return transform


def inc_result(field):
    # increments value in ['votes'] if it's there, otherwise creates it with value 1
    def transform(doc):
        if field in doc["votes"]:
            doc["votes"][field] += 1
        else:
            doc["votes"][field] = 1

    return transform


# Flask integration
def _get_db():
    if current_app.config["ENV"] == "production":
        return TinyDB(current_app.config["DATABASE"], storage=sz)
    else:
        return TinyDB(
            current_app.config["DATABASE"],
            storage=sz,
            sort_keys=True,
            indent=4,
            separators=(",", ": "),
        )
        
def get_db():
    if "db" not in g:
        g.db = _get_db()
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)  # close the db at the end of the request
