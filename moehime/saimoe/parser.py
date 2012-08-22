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

import re
import datetime
from itertools import izip_longest

from lxml import html

# 提取信息用的正则表达式
# REs for extracting various info
RE_EXPRS = [
        # 匹配回复头部
        # Post header
        (
            r'(?P<Y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2})\([日月水火木金土]\)'
            r'\s+(?P<H>\d{2}):(?P<i>\d{2}):(?P<s>\d{2}(?:\.\d{2})?)'
            r'\s+ID:(?P<id>[0-9A-Za-z+/.]{8,})'
            ),
        # 匹配code
        # Vote code
        r'\[\[asm12-(?P<day>\d{2})-[0-9A-Za-z./]{8}-[A-Za-z]{2}\]\]-\d{5}',
        # 匹配角色名/alias，之后对内容进行精确匹配
        # Character name/alias, the captured string is then matched
        # in an exact mannner
        r'<<(.*?)>>',
        ]

[RE_HEADER, RE_CODE, RE_CHARA, ] = [re.compile(_expr) for _expr in RE_EXPRS]
del _expr

# Element selectors
# 元素选择器
# TODO: make this configurable 让这个可配置
THREAD_SELECTORS = ['.thread', '#thread-body', ]

# "speed up" header group matching by not re-creating the same tuple every
# time a post is analyzed
# “加速”帖子头部匹配过程，不要每次都构造一遍元组
_RE_HEADER_GROUPS = ('Y', 'm', 'd', 'H', 'i', 's', 'id', )


# functions
# functions starting with 'i_' are iterators
# 函数
# 名字以“i_”打头的是迭代器
def i_dlthreadfromstring(s):
    root, dl = html.fromstring(s), None

    for selector in THREAD_SELECTORS:
        tmp = root.cssselect(selector)
        if len(tmp) > 0:
            dl = tmp[0]
            break

    if dl is None:
        raise RuntimeError('unrecognized page structure')

    headers = dl.iterfind('dt')
    contents = dl.iterfind('dd')
    return izip_longest(headers, contents)


def postfromelements(elems):
    hdr_elem, post_elem = elems

    hdr_txt = ''.join(hdr_elem.itertext())
    post_txt = '\n'.join(post_elem.itertext())

    # extract post time and tripcode
    # TODO: author name and mail address 作者名和邮件地址
    # 提取发贴时间和用户识别码
    hdr = RE_HEADER.search(hdr_txt)
    if hdr is None:
        # TODO: classify 分类各种视为无效的情况
        return False, None

    Y, m, d, H, i, s, tripcode = [
            hdr.group(name) for name in _RE_HEADER_GROUPS
            ]

    # XXX speed hack 写成这样仅仅是为了图快而已
    if len(s) == 2:
        cs = 0
    else:
        cs, s = int(s[3:]), s[:2]

    Y, m, d, H, i, s = int(Y), int(m), int(d), int(H), int(i), int(s)
    us = cs * 10000

    posttime = datetime.datetime(Y, m, d, H, i, s, us)

    return True, {
            'time': posttime,
            'tripcode': tripcode,
            'text': post_txt,
            }


def i_postfromthread(thread):
    for hdr_elem, post_elem in thread:
        is_valid, post = postfromelements((hdr_elem, post_elem, ))
        if is_valid:
            yield post


def posttime_validator_factory(valid_date):
    Y, m, d = valid_date.year, valid_date.month, valid_date.day

    def __is_posttime_valid(date):
        d_Y, d_m, d_d = date.year, date.month, date.day
        d_H, d_i = date.hour, date.minute

        if d_Y != Y or d_m != m or d_d != d:
            return False

        if not 1 <= d_H <= 23:
            return False

        if d_H == 23 and d_m >= 1:
            return False

        return True
    return __is_posttime_valid


def votefrompost(self, post):
    valid_date, aliases = self['date'], self['aliases']
    posttime, tripcode, txt = post['time'], post['tripcode'], post['text']
    is_posttime_valid = posttime_validator_fatory(valid_date)

    if not is_posttime_valid(posttime):
        # post time outside of accepted range, ignore the post
        # 发贴时间超出范围，忽略此帖
        return False, None

    codematch = RE_CODE.search(txt)
    if codematch is None:
        # this text has no well-formed code inside, ignore it altogether
        # 此帖正文内没有 code，无视
        return False, None

    code = codematch.group(0)
    if int(codematch.group('day')) != valid_date.day:
        # code not of the same day, ignore
        # code 和比赛日期不是同一天，无视
        # TODO: this generic filtering needs a BIG refactor....
        # 这部分过滤的架构需要大改
        # print 'Code date wrong: %s' % (code, )
        return False, None

    # individual votes for characters
    # 分离各角色的票
    votes = list(set(
        chara_match.group(1)
        for chara_match in RE_CHARA.finditer(txt)
        ))

    # normalize the character names
    # 标准化角色名
    norm_votes, invalids = [], []
    for name in votes:
        norm_name = aliases.get(name, None)
        if norm_name is None:
            # Invalid vote, record this fact
            # 无效票，记录下
            invalids.append(name)
            continue
        norm_votes.append(norm_name)

    return True, {
            'time': posttime,
            'tripcode': tripcode,
            'code': code,
            'votes': norm_votes,
            'invalids': invalids,
            }


def i_votefromposts(self, posts):
    for post in posts:
        is_valid_vote, vote_info = votefrompost(self, post)
        if is_valid_vote:
            yield vote_info


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
