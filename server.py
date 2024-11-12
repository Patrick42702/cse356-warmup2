import os
from flask import Flask, request
from bp.celery import make_celery
from bp.auth import auth
from bp.routes import routes
import logging

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.update(
        broker_url='redis://redis:6379/0',
        result_backend='redis://redis:6379/0',
        include=['bp.tasks']
    )
    app.logger.setLevel(logging.INFO)
    celery = make_celery(app)

    #config env variables
    os.environ['SECRET_KEY'] = os.urandom(12).hex()
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    @app.before_request
    def log_request_info():
        if not request.path.startswith('/static/media/'):
            app.logger.info("-" * 110)
            app.logger.info('--- REQUEST --- ')
            app.logger.info('Cookies: %s', request.cookies)

    @app.after_request
    def log_response(response):
        if not request.path.startswith('/static/media/'):
            try:
                app.logger.info('--- RESPONSE --- ')
                app.logger.info('Status: %s', response.status)
                app.logger.info('Cookies set: %s', response.headers.getlist("Set-Cookie"))
                app.logger.info('Body: %s', response.get_data())
            except Exception:
                app.logger.info("Can't display response.")
            app.logger.info("-" * 110)
        return response

    app.celery = celery
    app.register_blueprint(auth)
    app.register_blueprint(routes)
    return app, celery

app, celery = create_app()

if __name__ == "__main__":
    host = os.getenv('HOST', "0.0.0.0")
    port = int(os.getenv('PORT', 80))
    app.run(host=host, port=port)
