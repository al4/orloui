from orloWeb import app
from flask import request, abort
import arrow
import datetime
import orloclient


@app.route('/ping', methods=['GET'])
def home():
    """
    The home page
    """
    return "pong"
