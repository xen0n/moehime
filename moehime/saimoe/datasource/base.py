#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / data source - baseclass
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
import datetime

from ..exc import PostError
from ..voteobject import VoteEntry

URL_READ, URL_SEARCH = xrange(2)


class DatasourceBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(DatasourceBase, self).__init__()

    @abc.abstractproperty
    def post_url_prefix(self):
        return b''

    @abc.abstractproperty
    def search_url_prefix(self):
        return b''

    @property
    def default_state_key(self):
        return unicode(datetime.datetime.today().strftime('%Y%m%d'))

    def save_state(self, key=None):
        key = self.default_state_key if key is None else key

    def load_state(self, key=None):
        key = self.default_state_key if key is None else key

    def get_thread_list(self, max_count=None):
        thread_class = self.__class__.THREAD_INFO_CLASS

        threads = self._do_get_thread_list(max_count)
        return [thread_class(raw_thread, self) for raw_thread in threads]

    @abc.abstractmethod
    def _do_get_thread_list(self, max_count):
        return iter([])

    @abc.abstractmethod
    def _do_get_posts_from_thread(self, thread):
        return iter([])

    def get_posts_from_thread(self, thread):
        post_class = self.__class__.POST_CLASS
        thread_posts = self._do_get_posts_from_thread(thread)
        for raw_post in thread_posts:
            try:
                yield post_class(raw_post, thread)
            except PostError:
                continue

    def get_votes_from_thread(self, thread):
        for post in self.get_posts_from_thread(thread):
            yield post.to_vote()


class PostThreadInfoBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, raw_thread, datasource):
        self.datasource = datasource

    def get_posts(self):
        return self.datasource.get_posts_from_thread(self)


class PostBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, raw_post, thread_info):
        pass

    def to_vote(self):
        return VoteEntry(*self._to_voteobject_args())

    @abc.abstractmethod
    def _to_voteobject_args(self):
        return None, None, None


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
