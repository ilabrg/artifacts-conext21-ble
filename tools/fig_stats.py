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
import math
import json
import yaml
import argparse
import numpy as np
from datetime import datetime
from tools.exputil.ana import Ana
from tools.exputil.topo import Topo
from tools.exputil.expstats import Expstats
from tools.exputil.llstats import LLStats
from tools.exputil.alive import Alive
from tools.exputil.ifconfigval import Ifconfigval
from tools.exputil.plotter import Plotter
from tools.exputil.expbase import Expbase

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

SRC = {
    "100ms1h39b_i25-0": "exp_putnon_statconn-static_100ms1h39b_i25/exp_putnon_statconn-static_100ms1h39b_i25_20210923-111044",
    "100ms1h39b_i25-1": "exp_putnon_statconn-static_100ms1h39b_i25/exp_putnon_statconn-static_100ms1h39b_i25_20211022-093606",
    "100ms1h39b_i25-2": "exp_putnon_statconn-static_100ms1h39b_i25/exp_putnon_statconn-static_100ms1h39b_i25_20211020-172154",
    "100ms1h39b_i25-3": "exp_putnon_statconn-static_100ms1h39b_i25/exp_putnon_statconn-static_100ms1h39b_i25_20211017-080441",
    "100ms1h39b_i25-4": "exp_putnon_statconn-static_100ms1h39b_i25/exp_putnon_statconn-static_100ms1h39b_i25_20211024-174309",
    "100ms1h39b_i50-0": "exp_putnon_statconn-static_100ms1h39b_i50/exp_putnon_statconn-static_100ms1h39b_i50_20211017-091317",
    "100ms1h39b_i50-1": "exp_putnon_statconn-static_100ms1h39b_i50/exp_putnon_statconn-static_100ms1h39b_i50_20211024-185145",
    "100ms1h39b_i50-2": "exp_putnon_statconn-static_100ms1h39b_i50/exp_putnon_statconn-static_100ms1h39b_i50_20210923-121922",
    "100ms1h39b_i50-3": "exp_putnon_statconn-static_100ms1h39b_i50/exp_putnon_statconn-static_100ms1h39b_i50_20211020-183028",
    "100ms1h39b_i50-4": "exp_putnon_statconn-static_100ms1h39b_i50/exp_putnon_statconn-static_100ms1h39b_i50_20211022-104441",
    "100ms1h39b_i75-0": "exp_putnon_statconn-static_100ms1h39b_i75/exp_putnon_statconn-static_100ms1h39b_i75_20210923-132758",
    "100ms1h39b_i75-1": "exp_putnon_statconn-static_100ms1h39b_i75/exp_putnon_statconn-static_100ms1h39b_i75_20210301-164004",
    "100ms1h39b_i75-2": "exp_putnon_statconn-static_100ms1h39b_i75/exp_putnon_statconn-static_100ms1h39b_i75_20210301-140226",
    "100ms1h39b_i75-3": "exp_putnon_statconn-static_100ms1h39b_i75/exp_putnon_statconn-static_100ms1h39b_i75_20210914-101545",
    "100ms1h39b_i75-4": "exp_putnon_statconn-static_100ms1h39b_i75/exp_putnon_statconn-static_100ms1h39b_i75_20210301-164004",
    "100ms1h39b_i100-0": "exp_putnon_statconn-static_100ms1h39b_i100/exp_putnon_statconn-static_100ms1h39b_i100_20210923-143635",
    "100ms1h39b_i100-1": "exp_putnon_statconn-static_100ms1h39b_i100/exp_putnon_statconn-static_100ms1h39b_i100_20211022-115329",
    "100ms1h39b_i100-2": "exp_putnon_statconn-static_100ms1h39b_i100/exp_putnon_statconn-static_100ms1h39b_i100_20211024-224304",
    "100ms1h39b_i100-3": "exp_putnon_statconn-static_100ms1h39b_i100/exp_putnon_statconn-static_100ms1h39b_i100_20211020-193902",
    "100ms1h39b_i100-4": "exp_putnon_statconn-static_100ms1h39b_i100/exp_putnon_statconn-static_100ms1h39b_i100_20211017-102153",
    "100ms1h39b_i500-0": "exp_putnon_statconn-static_100ms1h39b_i500/exp_putnon_statconn-static_100ms1h39b_i500_20211022-130204",
    "100ms1h39b_i500-1": "exp_putnon_statconn-static_100ms1h39b_i500/exp_putnon_statconn-static_100ms1h39b_i500_20211020-204736",
    "100ms1h39b_i500-2": "exp_putnon_statconn-static_100ms1h39b_i500/exp_putnon_statconn-static_100ms1h39b_i500_20210923-154511",
    "100ms1h39b_i500-3": "exp_putnon_statconn-static_100ms1h39b_i500/exp_putnon_statconn-static_100ms1h39b_i500_20211025-022124",
    "100ms1h39b_i500-4": "exp_putnon_statconn-static_100ms1h39b_i500/exp_putnon_statconn-static_100ms1h39b_i500_20211017-113027",
    "100ms1h39b_i15r35-0": "exp_putnon_statconn-static_100ms1h39b_i15r35/exp_putnon_statconn-static_100ms1h39b_i15r35_20211020-215610",
    "100ms1h39b_i15r35-1": "exp_putnon_statconn-static_100ms1h39b_i15r35/exp_putnon_statconn-static_100ms1h39b_i15r35_20211022-141040",
    "100ms1h39b_i15r35-2": "exp_putnon_statconn-static_100ms1h39b_i15r35/exp_putnon_statconn-static_100ms1h39b_i15r35_20211017-123923",
    "100ms1h39b_i15r35-3": "exp_putnon_statconn-static_100ms1h39b_i15r35/exp_putnon_statconn-static_100ms1h39b_i15r35_20210923-165404",
    "100ms1h39b_i15r35-4": "exp_putnon_statconn-static_100ms1h39b_i15r35/exp_putnon_statconn-static_100ms1h39b_i15r35_20211025-081443",
    "100ms1h39b_i40r60-0": "exp_putnon_statconn-static_100ms1h39b_i40r60/exp_putnon_statconn-static_100ms1h39b_i40r60_20211017-134800",
    "100ms1h39b_i40r60-1": "exp_putnon_statconn-static_100ms1h39b_i40r60/exp_putnon_statconn-static_100ms1h39b_i40r60_20211025-103729",
    "100ms1h39b_i40r60-2": "exp_putnon_statconn-static_100ms1h39b_i40r60/exp_putnon_statconn-static_100ms1h39b_i40r60_20211022-152020",
    "100ms1h39b_i40r60-3": "exp_putnon_statconn-static_100ms1h39b_i40r60/exp_putnon_statconn-static_100ms1h39b_i40r60_20211020-230546",
    "100ms1h39b_i40r60-4": "exp_putnon_statconn-static_100ms1h39b_i40r60/exp_putnon_statconn-static_100ms1h39b_i40r60_20210923-180239",
    "100ms1h39b_i65r85-0": "exp_putnon_statconn-static_100ms1h39b_i65r85/exp_putnon_statconn-static_100ms1h39b_i65r85_20211017-145636",
    "100ms1h39b_i65r85-1": "exp_putnon_statconn-static_100ms1h39b_i65r85/exp_putnon_statconn-static_100ms1h39b_i65r85_20210923-191115",
    "100ms1h39b_i65r85-2": "exp_putnon_statconn-static_100ms1h39b_i65r85/exp_putnon_statconn-static_100ms1h39b_i65r85_20211021-001422",
    "100ms1h39b_i65r85-3": "exp_putnon_statconn-static_100ms1h39b_i65r85/exp_putnon_statconn-static_100ms1h39b_i65r85_20210301-204413",
    "100ms1h39b_i65r85-4": "exp_putnon_statconn-static_100ms1h39b_i65r85/exp_putnon_statconn-static_100ms1h39b_i65r85_20210305-205739",
    "100ms1h39b_i90r110-0": "exp_putnon_statconn-static_100ms1h39b_i90r110/exp_putnon_statconn-static_100ms1h39b_i90r110_20210923-202108",
    "100ms1h39b_i90r110-1": "exp_putnon_statconn-static_100ms1h39b_i90r110/exp_putnon_statconn-static_100ms1h39b_i90r110_20211025-131421",
    "100ms1h39b_i90r110-2": "exp_putnon_statconn-static_100ms1h39b_i90r110/exp_putnon_statconn-static_100ms1h39b_i90r110_20211021-012258",
    "100ms1h39b_i90r110-3": "exp_putnon_statconn-static_100ms1h39b_i90r110/exp_putnon_statconn-static_100ms1h39b_i90r110_20211022-162854",
    "100ms1h39b_i90r110-4": "exp_putnon_statconn-static_100ms1h39b_i90r110/exp_putnon_statconn-static_100ms1h39b_i90r110_20211017-160511",
    "100ms1h39b_i490r510-0": "exp_putnon_statconn-static_100ms1h39b_i490r510/exp_putnon_statconn-static_100ms1h39b_i490r510_20211021-023145",
    "100ms1h39b_i490r510-1": "exp_putnon_statconn-static_100ms1h39b_i490r510/exp_putnon_statconn-static_100ms1h39b_i490r510_20211025-142255",
    "100ms1h39b_i490r510-2": "exp_putnon_statconn-static_100ms1h39b_i490r510/exp_putnon_statconn-static_100ms1h39b_i490r510_20211017-171345",
    "100ms1h39b_i490r510-3": "exp_putnon_statconn-static_100ms1h39b_i490r510/exp_putnon_statconn-static_100ms1h39b_i490r510_20210923-212944",
    "100ms1h39b_i490r510-4": "exp_putnon_statconn-static_100ms1h39b_i490r510/exp_putnon_statconn-static_100ms1h39b_i490r510_20211022-173730",
    "500ms1h39b_i25-0": "exp_putnon_statconn-static_500ms1h39b_i25/exp_putnon_statconn-static_500ms1h39b_i25_20210923-223831",
    "500ms1h39b_i25-1": "exp_putnon_statconn-static_500ms1h39b_i25/exp_putnon_statconn-static_500ms1h39b_i25_20211025-153129",
    "500ms1h39b_i25-2": "exp_putnon_statconn-static_500ms1h39b_i25/exp_putnon_statconn-static_500ms1h39b_i25_20211022-184704",
    "500ms1h39b_i25-3": "exp_putnon_statconn-static_500ms1h39b_i25/exp_putnon_statconn-static_500ms1h39b_i25_20211027-111011",
    "500ms1h39b_i25-4": "exp_putnon_statconn-static_500ms1h39b_i25/exp_putnon_statconn-static_500ms1h39b_i25_20211028-111229",
    "500ms1h39b_i50-0": "exp_putnon_statconn-static_500ms1h39b_i50/exp_putnon_statconn-static_500ms1h39b_i50_20211022-195538",
    "500ms1h39b_i50-1": "exp_putnon_statconn-static_500ms1h39b_i50/exp_putnon_statconn-static_500ms1h39b_i50_20211017-182221",
    "500ms1h39b_i50-2": "exp_putnon_statconn-static_500ms1h39b_i50/exp_putnon_statconn-static_500ms1h39b_i50_20210923-234730",
    "500ms1h39b_i50-3": "exp_putnon_statconn-static_500ms1h39b_i50/exp_putnon_statconn-static_500ms1h39b_i50_20211021-034020",
    "500ms1h39b_i50-4": "exp_putnon_statconn-static_500ms1h39b_i50/exp_putnon_statconn-static_500ms1h39b_i50_20211025-164006",
    "500ms1h39b_i75-0": "exp_putnon_statconn-static_500ms1h39b_i75/exp_putnon_statconn-static_500ms1h39b_i75_20211021-044855",
    "500ms1h39b_i75-1": "exp_putnon_statconn-static_500ms1h39b_i75/exp_putnon_statconn-static_500ms1h39b_i75_20211022-210412",
    "500ms1h39b_i75-2": "exp_putnon_statconn-static_500ms1h39b_i75/exp_putnon_statconn-static_500ms1h39b_i75_20211025-174842",
    "500ms1h39b_i75-3": "exp_putnon_statconn-static_500ms1h39b_i75/exp_putnon_statconn-static_500ms1h39b_i75_20211017-232234",
    "500ms1h39b_i75-4": "exp_putnon_statconn-static_500ms1h39b_i75/exp_putnon_statconn-static_500ms1h39b_i75_20210924-005605",
    "500ms1h39b_i100-0": "exp_putnon_statconn-static_500ms1h39b_i100/exp_putnon_statconn-static_500ms1h39b_i100_20211028-122103",
    "500ms1h39b_i100-1": "exp_putnon_statconn-static_500ms1h39b_i100/exp_putnon_statconn-static_500ms1h39b_i100_20211025-185716",
    "500ms1h39b_i100-2": "exp_putnon_statconn-static_500ms1h39b_i100/exp_putnon_statconn-static_500ms1h39b_i100_20211022-221247",
    "500ms1h39b_i100-3": "exp_putnon_statconn-static_500ms1h39b_i100/exp_putnon_statconn-static_500ms1h39b_i100_20210924-020452",
    "500ms1h39b_i100-4": "exp_putnon_statconn-static_500ms1h39b_i100/exp_putnon_statconn-static_500ms1h39b_i100_20211027-121903",
    "500ms1h39b_i500-0": "exp_putnon_statconn-static_500ms1h39b_i500/exp_putnon_statconn-static_500ms1h39b_i500_20211018-003110",
    "500ms1h39b_i500-1": "exp_putnon_statconn-static_500ms1h39b_i500/exp_putnon_statconn-static_500ms1h39b_i500_20211021-055729",
    "500ms1h39b_i500-2": "exp_putnon_statconn-static_500ms1h39b_i500/exp_putnon_statconn-static_500ms1h39b_i500_20211025-200550",
    "500ms1h39b_i500-3": "exp_putnon_statconn-static_500ms1h39b_i500/exp_putnon_statconn-static_500ms1h39b_i500_20210924-031329",
    "500ms1h39b_i500-4": "exp_putnon_statconn-static_500ms1h39b_i500/exp_putnon_statconn-static_500ms1h39b_i500_20211022-232121",
    "500ms1h39b_i15r35-1": "exp_putnon_statconn-static_500ms1h39b_i15r35/exp_putnon_statconn-static_500ms1h39b_i15r35_20211021-070605",
    "500ms1h39b_i15r35-2": "exp_putnon_statconn-static_500ms1h39b_i15r35/exp_putnon_statconn-static_500ms1h39b_i15r35_20211018-013946",
    "500ms1h39b_i15r35-3": "exp_putnon_statconn-static_500ms1h39b_i15r35/exp_putnon_statconn-static_500ms1h39b_i15r35_20210928-184348",
    "500ms1h39b_i15r35-4": "exp_putnon_statconn-static_500ms1h39b_i15r35/exp_putnon_statconn-static_500ms1h39b_i15r35_20210928-162626",
    "500ms1h39b_i15r35-5": "exp_putnon_statconn-static_500ms1h39b_i15r35/exp_putnon_statconn-static_500ms1h39b_i15r35_20210928-140805",
    "500ms1h39b_i40r60-0": "exp_putnon_statconn-static_500ms1h39b_i40r60/exp_putnon_statconn-static_500ms1h39b_i40r60_20211025-211425",
    "500ms1h39b_i40r60-1": "exp_putnon_statconn-static_500ms1h39b_i40r60/exp_putnon_statconn-static_500ms1h39b_i40r60_20211018-024822",
    "500ms1h39b_i40r60-2": "exp_putnon_statconn-static_500ms1h39b_i40r60/exp_putnon_statconn-static_500ms1h39b_i40r60_20211021-081439",
    "500ms1h39b_i40r60-3": "exp_putnon_statconn-static_500ms1h39b_i40r60/exp_putnon_statconn-static_500ms1h39b_i40r60_20211023-002955",
    "500ms1h39b_i40r60-4": "exp_putnon_statconn-static_500ms1h39b_i40r60/exp_putnon_statconn-static_500ms1h39b_i40r60_20210924-053103",
    "500ms1h39b_i65r85-0": "exp_putnon_statconn-static_500ms1h39b_i65r85/exp_putnon_statconn-static_500ms1h39b_i65r85_20211018-054734",
    "500ms1h39b_i65r85-1": "exp_putnon_statconn-static_500ms1h39b_i65r85/exp_putnon_statconn-static_500ms1h39b_i65r85_20211023-013831",
    "500ms1h39b_i65r85-2": "exp_putnon_statconn-static_500ms1h39b_i65r85/exp_putnon_statconn-static_500ms1h39b_i65r85_20211021-092313",
    "500ms1h39b_i65r85-3": "exp_putnon_statconn-static_500ms1h39b_i65r85/exp_putnon_statconn-static_500ms1h39b_i65r85_20211025-222301",
    "500ms1h39b_i65r85-4": "exp_putnon_statconn-static_500ms1h39b_i65r85/exp_putnon_statconn-static_500ms1h39b_i65r85_20210924-063941",
    "500ms1h39b_i90r110-0": "exp_putnon_statconn-static_500ms1h39b_i90r110/exp_putnon_statconn-static_500ms1h39b_i90r110_20210924-074818",
    "500ms1h39b_i90r110-1": "exp_putnon_statconn-static_500ms1h39b_i90r110/exp_putnon_statconn-static_500ms1h39b_i90r110_20211018-065620",
    "500ms1h39b_i90r110-2": "exp_putnon_statconn-static_500ms1h39b_i90r110/exp_putnon_statconn-static_500ms1h39b_i90r110_20211025-233243",
    "500ms1h39b_i90r110-3": "exp_putnon_statconn-static_500ms1h39b_i90r110/exp_putnon_statconn-static_500ms1h39b_i90r110_20211023-024711",
    "500ms1h39b_i90r110-4": "exp_putnon_statconn-static_500ms1h39b_i90r110/exp_putnon_statconn-static_500ms1h39b_i90r110_20211021-103147",
    "500ms1h39b_i490r510-0": "exp_putnon_statconn-static_500ms1h39b_i490r510/exp_putnon_statconn-static_500ms1h39b_i490r510_20211021-114020",
    "500ms1h39b_i490r510-1": "exp_putnon_statconn-static_500ms1h39b_i490r510/exp_putnon_statconn-static_500ms1h39b_i490r510_20211023-035544",
    "500ms1h39b_i490r510-2": "exp_putnon_statconn-static_500ms1h39b_i490r510/exp_putnon_statconn-static_500ms1h39b_i490r510_20211018-080454",
    "500ms1h39b_i490r510-3": "exp_putnon_statconn-static_500ms1h39b_i490r510/exp_putnon_statconn-static_500ms1h39b_i490r510_20210924-085704",
    "500ms1h39b_i490r510-4": "exp_putnon_statconn-static_500ms1h39b_i490r510/exp_putnon_statconn-static_500ms1h39b_i490r510_20211026-004119",
    "1s1h39b_i25-2": "exp_putnon_statconn-static_1s1h39b_i25/exp_putnon_statconn-static_1s1h39b_i25_20201201-085319",
    "1s1h39b_i25-6": "exp_putnon_statconn-static_1s1h39b_i25/exp_putnon_statconn-static_1s1h39b_i25_20201202-085206",
    "1s1h39b_i25-8": "exp_putnon_statconn-static_1s1h39b_i25/exp_putnon_statconn-static_1s1h39b_i25_20201202-085206",
    "1s1h39b_i25-9": "exp_putnon_statconn-static_1s1h39b_i25/exp_putnon_statconn-static_1s1h39b_i25_20211018-091330",
    "1s1h39b_i25-10": "exp_putnon_statconn-static_1s1h39b_i25/exp_putnon_statconn-static_1s1h39b_i25_20210924-100553",
    "1s1h39b_i50-0": "exp_putnon_statconn-static_1s1h39b_i50/exp_putnon_statconn-static_1s1h39b_i50_20211006-092319",
    "1s1h39b_i50-1": "exp_putnon_statconn-static_1s1h39b_i50/exp_putnon_statconn-static_1s1h39b_i50_20211006-103617",
    "1s1h39b_i50-2": "exp_putnon_statconn-static_1s1h39b_i50/exp_putnon_statconn-static_1s1h39b_i50_20211018-102204",
    "1s1h39b_i50-3": "exp_putnon_statconn-static_1s1h39b_i50/exp_putnon_statconn-static_1s1h39b_i50_20210924-111429",
    "1s1h39b_i50-4": "exp_putnon_statconn-static_1s1h39b_i50/exp_putnon_statconn-static_1s1h39b_i50_20201201-101056",
    "1s1h39b_i75-0": "exp_putnon_statconn-static_1s1h39b_i75/exp_putnon_statconn-static_1s1h39b_i75_20211018-113040",
    "1s1h39b_i75-1": "exp_putnon_statconn-static_1s1h39b_i75/exp_putnon_statconn-static_1s1h39b_i75_20211013-235030",
    "1s1h39b_i75-2": "exp_putnon_statconn-static_1s1h39b_i75/exp_putnon_statconn-static_1s1h39b_i75_20201201-112834",
    "1s1h39b_i75-3": "exp_putnon_statconn-static_1s1h39b_i75/exp_putnon_statconn-static_1s1h39b_i75_20211004-101127",
    "1s1h39b_i75-7": "exp_putnon_statconn-static_1s1h39b_i75/exp_putnon_statconn-static_1s1h39b_i75_20211013-132854",
    "1s1h39b_i100-1": "exp_putnon_statconn-static_1s1h39b_i100/exp_putnon_statconn-static_1s1h39b_i100_20201216-092808",
    "1s1h39b_i100-5": "exp_putnon_statconn-static_1s1h39b_i100/exp_putnon_statconn-static_1s1h39b_i100_20201201-124611",
    "1s1h39b_i100-7": "exp_putnon_statconn-static_1s1h39b_i100/exp_putnon_statconn-static_1s1h39b_i100_20211018-123916",
    "1s1h39b_i100-8": "exp_putnon_statconn-static_1s1h39b_i100/exp_putnon_statconn-static_1s1h39b_i100_20210924-133306",
    "1s1h39b_i100-9": "exp_putnon_statconn-static_1s1h39b_i100/exp_putnon_statconn-static_1s1h39b_i100_20201216-110053",
    "1s1h39b_i500-0": "exp_putnon_statconn-static_1s1h39b_i500/exp_putnon_statconn-static_1s1h39b_i500_20201125-064455",
    "1s1h39b_i500-1": "exp_putnon_statconn-static_1s1h39b_i500/exp_putnon_statconn-static_1s1h39b_i500_20201201-152126",
    "1s1h39b_i500-2": "exp_putnon_statconn-static_1s1h39b_i500/exp_putnon_statconn-static_1s1h39b_i500_20211018-134754",
    "1s1h39b_i500-3": "exp_putnon_statconn-static_1s1h39b_i500/exp_putnon_statconn-static_1s1h39b_i500_20210924-144153",
    "1s1h39b_i500-4": "exp_putnon_statconn-static_1s1h39b_i500/exp_putnon_statconn-static_1s1h39b_i500_20201201-152126",
    "1s1h39b_i15r35-0": "exp_putnon_statconn-static_1s1h39b_i15r35/exp_putnon_statconn-static_1s1h39b_i15r35_20210924-155028",
    "1s1h39b_i15r35-1": "exp_putnon_statconn-static_1s1h39b_i15r35/exp_putnon_statconn-static_1s1h39b_i15r35_20211018-145629",
    "1s1h39b_i15r35-2": "exp_putnon_statconn-static_1s1h39b_i15r35/exp_putnon_statconn-static_1s1h39b_i15r35_20211006-114452",
    "1s1h39b_i15r35-3": "exp_putnon_statconn-static_1s1h39b_i15r35/exp_putnon_statconn-static_1s1h39b_i15r35_20211006-125328",
    "1s1h39b_i15r35-4": "exp_putnon_statconn-static_1s1h39b_i15r35/exp_putnon_statconn-static_1s1h39b_i15r35_20211023-050420",
    "1s1h39b_i40r60-0": "exp_putnon_statconn-static_1s1h39b_i40r60/exp_putnon_statconn-static_1s1h39b_i40r60_20211006-140208",
    "1s1h39b_i40r60-1": "exp_putnon_statconn-static_1s1h39b_i40r60/exp_putnon_statconn-static_1s1h39b_i40r60_20211006-151049",
    "1s1h39b_i40r60-2": "exp_putnon_statconn-static_1s1h39b_i40r60/exp_putnon_statconn-static_1s1h39b_i40r60_20211018-160505",
    "1s1h39b_i40r60-3": "exp_putnon_statconn-static_1s1h39b_i40r60/exp_putnon_statconn-static_1s1h39b_i40r60_20210924-165914",
    "1s1h39b_i40r60-5": "exp_putnon_statconn-static_1s1h39b_i40r60/exp_putnon_statconn-static_1s1h39b_i40r60_20201128-022306",
    "1s1h39b_i65r85-0": "exp_putnon_statconn-static_1s1h39b_i65r85/exp_putnon_statconn-static_1s1h39b_i65r85_20211023-061255",
    "1s1h39b_i65r85-1": "exp_putnon_statconn-static_1s1h39b_i65r85/exp_putnon_statconn-static_1s1h39b_i65r85_20210924-180749",
    "1s1h39b_i65r85-2": "exp_putnon_statconn-static_1s1h39b_i65r85/exp_putnon_statconn-static_1s1h39b_i65r85_20211018-171350",
    "1s1h39b_i65r85-3": "exp_putnon_statconn-static_1s1h39b_i65r85/exp_putnon_statconn-static_1s1h39b_i65r85_20210303-132319",
    "1s1h39b_i65r85-4": "exp_putnon_statconn-static_1s1h39b_i65r85/exp_putnon_statconn-static_1s1h39b_i65r85_20201126-022900",
    "1s1h39b_i90r110-0": "exp_putnon_statconn-static_1s1h39b_i90r110/exp_putnon_statconn-static_1s1h39b_i90r110_20210827-105702",
    "1s1h39b_i90r110-2": "exp_putnon_statconn-static_1s1h39b_i90r110/exp_putnon_statconn-static_1s1h39b_i90r110_20210908-165046",
    "1s1h39b_i90r110-6": "exp_putnon_statconn-static_1s1h39b_i90r110/exp_putnon_statconn-static_1s1h39b_i90r110_20210909-114216",
    "1s1h39b_i90r110-7": "exp_putnon_statconn-static_1s1h39b_i90r110/exp_putnon_statconn-static_1s1h39b_i90r110_20210924-191627",
    "1s1h39b_i90r110-8": "exp_putnon_statconn-static_1s1h39b_i90r110/exp_putnon_statconn-static_1s1h39b_i90r110_20211018-182337",
    "1s1h39b_i490r510-1": "exp_putnon_statconn-static_1s1h39b_i490r510/exp_putnon_statconn-static_1s1h39b_i490r510_20201128-073341",
    "1s1h39b_i490r510-2": "exp_putnon_statconn-static_1s1h39b_i490r510/exp_putnon_statconn-static_1s1h39b_i490r510_20210924-202515",
    "1s1h39b_i490r510-3": "exp_putnon_statconn-static_1s1h39b_i490r510/exp_putnon_statconn-static_1s1h39b_i490r510_20211018-193211",
    "1s1h39b_i490r510-4": "exp_putnon_statconn-static_1s1h39b_i490r510/exp_putnon_statconn-static_1s1h39b_i490r510_20211006-172818",
    "1s1h39b_i490r510-5": "exp_putnon_statconn-static_1s1h39b_i490r510/exp_putnon_statconn-static_1s1h39b_i490r510_20211006-161941",
    "5s1h39b_i25-0": "exp_putnon_statconn-static_5s1h39b_i25/exp_putnon_statconn-static_5s1h39b_i25_20211023-072129",
    "5s1h39b_i25-1": "exp_putnon_statconn-static_5s1h39b_i25/exp_putnon_statconn-static_5s1h39b_i25_20211021-125004",
    "5s1h39b_i25-2": "exp_putnon_statconn-static_5s1h39b_i25/exp_putnon_statconn-static_5s1h39b_i25_20211018-204046",
    "5s1h39b_i25-3": "exp_putnon_statconn-static_5s1h39b_i25/exp_putnon_statconn-static_5s1h39b_i25_20210924-213350",
    "5s1h39b_i25-4": "exp_putnon_statconn-static_5s1h39b_i25/exp_putnon_statconn-static_5s1h39b_i25_20211026-014956",
    "5s1h39b_i50-0": "exp_putnon_statconn-static_5s1h39b_i50/exp_putnon_statconn-static_5s1h39b_i50_20211026-025834",
    "5s1h39b_i50-1": "exp_putnon_statconn-static_5s1h39b_i50/exp_putnon_statconn-static_5s1h39b_i50_20210924-224227",
    "5s1h39b_i50-2": "exp_putnon_statconn-static_5s1h39b_i50/exp_putnon_statconn-static_5s1h39b_i50_20211023-083005",
    "5s1h39b_i50-3": "exp_putnon_statconn-static_5s1h39b_i50/exp_putnon_statconn-static_5s1h39b_i50_20211018-214932",
    "5s1h39b_i50-4": "exp_putnon_statconn-static_5s1h39b_i50/exp_putnon_statconn-static_5s1h39b_i50_20211021-135937",
    "5s1h39b_i75-0": "exp_putnon_statconn-static_5s1h39b_i75/exp_putnon_statconn-static_5s1h39b_i75_20210924-235114",
    "5s1h39b_i75-1": "exp_putnon_statconn-static_5s1h39b_i75/exp_putnon_statconn-static_5s1h39b_i75_20211018-225809",
    "5s1h39b_i75-2": "exp_putnon_statconn-static_5s1h39b_i75/exp_putnon_statconn-static_5s1h39b_i75_20211026-040709",
    "5s1h39b_i75-3": "exp_putnon_statconn-static_5s1h39b_i75/exp_putnon_statconn-static_5s1h39b_i75_20211021-150810",
    "5s1h39b_i75-4": "exp_putnon_statconn-static_5s1h39b_i75/exp_putnon_statconn-static_5s1h39b_i75_20211023-093938",
    "5s1h39b_i100-0": "exp_putnon_statconn-static_5s1h39b_i100/exp_putnon_statconn-static_5s1h39b_i100_20210925-005952",
    "5s1h39b_i100-1": "exp_putnon_statconn-static_5s1h39b_i100/exp_putnon_statconn-static_5s1h39b_i100_20211019-021249",
    "5s1h39b_i100-2": "exp_putnon_statconn-static_5s1h39b_i100/exp_putnon_statconn-static_5s1h39b_i100_20211023-104819",
    "5s1h39b_i100-3": "exp_putnon_statconn-static_5s1h39b_i100/exp_putnon_statconn-static_5s1h39b_i100_20211021-161648",
    "5s1h39b_i100-4": "exp_putnon_statconn-static_5s1h39b_i100/exp_putnon_statconn-static_5s1h39b_i100_20211026-051544",
    "5s1h39b_i500-0": "exp_putnon_statconn-static_5s1h39b_i500/exp_putnon_statconn-static_5s1h39b_i500_20211023-115652",
    "5s1h39b_i500-1": "exp_putnon_statconn-static_5s1h39b_i500/exp_putnon_statconn-static_5s1h39b_i500_20211021-172524",
    "5s1h39b_i500-2": "exp_putnon_statconn-static_5s1h39b_i500/exp_putnon_statconn-static_5s1h39b_i500_20211026-062419",
    "5s1h39b_i500-3": "exp_putnon_statconn-static_5s1h39b_i500/exp_putnon_statconn-static_5s1h39b_i500_20210925-020842",
    "5s1h39b_i500-4": "exp_putnon_statconn-static_5s1h39b_i500/exp_putnon_statconn-static_5s1h39b_i500_20211019-032230",
    "5s1h39b_i15r35-0": "exp_putnon_statconn-static_5s1h39b_i15r35/exp_putnon_statconn-static_5s1h39b_i15r35_20211023-130526",
    "5s1h39b_i15r35-1": "exp_putnon_statconn-static_5s1h39b_i15r35/exp_putnon_statconn-static_5s1h39b_i15r35_20211026-073255",
    "5s1h39b_i15r35-2": "exp_putnon_statconn-static_5s1h39b_i15r35/exp_putnon_statconn-static_5s1h39b_i15r35_20211021-183358",
    "5s1h39b_i15r35-3": "exp_putnon_statconn-static_5s1h39b_i15r35/exp_putnon_statconn-static_5s1h39b_i15r35_20210925-031717",
    "5s1h39b_i15r35-4": "exp_putnon_statconn-static_5s1h39b_i15r35/exp_putnon_statconn-static_5s1h39b_i15r35_20211019-043106",
    "5s1h39b_i40r60-0": "exp_putnon_statconn-static_5s1h39b_i40r60/exp_putnon_statconn-static_5s1h39b_i40r60_20211019-053942",
    "5s1h39b_i40r60-1": "exp_putnon_statconn-static_5s1h39b_i40r60/exp_putnon_statconn-static_5s1h39b_i40r60_20210925-042553",
    "5s1h39b_i40r60-2": "exp_putnon_statconn-static_5s1h39b_i40r60/exp_putnon_statconn-static_5s1h39b_i40r60_20211026-084129",
    "5s1h39b_i40r60-3": "exp_putnon_statconn-static_5s1h39b_i40r60/exp_putnon_statconn-static_5s1h39b_i40r60_20211021-194232",
    "5s1h39b_i40r60-4": "exp_putnon_statconn-static_5s1h39b_i40r60/exp_putnon_statconn-static_5s1h39b_i40r60_20211023-141401",
    "5s1h39b_i65r85-0": "exp_putnon_statconn-static_5s1h39b_i65r85/exp_putnon_statconn-static_5s1h39b_i65r85_20211026-095106",
    "5s1h39b_i65r85-1": "exp_putnon_statconn-static_5s1h39b_i65r85/exp_putnon_statconn-static_5s1h39b_i65r85_20211023-152235",
    "5s1h39b_i65r85-2": "exp_putnon_statconn-static_5s1h39b_i65r85/exp_putnon_statconn-static_5s1h39b_i65r85_20211019-064921",
    "5s1h39b_i65r85-3": "exp_putnon_statconn-static_5s1h39b_i65r85/exp_putnon_statconn-static_5s1h39b_i65r85_20210925-053430",
    "5s1h39b_i65r85-4": "exp_putnon_statconn-static_5s1h39b_i65r85/exp_putnon_statconn-static_5s1h39b_i65r85_20211021-205107",
    "5s1h39b_i90r110-0": "exp_putnon_statconn-static_5s1h39b_i90r110/exp_putnon_statconn-static_5s1h39b_i90r110_20211026-105943",
    "5s1h39b_i90r110-1": "exp_putnon_statconn-static_5s1h39b_i90r110/exp_putnon_statconn-static_5s1h39b_i90r110_20211023-163112",
    "5s1h39b_i90r110-2": "exp_putnon_statconn-static_5s1h39b_i90r110/exp_putnon_statconn-static_5s1h39b_i90r110_20211019-075757",
    "5s1h39b_i90r110-3": "exp_putnon_statconn-static_5s1h39b_i90r110/exp_putnon_statconn-static_5s1h39b_i90r110_20210925-064310",
    "5s1h39b_i90r110-4": "exp_putnon_statconn-static_5s1h39b_i90r110/exp_putnon_statconn-static_5s1h39b_i90r110_20211021-220041",
    "5s1h39b_i490r510-0": "exp_putnon_statconn-static_5s1h39b_i490r510/exp_putnon_statconn-static_5s1h39b_i490r510_20211023-173948",
    "5s1h39b_i490r510-1": "exp_putnon_statconn-static_5s1h39b_i490r510/exp_putnon_statconn-static_5s1h39b_i490r510_20210925-075146",
    "5s1h39b_i490r510-2": "exp_putnon_statconn-static_5s1h39b_i490r510/exp_putnon_statconn-static_5s1h39b_i490r510_20211026-120922",
    "5s1h39b_i490r510-3": "exp_putnon_statconn-static_5s1h39b_i490r510/exp_putnon_statconn-static_5s1h39b_i490r510_20211021-230915",
    "5s1h39b_i490r510-4": "exp_putnon_statconn-static_5s1h39b_i490r510/exp_putnon_statconn-static_5s1h39b_i490r510_20211019-090631",
    "10s1h39b_i25-0": "exp_putnon_statconn-static_10s1h39b_i25/exp_putnon_statconn-static_10s1h39b_i25_20211023-184823",
    "10s1h39b_i25-1": "exp_putnon_statconn-static_10s1h39b_i25/exp_putnon_statconn-static_10s1h39b_i25_20211026-131804",
    "10s1h39b_i25-2": "exp_putnon_statconn-static_10s1h39b_i25/exp_putnon_statconn-static_10s1h39b_i25_20211028-132937",
    "10s1h39b_i25-3": "exp_putnon_statconn-static_10s1h39b_i25/exp_putnon_statconn-static_10s1h39b_i25_20211027-132740",
    "10s1h39b_i25-4": "exp_putnon_statconn-static_10s1h39b_i25/exp_putnon_statconn-static_10s1h39b_i25_20210927-130542",
    "10s1h39b_i50-0": "exp_putnon_statconn-static_10s1h39b_i50/exp_putnon_statconn-static_10s1h39b_i50_20210927-143808",
    "10s1h39b_i50-1": "exp_putnon_statconn-static_10s1h39b_i50/exp_putnon_statconn-static_10s1h39b_i50_20211027-143624",
    "10s1h39b_i50-2": "exp_putnon_statconn-static_10s1h39b_i50/exp_putnon_statconn-static_10s1h39b_i50_20211028-143810",
    "10s1h39b_i50-3": "exp_putnon_statconn-static_10s1h39b_i50/exp_putnon_statconn-static_10s1h39b_i50_20211026-142638",
    "10s1h39b_i50-4": "exp_putnon_statconn-static_10s1h39b_i50/exp_putnon_statconn-static_10s1h39b_i50_20211023-195659",
    "10s1h39b_i75-0": "exp_putnon_statconn-static_10s1h39b_i75/exp_putnon_statconn-static_10s1h39b_i75_20211028-154646",
    "10s1h39b_i75-1": "exp_putnon_statconn-static_10s1h39b_i75/exp_putnon_statconn-static_10s1h39b_i75_20211027-154459",
    "10s1h39b_i75-2": "exp_putnon_statconn-static_10s1h39b_i75/exp_putnon_statconn-static_10s1h39b_i75_20210927-154643",
    "10s1h39b_i75-3": "exp_putnon_statconn-static_10s1h39b_i75/exp_putnon_statconn-static_10s1h39b_i75_20211023-210535",
    "10s1h39b_i75-4": "exp_putnon_statconn-static_10s1h39b_i75/exp_putnon_statconn-static_10s1h39b_i75_20211026-153512",
    "10s1h39b_i100-0": "exp_putnon_statconn-static_10s1h39b_i100/exp_putnon_statconn-static_10s1h39b_i100_20211023-221410",
    "10s1h39b_i100-1": "exp_putnon_statconn-static_10s1h39b_i100/exp_putnon_statconn-static_10s1h39b_i100_20211027-165335",
    "10s1h39b_i100-2": "exp_putnon_statconn-static_10s1h39b_i100/exp_putnon_statconn-static_10s1h39b_i100_20210927-165623",
    "10s1h39b_i100-3": "exp_putnon_statconn-static_10s1h39b_i100/exp_putnon_statconn-static_10s1h39b_i100_20211026-164346",
    "10s1h39b_i100-4": "exp_putnon_statconn-static_10s1h39b_i100/exp_putnon_statconn-static_10s1h39b_i100_20211028-185249",
    "10s1h39b_i500-0": "exp_putnon_statconn-static_10s1h39b_i500/exp_putnon_statconn-static_10s1h39b_i500_20210927-180458",
    "10s1h39b_i500-1": "exp_putnon_statconn-static_10s1h39b_i500/exp_putnon_statconn-static_10s1h39b_i500_20211023-232244",
    "10s1h39b_i500-2": "exp_putnon_statconn-static_10s1h39b_i500/exp_putnon_statconn-static_10s1h39b_i500_20211026-175221",
    "10s1h39b_i500-3": "exp_putnon_statconn-static_10s1h39b_i500/exp_putnon_statconn-static_10s1h39b_i500_20211028-200125",
    "10s1h39b_i500-4": "exp_putnon_statconn-static_10s1h39b_i500/exp_putnon_statconn-static_10s1h39b_i500_20211027-180212",
    "10s1h39b_i15r35-0": "exp_putnon_statconn-static_10s1h39b_i15r35/exp_putnon_statconn-static_10s1h39b_i15r35_20211024-003120",
    "10s1h39b_i15r35-1": "exp_putnon_statconn-static_10s1h39b_i15r35/exp_putnon_statconn-static_10s1h39b_i15r35_20210928-173511",
    "10s1h39b_i15r35-2": "exp_putnon_statconn-static_10s1h39b_i15r35/exp_putnon_statconn-static_10s1h39b_i15r35_20210927-191438",
    "10s1h39b_i15r35-3": "exp_putnon_statconn-static_10s1h39b_i15r35/exp_putnon_statconn-static_10s1h39b_i15r35_20210928-151639",
    "10s1h39b_i15r35-4": "exp_putnon_statconn-static_10s1h39b_i15r35/exp_putnon_statconn-static_10s1h39b_i15r35_20210928-195250",
    "10s1h39b_i40r60-0": "exp_putnon_statconn-static_10s1h39b_i40r60/exp_putnon_statconn-static_10s1h39b_i40r60_20210927-202313",
    "10s1h39b_i40r60-1": "exp_putnon_statconn-static_10s1h39b_i40r60/exp_putnon_statconn-static_10s1h39b_i40r60_20211028-211000",
    "10s1h39b_i40r60-2": "exp_putnon_statconn-static_10s1h39b_i40r60/exp_putnon_statconn-static_10s1h39b_i40r60_20211026-190056",
    "10s1h39b_i40r60-3": "exp_putnon_statconn-static_10s1h39b_i40r60/exp_putnon_statconn-static_10s1h39b_i40r60_20211027-191050",
    "10s1h39b_i40r60-4": "exp_putnon_statconn-static_10s1h39b_i40r60/exp_putnon_statconn-static_10s1h39b_i40r60_20211024-013955",
    "10s1h39b_i65r85-0": "exp_putnon_statconn-static_10s1h39b_i65r85/exp_putnon_statconn-static_10s1h39b_i65r85_20210927-213158",
    "10s1h39b_i65r85-1": "exp_putnon_statconn-static_10s1h39b_i65r85/exp_putnon_statconn-static_10s1h39b_i65r85_20211027-201924",
    "10s1h39b_i65r85-2": "exp_putnon_statconn-static_10s1h39b_i65r85/exp_putnon_statconn-static_10s1h39b_i65r85_20211028-221836",
    "10s1h39b_i65r85-3": "exp_putnon_statconn-static_10s1h39b_i65r85/exp_putnon_statconn-static_10s1h39b_i65r85_20211024-024835",
    "10s1h39b_i65r85-4": "exp_putnon_statconn-static_10s1h39b_i65r85/exp_putnon_statconn-static_10s1h39b_i65r85_20211026-200930",
    "10s1h39b_i90r110-0": "exp_putnon_statconn-static_10s1h39b_i90r110/exp_putnon_statconn-static_10s1h39b_i90r110_20211027-212758",
    "10s1h39b_i90r110-1": "exp_putnon_statconn-static_10s1h39b_i90r110/exp_putnon_statconn-static_10s1h39b_i90r110_20211024-035710",
    "10s1h39b_i90r110-2": "exp_putnon_statconn-static_10s1h39b_i90r110/exp_putnon_statconn-static_10s1h39b_i90r110_20211026-212111",
    "10s1h39b_i90r110-3": "exp_putnon_statconn-static_10s1h39b_i90r110/exp_putnon_statconn-static_10s1h39b_i90r110_20210927-224047",
    "10s1h39b_i90r110-4": "exp_putnon_statconn-static_10s1h39b_i90r110/exp_putnon_statconn-static_10s1h39b_i90r110_20211028-232712",
    "10s1h39b_i490r510-0": "exp_putnon_statconn-static_10s1h39b_i490r510/exp_putnon_statconn-static_10s1h39b_i490r510_20210927-234922",
    "10s1h39b_i490r510-1": "exp_putnon_statconn-static_10s1h39b_i490r510/exp_putnon_statconn-static_10s1h39b_i490r510_20211029-003551",
    "10s1h39b_i490r510-2": "exp_putnon_statconn-static_10s1h39b_i490r510/exp_putnon_statconn-static_10s1h39b_i490r510_20211024-050544",
    "10s1h39b_i490r510-3": "exp_putnon_statconn-static_10s1h39b_i490r510/exp_putnon_statconn-static_10s1h39b_i490r510_20211027-223644",
    "10s1h39b_i490r510-4": "exp_putnon_statconn-static_10s1h39b_i490r510/exp_putnon_statconn-static_10s1h39b_i490r510_20211026-223053",
    "30s1h39b_i25-0": "exp_putnon_statconn-static_30s1h39b_i25/exp_putnon_statconn-static_30s1h39b_i25_20210928-005756",
    "30s1h39b_i25-1": "exp_putnon_statconn-static_30s1h39b_i25/exp_putnon_statconn-static_30s1h39b_i25_20211027-234519",
    "30s1h39b_i25-2": "exp_putnon_statconn-static_30s1h39b_i25/exp_putnon_statconn-static_30s1h39b_i25_20211026-233929",
    "30s1h39b_i25-3": "exp_putnon_statconn-static_30s1h39b_i25/exp_putnon_statconn-static_30s1h39b_i25_20211024-061418",
    "30s1h39b_i25-4": "exp_putnon_statconn-static_30s1h39b_i25/exp_putnon_statconn-static_30s1h39b_i25_20211029-014428",
    "30s1h39b_i50-0": "exp_putnon_statconn-static_30s1h39b_i50/exp_putnon_statconn-static_30s1h39b_i50_20211027-004803",
    "30s1h39b_i50-1": "exp_putnon_statconn-static_30s1h39b_i50/exp_putnon_statconn-static_30s1h39b_i50_20211024-072253",
    "30s1h39b_i50-2": "exp_putnon_statconn-static_30s1h39b_i50/exp_putnon_statconn-static_30s1h39b_i50_20210928-020630",
    "30s1h39b_i50-3": "exp_putnon_statconn-static_30s1h39b_i50/exp_putnon_statconn-static_30s1h39b_i50_20211028-005509",
    "30s1h39b_i50-4": "exp_putnon_statconn-static_30s1h39b_i50/exp_putnon_statconn-static_30s1h39b_i50_20211029-031531",
    "30s1h39b_i75-0": "exp_putnon_statconn-static_30s1h39b_i75/exp_putnon_statconn-static_30s1h39b_i75_20210928-031515",
    "30s1h39b_i75-1": "exp_putnon_statconn-static_30s1h39b_i75/exp_putnon_statconn-static_30s1h39b_i75_20211027-015637",
    "30s1h39b_i75-2": "exp_putnon_statconn-static_30s1h39b_i75/exp_putnon_statconn-static_30s1h39b_i75_20211028-020343",
    "30s1h39b_i75-3": "exp_putnon_statconn-static_30s1h39b_i75/exp_putnon_statconn-static_30s1h39b_i75_20211029-042405",
    "30s1h39b_i75-4": "exp_putnon_statconn-static_30s1h39b_i75/exp_putnon_statconn-static_30s1h39b_i75_20211024-083128",
    "30s1h39b_i100-0": "exp_putnon_statconn-static_30s1h39b_i100/exp_putnon_statconn-static_30s1h39b_i100_20211027-030511",
    "30s1h39b_i100-1": "exp_putnon_statconn-static_30s1h39b_i100/exp_putnon_statconn-static_30s1h39b_i100_20211024-094001",
    "30s1h39b_i100-2": "exp_putnon_statconn-static_30s1h39b_i100/exp_putnon_statconn-static_30s1h39b_i100_20210928-042352",
    "30s1h39b_i100-3": "exp_putnon_statconn-static_30s1h39b_i100/exp_putnon_statconn-static_30s1h39b_i100_20211028-031219",
    "30s1h39b_i100-4": "exp_putnon_statconn-static_30s1h39b_i100/exp_putnon_statconn-static_30s1h39b_i100_20211029-053239",
    "30s1h39b_i500-0": "exp_putnon_statconn-static_30s1h39b_i500/exp_putnon_statconn-static_30s1h39b_i500_20211024-104837",
    "30s1h39b_i500-1": "exp_putnon_statconn-static_30s1h39b_i500/exp_putnon_statconn-static_30s1h39b_i500_20210928-053233",
    "30s1h39b_i500-2": "exp_putnon_statconn-static_30s1h39b_i500/exp_putnon_statconn-static_30s1h39b_i500_20211028-042055",
    "30s1h39b_i500-3": "exp_putnon_statconn-static_30s1h39b_i500/exp_putnon_statconn-static_30s1h39b_i500_20211027-041345",
    "30s1h39b_i500-4": "exp_putnon_statconn-static_30s1h39b_i500/exp_putnon_statconn-static_30s1h39b_i500_20211029-064114",
    "30s1h39b_i15r35-0": "exp_putnon_statconn-static_30s1h39b_i15r35/exp_putnon_statconn-static_30s1h39b_i15r35_20211024-115712",
    "30s1h39b_i15r35-1": "exp_putnon_statconn-static_30s1h39b_i15r35/exp_putnon_statconn-static_30s1h39b_i15r35_20210928-064216",
    "30s1h39b_i15r35-2": "exp_putnon_statconn-static_30s1h39b_i15r35/exp_putnon_statconn-static_30s1h39b_i15r35_20211028-052930",
    "30s1h39b_i15r35-3": "exp_putnon_statconn-static_30s1h39b_i15r35/exp_putnon_statconn-static_30s1h39b_i15r35_20211029-074950",
    "30s1h39b_i15r35-4": "exp_putnon_statconn-static_30s1h39b_i15r35/exp_putnon_statconn-static_30s1h39b_i15r35_20211027-052221",
    "30s1h39b_i40r60-0": "exp_putnon_statconn-static_30s1h39b_i40r60/exp_putnon_statconn-static_30s1h39b_i40r60_20210928-075051",
    "30s1h39b_i40r60-1": "exp_putnon_statconn-static_30s1h39b_i40r60/exp_putnon_statconn-static_30s1h39b_i40r60_20211028-063810",
    "30s1h39b_i40r60-2": "exp_putnon_statconn-static_30s1h39b_i40r60/exp_putnon_statconn-static_30s1h39b_i40r60_20211029-085824",
    "30s1h39b_i40r60-3": "exp_putnon_statconn-static_30s1h39b_i40r60/exp_putnon_statconn-static_30s1h39b_i40r60_20211027-063057",
    "30s1h39b_i40r60-4": "exp_putnon_statconn-static_30s1h39b_i40r60/exp_putnon_statconn-static_30s1h39b_i40r60_20211024-130546",
    "30s1h39b_i65r85-0": "exp_putnon_statconn-static_30s1h39b_i65r85/exp_putnon_statconn-static_30s1h39b_i65r85_20210928-085937",
    "30s1h39b_i65r85-1": "exp_putnon_statconn-static_30s1h39b_i65r85/exp_putnon_statconn-static_30s1h39b_i65r85_20211027-073931",
    "30s1h39b_i65r85-2": "exp_putnon_statconn-static_30s1h39b_i65r85/exp_putnon_statconn-static_30s1h39b_i65r85_20211024-141420",
    "30s1h39b_i65r85-3": "exp_putnon_statconn-static_30s1h39b_i65r85/exp_putnon_statconn-static_30s1h39b_i65r85_20211029-100659",
    "30s1h39b_i65r85-4": "exp_putnon_statconn-static_30s1h39b_i65r85/exp_putnon_statconn-static_30s1h39b_i65r85_20211028-074644",
    "30s1h39b_i90r110-0": "exp_putnon_statconn-static_30s1h39b_i90r110/exp_putnon_statconn-static_30s1h39b_i90r110_20211028-085520",
    "30s1h39b_i90r110-1": "exp_putnon_statconn-static_30s1h39b_i90r110/exp_putnon_statconn-static_30s1h39b_i90r110_20210928-100811",
    "30s1h39b_i90r110-2": "exp_putnon_statconn-static_30s1h39b_i90r110/exp_putnon_statconn-static_30s1h39b_i90r110_20211024-152353",
    "30s1h39b_i90r110-3": "exp_putnon_statconn-static_30s1h39b_i90r110/exp_putnon_statconn-static_30s1h39b_i90r110_20211029-111537",
    "30s1h39b_i90r110-4": "exp_putnon_statconn-static_30s1h39b_i90r110/exp_putnon_statconn-static_30s1h39b_i90r110_20211027-084805",
    "30s1h39b_i490r510-0": "exp_putnon_statconn-static_30s1h39b_i490r510/exp_putnon_statconn-static_30s1h39b_i490r510_20211024-163434",
    "30s1h39b_i490r510-1": "exp_putnon_statconn-static_30s1h39b_i490r510/exp_putnon_statconn-static_30s1h39b_i490r510_20211027-095928",
    "30s1h39b_i490r510-2": "exp_putnon_statconn-static_30s1h39b_i490r510/exp_putnon_statconn-static_30s1h39b_i490r510_20211029-122413",
    "30s1h39b_i490r510-3": "exp_putnon_statconn-static_30s1h39b_i490r510/exp_putnon_statconn-static_30s1h39b_i490r510_20210928-111649",
    "30s1h39b_i490r510-4": "exp_putnon_statconn-static_30s1h39b_i490r510/exp_putnon_statconn-static_30s1h39b_i490r510_20211028-100355",
}

