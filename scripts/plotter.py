#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / scripts / chart plotter
#
# Copyright (C) 2012 Wang Xuerui <idontknw.wang@gmail.com>
#
# This file is part of moehime.
#
# moehime is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# moehime is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with moehime.  If not, see <http://www.gnu.org/licenses/>.

# TODO: MASSIVELY REFACTOR THIS!!! 这个得大尺度重构

from __future__ import unicode_literals, division

import sys

stderr = sys.stderr

import cPickle
import re
from itertools import izip_longest

import datetime
from time import mktime

# backends possibly need configuration, mainly because of Windows
# Also Tk's look-and-feel sucks
# XXX this code is definitely smelly, needs to get rid of very soon
# 图形后端可能需要配置，主要是因为要支持 Windows 的原因
# 而且 Tk 界面给人感觉实在蛋疼
# XXX 这段代码味道很不好，需要非常快地解决掉
import matplotlib
_backend_decided = False

if sys.platform == 'win32':
    try:
        import PySide
        matplotlib.rc('backend', qt4='PySide')
        matplotlib.use('Qt4Agg')
        _backend_decided = True
    except ImportError:
        pass
else:
    # let's use auto detection on non-Windows platforms
    # 非 Windows 平台就用自动检测吧
    _backend_decided = True

if not _backend_decided:
    raise RuntimeError('could not decide what backend to use')
del _backend_decided

import matplotlib.pyplot as plt
import matplotlib.font_manager as fontmgr
from matplotlib.dates import date2num, AutoDateFormatter, AutoDateLocator

RE_NAME = re.compile(
        r'^(?P<name>.*?)(?:（(?P<shortname>[^）]+)）)?＠(?P<series>.*)$'
        )

#####################################################################
# Plotting settings

IMAGE_SIZE = (8.0, 6.0, )

AXES_TRANSPARENCY = True

SHOW_TITLE = False
TITLE_FORMAT = '最萌%(year)d %(month)02d/%(day)02d 第 %(group)d 组面票图'

TITLE_FONT = fontmgr.FontProperties(
        #family='WenQuanYi Micro Hei',
        size=20,
        #weight=500,
        #fname='/home/xenon/.fonts/wqy-microhei-lite.ttc',
        fname='/usr/share/fonts/wqy-microhei/wqy-microhei.ttc',
        )
LEGEND_FONT = fontmgr.FontProperties(
        #family='WenQuanYi Micro Hei',
        size=12,
        weight=100,
        fname='/home/xenon/.fonts/wqy-microhei-lite.ttc',
        )
ANNOTATION_FONT = fontmgr.FontProperties(
        family='Courier New',
        size=13,
        weight='bold',
        )

LINE_WIDTH = 0.75

AXES_BKGND_COLOR, AXES_BKGND_ALPHA = 'w', 0.5
LEGEND_BKGND_ALPHA = 0.5

# how long can a name be before it's considered "long"?
FULL_NAME_THRESHOLD = 8

# Sort based on vote count
DO_SORTING = True

# make the curve a LOT like those generated by @Zorya's ASTCounter
HARD_CURVE = False

# generate histograms; interval in seconds
DO_HISTOGRAM, HISTOGRAM_INTERVAL, HISTOGRAM_ALPHA = False, 1800.0, 0.5
HISTOGRAM_USE_SUBPLOT = False

# segmented curve, threshold is in seconds
SEGMENTED_CURVE, SEGMENT_FLAT_THRESHOLD = True, 1200.0

# in seconds, this is to reduce visual clutter
ANNOTATE_UNIFORM = True
ANNOTATE_MIN_INTERVAL = 1.5 * 3600.0
ANNOTATE_UNI_INTERVAL = 2 * 3600.0
ANNOTATE_COLLISION_INTERVAL = 0.5 * 3600.0

