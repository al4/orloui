from orloWeb import app
from orloWeb import charts
from orloWeb import orlo
from orloWeb.exceptions import OrloConnectionError
import orloWeb.template_filters
from flask import request, abort, jsonify, render_template
from requests.exceptions import ConnectionError
import arrow
import datetime


@app.errorhandler(OrloConnectionError)
def server_error(error):
    # TODO use application template to display errors nicely
    return error.message, error.status_code


@app.route('/ping', methods=['GET'])
def ping():
    """
    Ping!
    """
    return "pong"


@app.route('/', methods=['GET'])
def overview():
    """
    The home page

    Fetches the most recent releases
    """

    yesterday = arrow.utcnow().replace(days=-1).strftime('%Y-%m-%dT%H:%M:%SZ')
    last_week = arrow.utcnow().replace(days=-28).strftime('%Y-%m-%dT%H:%M:%SZ')
    last_month = arrow.utcnow().replace(months=-1).strftime('%Y-%m-%dT%H:%M:%SZ')

    try:
        last_rollback = orlo.get_releases(package_rollback=True, stime_after=last_week)[
            'releases'][0]
        r_lastwk = orlo.get_releases(stime_after=last_week)['releases']
        r_yest = orlo.get_releases(stime_after=yesterday)['releases']
        r_month = orlo.get_releases(stime_after=last_month)['releases']
    except ConnectionError:
        # Catch requests connection error and rethrow
        raise OrloConnectionError("Could not connect to orlo server: {}".format(orlo.uri))

    releases_in_progress = orlo.get_releases(
        package_rollback=False, package_status="IN_PROGRESS")['releases']
    rollbacks_n_progress = orlo.get_releases(
        package_rollback=True, package_status="IN_PROGRESS")['releases']

    chart_package_data, chart_package_rollback_data, chart_rollback_data = \
        charts.pie(r_month)

    return render_template(
        'overview.html',
        last_release=r_lastwk[-1:],
        last_rollback=last_rollback,  # release info
        releases_past=r_lastwk,
        releases_in_progress=releases_in_progress,  # int
        rollbacks_in_progress=rollbacks_n_progress,  #
        chart_package_data=chart_package_data,
        chart_package_rollback_data=chart_package_rollback_data,
        chart_rollback_data=chart_rollback_data,
    )


@app.route('/list', methods=['GET'])
def list():
    """
    List of releases
    """
