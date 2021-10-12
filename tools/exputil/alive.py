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


class Alive:

    def __init__(self, ana):
        self.ana = ana
        self.used = False
        self.data = {}
        for n in self.ana.desc["used_nodes"]:
            self.data[n] = {
                "max": -1,      # maximum alive counter seen in log
                "cnt": 0,       # number of alive message per node seen
                "lost": [],     # lost sequence numbers
                "dups": [],     # duplicate sequence numbers
            }

        self.re_alive = re.compile(r'ALIVE-(?P<seq>[0-9]+)')


    def update(self, time, node, line):
        m = self.re_alive.search(line)
        if m:
            self.used = True
            seq = int(m.group('seq'))
            prior = seq - 1

            if seq == self.data[node]["max"]:
                self.data[node]["dups"].append(seq)
            elif prior != self.data[node]["max"]:
                self.data[node]["lost"].append(seq - 1)

            self.data[node]["max"] = seq
            self.data[node]["cnt"] += 1


    def summary(self):
        if self.used == False:
            self.ana.statwrite("ALIVE: skipped")
            return

        self.ana.statwrite("ALIVE signal summary:")

        for n in self.ana.nsort(self.data):
            a = self.data[n]

            self.ana.statwrite("{:>15}: max:{:>5} cnt:{:>5} dups:{} lost:{}".format(n, a["max"], a["cnt"], a["dups"], a["lost"]))

        broken = []

        for n in self.data:
            if self.data[n]["cnt"] < 10:
                broken.append(n)

        if len(broken) > 0:
            self.ana.warn_blocking("ALIVE: nodes {} seems to be broken, bad ALIVE count!".format(broken))


    def getraw(self):
        return {"data": self.data}


    def readraw(self, raw):
        self.data = raw["data"]
