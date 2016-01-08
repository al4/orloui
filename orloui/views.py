from copy import copy
from orloui import app, charts, orlo, config
from orloui.exceptions import OrloConnectionError
import orloui.template_filters
from flask import request, abort, jsonify, render_template, redirect, make_response
from requests.exceptions import ConnectionError
import arrow
from orloui.util import calculate_offset
from collections import OrderedDict

TFMT = config.get('main', 'time_format')


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

    last_week = arrow.utcnow().replace(days=-14).strftime(TFMT)
    last_month = arrow.utcnow().replace(months=-1).strftime(TFMT)
    last_year = arrow.utcnow().replace(years=-1).strftime(TFMT)

    try:
        r_month = orlo.get_releases(desc=True, stime_after=last_month)['releases']
    except ConnectionError:
        # Catch requests connection error and rethrow
        raise OrloConnectionError("Could not connect to orlo server: {}".format(orlo.uri))

    render_args = {
        'chart_rollback_data': charts.pie_normal_vs_rollback(r_month),
        'chart_package_data': charts.pie_releases_by_package(r_month),
        'chart_package_rollback_data': charts.pie_rollbacks_by_package(r_month),
        'last_release': orlo.get_releases(
            limit=1, desc=True, stime_after=last_year, package_rollback=False)['releases'][0],
        'last_rollback': orlo.get_releases(
            limit=1, desc=True, stime_after=last_year, package_rollback=True)['releases'][0],
        'releases_in_progress': orlo.get_releases(
            package_rollback=False, package_status="IN_PROGRESS")['releases'],
        'rollbacks_in_progress': orlo.get_releases(
            package_rollback=True, package_status="IN_PROGRESS")['releases'],
        'releases_past': orlo.get_releases(desc=True, stime_after=last_week)['releases'],
    }

    return render_template('overview.html', **render_args)


@app.route('/releases', methods=['GET'])
def page_releases():
    """
    List of releases
    """

    args = dict((k, v) for k, v in request.args.items())
    per_page = int(args.pop('pp', 10))
    page = int(args.pop('page', 1))

    packages = orlo.get_info('packages', 'list')['packages']

    # Orlo query params
    release_query_params = {
        'desc': True,
        'offset': calculate_offset(page, per_page),
    }
    if per_page:
        release_query_params['limit'] = per_page
    for field, value in args.iteritems():
        release_query_params[field] = value
    releases = orlo.get_releases(**release_query_params)['releases']

    # Template params
    template_params = {
        'releases': releases,
        'package_list': sorted(packages),
        'page': page,
        'user_list': orlo.get_info('users', 'list'),
    }
    return render_template('list.html', **template_params)


@app.route('/releases/<release_id>', methods=['GET'])
def page_releases_single(release_id):
    """
    Display a single release

    :param UUID release_id: ID of release to display
    """

    release = orlo.get_releases(release_id)['releases'][0]

    return render_template('display.html',
                           release=release)


@app.route('/status', methods=['GET'])
def page_status():
    """
    Release status page, suitable for wall display
    """
    # Dates we need
    past_week = arrow.utcnow().replace(weeks=-1).strftime(TFMT)
    past_month = arrow.utcnow().replace(months=-1).strftime(TFMT)
    past_year = arrow.utcnow().replace(years=-1).strftime(TFMT)
    this_year = arrow.get('{}-01-01'.format(arrow.now().year)).strftime(TFMT)

    # Get releases for these time periods
    r_past_week = orlo.get_releases(stime_after=past_week)['releases']
    r_past_month = orlo.get_releases(stime_after=past_month)['releases']
    r_this_year = orlo.get_releases(stime_after=this_year)['releases']
    chart_data_30 = charts.pie_normal_vs_rollback(r_past_month)
    chart_data_7 = charts.pie_normal_vs_rollback(r_past_week)
    chart_data_year = charts.pie_normal_vs_rollback(r_this_year)

    # Build the charts
    render_args = {
        'last_release': orlo.get_releases(
            latest=True, stime_after=past_year, package_rollback=False)['releases'][0],
        'last_rollback': orlo.get_releases(
            latest=True, stime_after=past_year, package_rollback=True)['releases'][0],
        'releases_in_progress': orlo.get_releases(
            package_rollback=False, package_status="IN_PROGRESS")['releases'],
        'rollbacks_in_progress': orlo.get_releases(
            package_rollback=True, package_status="IN_PROGRESS")['releases'],
        'chart_data_30': chart_data_30,
        'chart_data_7': chart_data_7,
        'chart_data_year': chart_data_year,
    }
    response = make_response(render_template('status.html', **render_args))
    # response.headers['Refresh'] = 10
    return response


@app.route('/releases/<release_id>', methods=['GET'])
def page_release_single(release_id=None):
    """
    Display a single release

    :param release_id: The UUID of the release to display
    """

    release = orlo.get_releases(release_id)

    view = request.args.get('view', 'html')
    if view == "json":
        return jsonify(release)
    elif view == "html":
        render_args = {
            'version': "<version>",
            'title': "Release {}".format(release_id),
            'release': release,
        }
        return render_template('display.html', **render_args)


@app.route('/packages/versions', methods=['GET'])
def page_packages_versions():
    """
    Display the last successful release of all packages
    """

    versions = OrderedDict(sorted(
            orlo.get_info('packages', 'versions').items()
    ))

    view = request.args.get('view', 'html')
    if view == "json":
        return jsonify(versions)
    elif view == "html":
        render_args = {
            'versions': versions,
        }
        return render_template('versions.html', **render_args)


@app.route('/packages', methods=['GET'])
def page_packages():
    """
    Landing page for packages
    """

    packages = sorted(
            orlo.get_info('packages', 'list')['packages']
    )

    print(packages)
    return render_template('package_list.html', packages=packages)
