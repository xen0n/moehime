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
from .s_2ch import Base2chDatasource


@src_manager.register_datasource('livedoor')
class LivedoorDatasource(Base2chDatasource):
    def get_encoding(self, kind):
        return 'euc-jp'

    @property
    def readcgi_url(self):
        return 'bbs/read.cgi/anime/8440/%(tid)d/%(start)d-%(end)s'

    # TODO: implement thread list parsing


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
