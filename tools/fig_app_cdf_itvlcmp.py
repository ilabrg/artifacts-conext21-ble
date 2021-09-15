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
import copy
import yaml
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
    "i25": "exp_putnon_statconn-static_1s1h39b_i25/exp_putnon_statconn-static_1s1h39b_i25_20201202-085206_cdf.json",
    "i50": "exp_putnon_statconn-static_1s1h39b_i50/exp_putnon_statconn-static_1s1h39b_i50_20201201-101056_cdf.json",
    "i75": "exp_putnon_statconn-static_1s1h39b_i75/exp_putnon_statconn-static_1s1h39b_i75_20201201-112834_cdf.json",
    "i100": "exp_putnon_statconn-static_1s1h39b_i100/exp_putnon_statconn-static_1s1h39b_i100_20201216-110053_cdf.json",
    "i250": "exp_putnon_statconn-static_1s1h39b_i250/exp_putnon_statconn-static_1s1h39b_i250_20201201-140349_cdf.json",
    "i500": "exp_putnon_statconn-static_1s1h39b_i500/exp_putnon_statconn-static_1s1h39b_i500_20201201-152126_cdf.json",
    "i750": "exp_putnon_statconn-static_1s1h39b_i750/exp_putnon_statconn-static_1s1h39b_i750_20201201-163906_cdf.json",
    "i1000": "exp_putnon_statconn-static_1s1h39b_i1000/exp_putnon_statconn-static_1s1h39b_i1000_20201201-175643_cdf.json",
}

class Fig(Expbase):
    def __init__(self):
        super().__init__()

        base = os.path.splitext(os.path.basename(__file__))[0]
        os.makedirs(os.path.join(self.basedir, "results/figs"), exist_ok=True)
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
        fig.set_figheight(2)

        # set generic axis options
        ax.set_xlim(0.0, 5.5)
        xtick = np.arange(0, 6, .5)
        ax.set_xticks(xtick)
        ax.set_xticklabels(xtick, size=8)

        ax.set_ylim(0.0, 1.02)
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.xaxis.grid(True)
        ax.yaxis.grid(True)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(8)

        # for dat in [
        #     self.dat["i25"]["data"][1],
        #     self.dat["i50"]["data"][1],
        #     self.dat["i75"]["data"][1],
        #     self.dat["i100"]["data"][1],
        #     self.dat["i250"]["data"][1],
        #     self.dat["i500"]["data"][1],
        #     self.dat["i750"]["data"][1],]:
        #     dat["x"].append(5.5)
        #     dat["y"].append(dat["y"][-1])


        # ax.set_title("Round Trip Times for Varying Connection Intervals", size=9)
        ax.plot(self.dat["i25"]["data"][1]["x"], self.dat["i25"]["data"][1]["y"], color="C0", label="connection interval 25ms")
        ax.plot(self.dat["i50"]["data"][1]["x"], self.dat["i50"]["data"][1]["y"], color="C1", label="connection interval 50ms")
        ax.plot(self.dat["i75"]["data"][1]["x"], self.dat["i75"]["data"][1]["y"], color="C2", label="connection interval 75ms")
        ax.plot(self.dat["i100"]["data"][1]["x"], self.dat["i100"]["data"][1]["y"], color="C3", label="connection interval 100ms")
        ax.plot(self.dat["i250"]["data"][1]["x"], self.dat["i250"]["data"][1]["y"], color="C4", label="connection interval 250ms")
        ax.plot(self.dat["i500"]["data"][1]["x"], self.dat["i500"]["data"][1]["y"], color="C5", label="connection interval 500ms")
        ax.plot(self.dat["i750"]["data"][1]["x"], self.dat["i750"]["data"][1]["y"], color="C6", label="connection interval 750ms")
        # ax.plot(self.dat["i1000"]["data"][1]["x"], self.dat["i1000"]["data"][1]["y"], color="C7", label="ConnItvl 1000ms")
        ax.legend(fontsize=8, loc="lower right")

        # ax[1].set_title("Line Topology with 75ms connection interval", size=9)
        # print(self.tree["info"]["xtick_lbl"])
        # ax[1].plot(self.line["data"][1]["x"], self.line["data"][1]["y"], color="C1")

        # Set common labels
        fig.text(0.5, 0.00, 'RTT [in s]', ha='center', va='center', size=9)
        fig.text(0.00, 0.5, 'CDF', ha='center', va='center', rotation='vertical', size=9)



        # ax.set_ylabel("moinfoo")
        # ax.set_title("Herrlich")

        # plt.xlabel("Experiment runtime [in s]")
        # plt.ylabel("moisnen")


        plt.tight_layout()

        plt.savefig(self.out_pdf, dpi=300, format='pdf', bbox_inches='tight')
        plt.savefig(self.out_png, dpi=300, format='png', bbox_inches='tight', pad_inches=0.01)
        plt.show()
        plt.close()

    def load(self, file):
        path = os.path.join(self.plotdir, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.load(f, Loader=yaml.SafeLoader)
        except Exception as e:
            sys.exit("Error: unable to load file {}: {}".format(file, e))


def main():
    f = Fig()
    f.make()


if __name__ == "__main__":
    main()
