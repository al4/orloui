from orloWeb import app
from orloWeb import orlo
from flask import request, abort, jsonify
import arrow
import datetime


@app.route('/ping', methods=['GET'])
def ping():
    """
    Ping!
    """
    return "pong"


@app.route('/', methods=['GET'])
def home():
    """
    The home page
    """
    releases = orlo.get_releases()
    return releases
