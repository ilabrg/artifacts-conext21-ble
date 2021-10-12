#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019 Hauke Petersen <hauke.petersen@fu-berlin.de>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

import os
import re
import sys
import copy

MAX_CONNS = 20

class Connitvl:

    def __init__(self, ana):
        self.ana = ana
        self.conns = {n: [None for _ in range(MAX_CONNS)] for n in self.ana.desc["used_nodes"]}

        self.re_itvl = re.compile(r'\[ ?(?P<handle>\d+)\] '
                                  r'(?P<peer>[0-9a-zA-Z:]+) \[(?P<lladdr>[0-9a-zA-Z:]+)\] '
                                  r'\((?P<role>[MS]),(?P<itvl>\d+)ms,(?P<super>\d+)ms,(?P<slat>\d+)\)')
        self.re_unused = re.compile(r'\[ ?(?P<handle>\d+)\] state: 0x\d+ - unused')


    def update(self, time, node, line):
        m = self.re_itvl.search(line)
        if m:
            handle = int(m.group("handle"))
            peer = self.ana.nodename_from_mac(m.group('peer'))
            self.conns[node][handle] = {
                "peer": peer,
                "role": m.group("role"),
                "itvl": int(m.group("itvl")),
                "super": int(m.group("super")),
                "slat": int(m.group("slat")),
            }
            # print("Hello peer {}".format(self.conns[node][handle]))

        m = self.re_unused.search(line)
        if m:
            handle = int(m.group("handle"))
            self.conns[node][handle] = None


    def summary(self):
        print("\nConnection Interval Summary:")
        for n in self.conns:
            itvls = []
            for h in range(MAX_CONNS):
                val = self.conns[n][h]
                if val != None:
                    itvls.append(val["itvl"])

            if len(itvls) > 1:
                diff = 100000
                itvls = sorted(itvls)
                for i in range(len(itvls) - 1):
                    if itvls[i + 1] - itvls[i] < diff:
                        diff = itvls[i + 1] - itvls[i]
            else:
                diff = "-"

            print("{:>15} min spacing:{:>3} itvls:{}".format(n, diff, itvls))
        print("")
