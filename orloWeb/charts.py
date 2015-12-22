import arrow
import operator
from itertools import cycle
import datetime
import calendar
from copy import deepcopy
from flask import current_app as app

'''
Functions for building charts from a list of releases

For consumption by Chart.js
'''


# Chart colour configuration
DATASET_RELEASE = {
    "label": "Release",
    "fillColor": "rgba(215,235,220,0.5)",
    "strokeColor": "rgba(215,235,220,1)",
    "highlightFill": "rgba(215,235,220,0.5)",
    "highlightStroke": "rgba(226,223,211,1)",
    "pointColor": "rgba(215,235,220,1)",
    "pointStrokeColor": "#fff",
    "pointHighlightFill": "#fff",
    "pointHighlightStroke": "rgba(226,223,211,1)",
    "data": []
}

DATASET_ROLLBACK = {
    "label": "Rollback",
    "fillColor": "rgba(255,206,183,0.5)",
    "strokeColor": "rgba(255,206,183,1)",
    "highlightFill": "rgba(255,206,183,0.5)",
    "highlightStroke": "rgba(226,223,211,1)",
    "pointColor": "rgba(255,206,183,1)",
    "pointStrokeColor": "#fff",
    "pointHighlightFill": "#fff",
    "pointHighlightStroke": "rgba(226,223,211,1)",
    "data": []
}


def pie(releases):
    """
    Return package stats given a list of releases in JSON format suitable for
    use by Chart.js
    """

    package_data = []
    package_rollback_data = []

    packages = {}
    packages_rollback = {}

    # colours = cycle(['#128C80', '#185556', '#128C80', '#E2E8CE', '#D9C127'])
    # colours = cycle(['#556270', '#4ECDC4', '#C7F464', '#FF6B6B', '#C44D58'])
    colours = cycle(['#D6C9D2', '#FFCEB7', '#EAD6CB', '#E2DFD3', '#D7EBDC'])

    # First build counts of all the packages
    for r in releases:
        for p in r['packages']:
            if p['rollback']:
                try:
                    packages_rollback[p['name']] += 1
                except KeyError:
                    packages_rollback[p['name']] = 1
            else:
                try:
                    packages[p['name']] += 1
                except KeyError:
                    packages[p['name']] = 1

    # Generate the package chart data
    for package, count in packages.iteritems():
        package_data.append({
            "value": count,
            "color": colours.next(),
            "highlight": '#7AA0AD',
            "label": package
            })

    for package, count in packages_rollback.iteritems():
        package_rollback_data.append({
            "value": count,
            "color": colours.next(),
            "highlight": '#7AA0AD',
            "label": package
            })

    c = 0
    for k, v in packages.iteritems():
        c += v

    c_normal = [v for k, v in packages_rollback.iteritems()]
    c_rollbacks = [v for k, v in packages_rollback.iteritems()]

    rollback_data = [
        {
            "value": sum(c_normal),
            "color": '#D7EBDC',
            "highlight": '#7AA0AD',
            "label": "Normal Release"
        },
        {
            "value": sum(c_rollbacks),
            "color": '#FFCEB7',
            "highlight": '#7AA0AD',
            "label": "Rollbacks"
        }
    ]

    return package_data, package_rollback_data, rollback_data


def bar_monthly(releases):
    """
    Return releases by month in a bar chart

    Suitable for consumption by Chart.js
    """

    n_data = {}  # normal data
    r_data = {}  # rollback data

    # Initial chart setup
    chart_data = {
        'labels': [],
        'datasets': [
            deepcopy(DATASET_RELEASE),
            deepcopy(DATASET_ROLLBACK)
        ]}

    for release in releases:
        t = datetime.datetime.fromtimestamp(release['stime'])
        month = t.utctimetuple().tm_mon
        # month = t.strftime('%B')
        year = t.strftime('%Y')

        if not release['rollback']:
            try:
                n_data[year]
            except KeyError:
                n_data[year] = {}
            try:
                n_data[year][month] += 1
            except KeyError:
                n_data[year][month] = 1
        else:
            try:
                r_data[year]
            except KeyError:
                r_data[year] = {}
            try:
                r_data[year][month] += 1
            except KeyError:
                r_data[year][month] = 1
    # Now we have a dict of releases by calendar month

    if len(n_data) is 0:
        app.logger.debug("No data when generating chart, returning None")
        return None

    # Dicts aren't sorted, make sure we're in chronological order
    for year in sorted(n_data.keys()):
        # Same with months
        month_data = sorted(n_data[year].keys())

        first_month = 1
        last_month = 12
        if len(n_data) > 1:
            if year == min(sorted(n_data.keys())):
                # first year, so we must start at the first month
                first_month = month_data[0]
            elif year == max(sorted(n_data.keys())):
                # last year, so we must stop at the last month
                last_month = month_data[-1]
        else:
            # Only one year, so start at the begin/finish months of this year
            first_month = month_data[0]
            last_month = month_data[-1]

        # Iterate over all months from first to last so we include months which
        # have no value
        for m in range(first_month, last_month+1):
            # Need to add 1 to month to ensure correct range

            # Add a label for the month
            chart_data['labels'].append("{} {}".format(
                calendar.month_name[m],
                year))

            # Insert a value for the month if it exists, else 0
            try:
                chart_data['datasets'][0]['data'].append(n_data[year][m])
            except KeyError:
                chart_data['datasets'][0]['data'].append(0)

            # Get rollbacks for the same month
            # We're assuming here, that rollbacks can only happen in a month
            # in which there was a normal release, which is a fair assumption
            try:
                chart_data['datasets'][1]['data'].append(r_data[year][m])
            except KeyError:
                # Append 0 rollbacks if not found
                chart_data['datasets'][1]['data'].append(0)

    app.logger.debug("Generated chart data: {}".format(str(chart_data)))

    return chart_data


