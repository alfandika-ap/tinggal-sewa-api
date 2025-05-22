from dotenv import load_dotenv
import os

load_dotenv()

def get_proxy_config():
    return {
        "server": os.getenv("PROXY_SERVER"),
        "username": os.getenv("PROXY_USERNAME"),
        "password": os.getenv("PROXY_PASSWORD"),
    }
