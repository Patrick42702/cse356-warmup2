# celery.py
from celery import Celery

def make_celery(app):
    # Configure Celery to use Redis as the broker
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['broker_url'],
        include=app.config['include']
    )
    celery.conf.update(app.config)

    # Make context for Flask application in Celery tasks
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery
