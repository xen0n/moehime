#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / vote object
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

from .votecode import VoteCode

# 匹配角色名/alias，之后对内容进行精确匹配
# Character name/alias, the captured string is then matched
# in an exact mannner
RE_CHARA = re.compile(r'<<(.*?)>>')

# reduce lookups 减少查找
VOTECODE_RECOGNIZE = VoteCode.recognize


class VoteEntry(object):
    def __init__(self, author, ctime, text):
        self.author = author
        self.ctime = ctime
        self.full_text = text
        self.text = ''

        code = VOTECODE_RECOGNIZE(text)
        is_valid = self.is_valid = code is not None
        self.charas = []
        self.annotations = {}

        if is_valid:
            self._extract_charas()

    def _chara_match_helper(self, match):
        # record the chara and strip it out of text
        # this way we get pure moe-mon
        # 记录角色并将其从正文中剔除
        # 这样我们就得到纯粹的萌文
        self.charas.append(match.group(1))
        return ''

    def _extract_charas(self):
        self.text = RE_CHARA.sub(self._chara_match_helper, self.full_text)


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
