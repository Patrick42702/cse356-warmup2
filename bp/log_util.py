from logging.config import dictConfig
from logging import getLogger

request_logger_types = ["video_interaction", "get_videos", "upload_file", "processing_status", "auth"]

logging_config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        },
        "celery": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "/var/log/celery.log",
        },
        "other": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "/var/log/other.log",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "celery": {
            "level": "INFO",
            "handlers": ["celery"],
        },
        "other": {
            "level": "INFO",
            "handlers": ['other']
        }
    }
}
for rlt in request_logger_types:
    logging_config['handlers'][rlt] = {
        'level': 'DEBUG', "class": "logging.FileHandler", "formatter": "default", "filename": f"/var/log/{rlt}.log"
    }
    logging_config['loggers'][rlt] = {'level': 'DEBUG', 'handlers': [rlt]}

dictConfig(logging_config)
celery_logger = getLogger("celery")
other_logger = getLogger("other")
request_loggers = [getLogger(rlt) for rlt in request_logger_types]

def get_logger(request_path):
    if request_path.startswith("/play") or request_path in ("/api/view", "/api/like"): return request_loggers[0]
    if request_path == "/api/videos": return request_loggers[1]
    if request_path == "/api/upload": return request_loggers[2]
    if request_path == "/api/processing-status": return request_loggers[3]
    if request_path in ("/api/adduser", "/api/login", "/api/verify", "/api/logout", "/api/check-auth"): return request_loggers[4]
    return other_logger