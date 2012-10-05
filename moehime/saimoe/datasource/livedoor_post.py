#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / data source - livedoor - post
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

from pyquery import PyQuery as pq

from .s_2ch_post import BasePost_2ch


class Post_livedoor(BasePost_2ch):
    def __init__(self, raw_post, thread_info):
        super(Post_livedoor, self).__init__(raw_post, thread_info)

    def get_floor_from_header(self, raw_post):
        e_dt, e_dd = raw_post
        dt = pq(e_dt)

        return int(dt(b'a:first').text())

    def get_author_info(self, raw_post):
        e_dt, e_dd = raw_post
        dt = pq(e_dt)

        author_elem = dt(b'a:first + a, a:first + font')
        author, email = (
                author_elem.text(),
                self._mailto_helper(author_elem.attr('href')),
                )

        return author, email


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
