"""
make an .env file:

DEBUG_MODE=can be 0 or 1
SECRET_KEY=
"""


import os
from dotenv import load_dotenv


CURRENT_PATH =  os.path.dirname(os.path.abspath(__file__))


ENV_FILE = os.path.join(CURRENT_PATH, ".env")
load_dotenv(dotenv_path=ENV_FILE)


DEBUG_MODE = os.getenv("DEBUG_MODE")
SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_FILE = os.path.join(CURRENT_PATH, "data.db")