# override curve line color, key is index of the line being drawn
LINE_COLORS = {
        0: 'r',
        1: 'b',
        2: 'g',
        }


def compute_rate_histogram(starttime, timevals):
    tm_start, tm_sofar = timevals[0], timevals[-1]
    #tm_elapsed = (tm_sofar - tm_start).total_seconds()
    tm_delta = datetime.timedelta(seconds=HISTOGRAM_INTERVAL)

    # scan the timevals into bins of [start + (n-1)delta, start+n*delta)
    # that is, [ref_tm, next_ref_tm)
    data, bins, ref_tm, tmp = [], [], starttime, 0
    add_data, add_bin = data.append, bins.append

    next_ref_tm = ref_tm + tm_delta
    #for prev_count, tm in enumerate(timevals):
    for tm in timevals:
        if tm >= next_ref_tm:
            # one bin completed, record this bin and move the "pointers"
            while tm >= next_ref_tm:
                add_data(tmp)
                #add_data(prev_count + 1)
                add_bin(ref_tm)
                ref_tm = next_ref_tm
                next_ref_tm += tm_delta
                tmp = 0

            # continue to the next bin, this point is the first value
            tmp = 1
            continue

        # add to bin accumulator
        tmp += 1

    # last bin
    # this is nearly always the case
    if ref_tm < tm_sofar:
        add_data(tmp)
        #add_data(len(timevals))
        add_bin(ref_tm)

    # IMPORTANT: convert date using matplotlib function!
    #print data
    #print bins
    return {
            'data': data,
            'bins': date2num(bins),
            }


def display_rate_histograms(axes, hist_bundles):
    x = [params['data'] for params in hist_bundles]
    bins = [params['bins'] for params in hist_bundles]
    #bins = [range(len(i)) for i in x]
    #print x
    #print bins
    maxlength = max(len(i) for i in x)
    tm_min, tm_max = min(i[0] for i in bins), max(i[-1] for i in bins)
    tm_interval = (tm_max - tm_min) / maxlength
    grp_ticks = [tm_min + i * tm_interval for i in range(maxlength)]
    ticks = [grp_ticks for i in x]

    # prepare parameters of pyplot.hist
    ##kwargs = {
    ##        'cumulative': True,
    ##        'fill': True,
    ##        'alpha': HISTOGRAM_ALPHA,
    ##        'ec': 'none',
    ##        }

    # color
    #if idx in LINE_COLORS:
    #    # facecolor
    #    kwargs['fc'] = LINE_COLORS[idx]
    #    #kwargs['color'] = LINE_COLORS[idx]
    #colorspec = [LINE_COLORS.get(idx, '') for idx, dummy in enumerate(x)]
    #kwargs['color'] = colorspec

    # plot
    #result = axes.hist(
#    result = axes.step(
#            bins,
#            x,
#            where='post',
###            len(x),
###            **kwargs
#            )
    result = axes.bar(
            ticks,
            x,
            #width=1,
            )

    print result  # , bins, patches


def main(argv):
    pickle_path = argv[1]

    with open(pickle_path, 'rb') as fp:
        pickle = fp.read()

    state = cPickle.loads(pickle)

    cfg, result = state['cfg'], state['result']

    # start time
    startdate = cfg['date']
    starttime = datetime.datetime(
            startdate.year,
            startdate.month,
            startdate.day,
            1,
            0,
            0,
            )
