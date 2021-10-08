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


SRC_PDR_M3 = "exp_putnon_m3-static_1s1h39b/exp_putnon_m3-static_1s1h39b_20200916-081327_pdr.json"
SRC_PDR_BLE_25 = "exp_putnon_statconn-static_1s1h39b_i25/exp_putnon_statconn-static_1s1h39b_i25_20201202-085206_pdr.json"
SRC_PDR_BLE_75 = "exp_putnon_statconn-static_1s1h39b_i75/exp_putnon_statconn-static_1s1h39b_i75_20201201-112834_pdr.json"
SRC_CDF_M3 = "exp_putnon_m3-static_1s1h39b/exp_putnon_m3-static_1s1h39b_20200916-081327_cdf.json"
SRC_CDF_BLE_25 = "exp_putnon_statconn-static_1s1h39b_i25/exp_putnon_statconn-static_1s1h39b_i25_20201202-085206_cdf.json"
SRC_CDF_BLE_75 = "exp_putnon_statconn-static_1s1h39b_i75/exp_putnon_statconn-static_1s1h39b_i75_20201201-112834_cdf.json"


class Fig(Expbase):
    def __init__(self):
        super().__init__()

        base = os.path.splitext(os.path.basename(__file__))[0]
        os.makedirs(os.path.join(self.basedir, "results/figs"), exist_ok=True)
        self.out_pdf = os.path.join(self.basedir, "results/figs", f'{base}.pdf')
        self.out_png = os.path.join(self.basedir, "results/figs", f'{base}.png')
        print(self.out_pdf)

        self.pdr_m3 = self.load(SRC_PDR_M3)
        self.pdr_ble25 = self.load(SRC_PDR_BLE_25)
        self.pdr_ble75 = self.load(SRC_PDR_BLE_75)
        # self.pdr_m3 = self.load(SRC_CDF_M3)
        # self.pdr_m3 = self.load(SRC_CDF_BLE_25)
        # self.pdr_m3 = self.load(SRC_CDF_BLE_75)


        # print(self.tree["data"][1]["label"])


    def make(self):
        # fig = plt.figure()
        # ax = fig.add_subplot(111)    # The big subplot
        # ax1 = fig.add_subplot(211)
        # ax2 = fig.add_subplot(212)

        fig, ax = plt.subplots(1, 1, sharex=True)
        fig.set_size_inches(5, 5)
        fig.set_figheight(1.75)

        # set generic axis options
        ax.set_xticks(self.pdr_m3["info"]["xticks"])
        ax.set_xticklabels(self.pdr_m3["info"]["xtick_lbl"], size=8)
        ax.set_xlim(0.0, 3600)
        ax.set_ylim(0.65, 1.02)
        ax.set_yticks([0.75, 1.0])
        ax.xaxis.grid(True)
        ax.yaxis.grid(True)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(8)

        # ax.set_title("CoAP Packet Delivery Rate Comparison", size=9)
        ax.plot(self.pdr_m3["data"][1]["x"], self.pdr_m3["data"][1]["y"], color="C4", label="IEEE802.15.4, CSMA/CA")
        ax.plot(self.pdr_ble25["data"][1]["x"], self.pdr_ble25["data"][1]["y"], color="C0", label="BLE, 25ms")
        ax.plot(self.pdr_ble75["data"][1]["x"], self.pdr_ble75["data"][1]["y"], color="C1", label="BLE, 75ms")
        ax.legend(fontsize=8, loc="lower right", ncol=3, borderaxespad=0.1)

        # ax[1].set_title("Line Topology with 75ms connection interval", size=9)
        # print(self.tree["info"]["xtick_lbl"])
        # ax[1].plot(self.line["data"][1]["x"], self.line["data"][1]["y"], color="C1")

        # Set common labels
        fig.text(0.5, 0.00, 'Experiment runtime [s]', ha='center', va='center', size=9)
        fig.text(0.00, 0.5, 'CoAP PDR [0:1.0]', ha='center', va='center', rotation='vertical', size=9)



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
                return json.load(f)
        except Exception as e:
            sys.exit("Error: unable to load file {}: {}".format(file, e))


def main():
    f = Fig()
    f.make()


if __name__ == "__main__":
    main()
