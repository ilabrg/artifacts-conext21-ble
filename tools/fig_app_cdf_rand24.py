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
    "i75":  "exp_putnon_statconn-static_1s24h39b_i75/exp_putnon_statconn-static_1s24h39b_i75_20210308-104935_cdf.json",
    "rand": "exp_putnon_statconn-static_1s24h39b_i65r85/exp_putnon_statconn-static_1s24h39b_i65r85_20210303-145836_cdf.json",
    "i75-line":  "exp_putnon_statconn-static-line_1s24h39b_i75/exp_putnon_statconn-static-line_1s24h39b_i75_20210916-203133_cdf.json",
    "rand-line": "exp_putnon_statconn-static-line_1s24h39b_i65r85/exp_putnon_statconn-static-line_1s24h39b_i65r85_20210920-102945_cdf.json",
}

TICKLBLSIZE = 9
AXISLBLSIZE = 11

class Fig(Expbase):
    def __init__(self):
        super().__init__()

        base = os.path.splitext(os.path.basename(__file__))[0]
        self.out_pdf = os.path.join(self.basedir, "results/figs", f'{base}.pdf')
        self.out_png = os.path.join(self.basedir, "results/figs", f'{base}.png')
        print(self.out_pdf)

        self.dat = {}
        for s in SRC:
            print(f"loading {s}; {SRC[s]}")
            self.dat[s] = self.load(SRC[s])

    def make(self):
        fig, ax = plt.subplots(1, 1, sharex=True)
        fig.set_size_inches(5, 5)
        fig.set_figheight(1.75)

        # set generic axis options
        xt = [i / 10 for i in range(0, 32, 2)]
        ax.set_xlim(0.0, 1.4)
        ax.set_xticks(xt)
        ax.set_xticklabels(xt, size=TICKLBLSIZE)

        yt = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        ax.set_ylim(0.0, 1.02)
        ax.set_yticks(yt)
        ax.set_yticklabels(yt, size=TICKLBLSIZE)
        for index, label in enumerate(ax.xaxis.get_ticklabels()):
            if index % 2 != 1:
                label.set_visible(False)

        ax.xaxis.grid(True)
        ax.yaxis.grid(True)

        # ax.set_title("CDF of Round Trip Times (RTT)", size=9)
        ax.plot(self.dat["i75"]["data"][1]["x"], self.dat["i75"]["data"][1]["y"], color="C0", label="Tree, Static ConnItvl")
        ax.plot(self.dat["rand"]["data"][1]["x"], self.dat["rand"]["data"][1]["y"], color="C1", label="Tree, Random ConnItvl")
        ax.plot(self.dat["i75-line"]["data"][1]["x"], self.dat["i75-line"]["data"][1]["y"], color="C2", label="Line, Static ConnItvl")
        ax.plot(self.dat["rand-line"]["data"][1]["x"], self.dat["rand-line"]["data"][1]["y"], color="C3", label="Line, Random ConnItvl")
        ax.legend(fontsize=9, loc="lower right")

        # ax[1].set_title("Line Topology with 75ms connection interval", size=9)
        # print(self.tree["info"]["xtick_lbl"])
        # ax[1].plot(self.line["data"][1]["x"], self.line["data"][1]["y"], color="C1")

        # Set common labels
        fig.text(0.5, 0.00, 'RTT [s]', ha='center', va='center', size=AXISLBLSIZE)
        fig.text(0.00, 0.55, 'CDF', ha='center', va='center', rotation='vertical', size=AXISLBLSIZE)



        # ax.set_ylabel("moinfoo")
        # ax.set_title("Herrlich")

        # plt.xlabel("Experiment runtime [in s]")
        # plt.ylabel("moisnen")


        plt.tight_layout()
        plt.subplots_adjust(left=0.1, right=1.0)

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
