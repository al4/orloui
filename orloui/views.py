from copy import copy
from orloui import app, charts, orlo, config
from orloui.exceptions import OrloConnectionError
import orloui.template_filters
from flask import request, abort, jsonify, render_template, redirect
from requests.exceptions import ConnectionError
import arrow
import datetime
import json

TFMT = config.get('main', 'time_format')


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
def page_overview():
    """
    The home page

    Fetches the most recent releases
    """

    # yesterday = arrow.utcnow().replace(days=-1).strftime(TFMT)
    last_week = arrow.utcnow().replace(days=-14).strftime(TFMT)
    last_month = arrow.utcnow().replace(months=-1).strftime(TFMT)
    last_year = arrow.utcnow().replace(years=-1).strftime(TFMT)

    try:
        last_release = orlo.get_releases(latest=True, stime_after=last_year,
                                         package_rollback=False)['releases'][0]
        last_rollback = orlo.get_releases(latest=True, stime_after=last_year,
                                          package_rollback=True)['releases'][0]
        r_last_week = orlo.get_releases(stime_after=last_week)['releases']
        # r_yesterday = orlo.get_releases(stime_after=yesterday)['releases']
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
        last_release=last_release,
        last_rollback=last_rollback,  # release info
        releases_past=r_last_week,
        releases_in_progress=releases_in_progress,  # int
        rollbacks_in_progress=rollbacks_n_progress,  #
        chart_package_data=chart_package_data,
        chart_package_rollback_data=chart_package_rollback_data,
        chart_rollback_data=chart_rollback_data,
    )


@app.route('/releases', methods=['GET'])
def page_releases():
    """
    List of releases
    """

    args = dict((k, v) for k, v in request.args.items())
    per_page = int(args.pop('pp', 30))

    query_params = {}
    for field, value in args.iteritems():
        query_params[field] = value

    releases = orlo.get_releases(**query_params)['releases']

    return render_template('list.html', releases=reversed(releases),
                           package_list=['foo', 'bar'],
                           user_list=['foouser', 'baruser'],
                           )


@app.route('/releases/<release_id>', methods=['GET'])
def page_release_single(release_id):
    """
    Display a single release

    :param UUID release_id: ID of release to display
    """

    release = orlo.get_releases(release_id)['releases'][0]
    print(release)

    return render_template('display.html',
                           release=release)



