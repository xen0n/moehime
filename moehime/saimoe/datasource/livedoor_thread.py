#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / data source - livedoor - thread
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
RE_SIMPLE_TID = re.compile(r'read.cgi/anime/10101/(\d+)/$')
RE_MTIME = re.compile(
        r'投稿日：\s+'
        r'(?P<Y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2})\([日月水火木金土]\)\s+'
        r'(?P<H>\d{2}):(?P<M>\d{2}):(?P<S>\d{2})'
        )

VOTE_THREAD_SIGNATURE = '投票スレ'


class PostThreadInfo_livedoor(PostThreadInfoBase):
    def __init__(self, raw_thread, datasource):
        super(PostThreadInfo_livedoor, self).__init__(raw_thread, datasource)

        dl = pq(raw_thread)

        # header
        hdr_elem = dl(b'table:first')
        title = hdr_elem(b'font[color = "#FF0000"]').text()

        # only interested in vote threads
        # 只对票箱感兴趣
        if VOTE_THREAD_SIGNATURE not in title:
            raise ThreadBadTitleError

        # this is of format "(Res:\d+)"
        num_replies_txt = hdr_elem(b'tr>td:first>b + font').text()
        num_replies = int(num_replies_txt[5:-1])

        # again walking the table layout
        href = hdr_elem(b'tr>td:last>font>a:first').attr('href')

        # extract thread id from href
        # 从链接地址里提取线索 id
        tid = RE_SIMPLE_TID.search(href).group(1)

        # extract last reply time from <dt>
        # 从 <dt> 中提取最后回复时间
        lastreply_text = dl(b'dt:last').text()
        mtime_match = RE_MTIME.search(lastreply_text)
        if mtime_match is None:
            raise RuntimeError('mtime RE match failed')

        m_grp = lambda x: int(mtime_match.group(x))
        mtime = datetime.datetime(
                m_grp('Y'),
                m_grp('m'),
                m_grp('d'),
                m_grp('H'),
                m_grp('M'),
                m_grp('S'),
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