#    endtime = datetime.datetime(
#            startdate.year,
#            startdate.month,
#            startdate.day,
#            23,
#            0,
#            0,
#            )

    # groups config
    groups = cfg['groups']

    # vote pool
    charas = result['charas']

    for idx, group in enumerate(groups):
        fig = plt.figure(idx + 1, figsize=IMAGE_SIZE, )

        names = (chara['name'] for chara in group)

        if DO_SORTING:
            pools = [
                    (len(charas[name]), name, charas[name], )
                    for name in names
                    ]
            pools.sort(reverse=True)
            pools = (i[1:] for i in pools)
        else:
            pools = ((name, charas[name], ) for name in names)

        # sort the time points
        tm_pools = [
                (name, list(sorted(vote['time'] for vote in pool)), )
                for name, pool in pools
                ]

        # get the rightmost (latest) time point
        max_time = max(
                timevals[-1]
                for name, timevals in tm_pools
                )

        hist_data, plot_params, count_anns = [], [], []

        # generate plotting params
        for chara_idx, chara_bundle in enumerate(tm_pools):
            name, timevals = chara_bundle

            # len(timevals) is just the vote count
            tmpoints, vote_count = [starttime], len(timevals)

            # generate histogram for display of vote speed
            if DO_HISTOGRAM:
                hist_data.append(
                        compute_rate_histogram(starttime, timevals)
                        )

            if HARD_CURVE:
                # add MANY interpolation points
                # this is why vote_count must be acquired earlier
                countlist = [0]
                for old_count, tm in enumerate(timevals):
                    tmpoints.extend([tm, tm])
                    countlist.extend([old_count, old_count + 1])

            elif SEGMENTED_CURVE:
                # draw flat line in case of SEGMENT_FLAT_THRESHOLD seconds
                # of inactivity
                countlist = [0]

                prev_tm, prev_ann = starttime, starttime
                for old_count, tm in enumerate(timevals):
                    # elapsed seconds between 2 consecutive votes
                    delta = (tm - prev_tm).total_seconds()
                    # print delta

                    if delta >= SEGMENT_FLAT_THRESHOLD:
                        # add a flat segment
                        tmpoints.extend([tm, tm])
                        countlist.extend([old_count, old_count + 1])

                        if not ANNOTATE_UNIFORM:
                            # annotate the last segment
                            # only if interval >= minimum ann. interval
                            ann_interval = (prev_tm - prev_ann).total_seconds()
                            if ann_interval >= ANNOTATE_MIN_INTERVAL:
                                count_anns.append((
                                    chara_idx,
                                    prev_tm,
                                    old_count,
                                    ))
                                prev_ann = prev_tm

                    else:
                        tmpoints.append(tm)
                        countlist.append(old_count + 1)

                    prev_tm = tm

            else:
                tmpoints.extend(timevals)
                countlist = range(vote_count + 1)

            # uniform intrval annotating
            if ANNOTATE_UNIFORM:
                ann_delta = datetime.timedelta(seconds=ANNOTATE_UNI_INTERVAL)
                ann_point = starttime + ann_delta
                for old_count, tm in enumerate(timevals):
                    if tm <= ann_point:
                        # not arrived at the checkpoint yet, skip over
                        continue

                    if ((max_time - tm).total_seconds()
                            < ANNOTATE_COLLISION_INTERVAL
                            ):
                        # visual clutter may result, don't annotate
                        # this (last) point
                        continue

                    # checkpoint
                    count_anns.append((chara_idx, ann_point, old_count))
                    ann_point += ann_delta

            # stretch the curve's endpoints to the right
            # this is done by inserting point with x=max(times)
            if tmpoints[-1] != max_time:
                tmpoints.append(max_time)
                countlist.append(vote_count)

            #print [(i - starttime).total_seconds() for i in timevals]

            # shorten name
            # TODO: refactor into saimoe library
            name_match, legendname = RE_NAME.search(name), name
            if name_match is not None:
                fullname, shortname, series = (
                        name_match.group('name'),
                        name_match.group('shortname'),
                        name_match.group('series'),
                        )

                if shortname is None or len(fullname) < FULL_NAME_THRESHOLD:
                    eff_name = fullname
                else:
                    eff_name = shortname

                # remove that fullwidth @ symbol...
                legendname = '%s @ %s' % (eff_name, series, )

            # determine color
            plot_kwargs = {}
            if chara_idx in LINE_COLORS:
                plot_kwargs['c'] = LINE_COLORS[chara_idx]

            # plot one character's curve
            #axes.plot_date(
            plot_kwargs['lw'] = LINE_WIDTH
            plot_kwargs['label'] = legendname

            plot_params.append((
                    (
                        tmpoints,
                        countlist,
                        '-',
                        ),
                    plot_kwargs,
                    ))

            # annotate the final apparent count values
            #axes.text(tmpoints[-1], vote_count, str(vote_count))
            count_anns.append((chara_idx, tmpoints[-1], vote_count))

        # carry out the drawing operations
        axes = fig.add_subplot(
                211 if DO_HISTOGRAM and HISTOGRAM_USE_SUBPLOT else 111
                )

        # plot lines and annotation
        for params in plot_params:
            axes.plot_date(*params[0], **params[1])

        for chara_idx, ann_tm, ann_val in count_anns:
            text_kwargs = {
                    'fontproperties': ANNOTATION_FONT,
                    }

            if chara_idx in LINE_COLORS:
                text_kwargs['color'] = LINE_COLORS[chara_idx]
            axes.text(ann_tm, ann_val, str(ann_val), **text_kwargs)

        # place the character name legend on the graph
        # loc=0 'best'
        # loc=2 'upper left'
        fig_legend = axes.legend(
                loc=2,  # 0,
                fancybox=True,
                #frameon=False,
                #shadow=True,
                prop=LEGEND_FONT,
                )
        # set bkgnd opacity of legend
        fig_legend.get_frame().set_alpha(LEGEND_BKGND_ALPHA)

        # grid lines behind the curves
        # see stackoverflow.com/questions/1726391
        #     /matplotlib-draw-grid-lines-behind-other-graph-elements
        axes.set_axisbelow(True)
        #axes.xaxis.grid(color='0.5', linestyle='-', lw=0.1)
        axes.xaxis.grid()
        axes.yaxis.grid()

        # histogram
        if DO_HISTOGRAM:
            # save x formatter
            orig_xformatter = axes.xaxis.get_major_formatter()

            # twinx has WAY TOO many problems...
            # let's use subfigure to circumvent this for now
            hist_axes = (
                    fig.add_subplot(212)
                    if HISTOGRAM_USE_SUBPLOT
                    else axes.twinx()
                    )

            #for idx, hist_params in enumerate(hist_data):
            #    print hist_params
            #    display_rate_histogram(hist_axes, idx, hist_params)
            display_rate_histograms(hist_axes, hist_data)

            #hist_xformatter = AutoDateFormatter(AutoDateLocator())
            #hist_xformatter.scaled[1. / 24.] = '%H:%M'
            #hist_axes.xaxis.set_major_formatter(hist_xformatter)
            #hist_axes.xaxis.set_major_formatter(xformatter)

            hist_axes.xaxis.set_major_formatter(orig_xformatter)

        # also make date format more concise
        xformatter = axes.xaxis.get_major_formatter()
        xformatter.scaled[1. / 24.] = '%H:%M'

        fig.autofmt_xdate()

        # title
        if SHOW_TITLE:
            axes.set_title(
                    TITLE_FORMAT % {
                        'year': startdate.year,
                        'month': startdate.month,
                        'day': startdate.day,
                        'group': idx + 1,
                        },
                    fontproperties=TITLE_FONT,
                    )

        # background of axes box
        axes.patch.set_color(AXES_BKGND_COLOR)
        axes.patch.set_alpha(AXES_BKGND_ALPHA)

        # bkgnd of figure
        #fig.patch.set_alpha(0)

        # save png's
        fig.savefig(
                '%04d%02d%02d-%d.png' % (
                    starttime.year,
                    starttime.month,
                    starttime.day,
                    idx + 1,
                    ),
                #transparent=AXES_TRANSPARENCY,
                facecolor='none',
                edgecolor='none',
                )

    plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
