#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / content parsing
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


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:

from __future__ import unicode_literals, division

from itertools import chain


def insertvote(dct, key, vote):
    if key not in dct:
        dct[key] = []

    dct[key].append(vote)


def countvotes(cfg, votes):
    aliases = cfg['aliases']

    charas, invalids = {}, {}
    tripcodes, codes = {}, {}
    dup_tripcode, dup_code = {}, {}

    for vote in votes:
        tripcode, code = vote['tripcode'], vote['code']
        if tripcode in tripcodes:
            # Duplicate tripcode, record this fact and ignore the vote
            # key is ID, value is dup count starting from 1
            # 用户识别码重复，记录这个事实，无视这张票
            # 键为识别码，值为从 1 开始的重复计数
            insertvote(dup_tripcode, tripcode, vote)
            #print 'duplicate tripcode: [%s] invalid: [%s]' % (
            #        ', '.join(vote['votes']),
            #        ', '.join(vote['invalids']),
            #        )
            continue
        tripcodes[tripcode] = None

        if code in codes:
            # Duplicate code, handling method same as above
            # 重复的投票 code，处理方法同上
            insertvote(dup_code, code, vote)
            #print 'duplicate votecode: [%s] invalid: [%s]' % (
            #        ', '.join(vote['votes']),
            #        ', '.join(vote['invalids']),
            #        )
            continue
        codes[code] = None

        vote_invalids = vote['invalids']
        if len(vote_invalids) > 0:
            # has invalid votes inside, ignore other valid votes from this
            # entry
            # 有无效角色名，作废
            for name in vote_invalids:
                insertvote(invalids, name, vote)

            continue

        for name in vote['votes']:
            # the name is already canonicalized in parser
            # 解析模块里面已经把名字标准化了
            insertvote(charas, name, vote)

    # pass back the various pools
    # 将各种计票池传回
    return {
            'dup_codes': dup_code,
            'dup_tripcodes': dup_tripcode,
            'charas': charas,
            'invalids': invalids,
            }


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
