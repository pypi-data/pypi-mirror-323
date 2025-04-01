"""Initialize environment variables for the dataset module."""

import os

from dotenv import load_dotenv

load_dotenv()

PURPLE_PROTOCOL = os.getenv("PURPLE_PROTOCOL")
PURPLE_PORT = os.getenv("PURPLE_PORT")
PURPLE_HOST = os.getenv("PURPLE_HOST")
PURPLE_DEBUG = os.getenv("PURPLE_DEBUG")

APP_URL = f"{PURPLE_PROTOCOL}://{PURPLE_HOST}:{PURPLE_PORT}"
