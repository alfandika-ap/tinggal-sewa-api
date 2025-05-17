from dotenv import load_dotenv
import os

load_dotenv()

server = os.getenv("PROXY_SERVER")
username = os.getenv("PROXY_USERNAME")
password = os.getenv("PROXY_PASSWORD")

config = {
    "server": server,
    "username": username,
    "password": password,
}