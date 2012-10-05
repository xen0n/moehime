#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / data source - 2channel - thread
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

from pyquery import PyQuery as pq

from .base import PostThreadInfoBase
from ..exc import ThreadBadTitleError

# RE_NUM_REPLIES = re.compile(r'^\((\d+)\)$')
RE_TID = re.compile(r'read.cgi/[^/]+/(\d+)/(?:\d+)-(?:\d+)?$')
RE_MTIME = re.compile(
        r'^最新:'
        r'(?P<Y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2})\s+'
        r'(?P<H>\d{2}):(?P<M>\d{2})$'
        )

VOTE_TITLE_SIGNATURE = '投票スレ'


class PostThreadInfo_2ch(PostThreadInfoBase):
    def __init__(self, raw_thread, datasource):
        super(PostThreadInfo_2ch, self).__init__(raw_thread, datasource)

        e_dt, e_dd = raw_thread
        dt, dd = pq(e_dt), pq(e_dd)

        # extract header info from <dt>
        # 提取 <dt> 中的头部信息
        link = dt(b'a')
        title, href = link.text(), link.attr('href')

        if VOTE_TITLE_SIGNATURE not in title:
            raise ThreadBadTitleError

        # extract thread id from href
        # 从链接地址里提取线索 id
        tid = RE_TID.search(href).group(1)

        # remove the <a> for easy retrieval of num_replies
        # 去掉 <a> 元素，这样拿 num_replies 会更方便
        link.remove()

        # Not using RE to extract number of replies in order to save some time
        # 为了省时间，就不用正则处理这个数了
        # num_replies = int(RE_NUM_REPLIES.match(dt.text()).group(1))
        num_replies = int(dt.text()[1:-1])

        # extract last reply time from <dd>
        # 从 <dd> 中提取最后回复时间
        lastreply_text = dd(b'font[color="#228822"]').text()
        mtime_match = RE_MTIME.match(lastreply_text)
        if mtime_match is None:
            raise RuntimeError('mtime RE match failed')

        m_grp = lambda x: int(mtime_match.group(x))
        mtime = datetime.datetime(
                m_grp('Y'),
                m_grp('m'),
                m_grp('d'),
                m_grp('H'),
                m_grp('M'),
                )

        # populate self
        # 填充数据
        self.title = title
        self.tid = tid
        self.num_replies = num_replies
        self.mtime = mtime

        # range information
        # 范围信息
        self.start = 1
        self.end = None


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
