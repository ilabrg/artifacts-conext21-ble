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
        self.res = {}

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


        # with open(rawdata, "r", encoding="utf-8") as f:
        #     print(f"loading: {rawdata}")
        #     self.raw = json.load(f)



    def _get_xlab(self, cfg):
        print(cfg)
        if "r" in cfg:
            tmp = cfg[1:].split("r")
            return f'[{tmp[0]}:{tmp[1]}]'
        else:
            return f'{cfg[1:]}'


    def _get_itvl(self, name):
        tmp = name.split("-")
        tmp = tmp[0].split("_")
        return tmp[0][:-5], tmp[1]

    def create(self):

        # for k, v in self.raw.items():
        #     name = k[:-3]
        #     if name not in self.res:

        #         self.res[name] = {"reconns": [], "prod_itvl": v["prod_itvl"], "conn_itvl": v["conn_itvl"]}
        #     self.res[name]["reconns"].append(v["reconns"])

        print("moinsen")
        tmp = {}
        for v in self.raw:
            istr = self._get_itvl(v)[1]
            if istr not in tmp:
                tmp[istr] = []
            tmp[istr].append(self.raw[v]["reconns"])

        for foo in tmp:
            print(foo, tmp[foo])

        y = []
        labels = []
        for i, item in enumerate(ORDER):
            if item not in tmp:
                print("Skipping", item)
                continue
            y.append(tmp[item])
            labels.append(self._get_xlab(item))

        print(y)
        print(labels)

        fig, ax = plt.subplots(1, 1, sharex=True)
        fig.set_size_inches(5, 5)
        fig.set_figheight(1.85)


        ax.boxplot(y, whis=[0, 100])

        # ax.set_xlim(-1, len(y))
        # ax.set_xticks(x)
        ax.set_xticklabels([f'{l}' for l in labels], rotation=90, size=TICKLBLSIZE)
        ax.set_yticks([0, 5, 10, 15, 20, 25])
        ax.set_ylim(-2, 25)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(TICKLBLSIZE)
        for index, label in enumerate(ax.yaxis.get_ticklabels()):
            if index % 2 != 0:
                label.set_visible(False)

        ax.axvspan(5.5, 10.5, facecolor='grey', alpha=0.2)
        ax.yaxis.grid(True)

        # Set common labels
        fig.text(.35, .865, 'Static Intervals', ha='center', va='center', size=TICKLBLSIZE)
        fig.text(.8, .865, 'Random Intervals', ha='center', va='center', size=TICKLBLSIZE)

        fig.text(0.5, 0.0, 'BLE Connection itvl [ms]', ha='center', va='center', size=AXISLBLSIZE)
        fig.text(0.0, 0.5, '# of connection\n losses', ha='left', va='center', rotation='vertical', size=AXISLBLSIZE)

        plt.tight_layout()
        plt.subplots_adjust(left=0.1, right=1.0, hspace=0.15)


        plt.savefig(f'{self.out}.pdf', dpi=300, format='pdf', bbox_inches='tight')
        plt.savefig(f'{self.out}.png', dpi=300, format='png', bbox_inches='tight', pad_inches=0.01)
        plt.show()
        plt.close()




def main():
    tab = Fig()
    tab.create()


if __name__ == "__main__":
    main()
