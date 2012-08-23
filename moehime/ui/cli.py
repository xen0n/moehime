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

from sys import stderr
from itertools import chain
import cPickle

from ..saimoe import fetch
from ..saimoe import config
from ..saimoe import parser
from ..saimoe import counter


def print_list(lst):
    for count, name in lst:
        print '%-3d 票 %s' % (count, name, )

    print
    return


def cli_entry(argv):
    cfg_path = argv[1]
    urls = argv[2:]

    cfg = None
    print >>stderr, 'reading config'
    with open(cfg_path, 'r') as fp:
        cfg = config.readconfig(fp)

    # TODO: refactor this!
    groups, aliases = cfg['groups'], cfg['aliases']
    # print '\n'.join('%s|%s' % (k, v, )
    #         for k, v in sorted((v, k) for k, v in aliases.items())
    #         )

    print >>stderr, 'fetching'
    htmls = []
    for url in urls:
        print >>stderr, '  %s ...' % (url, ),
        s = fetch.do_fetch(url)
        print >>stderr, '%d bytes' % len(s)

        # XXX: chardet couldn't be used, it reported ISO-8859-2 for the
        # livedoor.jp thing!
        if url.startswith('http://jbbs.livedoor.jp/'):
            page_enc = 'euc-jp'
        else:
            page_enc = 'cp932'

        htmls.append(s.decode(page_enc, 'replace'))

    print >>stderr, 'parsing'

    thread = chain(*[parser.i_dlthreadfromstring(s) for s in htmls])

    posts = parser.i_postfromthread(thread)
    votes = parser.i_votefromposts(cfg, posts)
    count_result = counter.countvotes(cfg, votes)

    counts, invalids, dup_ids, dup_codes = [
            count_result['charas'],
            count_result['invalids'],
            count_result['dup_tripcodes'],
            count_result['dup_codes'],
            ]

    print >>stderr, 'processing done, writing pickle'
    with open(
            '%02d%02d%02d.pickle' % (
                cfg['date'].year,
                cfg['date'].month,
                cfg['date'].day,
                ),
            'wb',
            ) as fp:
        fp.write(cPickle.dumps({
            'cfg': cfg,
            'result': count_result,
            }))

    print >>stderr, 'arranging result for display\n'

    displaylists, total_counts = [], []
    for group in groups:
        sublist = []
        for chara in group:
            name = chara['name']
            name_end = name.find('＠')
            short_name = name if name_end == -1 else name[:name_end]

            chara_pool = counts.get(name, [])
            chara_count = len(chara_pool)

            sublist.append((chara_count, short_name, ))

        sublist.sort(reverse=True)
        displaylists.append(sublist)
        total_counts.append(sum(i[0] for i in sublist))

    invalids_list = [(len(v), k) for k, v in invalids.iteritems()]
    invalids_list.sort(reverse=True)

    # display
    for idx, lst in enumerate(displaylists):
        print '今日第 %d 组 [%d 票]' % (idx + 1, total_counts[idx], )
        print_list(lst)

    print '以下为今日无效票'
    print_list(invalids_list)

    print '以下为重复的帖子 ID'
    print_list(sorted((len(v) + 1, k) for k, v in dup_ids.iteritems()))

    print '以下为重复的 code'
    print_list(sorted((len(v) + 1, k) for k, v in dup_codes.iteritems()))

    # print >>stderr, '\n'.join(repr(i) for i in aliases.iterkeys())

    return 0


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