ORDER = [
    "i25",
    "i50",
    "i75",
    "i100",
    "i500",
    "i15r35",
    "i40r60",
    "i65r85",
    "i90r110",
    "i490r510",
]

LOGPATH = "/home/hauke/fucloud/ipble_measurements/logs"

TICKLBLSIZE = 9
LEGENDSIZE = 9
AXISLBLSIZE = 11


class Results(Ana):
    def __init__(self, logfile):
        super().__init__(logfile)

        self.expstats = Expstats(self)
        self.llstats = LLStats(self)
        self.topo = Topo(self)

        self.parse_log(self.update)

        self.expstats.finish()
        self.llstats.finish()
        self.topo.finish()

        self.write_overview(self.llstats, self.expstats, self.topo)


    def update(self, time, node, line):
        self.expstats.update(time, node, line)
        self.llstats.update(time, node, line)
        self.topo.update(time, node, line)



class Fig(Expbase):
    def __init__(self):
        super().__init__()

        self.raw = {}

        base = os.path.splitext(os.path.basename(__file__))[0]
        self.out = os.path.join(self.basedir, "results/figs", f'{base}')
        print(f'output:  {self.out}')

        for name, src in SRC.items():
            file = os.path.join(self.plotdir, f'{src}_overview.json')

            if not os.path.isfile(file):
                print(f'generating {file}')
                Results(os.path.join(self.logdir, f'{src}.dump'))

            print(f'loading {file}')
            self.raw[name] = self.load_json(file)


        # for name in self.raw:
        #     print(f'{name}: conloss {self.raw[name]["reconns"]}')



    def _prettyprint_conn_itvl(self, pitvl_str, citvl_str):
        res = ""
        if "ms" in pitvl_str:
            res += f'{float(pitvl_str[:-2]) / 1000:.1f}'
        else:
            res += f'{int(pitvl_str[:-1])}'

        res += "-"

        if "r" in citvl_str:
            tmp = citvl_str[1:].split("r")
            res += f'[{tmp[0]},{tmp[1]}]'
        else:
            res += f'{citvl_str[1:]}'

        return res

    def _get_itvl(self, name):
        tmp = name.split("-")
        tmp = tmp[0].split("_")
        return tmp[0][:-5], tmp[1]

    def _get_xlab(self, cfg):
        if "r" in cfg:
            tmp = cfg[1:].split("r")
            return f'[{tmp[0]}:{tmp[1]}]'
        else:
            return f'{cfg[1:]}'


    def create(self):

        data = {}

        for cfg in self.raw:
            pitvl, citvl = self._get_itvl(cfg)

            if pitvl not in data:
                data[pitvl] = {}
            if citvl not in data[pitvl]:
                data[pitvl][citvl] = {"reconns": [], "pdr_app": [], "pdr_ll": [], "latency": []}

            if self.raw[cfg]["pdr_ll"] < 0:
                sys.exit(f'INPUT error: {cfg} has broken ll_pdr: {self.raw[cfg]["pdr_ll"]}')

            data[pitvl][citvl]["reconns"].append(self.raw[cfg]["reconns"])
            data[pitvl][citvl]["pdr_app"].append(self.raw[cfg]["pdr_app"])
            data[pitvl][citvl]["pdr_ll"].append(self.raw[cfg]["pdr_ll"])
            # copy latencies, filter out too small values that were caused by iotlab tooling and
            # are not valid
            data[pitvl][citvl]["latency"] += [lat for lat in self.raw[cfg]["latency"]["latency_all"] if lat >= 0.01]

            # for s in ("avg", "min", "max"):
                # data[pitvl][citvl]["latency"].append(self.raw[cfg]["latency"][f'latency_{s}'])
            # data[pitvl][citvl]["latency"].append(self.raw[cfg]["latency"]["latency_avg"])


        # verify data
        for pitvl in data:
            print("#### PITVL", pitvl)
            for citvl in ORDER:
                print(f'--- CTIVL {citvl}, loss:{data[pitvl][citvl]["reconns"]} ll-pdr:{data[pitvl][citvl]["pdr_ll"]}')

        # sys.exit("VERIFY")


        fig, ax = plt.subplots(4, 6, sharex=True)
        fig.set_size_inches(12, 5)
        fig.set_figheight(12)

        titles = []
        latplot = []
        for col, pitvl in enumerate(data):
            titles.append(pitvl)
            y_reconns = []
            y_pdr_app = []
            y_pdr_ll = []
            y_lat = []
            for citvl in ORDER:
                y_reconns.append(data[pitvl][citvl]["reconns"])
                y_pdr_app.append(data[pitvl][citvl]["pdr_app"])
                y_pdr_ll.append(data[pitvl][citvl]["pdr_ll"])
                y_lat.append(data[pitvl][citvl]["latency"])

            ax[0][col].boxplot([[vv - 100 for vv in v] for v in y_pdr_ll], whis=[0, 100])
            ax[1][col].boxplot([[vv - 100 for vv in v] for v in y_pdr_app], whis=[0, 100])
            latp = ax[2][col].boxplot(y_lat, whis=[0, 100]) # flierprops={"markersize": 2})
            latplot.append(latp)
            ax[3][col].boxplot(y_reconns, whis=[0, 100])


        # scale axis and set axis labels


        ylogt = [-100, -50, -20, -10, -5, -2, -1, 0]
        ylogl = [f'{((t + 100) / 100):.2f}' for t in ylogt]
        print(titles)
        print(ylogl)

        yt = [
            # {
            #     "title": "LL PDR [0:1.0]",
            #     "t": [90, 95, 100],
            #     "l": [.9, .95, 1.0],
            #     "lim": [90, 102],
            # },
            {
                "title": "Link layer PDR [0:1.0]",
                "t": ylogt,
                "l": ylogl,
                "lim": [-100, 0.1],
                "scale": "symlog",
            },
            # {
            #     "title": "CoAP PDR [0:1.0]",
            #     "t": [98, 99, 100],
            #     "l": [.98, .99, 1.0],
            #     "lim": [98, 100.05],
            # },
            {
                "title": "CoAP PDR [0:1.0]",
                "t": ylogt,
                "l": ylogl,
                "lim": [-100, 0.1],
                "scale": "symlog",
            },
            # {
            #     "title": "Latency [s]",
            #     "t": [0, 5, 10, 15, 20, 25],
            #     "lim": [0, 27],
            # },
            {
                "title": "CoAP round-trip time [s]",
                "t": [0.01, .1, 1.0, 10, 60],
                "lim": [0.01, 60],
                "scale": "log",
            },
            {
                "title": "# of connection losses",
                "t": [0, 5, 10, 15, 20],
                "lim": [-1, 25],
            },
        ]

        xt = {
            "t": [i + 1 for i in range(len(ORDER))],
            "l": ORDER,
        }


        for row, ar in enumerate(ax):
            for col, a in enumerate(ar):
                if row == 0:
                    a.set_title(f'Producer Interval\n{titles[col]}')

                a.set_xticks(xt["t"])
                if row != len(ax) - 1:
                    a.set_xticklabels([])
                else:
                    a.set_xticklabels([self._get_xlab(l) for l in xt["l"]], rotation=90, size=TICKLBLSIZE)

                if "scale" in yt[row]:
                    a.set_yscale(yt[row]["scale"])
                a.set_ylim(yt[row]["lim"])
                a.set_yticks(yt[row]["t"])
                if col != 0:
                    a.set_yticklabels([])
                else:
                    a.set_ylabel(yt[row]["title"], size=AXISLBLSIZE)
                    if "l" in yt[row]:
                        a.set_yticklabels(yt[row]["l"], size=TICKLBLSIZE)
                    else:
                        a.set_yticklabels(yt[row]["t"], size=TICKLBLSIZE)

                a.axvspan(5.5, 10.5, facecolor='grey', alpha=0.2)

                a.yaxis.grid(True)
                # else:
                #     a.set_yticks(yt[col])
                #     if "l" in yt[col]:
                #         a.set_yticklabels(yt[col]["l"])
                #     else:
                #         print(yt[col]["t"])
                #         a.set_yticklabels(yt[col]["t"])

        # for p in latplot:
        #     for fly in p['fliers']:
        #         for i in range(len(fly)):
        #             box = fly[i] # this accesses the x and y vectors for the fliers for each box
        #             box.set_data([ [box.get_xdata()[0], box.get_xdata()[0]], [np.min(box.get_ydata()), np.max(box.get_ydata())]])

        # for p in latplot:
        #     for fly in p['fliers']:
        #         fdata = fly.get_data() # iterate through the Line2D objects for the fliers for each boxplot
        #         for box in fdata:
        #             box.set_data([[box.get_xdata()[0],box.get_xdata()[0]],[np.min(box.get_ydata()), np.max(box.get_ydata())]])
                # note that you can use any two values from the xdata vector
        # for k in data:
        #     print(k)


        # ax.boxplot(y, whis=[0, 100])

        # ax.set_xlim(-1, len(y))
        # ax.set_xticks(x)
        # ax.set_xticklabels([f'{l[2:]}' for l in labels], rotation=90, size=TICKLBLSIZE)
        # ax.set_yticks([0, 5, 10, 15, 20, 25])
        # ax.set_ylim(-2, 25)
        # for tick in ax.yaxis.get_major_ticks():
        #     tick.label.set_fontsize(TICKLBLSIZE)
        # for index, label in enumerate(ax.yaxis.get_ticklabels()):
        #     if index % 2 != 0:
        #         label.set_visible(False)

        # ax.yaxis.grid(True)

        # # Set common labels
        fig.text(0.1, 0.77, 'Static\nIntervals', ha='center', va='center', size=TICKLBLSIZE)
        fig.text(0.165, 0.77, 'Random\nIntervals', ha='center', va='center', size=TICKLBLSIZE)

        fig.text(0.5, 0.0, 'Connection Interval [ms]', ha='center', va='center', size=AXISLBLSIZE)
        # fig.text(0.0, 0.3, 'CoAP PDR [0:1.0]', ha='left', va='center', rotation='vertical', size=AXISLBLSIZE)
        # fig.text(0.0, 0.7, 'LL PDR [0:1.0]', ha='left', va='center', rotation='vertical', size=AXISLBLSIZE)

        plt.tight_layout()
        plt.subplots_adjust(wspace=0.1, hspace=0.1)


        plt.savefig(f'{self.out}.pdf', dpi=300, format='pdf', bbox_inches='tight')
        plt.savefig(f'{self.out}.png', dpi=300, format='png', bbox_inches='tight', pad_inches=0.01)
        plt.show()
        plt.close()



def main():
    fig = Fig()
    fig.create()


if __name__ == "__main__":
    main()
