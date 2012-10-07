#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / user interface / command line interface
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

from __future__ import unicode_literals, division

from sys import stdout, stderr
from itertools import chain

import cPickle
import datetime

from ..__version__ import VERSION_STR

from ..saimoe.config import WebBackedCrawlConfig
from ..saimoe.datasource import src_manager
from ..saimoe.filters import filter_manager

from .cliutils import print_wrapper

DATASOURCES = ('kohada', 'livedoor', )
FILTERS = (
        'initial',
        'basic',
        'dup',
        'alias',
        'count',
        )


def show_banner():
    now = datetime.datetime.today()
    print_wrapper('结果提供：萌姬 v%s' % (VERSION_STR, ))
    print_wrapper('生成时间：%s' % now.strftime('%F %T'))


def print_list(lst):
    for count, name in lst:
        print_wrapper('%-3d 票 %s' % (count, name, ))

    print_wrapper()
    return


def cli_entry(argv):
    cfg = WebBackedCrawlConfig(
            datetime.datetime.today(),
            )
    print_wrapper('reading config', file=stderr)
    cfg.readconfig()

    # initialize managers
    src_manager.config = {
            'date': cfg.date,
            'datasources': DATASOURCES,
            }
    vote_filter = filter_manager.get_filter(FILTERS, cfg)

    # TODO: refactor this!
    groups, aliases = cfg.groups, cfg.aliases

    print_wrapper('fetching', file=stderr)
    votes = list(src_manager.fetch_votes())

    print_wrapper('parsing', file=stderr)
    count_result = vote_filter.judge(votes)

    counts, invalids, dup_ids, dup_codes = [
            count_result['count'],
            count_result['alias']['invalids'],
            count_result['dup']['tripcodes'],
            count_result['dup']['codes'],
            ]

    #print_wrapper('processing done, writing pickle', file=stderr)
    #with open('%s.pickle' % cfg.date.strftime('%Y%m%d'), 'wb') as fp:
    #    fp.write(cPickle.dumps({
    #        'cfg': cfg,
    #        'result': count_result,
    #        }))

    print_wrapper('arranging result for display', end='\n\n', file=stderr)

    displaylists, total_counts = [], []
    for group in groups:
        sublist = []
        for chara in group:
            name = chara['name']
            name_end = name.find('＠')
            short_name = name if name_end == -1 else name[:name_end]

            #chara_pool = counts.get(name, [])
            #chara_count = len(chara_pool)
            chara_count = counts.get(name, [])

            sublist.append((chara_count, short_name, ))

        sublist.sort(reverse=True)
        displaylists.append(sublist)
        total_counts.append(sum(i[0] for i in sublist))

    #invalids_list = [(len(v), k) for k, v in invalids.iteritems()]
    invalids_list = [(v, k) for k, v in invalids.iteritems()]
    invalids_list.sort(reverse=True)

    # display
    show_banner()
    for idx, lst in enumerate(displaylists):
        print_wrapper('今日第 %d 组 [%d 票]' % (idx + 1, total_counts[idx], ))
        print_list(lst)

    print_wrapper('以下为今日无效票')
    print_list(invalids_list)

    print_wrapper('以下为重复的帖子 ID')
    #print_list(sorted((len(v) + 1, k) for k, v in dup_ids.iteritems()))
    print_list(sorted((v + 1, k) for k, v in dup_ids.iteritems()))

    print_wrapper('以下为重复的 code')
    #print_list(sorted((len(v) + 1, k) for k, v in dup_codes.iteritems()))
    print_list(sorted((v + 1, k) for k, v in dup_codes.iteritems()))

    # print >>stderr, '\n'.join(repr(i) for i in aliases.iterkeys())

    return 0


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
