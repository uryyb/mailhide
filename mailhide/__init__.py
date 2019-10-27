from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import logging
import os
from pathlib import Path
from mailhide import helpers

config_dic = helpers.load_config()


# setup logging
# need to adjust to values set in config file after loaded
logger = logging.getLogger("mailhide")

log_level = logging.getLevelName(config_dic["log_level"])

f_handler = logging.FileHandler(config_dic["log_file"])
f_handler.setLevel(logging.DEBUG)
f_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logger.addHandler(f_handler)

# flask app setup
app = Flask("mailhide")
app.secret_key = config_dic["app_secret_key"]
app.config["DEBUG"] = config_dic["debug"]
app.config["HOST"] = config_dic["host"]
app.config["PORT"] = config_dic["port"]

# setup flask sqlalchemy
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config_dic["sqlalchemy_track_modifications"]
app.config["SQLALCHEMY_DATABASE_URI"] = config_dic["sqlalchemy_database_uri"]
db = SQLAlchemy(app)

# flask-login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

import mailhide.views