#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / filter package
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


class FilterManager(object):
    def __init__(self, cfg=None):
        self._classes = {}
        self._filters = {}
        self.config = cfg

    def register(self, cls):
        name = cls.FILTER_NAME
        self._classes[name] = cls
        return cls

    @property
    def filters(self):
        return self._classes

    def get_filter(self, filters, cfg=None, force_empty_cfg=False):
        cfg = self.cfg if cfg is None and not force_empty_cfg else cfg
        return ChainedFilter(filters, cfg)


class ChainedFilter(object):
    def __init__(self, filters, cfg):
        self._filters = []
        for filter_arg in filters:
            if type(filter_arg) in (tuple, list, ):
                name, args, kwargs = filter_arg
            else:
                name, args, kwargs = filter_arg, (), {}

            filter_cls = filter_manager.filters[name]
            self._filters.append(filter_cls(cfg, *args, **kwargs))

    def judge(self, dataset):
        report = {}
        for filter_obj in self._filters:
            report[filter_obj.FILTER_NAME] = filter_obj.judge(dataset)

        return report


filter_manager = FilterManager()

from . import _reg
del _reg


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
