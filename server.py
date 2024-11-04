# import os
# from flask import Flask, request
# from bp.celery import make_celery
#
# from bp.auth import auth
# from bp.routes import routes

# app = Flask(__name__, static_folder='static', template_folder='templates')
#
# app.config.update(
#     CELERY_BROKER_URL='redis://localhost:6379/0',
#     CELERY_RESULT_BACKEND='redis://localhost:6379/0'
# )
#
# celery = make_celery(app)
#
# #config env variables
# os.environ['SECRET_KEY'] = os.urandom(12).hex()
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
#
# @app.before_request
# def log_request_info():
#     app.logger.debug("-" * 110)
#     app.logger.debug('--- REQUEST --- ')
#     if (len(request.get_data()) < 2 ** 15):
#         app.logger.debug('Body: %s', request.get_data())
#     # app.logger.debug('Body: %s', request.get_data())
#     app.logger.debug('Cookies: %s', request.cookies)
#
# @app.after_request
# def log_response(response):
#     try:
#         app.logger.debug('--- RESPONSE --- ')
#         app.logger.debug('Status: %s', response.status)
#         app.logger.debug('Cookies set: %s', response.headers.getlist("Set-Cookie"))
#         app.logger.debug('Body: %s', response.get_data())
#     except Exception:
#         app.logger.debug("Can't display response.")
#     app.logger.debug("-" * 110)
#     return response


# host = os.getenv('HOST', "localhost")
# port = int(os.getenv('PORT', 5050))

# app.register_blueprint(auth)
# app.register_blueprint(routes)

# app.run(host=host, port=port, debug=True)
import os
from flask import Flask, request
from bp.celery import make_celery

from bp.auth import auth
from bp.routes import routes


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.update(
        broker_url='redis://localhost:6379/0',
        result_backend='redis://localhost:6379/0',
        include=['bp.tasks']
    )

    celery = make_celery(app)

    #config env variables
    os.environ['SECRET_KEY'] = os.urandom(12).hex()
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    @app.before_request
    def log_request_info():
        app.logger.debug("-" * 110)
        app.logger.debug('--- REQUEST --- ')
        if (len(request.get_data()) < 2 ** 15):
            app.logger.debug('Body: %s', request.get_data())
            # app.logger.debug('Body: %s', request.get_data())
        app.logger.debug('Cookies: %s', request.cookies)

    @app.after_request
    def log_response(response):
        try:
            app.logger.debug('--- RESPONSE --- ')
            app.logger.debug('Status: %s', response.status)
            app.logger.debug('Cookies set: %s', response.headers.getlist("Set-Cookie"))
            app.logger.debug('Body: %s', response.get_data())
        except Exception:
            app.logger.debug("Can't display response.")
        app.logger.debug("-" * 110)
        return response

    app.celery = celery
    app.register_blueprint(auth)
    app.register_blueprint(routes)
    return app, celery

app, celery = create_app()

if __name__ == "__main__":
    host = os.getenv('HOST', "localhost")
    port = int(os.getenv('PORT', 5050))
    app.run(host=host, port=port, debug=True)
