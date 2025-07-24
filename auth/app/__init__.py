from flask import Flask


def create_app():
    app = Flask(__name__)

    from .routes import auth
    app.register_blueprint(auth)

    return app
