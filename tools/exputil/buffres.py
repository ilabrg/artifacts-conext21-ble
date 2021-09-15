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
import sys
from pathlib import Path
sys.path.append(str(Path(os.path.abspath(__file__)).parent.parent))

import re
import copy
import json
import math
from datetime import datetime
from tools.exputil.ana import Ana
from tools.exputil.topo import Topo
from tools.exputil.expstats import Expstats
from tools.exputil.alive import Alive
from tools.exputil.ifconfigval import Ifconfigval
from tools.exputil.llstats import LLStats


class Buffres(Ana):

    def __init__(self, logfile):
        super().__init__(logfile)

        self.alive = None
        self.expstats = None
        self.ifconfigval = None
        self.llstats = None
        self.topo = None

        # find buffered data file
        srcfile = f"{self.plotbase}_raw.json"
        self.checkpath(srcfile)
        with open(srcfile, "r", encoding="utf-8") as f:
            data = json.load(f)

            self.t = data["t"]

            if "alive" in data:
                self.alive = Alive(self)
                self.alive.readraw(data["alive"])
                # self.alive.summary()

            if "llstats" in data:
                self.llstats = LLStats(self)
                self.llstats.readraw(data["llstats"])
                # self.llstats.summary()

            if "expstats" in data:
                self.expstats = Expstats(self)
                self.expstats.readraw(data["expstats"])
                # self.expstats.summary()
