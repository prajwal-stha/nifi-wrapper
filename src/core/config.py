from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

POSTGRES_USER = config("POSTGRES_USER", cast=str)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="db")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str)
NIFI_IP = config("NIFI_IP", cast=str)
ROOT_CANVAS_ID = config("ROOT_CANVAS_ID", cast=str)
NIFI_USER = config("NIFI_USER", cast=str)
NIFI_PASSWORD = config("NIFI_PASSWORD", cast=str)