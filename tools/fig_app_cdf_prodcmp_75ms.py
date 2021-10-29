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
import argparse
from datetime import datetime
from tools.exputil.expbase import Expbase
from tools.exputil.ana import Ana
from tools.exputil.topo import Topo
from tools.exputil.expstats import Expstats
from tools.exputil.alive import Alive
from tools.exputil.ifconfigval import Ifconfigval
from tools.exputil.llstats import LLStats

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

SRC = {
    "100ms1h39b-i75-0": "exp_putnon_statconn-static_100ms1h39b_i75/exp_putnon_statconn-static_100ms1h39b_i75_20210923-132758",
    # "100ms1h39b-i65r85-0": "exp_putnon_statconn-static_100ms1h39b_i65r85/exp_putnon_statconn-static_100ms1h39b_i65r85_20210923-191115",
    "500ms1h39b-i75-0": "exp_putnon_statconn-static_500ms1h39b_i75/exp_putnon_statconn-static_500ms1h39b_i75_20210924-005605",
    # "500ms1h39b-i65r85-0": "exp_putnon_statconn-static_500ms1h39b_i65r85/exp_putnon_statconn-static_500ms1h39b_i65r85_20210924-063941",
    "1s1h39b-i75-0": "exp_putnon_statconn-static_1s1h39b_i75/exp_putnon_statconn-static_1s1h39b_i75_20210924-122420",
    # "1s1h39b-i65r85-0": "exp_putnon_statconn-static_1s1h39b_i65r85/exp_putnon_statconn-static_1s1h39b_i65r85_20210924-180749",
    "5s1h39b-i75-0": "exp_putnon_statconn-static_5s1h39b_i75/exp_putnon_statconn-static_5s1h39b_i75_20210924-235114",
    # "5s1h39b-i65r85-0": "exp_putnon_statconn-static_5s1h39b_i65r85/exp_putnon_statconn-static_5s1h39b_i65r85_20210925-053430",
    "10s1h39b-i75-0": "exp_putnon_statconn-static_10s1h39b_i75/exp_putnon_statconn-static_10s1h39b_i75_20210927-154643",
    # "10s1h39b-i65r85-0": "exp_putnon_statconn-static_10s1h39b_i65r85/exp_putnon_statconn-static_10s1h39b_i65r85_20210927-213158",
    "30s1h39b-i75-0": "exp_putnon_statconn-static_30s1h39b_i75/exp_putnon_statconn-static_30s1h39b_i75_20210928-031515",
}




TYPE = "_cdf.json"

LBL = {
    "100ms1h39b-i75-0": "producer interval 100ms",
    "500ms1h39b-i75-0": "producer interval 500ms",
    "1s1h39b-i75-0":    "producer interval 1s",
    "5s1h39b-i75-0":    "producer interval 5s",
    "10s1h39b-i75-0":   "producer interval 10s",
    "30s1h39b-i75-0":   "producer interval 30s",
    "100ms1h39b-i65r85-0": "100ms1h39b-i65r85-0",
    "500ms1h39b-i65r85-0": "500ms1h39b-i65r85-0",
    "1s1h39b-i65r85-0": "1s1h39b-i65r85-0",
    "5s1h39b-i65r85-0": "5s1h39b-i65r85-0",
    "10s1h39b-i65r85-0": "10s1h39b-i65r85-0",
}

COL = {
    "foo": "baf",
}

STYLE = {
    # "500ms1h39b-i15r35-0":   "--",
    # "500ms1h39b-i40r60-0":   "--",
    # "500ms1h39b-i65r85-0":   "--",
    # "500ms1h39b-i90r110-0":  "--",
    # "500ms1h39b-i490r510-0": "--",
}

class Fig(Expbase):
    def __init__(self):
        super().__init__()

        base = os.path.splitext(os.path.basename(__file__))[0]
        self.out_pdf = os.path.join(self.basedir, "results/figs", f'{base}.pdf')
        self.out_png = os.path.join(self.basedir, "results/figs", f'{base}.png')
        print(self.out_pdf)

        self.dat = {}
        for s in SRC:
            print(f"loading {s}; {SRC[s]}{TYPE}")
            self.dat[s] = self.load(f'{SRC[s]}{TYPE}')


    def make(self):
        fig, ax = plt.subplots(1, 1, sharex=True)
        fig.set_size_inches(5, 5)
        fig.set_figheight(2)

        # set generic axis options
        ax.set_xlim(0.0, 3.0)
        xtick = np.arange(0, 3.5, .5)
        ax.set_xticks(xtick)
        ax.set_xticklabels(xtick, size=8)

        ax.set_ylim(0.0, 1.02)
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.xaxis.grid(True)
        ax.yaxis.grid(True)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(8)

        # ax.set_title("Round Trip Times for Varying Connection Intervals", size=9)
        for s in SRC:
            parm = {
                "label": LBL[s] if s in LBL else s
            }
            if s in COL:
                parm["color"] = COL[s]
            if s in STYLE:
                parm["linestyle"] = STYLE[s]
            ax.plot(self.dat[s]["data"][1]["x"], self.dat[s]["data"][1]["y"], **parm)

        ax.legend(fontsize=8, loc="lower right")

        # Set common labels
        fig.text(0.5, 0.00, 'RTT [in s]', ha='center', va='center', size=9)
        fig.text(0.00, 0.5, 'CDF', ha='center', va='center', rotation='vertical', size=9)


        plt.tight_layout()
        plt.savefig(self.out_pdf, dpi=300, format='pdf', bbox_inches='tight')
        plt.savefig(self.out_png, dpi=300, format='png', bbox_inches='tight', pad_inches=0.01)
        plt.show()
        plt.close()

    def load(self, file):
        path = os.path.join(self.plotdir, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            sys.exit("Error: unable to load file {}: {}".format(file, e))


def main():
    f = Fig()
    f.make()


if __name__ == "__main__":
    main()
