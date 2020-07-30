import logging.handlers
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

import fanyuanapp.core.constants as constants
if not os.path.exists(constants.USERDATA_FOLDER):
    os.makedirs(constants.USERDATA_FOLDER)
if not os.path.exists(constants.USERINPUT_FOLDER):
    os.makedirs(constants.USERINPUT_FOLDER)
if not os.path.exists(constants.MARKETDATA_FOLDER):
    os.makedirs(constants.MARKETDATA_FOLDER)
# if not os.path.exists(constants.BUYINFO_FOLDER):
#     os.makedirs(constants.BUYINFO_FOLDER)

BASIC_FORMAT = "%(message)s"
logfilename = app.config.get('LOG_FILE_NAME')
handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", logfilename))
formatter = logging.Formatter(BASIC_FORMAT)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))
logger.addHandler(handler)

from fanyuanapp.core.marketdata_manager import MarketDataManager

marketdataManager = MarketDataManager()

from fanyuanapp.main.routes import main
from fanyuanapp.indicator.routes import indicator
from fanyuanapp.database.routes import database
from fanyuanapp.backtest.routes import backtest
from fanyuanapp.errors.handlers import errors

app.register_blueprint(main)
app.register_blueprint(indicator)
app.register_blueprint(database)
app.register_blueprint(backtest)
app.register_blueprint(errors)


