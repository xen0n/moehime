#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / filters - basic filter
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
from functools import partial

from . import filter_manager
from .base import BaseFilter
from ..votecode import VoteCode

_ = lambda x: x

# 匹配角色名/alias，之后对内容进行精确匹配
# Character name/alias, the captured string is then matched
# in an exact mannner
RE_CHARA = re.compile(r'<<(.*?)>>')

# reduce lookups 减少查找
VOTECODE_RECOGNIZE = VoteCode.recognize


def _chara_match_helper(charas, match):
    # record the chara and strip it out of text
    # this way we get pure moebun
    # 记录角色并将其从正文中剔除
    # 这样我们就得到纯粹的萌文
    charas.append(match.group(1))
    return ''


def extract_moebun(text):
    charas = []

    helper = partial(_chara_match_helper, charas)
    moebun = RE_CHARA.sub(helper, text).strip()

    return charas, moebun


def posttime_validator_factory(valid_date):
    Y, m, d = valid_date.year, valid_date.month, valid_date.day

    def __is_posttime_valid(date):
        d_Y, d_m, d_d = date.year, date.month, date.day
        d_H, d_i = date.hour, date.minute

        if d_Y != Y or d_m != m or d_d != d:
            return False

        if not 1 <= d_H <= 23:
            return False

        if d_H == 23 and d_m >= 1:
            return False

        return True
    return __is_posttime_valid


@filter_manager.register
class InitialFilter(BaseFilter):
    '''初始过滤器。

    作用是初始化一些投票对象内部的属性，比如提取 code 和角色名之类。

    为了过滤机制正常工作，此过滤器必须存在于过滤序列中，且必须第一个执行。

    '''

    FILTER_NAME = 'initial'

    def _do_judge(self, datum):
        text = datum.full_text
        datum.code, text_w_o_code = VOTECODE_RECOGNIZE(text)

        charas, moebun = extract_moebun(text_w_o_code)
        datum.charas.extend(charas)
        datum.text = moebun

        return True, None


@filter_manager.register
class BasicFilter(BaseFilter):
    '''基础过滤器。

    此过滤器对投票执行最基本的判断：发帖时间检查、code 有效性检查、
    萌文不为空检查、角色不为空检查。

    一般情况下请选中此过滤器，并紧随初始过滤器之后。

    '''

    FILTER_NAME = 'basic'

    def __init__(self, config):
        valid_date = self.valid_date = config.date
        self.date_validator = posttime_validator_factory(valid_date)

    def _do_judge(self, datum):
        if datum.code is None:
            return False, _('正文无 code')

        if len(datum.text) == 0:
            return False, _('除去 code 与角色名的萌文为空')

        if len(datum.charas) == 0:
            return False, _('未识别出任何角色')

        if not self.date_validator(datum.ctime):
            return False, _('投票不在有效时间段')

        return True, None


@filter_manager.register
class CountFilter(BaseFilter):
    '''集计过滤器。

    此过滤器集计所有经过它的有效票。

    为使计票器正常工作并给出有意义结果，此过滤器必须位于过滤序列最后。

    '''

    FILTER_NAME = 'count'

    def setup(self):
        self._result = {}

    def _do_judge(self, datum):
        for chara in datum.charas:
            self._result.setdefault(chara, 0)
            self._result[chara] += 1
        return True, None

    def report(self):
        return self._result


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
