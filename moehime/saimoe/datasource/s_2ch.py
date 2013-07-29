#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / data source - 2channel
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
from itertools import izip
from urllib import urlencode

from . import src_manager
from .base import DatasourceBase, URL_READ, URL_SEARCH
from ..net.fetch import ResourceRequester
from .s_2ch_thread import PostThreadInfo_2ch
from .s_2ch_post import Post_2ch

FIND_STRING = 'アニメ最萌トーナメント2013 board:投票所'


class Base2chDatasource(DatasourceBase, ResourceRequester):
    __metaclass__ = abc.ABCMeta

    THREAD_INFO_CLASS = PostThreadInfo_2ch
    POST_CLASS = Post_2ch

    def __init__(self):
        super(Base2chDatasource, self).__init__()

    @abc.abstractproperty
    def board_name(self):
        return b'www'

    @abc.abstractproperty
    def readcgi_url(self):
        return b''

    @abc.abstractproperty
    def post_list_selector(self):
        return b''

    @property
    def post_url_prefix(self):
        return b'http://%s.2ch.net/' % (self.board_name, )

    @property
    def search_url_prefix(self):
        return b'http://find.2ch.net/'

    def _format_url_read(self, tid, start, end):
        end_str = b'' if end is None else str(end)
        return self.post_url_prefix + self.readcgi_url % {
                'tid': tid,
                'start': start,
                'end': end_str,
                }

    def _format_url_search(self, qs, max_count=None):
        count = 10 if max_count is None else max_count
        return b''.join([
                self.search_url_prefix,
                b'?',
                urlencode((
                    ('STR', self.to_str(URL_SEARCH, qs)),
                    ('COUNT', count),
                    ('TYPE', 'TITLE'),
                    ('BBS', 'ALL'),
                    )),
                ])

    def format_url(self, kind, *args, **kwargs):
        if kind == URL_READ:
            url = self._format_url_read(*args, **kwargs)
        elif kind == URL_SEARCH:
            url = self._format_url_search(*args, **kwargs)
        else:
            raise NotImplementedError

        return self.to_str(kind, url)

    def _do_get_thread_list(self, max_count):
        result_page = self.fetch_pq(URL_SEARCH, FIND_STRING, max_count)
        dl = result_page(b'.wrapper dl')
        dt = dl(b'dt')[:-1]
        dd = dl(b'dd')[:]
        if len(dt) != len(dd):
            raise RuntimeError('thread list structure imbalanced')

        return izip(dt, dd)

    def _do_get_posts_from_thread(self, thread):
        tid, start, end = thread.tid, thread.start, thread.end
        thread_page = self.fetch_pq(URL_READ, tid, start, end)

        dl = thread_page(self.post_list_selector)
        dt = dl(b'dt')
        dd = dl(b'dd')
        if len(dt) != len(dd):
            raise RuntimeError('post list structure imbalanced')

        return izip(dt, dd)


@src_manager.register_datasource('kohada')
class Kohada2chDatasource(Base2chDatasource):
    def get_encoding(self, kind):
        if kind == URL_SEARCH:
            return 'euc-jp'
        else:
            return 'cp932'

    @property
    def board_name(self):
        return 'kohada'

    @property
    def readcgi_url(self):
        return b'test/read.cgi/vote/%(tid)s/%(start)d-%(end)s'

    @property
    def post_list_selector(self):
        return b'dl.thread'


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
