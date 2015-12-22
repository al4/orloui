from __future__ import print_function
from orloWeb import app, config
import arrow
import datetime

__author__ = 'alforbes'


@app.template_filter('short_uuid')
def short_uuid(s):
    return s[:5]


@app.template_filter('friendly_time')
def friendly_time(s):
    t = arrow.get(s)
    return t.format('YYYY-MM-DD HH:MM')


@app.template_filter('friendly_time_relative')
def friendly_time_relative(s):
    now = arrow.utcnow()
    t = arrow.get(s)
    return t.humanize(now)


@app.template_filter('friendly_duration')
def friendly_duration(s):
    td = datetime.timedelta(seconds=int(s))
    return arrow.Loc