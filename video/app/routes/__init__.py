# from .serve import serve_bp
from .transcode import transcode_bp
from .upload import upload_bp


def register_routes(app):
    app.register_blueprint(upload_bp)
    # app.register_blueprint(serve_bp)
    app.register_blueprint(transcode_bp)
