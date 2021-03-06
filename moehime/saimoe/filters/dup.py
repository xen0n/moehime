#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / filters - simple duplication filter
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

from . import filter_manager
from .base import BaseFilter

_ = lambda x: x


@filter_manager.register
class DuplicationFilter(BaseFilter):
    '''重复过滤器。

    用来过滤重复 code 及重复识别码的投票。

    '''

    FILTER_NAME = 'dup'

    def setup(self):
        self._codes, self._tripcodes = {}, {}

    def _do_judge(self, datum):
        codes, tripcodes = self._codes, self._tripcodes
        tripcode, code = datum.author['tripcode'], unicode(datum.code)

        if tripcode in tripcodes:
            return False, _('识别码重复')

        if code in codes:
            return False, _('code 重复')

        codes.setdefault(code, 0)
        tripcodes.setdefault(tripcode, 0)

        self._codes[code] += 1
        self._tripcodes[tripcode] += 1
        return True, None

    def report(self):
        return {
                'codes': {
                    k: v for k, v in self._codes.iteritems() if v > 1
                    },
                'tripcodes': {
                    k: v for k, v in self._tripcodes.iteritems() if v > 1
                    },
                }


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
