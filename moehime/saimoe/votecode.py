#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / vote code object
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

import re

from .exc import MalformedCodeError


# 匹配code
# Vote code
RE_CODE_EXPR = (
        r'^\[\[AS(?P<yy>\d{2})-(?P<d>\d+)-'
        r'(?P<nonce>[0-9A-Za-z./]{8})-'
        r'(?P<issued>[A-Za-z])(?P<tail>[A-Za-z])'
        r'\]\]-(?P<ord>\d{5})$'
        )

# this is only for recognizing codes, so it doesn't have any
# groups inside
# 这个只是识别用的，没有组
RE_CODE_RECOG_EXPR = (
        r'\[\[AS\d{2}-\d+-'
        r'[0-9A-Za-z./]{8}-'
        r'[A-Za-z][A-Za-z]'
        r'\]\]-\d{5}'
        )


RE_CODE_RECOGNIZER = re.compile(RE_CODE_RECOG_EXPR)
RE_CODE_MATCHER = re.compile(RE_CODE_EXPR)


class VoteCode(object):
    def __init__(self, s):
        match = RE_CODE_MATCHER.match(s)
        if match is None:
            raise MalformedCodeError

        m_grp = match.group
        # TODO: move here some comments written earlier
        self.year = int(m_grp('yy')) + 2000
        self.day = int(m_grp('d'))
        self.nonce = m_grp('nonce')
        self.issued = m_grp('issued')
        self.tail = m_grp('tail')
        self.ordinal = m_grp('ord')

        self._content = s if isinstance(s, unicode) else s.decode('ascii')

    @staticmethod
    def recognize(text):
        codes = RE_CODE_RECOGNIZER.findall(text)
        if len(codes) == 1:
            return VoteCode(codes[0]), RE_CODE_RECOGNIZER.sub('', text)

        # multiple codes or no code found...
        return None, text

    @property
    def content(self):
        return self._content

    def __unicode__(self):
        return self.content

    def __str__(self):
        return self.content.encode('ascii')


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
