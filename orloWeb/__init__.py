from flask import Flask
from logging.handlers import RotatingFileHandler
from orloWeb.config import config
from orloWeb.orlo_client import orlo
from orloWeb._version import __version__


app = Flask(__name__)
app.config['VERSION'] = __version__

if config.getboolean('main', 'propagate_exceptions'):
    app.config['PROPAGATE_EXCEPTIONS'] = True

if not config.getboolean('main', 'strict_slashes'):
    app.url_map.strict_slashes = False

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
import orloWeb.view_stats

