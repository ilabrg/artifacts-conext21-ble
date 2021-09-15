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
import numpy as np

STATS = ["TX", "RX", "FW"]

class Procdelay:
    def __init__(self, ana):
        self.ana = ana

        self.delay = {n: {t: [] for t in STATS} for n in self.ana.desc["used_nodes"]}


    def update(self, time, node, line):
        m = re.search(r'^>? *\*(?P<type>[A-Z]+):(?P<time>\d+)', line)
        if m:
            self.delay[node][m.group("type")].append(int(m.group("time")))


    def finish(self):
        pass


    def summary(self):
        su = {t: 0 for t in STATS}
        self.ana.statwrite("Procdelay Summary")
        self.ana.statwrite("{:>15} {:>6} {:>6} {:>6}".format("node", "#TX", "#RX", "#FW"))
        for n in self.delay:
            self.ana.statwrite("{:>15} {:>6} {:>6} {:>6}".format(
                                n,
                                len(self.delay[n]["TX"]),
                                len(self.delay[n]["RX"]),
                                len(self.delay[n]["FW"])))
            for t in STATS:
                su[t] += len(self.delay[n][t])
        self.ana.statwrite("{:>15} {:>6} {:>6} {:>6}".format(
                            "sum", su["TX"], su["RX"], su["FW"]))
