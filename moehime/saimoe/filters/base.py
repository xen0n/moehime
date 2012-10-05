#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / filters - baseclass
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


class BaseFilter(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config=None):
        super(BaseFilter, self).__init__()

    def judge(self, dataset):
        self.examine(dataset)

        for datum in dataset:
            if datum.is_valid:
                result, annotation = self._do_judge(datum)
                datum.is_valid = result
                if annotation is not None:
                    datum.annotations[self.FILTER_NAME] = annotation

    def examine(self, dataset):
        pass

    @abc.abstractmethod
    def _do_judge(self, datum):
        pass


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
