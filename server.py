import os
from flask import Flask, request

from bp.auth import auth
from bp.routes import routes

app = Flask(__name__, static_folder='static', template_folder='templates')

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


host = os.getenv('HOST', "localhost")
port = int(os.getenv('PORT', 5050))

app.register_blueprint(auth)
app.register_blueprint(routes)

app.run(host=host, port=port, debug=True)