def bar_weekly(releases):
    """
    Return releases by week in a bar/line chart

    Suitable for consumption by Chart.js
    """

    n_data = {}  # normal data
    r_data = {}  # rollback data


    chart_data = {
        'labels': [],
        'datasets': [
            deepcopy(DATASET_RELEASE),
            deepcopy(DATASET_ROLLBACK)
        ]
    }

    for release in releases:
        t = datetime.datetime.fromtimestamp(release['stime'])
        week = t.isocalendar()[1]
        year = t.strftime('%Y')

        if not release['rollback']:
            try:
                n_data[year]
            except KeyError:
                n_data[year] = {}
            try:
                n_data[year][week] += 1
            except KeyError:
                n_data[year][week] = 1
        else:
            try:
                r_data[year]
            except KeyError:
                r_data[year] = {}
            try:
                r_data[year][week] += 1
            except KeyError:
                r_data[year][week] = 1
    # Now we have a dict of releases by calendar week

    if len(n_data) is 0:
        app.logger.debug("No data when generating chart, returning None")
        return None

    # Dicts aren't sorted, make sure we're in chronological order
    for year in sorted(n_data.keys()):
        # Same with weeks
        week_data = sorted(n_data[year].keys())

        first_week = 1
        last_week = 52
        if len(n_data) > 1:
            if year == min(sorted(n_data.keys())):
                # first year, so we must start at the first week
                first_week = week_data[0]
            elif year == max(sorted(n_data.keys())):
                # last year, so we must stop at the last week
                last_week = week_data[-1]
        else:
            # Only one year, so start at the begin/finish weeks of this year
            first_week = week_data[0]
            last_week = week_data[-1]

        # Iterate over all weeks from first to last so we include weeks which
        # have no value
        for w in range(first_week, last_week+1):
            # Need to add 1 to week to ensure correct range

            # Add a label for the week
            chart_data['labels'].append("Week {}".format(w, year))

            # Insert a value for the week if it exists, else 0
            try:
                chart_data['datasets'][0]['data'].append(n_data[year][w])
            except KeyError:
                chart_data['datasets'][0]['data'].append(0)

            # Get rollbacks for the same week
            # We're assuming here, that rollbacks can only happen in a week
            # in which there was a normal release, which is a fair assumption
            try:
                chart_data['datasets'][1]['data'].append(r_data[year][w])
            except KeyError:
                # Append 0 rollbacks if not found
                chart_data['datasets'][1]['data'].append(0)

    app.logger.debug("Generated chart data: {}".format(str(chart_data)))

    return chart_data


def bar_daily(releases):
    """
    Return releases by day in a bar/line chart

    Suitable for consumption by Chart.js
    """

    n_data = {}  # normal data
    r_data = {}  # rollback data


    chart_data = {
        'labels': [],
        'datasets': [
            deepcopy(DATASET_RELEASE),
            deepcopy(DATASET_ROLLBACK)
        ]
    }

    for release in releases:
        t = datetime.datetime.fromtimestamp(release['stime'])
        day = t.weekday()

        if not release['rollback']:
            try:
                n_data[day] += 1
            except KeyError:
                n_data[day] = 1
        else:
            try:
                r_data[day] += 1
            except KeyError:
                r_data[day] = 1
    # Now we have a dict of releases by calendar day

    if len(n_data) is 0:
        app.logger.debug("No data when generating chart, returning None")
        return None

    # Dicts aren't sorted, make sure we're in chronological order
    for d in sorted(n_data.keys()):
        # Iterate over all days from first to last so we include days which
        # have no value
        chart_data['labels'].append(calendar.day_name[d])

        # Insert a value for the day if it exists, else 0
        try:
            chart_data['datasets'][0]['data'].append(n_data[d])
        except KeyError:
            chart_data['datasets'][0]['data'].append(0)

        # Get rollbacks for the same day
        # We're assuming here, that rollbacks can only happen in a day
        # in which there was a normal release, which is a fair assumption
        try:
            chart_data['datasets'][1]['data'].append(r_data[d])
        except KeyError:
            # Append 0 rollbacks if not found
            chart_data['datasets'][1]['data'].append(0)

    app.logger.debug("Generated chart data: {}".format(str(chart_data)))

    return chart_data


