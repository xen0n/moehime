#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / user interface / command line interface
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

__all__ = [
        'print_wrapper',
        'fetch_with_prompt',
        ]

import sys
import locale


# Windows console encoding is WAY more restrictive than UTF-8 used by Linux
# Must provide a wrapper to hide the difference
# Windows 控制台编码比起 Linux 的 UTF-8 来实在是太不自由了
# 必须用一层包装隐藏掉这个差异性
def print_wrapper_factory():
    enc = locale.getpreferredencoding()

    def _print_wrapper(value='', *args, **kwargs):
        if isinstance(value, unicode):
            value = value.encode(enc, 'replace')

        print(value, *args, **kwargs)
        return
    return _print_wrapper

#
#def fetch_with_prompt(url, stream=sys.stderr):
#    print_wrapper('    %s ...' % (url, ), end='', file=stream)
#    content = do_fetch(url)
#    print_wrapper('%d B' % (len(content), ), file=stream)
#
#    return content


print_wrapper = print_wrapper_factory()


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
