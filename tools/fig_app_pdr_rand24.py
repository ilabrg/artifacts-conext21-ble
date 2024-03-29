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
    "i75":  "exp_putnon_statconn-static_1s24h39b_i75/exp_putnon_statconn-static_1s24h39b_i75_20210308-104935_pdr.json",
    "rand": "exp_putnon_statconn-static_1s24h39b_i65r85/exp_putnon_statconn-static_1s24h39b_i65r85_20210303-145836_pdr.json",
    "line-i75":  "exp_putnon_statconn-static-line_1s24h39b_i75/exp_putnon_statconn-static-line_1s24h39b_i75_20210916-203133_pdr.json",
    "line-rand": "exp_putnon_statconn-static-line_1s24h39b_i65r85/exp_putnon_statconn-static-line_1s24h39b_i65r85_20210920-102945_pdr.json",
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
        # fig = plt.figure()
        # ax = fig.add_subplot(111)    # The big subplot
        # ax1 = fig.add_subplot(211)
        # ax2 = fig.add_subplot(212)

        fig, ax = plt.subplots(2, 1, sharex=True)
        fig.set_size_inches(5, 5)
        fig.set_figheight(2.3)

        # set generic axis options
        for a in ax:
            a.set_xlim(0.0, 86400)
            a.set_xticks(np.arange(0, 86401, 3600))
            a.set_xticklabels(np.arange(0, 25, 1), size=TICKLBLSIZE)
            for index, label in enumerate(a.xaxis.get_ticklabels()):
                if index % 2 != 0:
                    label.set_visible(False)

            yt = [0.25, 0.5, 0.75, 1.0]
            a.set_ylim(0.25, 1.05)
            a.set_yticks(yt)
            a.set_yticklabels([f'{l:.2f}' for l in yt], size=TICKLBLSIZE)
            a.xaxis.grid(True)
            a.yaxis.grid(True)

        # ax[0].yaxis.get_ticklabels()[0].set_visible(False)

        # ax[0].set_title("Static BLE Connection Interval (75ms)", size=9)
        # ax[0].set_xticks([])
        # ax[0].set_xticklabels([])
        ax[0].plot(self.dat["i75"]["data"][1]["x"], self.dat["i75"]["data"][1]["y"], color="C0", label="tree: static connection interval 75ms")
        ax[0].plot(self.dat["rand"]["data"][1]["x"], self.dat["rand"]["data"][1]["y"], color="C1", label="tree: random connection interval [65:85]ms")
        ax[0].legend(fontsize=LEGENDSIZE, loc="lower left", borderaxespad=0.1)

        # ax[1].set_title("Random BLE Connection Interval ([65:85]ms)", size=9)
        # ax[1].set_xticklabels(self.dat["100ms"]["info"]["xtick_lbl"], size=8)
        ax[1].plot(self.dat["line-i75"]["data"][1]["x"], self.dat["line-i75"]["data"][1]["y"], color="C2", label="line: static connection interval 75ms")
        ax[1].plot(self.dat["line-rand"]["data"][1]["x"], self.dat["line-rand"]["data"][1]["y"], color="C3", label="line: random connection interval [65:85]ms")
        ax[1].legend(fontsize=LEGENDSIZE, loc="lower left", borderaxespad=0.1)

        # Set common labels
        fig.text(0.5, 0.00, 'Experiment runtime [h]', ha='center', va='center', size=AXISLBLSIZE)
        fig.text(0.00, 0.5, 'CoAP PDR [0:1.0]', ha='center', va='center', rotation='vertical', size=AXISLBLSIZE)


        # ax.set_ylabel("moinfoo")
        # ax.set_title("Herrlich")

        # plt.xlabel("Experiment runtime [in s]")
        # plt.ylabel("moisnen")


        plt.tight_layout()
        plt.subplots_adjust(left=0.1, right=1.0, hspace=0.15)

        print("final size:", fig.get_figwidth(), fig.get_figheight())

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
