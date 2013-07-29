#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / data source - livedoor
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

from . import src_manager
from .base import URL_SEARCH
from .s_2ch import Base2chDatasource
from .livedoor_thread import PostThreadInfo_livedoor
from .livedoor_post import Post_livedoor

THREAD_LIST_URL = b'http://jbbs.livedoor.jp/anime/10101/'
THREAD_LIST_SELECTOR = b'a[name != "menu"] + table dl'


@src_manager.register_datasource('livedoor')
class LivedoorDatasource(Base2chDatasource):
    THREAD_INFO_CLASS = PostThreadInfo_livedoor
    POST_CLASS = Post_livedoor

    def get_encoding(self, kind):
        return 'euc-jp'

    @property
    def board_name(self):
        # This is actually useless for livedoor, but a concrete implementation
        # must be in place
        # 这对 livedoor 实际上没有意义，但必须要是一个具体的实现
        return b'jbbs'

    @property
    def post_url_prefix(self):
        return b'http://jbbs.livedoor.jp/'

    @property
    def readcgi_url(self):
        return 'bbs/read.cgi/anime/10101/%(tid)s/%(start)d-%(end)s'

    @property
    def post_list_selector(self):
        return b'#thread-body'

    def _format_url_search(self):
        # This interface does not (need to) respect the max count setting
        # Also query string is ignored
        # 这个界面不（需要）遵守最多结果数设置的
        # 查询字串也被无视了
        return THREAD_LIST_URL

    def _do_get_thread_list(self, max_count):
        result_page = self.fetch_pq(URL_SEARCH)
        threads_dl = result_page(THREAD_LIST_SELECTOR)

        return threads_dl


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