def line_avg_duration(releases):
    """
    Return average release duration by month, for Chart.js
    """

    n_data = {}  # normal data

    chart_data = {
        'labels': [],
        'datasets': [
            deepcopy(DATASET_RELEASE),
        ]
    }
    chart_data['datasets'][0]["label"] = "Duration in seconds"

    for release in releases:
        t = datetime.datetime.fromtimestamp(release['stime'])
        month = t.utctimetuple().tm_mon
        # month = t.strftime('%B')
        year = t.strftime('%Y')

        if release['duration']:
            try:
                n_data[year]
            except KeyError:
                n_data[year] = {}
            try:
                n_data[year][month].append(release['duration'])
            except KeyError:
                n_data[year][month] = [release['duration']]

    if len(n_data) is 0:
        return None

    for year, months in n_data.iteritems():
        for month, values in months.iteritems():
            chart_data['labels'].append('{} {}'.format(
                calendar.month_name[month],
                year))

            '''
            # Append average duration to our data
            chart_data['datasets'][0]['data'].append(
                numpy.round(numpy.average(
                    [int(d) for d in values]),
                    decimals=0)
                )
            '''
            # Append average duration to our data
            l = [int(d) for d in values]
            avg = sum(l) / len(l)

            chart_data['datasets'][0]['data'].append(int(round(avg)))

    return chart_data


def line_duration(releases):
    """
    Return line charting release durations, for Chart.js
    """

    if len(releases) > 30:
        # Trim the releases to the last of the list, to avoid too many plot
        # points
        releases = releases[len(releases)-30:]

    chart_data = {
        'labels': [],
        'datasets': [
            deepcopy(DATASET_RELEASE),
        ]
    }
    chart_data['datasets'][0]["label"] = "Duration in seconds"

    for release in releases:
        stime = arrow.get(release['stime'])
        month_name = arrow.arrow.locales.Locale.month_name(stime.month)
        legend_value = "{} {}".format(stime.year, month_name)

        if release['duration']:
            chart_data['datasets'][0]['data'].append(release['duration'])
            chart_data['labels'].append(legend_value)

    return chart_data


def line_duration_pkg(releases, package_name):
    """
    Return a chart of up to the last 30 release durations, for Chart.js
    """

    chart_data = {
        'labels': [],
        'datasets': [
            deepcopy(DATASET_RELEASE),
        ]
    }
    chart_data['datasets'][0]["label"] = "Duration in seconds"

    for release in releases:
        legend_value = release['id']
        for package in release['packages']:
            if package['name'] != package_name:
                continue
            if package['duration']:
                chart_data['datasets'][0]['data'].append(package['duration'])
                chart_data['labels'].append(legend_value)

    l = len(chart_data['datasets'][0]['data'])
    if l > 30:
        # Trim the datasets and labels lists
        chart_data['datasets'][0]['data'] = \
            chart_data['datasets'][0]['data'][l-30:]
        chart_data['labels'] = chart_data['labels'][l-30:]

    return chart_data


def bar_user(releases):
    """
    Return releases by user in a bar chart

    Suitable for consumption by Chart.js
    """

    data = {}

    chart_data = {
        'labels': [],
        'datasets': [
            deepcopy(DATASET_RELEASE),
        ]
    }
    chart_data['datasets'][0]["label"] = "User"

    for release in releases:
        user = release['user']

        try:
            data[user] += 1
        except KeyError:
            data[user] = 1

    sorted_data = sorted(data.items(), key=operator.itemgetter(1),
                         reverse=True)

    for key, value in sorted_data:
        chart_data['labels'].append(key)
        chart_data['datasets'][0]['data'].append(value)

    return chart_data


def bar_pkg(releases, rollback=False):
    """
    Return releases by package in a bar chart, suitable for Chart.js

    Arguments:
    rollback -- if True, return data for rollback releases only
    """

    packages = {}

    if not rollback:
        datasets = deepcopy(DATASET_RELEASE)
    elif rollback:
        datasets = deepcopy(DATASET_ROLLBACK)
    chart_data = {
        'labels': [],
        'datasets': [
            datasets
        ]
    }

    for release in releases:
        if rollback and release['rollback'] == 0:
            # If getting rollback chart, we don't want non-rollback releases
            continue
        elif not rollback and release['rollback'] == 1:
            # If getting a normal chart, we don't want rollback releases
            continue

        for package in release['packages']:
            name = package['name']
            if "assets" in name:
                continue
            name = name.replace("gumtree-", "")
            try:
                packages[name] += 1
            except KeyError:
                packages[name] = 1

    sorted_packages = sorted(packages.items(), key=operator.itemgetter(1),
                             reverse=True)
    for key, value in sorted_packages:
        chart_data['labels'].append(key)
        chart_data['datasets'][0]['data'].append(value)

    return chart_data
