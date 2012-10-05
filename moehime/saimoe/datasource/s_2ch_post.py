#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / data source - 2channel - post
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

import abc
import re
import datetime

from pyquery import PyQuery as pq

from ..exc import PostBadHeaderError, PostOutOfRangeError
from .base import PostBase

# 匹配回复头部
# Post header
RE_HEADER = re.compile(
        r'(?P<Y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2})\([日月水火木金土]\)'
        r'\s+(?P<H>\d{2}):(?P<i>\d{2}):(?P<s>\d{2}(?:\.\d{2})?)'
        r'\s+ID:(?P<id>[0-9A-Za-z+/.]{8,})'
        )

# "speed up" header group matching by not re-creating the same tuple every
# time a post is analyzed
# “加速”帖子头部匹配过程，不要每次都构造一遍元组
_RE_HEADER_GROUPS = ('Y', 'm', 'd', 'H', 'i', 's', 'id', )


def is_post_in_thread_range(floor_no, thread_info):
    start, end = thread_info.start, thread_info.end
    if end is None:
        return start <= floor_no
    return start <= floor_no <= end


class BasePost_2ch(PostBase):
    __metaclass__ = abc.ABCMeta

    def __init__(self, raw_post, thread_info):
        super(BasePost_2ch, self).__init__(raw_post, thread_info)

        e_dt, e_dd = raw_post
        dt, dd = pq(e_dt), pq(e_dd)

        hdr_txt = dt.text()

        # is the post ACTUALLY in range specified by thread?
        # 帖子真的在线索指定的范围吗？
        floor_no = self.get_floor_from_header(raw_post)

        if not is_post_in_thread_range(floor_no, thread_info):
            # abort instantiation, because it's useless
            # 中断实例化，因为再进行下去已经没有意义了
            raise PostOutOfRangeError

        post_txt = '\n'.join(e_dd.itertext())

        # post author info 帖子作者信息
        author, email = self.get_author_info(raw_post)

        # extract post time and tripcode
        # TODO: author name and mail address 作者名和邮件地址
        # 提取发贴时间和用户识别码
        hdr = RE_HEADER.search(hdr_txt)
        if hdr is None:
            # TODO: classify 分类各种视为无效的情况
            raise PostBadHeaderError

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

        # populate self
        self.thread = thread_info
        self.floor_no = floor_no
        self.author = author
        self.email = email
        self.tripcode = tripcode
        self.posttime = posttime
        self.text = post_txt

    @abc.abstractmethod
    def get_floor_from_header(self, hdr_txt):
        return 0

    @abc.abstractmethod
    def get_author_info(self):
        return '', ''

    def _mailto_helper(self, addr):
        return '' if addr is None else addr[7:]  # len('mailto:') == 7


    def _to_voteobject_args(self):
        author = {
                'name': self.author,
                'email': self.email,
                'tripcode': self.tripcode,
                }

        return author, self.posttime, self.text


class Post_2ch(BasePost_2ch):
    def __init__(self, raw_post, thread_info):
        super(Post_2ch, self).__init__(raw_post, thread_info)

    def get_floor_from_header(self, raw_post):
        e_dt, e_dd = raw_post
        dt, dd = pq(e_dt), pq(e_dd)

        hdr_txt = dt.text()
        # XXX hack here 这里图省事了
        return int(hdr_txt[:hdr_txt.find(' ')])

    def get_author_info(self, raw_post):
        e_dt, e_dd = raw_post
        dt, dd = pq(e_dt), pq(e_dd)

        author_link = dt(b'a')
        author_elem = author_link if len(author_link) != 0 else dt(b'font')
        author, email = (
                author_elem.text(),
                self._mailto_helper(author_elem.attr('href')),
                )

        return author, email


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
