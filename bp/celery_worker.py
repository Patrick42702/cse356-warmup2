from celery import Celery
from pymongo import MongoClient

ip = "ip addr"

def celery_conndb():
    try:
        client = MongoClient(ip, 27017) # add ip address of main server here
        db = client.eskpj_airplanes
        return db
    except Exception as e:
        return error(str(e))


# Replace "main_machine_ip" with the actual IP address of your main machine.
REDIS_URL = f"redis://{ip}:6379/0"

app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL, include=['bp.tasks'])
