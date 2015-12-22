from __future__ import print_function
from orloWeb import app, config
import arrow
import datetime

__author__ = 'alforbes'


@app.template_filter('short_uuid')
def short_uuid(s):
    return s[:8]


@app.template_filter('humanise_time')
def humanise_time(s):
    t = arrow.get(s)
    return t.format('YYYY-MM-DD HH:MM')


@app.template_filter('humanise_time_relative')
def humanise_time_relative(s):
    now = arrow.utcnow()
    t = arrow.get(s)
    return t.humanize(now)


@app.template_filter('humanise_duration')
def humanise_duration(seconds):
    """
    Convert time delta object into plain english

    :param int seconds: timedelta object
    """

    if not seconds:
        return "Unknown"

    days, r = divmod(seconds, 84600)
    hours, r = divmod(r, 3600)
    mins, r = divmod(r, 60)
    secs = r

    if days > 0:
        return '{} days, {} hours'.format(days, hours)
    elif hours > 1:
        return '{} hours, {} mins'.format(hours, mins)
    elif hours == 1:
        return '{} hour, {} mins'.format(hours, mins)
    else:
        return '{} mins, {} sec'.format(mins, secs)


@app.template_filter('get_release_status')
def get_release_status(release):
    """
    Determine the status of a release based on the packages

    :param dict release: Release dictionary
    :return: String
    """

    statuses = set([p['status'] for p in release['packages']])

    if "IN_PROGRESS" in statuses:
        return "In Progress"
    elif "FAILED" in statuses:
        return "Failed"
    elif "SUCCESSFUL" in statuses and len(statuses) == 1:
        return "Successful"
    else:
        return "Unknown"


@app.template_filter('get_rollback_status')
def get_rollback_status(release):
    statuses = set([p['rollback'] for p in release['packages']])
    print(statuses)

    if True in statuses:
        return "Yes"
    else:
        return "No"
