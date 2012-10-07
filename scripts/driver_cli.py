#!/usr/bin/env python
# -*- coding: utf-8 -*-
# moehime / scripts / CLI driver
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

import sys
import os

_realpath = os.path.realpath(__file__)
_basedir = os.path.dirname(_realpath)
_pkg_root = os.path.abspath(os.path.join(_basedir, '..'))

sys.path.insert(1, _pkg_root)

from moehime.ui.cli import cli_entry


if __name__ == '__main__':
    sys.exit(cli_entry(sys.argv))


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
