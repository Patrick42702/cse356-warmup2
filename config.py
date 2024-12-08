import os
from dotenv import load_dotenv
load_dotenv("env")

REDIS_IP = os.getenv("REDIS_IP")
POSTFIX_IP=os.getenv("POSTFIX_IP")
MONGO_IP=os.getenv("MONGO_IP")
HOST=os.getenv("HOST")
PORT=os.getenv("PORT")
SECRET_KEY="A SECRET KEY"
