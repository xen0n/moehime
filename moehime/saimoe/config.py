#!/usr/bin/python
# -*- coding: utf-8 -*-
# moehime / saimoe / counter configuration
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

from itertools import chain
import datetime

from os.path import exists

from .net.fetch import ResourceRequester

# TODO: make this configurable thru app config (although not so useful)
# 让这个可以通过程序配置自定义（虽然没什么好处）
CONFIG_ENCODING = 'sjis'
CONFIG_URL_PREFIX = 'http://saimoe.googlecode.com/files/config'
CONFIG_PATH_PREFIX = './configs/'
CONFIG_EXTENSION = '.txt'

# The only "kind" used with ResourceRequester
URL_CONFIG = 0


class CrawlConfig(object):
    def __init__(self, date, path=None):
        super(CrawlConfig, self).__init__()
        self.date = date
        # TODO: adapt to some unified persistence management
        self.path = path if path is not None else self.get_path(date)
        self._inited = False

    def get_path(self, date):
        # while this seems duplicate wrt WebBasedCrawlConfig.get_config_url,
        # actually the local config file's naming convention has nothing to
        # do with that of theremote repository.
        return unicode(date.strftime('%m%d')).join((
            CONFIG_PATH_PREFIX,
            CONFIG_EXTENSION,
            ))

    def readconfig(self):
        return self._do_readconfig()

    def _do_readconfig(self, s=None):
        lines = None

        if s is None:
            with open(self.path, 'rb') as fp:
                content = _read_raw_lines(fp)
        else:
            content = s

        lines = _lines_from_config(content)

        config = parse_config(lines)

        if self.date != config['date']:
            raise ValueError('config date mismatch')

        self.groups = config['groups']
        self.limit = config['limit']
        self.aliases = config['aliases']


class WebBackedCrawlConfig(CrawlConfig, ResourceRequester):
    def __init__(self, date, path=None):
        super(WebBackedCrawlConfig, self).__init__(date, path)

    def get_encoding(self, kind):
        return CONFIG_ENCODING

    def format_url(self, kind, date=None):
        date = self.date if date is None else date

        # http://.../config%m%d.txt
        # construct the string 构建字符串
        return unicode(date.strftime('%m%d')).join((
                CONFIG_URL_PREFIX,
                CONFIG_EXTENSION,
                ))

    def readconfig(self):
        if not exists(self.path):
            # TOCTTOU here... how to fix this ugliness?
            # 这里有TOCTTOU情况。。谁知道怎么解决？
            # TODO: fix the condition by using file.truncate()
            configcontent = self.fetch(URL_CONFIG)
            with open(self.path, 'wb') as fp:
                fp.write(configcontent)

            # save a file read, but is this worth the gained
            # complexity of base class?
            # 省一次读文件，但是值得为此增加基类的代码复杂度么？
            return self._do_readconfig(configcontent)

        return self._do_readconfig()


def _lines_from_config(s):
    # XXX DAMN WINDOWS CRLF LINE-ENDING!!!
    # This led to MYSTERIOUS "invalid" aliases!!!
    # 去你妹的 Windows 行尾！这个导致了各种奇怪的“无效”别名。。
    #
    # thx @cerenkov, there's a string method called ``splitlines``...
    # 感谢 @cerenkov，string 有个方法叫 ``splitline``...
    return s.decode(CONFIG_ENCODING).splitlines()


def _read_raw_lines(fp):
    content = fp.read()

    return _lines_from_config(content)


# config.txt syntax:
# http://tieba.baidu.com/p/1802674085
# thx @灵剑2006 for this information
def parse_config(lines):
    # Erlang-like syntax... don't mind
    # the second line is not used
    # Erlang 既视感。。。不要在意。第二行用不着
    ln_date, _dummy, ln_grp = lines[:3]

    # tournament date
    # 比赛日期
    date_val = [int(i) for i in ln_date.split('/')]

    # convert year val.
    # since the first anime saimoe was in 2002 there is no need to consider
    # pre-Y2K dates (and doing so would cause trouble in the far future, if
    # there is still a saimoe tournament when it's 2050, and this library
    # is still in use).
    # 转换年份。因为第一届萌战是 2002 年举行的，就没必要考虑 2000 年以前的
    # 日期了（这么做的话在很久的将来会出问题的，如果 2050 年还有萌战，而且
    # 这个库那时还在使用。。）
    date_val[0] = date_val[0] + 2000
    date = datetime.datetime(*date_val[:3])  # in case of malformed input

    # group config
    # 分组设定
    grp_cnt, num_per_grp, grp_limit = [int(i) for i in ln_grp.split(' ')]

    # names of characters
    # 角色名
    ln_charas = lines[3:3 + (grp_cnt * num_per_grp)]

    # parse character aliases and separate into group in one pass
    # 一遍扫描，解析角色描述行，同时进行分组

    # [[] * num_per_grp] is WRONG: it's SHALLOW copy!
    # [[] * num_per_grp] 是不行的：那是浅拷贝！
    groups = [[] for i in xrange(num_per_grp)]
    for count, ln in enumerate(ln_charas):
        chara = parse_chara(ln)

        # insert into the appropriate group
        # notice the explicit FLOOR division (due to the future stmt)
        # 插入合适的分组
        # 注意这里要用取整除法，因为用了 future 语句
        groups[count // num_per_grp].append(chara)

    # build alias-to-name mapping
    # directly chaining the groups together is OK
    # 构造别名-角色名映射
    # 直接把组列表串起来就行了
    alias_map = build_alias_map(chain(*groups))

    return {
            'date': date,
            'groups': groups,
            'limit': grp_limit,
            'aliases': alias_map,
            }


def parse_chara(line):
    names = line.split(',')

    # TODO: further canonicalize the names 让名字更标准化一点
    name, aliases = names[0], names[1:]
    return {
            'name': name,
            'aliases': aliases,
            }


def build_alias_map(charas):
    result = {}

    for chara in charas:
        name = chara['name']

        # the structure can't be a simple reverse index, due to the alias
        # match not being exact. Using such a mapping would complicate the
        # code when it comes to handling those non-exact-match cases.
        # 这个数据结构不能简单地用反向索引，因为别名匹配不是精确的。
        # 用了这种映射会复杂化处理模糊匹配情况的那部分代码。
        aliases = result[name] = []
        for alias in chara['aliases']:
            aliases.append(alias)

    return result


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
