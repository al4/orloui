from __future__ import print_function
from orloui import app
from flask import make_response
from orloclient.exceptions import OrloClientError, OrloServerError
from orloui.exceptions import OrloConnectionError

__author__ = 'alforbes'

# TODO use an application template to display errors nicely


@app.errorhandler(OrloConnectionError)
def server_error(error):
    return error.message, error.status_code


@app.errorhandler(OrloClientError)
@app.errorhandler(OrloServerError)
def handle_orlo_error(error):
    response = make_response(error.message)
    response.status_code = 500
    return response
