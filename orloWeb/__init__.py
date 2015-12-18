from flask import Flask
from logging.handlers import RotatingFileHandler

from orlo.config import config

app = Flask(__name__)

if config.getboolean('main', 'propagate_exceptions'):
    app.config['PROPAGATE_EXCEPTIONS'] = True

if config.getboolean('logging', 'debug'):
    app.debug = True
app.logger.debug('Debug enabled')

logfile = config.get('logging', 'file')
if logfile != 'disabled':
    handler = RotatingFileHandler(
        logfile,
        maxBytes=10000,
        backupCount=1,
    )
    app.logger.addHandler(handler)

# Must be imported last
import orloWeb.views
