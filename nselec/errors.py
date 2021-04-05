# Error pages etc

# possible todo: make the application raise custom exceptions and handle them here
# also possible todo: replace "you don't have permission" errors with 403's
from flask import render_template

# fmt: off
def handle_404(e):
    return render_template("errors/404.html"), 404
def handle_500(e):
    return render_template("errors/500.html"), 500

# fmt: on
def init_app(app):
    app.register_error_handler(404, handle_404)
    app.register_error_handler(500, handle_500)

