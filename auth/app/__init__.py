from flask import Flask

from .routes import auth


def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth)
    return app
