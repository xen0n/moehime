#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / data source package
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

import datetime
from threading import Lock
from itertools import chain
from functools import wraps


class DatasourceManager(object):
    def __init__(self, cfg=None):
        self.config = {} if cfg is None else cfg
        self._classes, self._sources = {}, None
        self._lock = Lock()

    def register_datasource(self, name):
        def _decorator_(cls):
            self._classes[name] = cls
            return cls
        return _decorator_

    def _init_sources(self):
        if self._sources is not None:
            return

        # initialize datasource objects exactly once
        # 仅初始化数据源对象一次
        with self._lock:
            self._sources = []

            datasource_cfg = self.config['datasources']
            for name in datasource_cfg:
                try:
                    cls = self._classes[name]
                except KeyError:
                    raise ValueError(
                            "datasource '%s' does not exist" % (
                                name,
                                )
                            )

                self._sources.append(cls())

    def fetch_all_threads(self):
        self._init_sources()
        for src in self._sources:
            lst = src.get_thread_list()
            for thread in lst:
                yield thread

    def fetch_threads(self):
        day = self.config['date']
        day_tuple = (day.year, day.month, day.day, )

        for thread in self.fetch_all_threads():
            mtime = thread.mtime
            mtime_tuple = (mtime.year, mtime.month, mtime.day, )
            if day_tuple != mtime_tuple:
                # not the same day 不是同一天
                continue
            yield thread

    def fetch_posts(self):
        for thread in self.fetch_threads():
            for post in thread.get_posts():
                yield post

    def fetch_votes(self):
        for post in self.fetch_posts():
            yield post.to_vote()


src_manager = DatasourceManager()


# populate class registry 充实类注册表
from . import s_2ch
from . import livedoor


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
