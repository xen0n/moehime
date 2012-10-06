#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / filters - alias filter
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

from functools import wraps

from . import filter_manager
from .base import BaseFilter

_ = lambda x: x


def simple_memoize(fn):
    __cache = {}

    @wraps(fn)
    def _wrapped_(self, arg):
        if arg in __cache:
            return __cache[arg]
        result = __cache[arg] = fn(self, arg)
        return result

    return _wrapped_


@filter_manager.register
class AliasFilter(BaseFilter):
    '''别名过滤器。

    将票面中角色的别名标准化为其完全形式。

    '''

    FILTER_NAME = 'alias'

    def __init__(self, config=None):
        super(AliasFilter, self).__init__(config)

        self._aliases = config['aliases']
        self._canonical_names = aliases.keys()

    @simple_memoize
    def _map_name(self, name):
        if name in self._canonical_names:
            # shortcut
            # 捷径
            return True, True, name

        # fuzzy alias matching
        # 模糊的别名匹配
        matched_name = None
        for canonical, alias_list in self._aliases.iteritems():
            for alias in alias_list:
                if alias in name:
                    # the alias matches, but we must pay attention to
                    # the invalid case in which ``entry`` matches more
                    # than one character.
                    # 匹配到别名，不过要小心同时匹配多个角色的无效情况
                    if matched_name is not None:
                        # ambiguous vote, considered invalid
                        # 歧义票，无效
                        return False, False, None

                    # remember the currently matched canonical name,
                    # then break out to try the next character
                    # 记住目前匹配上的标准角色名，然后去匹配下一个角色
                    matched_name = canonical
                    break

        if matched_name is not None:
            return True, False, matched_name
        return False, False, None

    def setup(self):
        self._aliases_encountered = {}
        self._invalids_encountered = {}

    def _do_judge(self, datum):
        norm_charas, aliases, invalids = [], [], []
        for chara in datum.charas:
            is_valid, is_exact, canonical_name = self._map_name(chara)

            if is_valid:
                norm_charas.append(canonical_name)
                if not is_exact:
                    aliases.append(chara)

                    # update global statistics
                    # 更新全局统计信息
                    self._aliases_encountered.setdefault(chara, 0)
                    self._aliases_encountered[chara] += 1
            else:
                invalids.append(chara)

                self._invalids_encountered.setdefault(chara, 0)
                self._invalids_encountered[chara] += 1

        datum.charas = norm_charas
        is_vote_valid = len(norm_charas) > 0

        return is_vote_valid, {
                'aliases': aliases,
                'invalids': invalids,
                }

    def report(self):
        return {
                'aliases': self._aliases_encountered,
                'invalids': self._invalids_encountered,
                }


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
