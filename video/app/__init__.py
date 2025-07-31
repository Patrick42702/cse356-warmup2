import os

from flask import Flask
from flask_cors import CORS

from .routes import register_routes

frontend_url = os.environ.get("FRONTEND_URL", "http://host.docker.internal:3000")

def create_app():
    app = Flask(__name__)
    CORS(app, origins=[frontend_url])
    register_routes(app)
    return app
