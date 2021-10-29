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
    "i2000": "exp_putnon_statconn-static_1s1h39b_i2000/exp_putnon_statconn-static_1s1h39b_i2000_20201201-191422_pdr.json",
}

TICKLBLSIZE = 9
LEGENDSIZE = 9
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
        fig.set_figheight(1.35)

        # set generic axis options
        xt = np.arange(0, 3601, 300)
        ax.set_xticks(xt)
        ax.set_xticklabels(xt, size=TICKLBLSIZE)
        ax.set_xlim(0.0, 3600)

        yt = [0.0, .25, .5, .75, 1.0]
        ax.set_ylim(0.0, 1.05)
        ax.set_yticks(yt)
        ax.set_yticklabels(yt, size=TICKLBLSIZE)

        ax.xaxis.grid(True)
        ax.yaxis.grid(True)

        for index, label in enumerate(ax.xaxis.get_ticklabels()):
            if index % 2 != 0:
                label.set_visible(False)
        for index, label in enumerate(ax.yaxis.get_ticklabels()):
            if index % 2 != 0:
                label.set_visible(False)

        # # ax].set_title("Producer Itvl 100ms, BLE ConnItvl 75ms", size=9)
        # # ax].set_xticks([])
        # # ax].set_xticklabels([])
        # ax.plot(self.dat["100ms"]["data"][ax["x"], self.dat["100ms"]["data"][ax["y"], color="C0", label="producer interval 100ms±50ms, connection interval 75ms")
        # # ax].legend(fontsize=8, loc="lower right")
        # ax.legend(fontsize=8, loc="lower left")

        # ax[ax.set_title("Producer Itvl 1s, BLE ConnItvl 2s", size=9)
        # ax[ax.set_xticklabels(self.dat["100ms"]["info"]["xtick_lbl"], size=8)
        ax.plot(self.dat["i2000"]["data"][1]["x"], self.dat["i2000"]["data"][1]["y"], color="C1", label="Average CoAP PDR")
        ax.legend(fontsize=LEGENDSIZE, loc="upper right")

        # Set common labels
        fig.text(0.552, 0.0, 'Experiment runtime [s]', ha='center', va='center', size=AXISLBLSIZE)
        fig.text(0.00, 0.55, 'PDR [0:1.0]', ha='center', va='center', rotation='vertical', size=AXISLBLSIZE)


        # ax.set_ylabel("moinfoo")
        # ax.set_title("Herrlich")

        # plt.xlabel("Experiment runtime [in s]")
        # plt.ylabel("moisnen")


        # plt.legend(fontsize=8)
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
                return yaml.load(f, Loader=yaml.SafeLoader)
        except Exception as e:
            sys.exit("Error: unable to load file {}: {}".format(file, e))


def main():
    f = Fig()
    f.make()


if __name__ == "__main__":
    main()
