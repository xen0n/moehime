#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / net resource fetching
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

from __future__ import unicode_literals, division, print_function

import abc

import requests
from pyquery import PyQuery as pq

UA = 'Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'


# TODO: make this non-blocking 让这个模块不阻塞
def do_fetch(url, session=None):
    import sys
    print('[GET] %s' % (url, ), file=sys.stderr)
    response = (session if session is not None else requests).get(url)
    print('    -> %d B' % (len(response.content), ), file=sys.stderr)
    return response.content


class ResourceRequester(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(ResourceRequester, self).__init__()
        session = self._requests_session = requests.Session()
        session.headers.update({
                'User-Agent': UA,
                })

    @abc.abstractmethod
    def format_url(self, kind, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_encoding(self, kind):
        return 'utf-8'

    def to_unicode(self, kind, s, *args, **kwargs):
        if not isinstance(s, unicode):
            return s.decode(self.get_encoding(kind), *args, **kwargs)
        return s

    def to_str(self, kind, s, *args, **kwargs):
        if not isinstance(s, str):
            return s.encode(self.get_encoding(kind), *args, **kwargs)
        return s

    def fetch(self, kind, *args, **kwargs):
        url = self.format_url(kind, *args, **kwargs)
        return do_fetch(url, self._requests_session)

    def fetch_pq(self, kind, *args, **kwargs):
        return pq(self.to_unicode(
                kind,
                self.fetch(kind, *args, **kwargs),
                'replace',
                ))


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
