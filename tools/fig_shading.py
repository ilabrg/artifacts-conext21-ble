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


SRC_LLCHAN = "exp_putnon_statconn-static_250ms1h39b_i75/exp_putnon_statconn-static_250ms1h39b_i75_20210302-091848_ll_pdr_pc.json"
SRC_LLPDR =  "exp_putnon_statconn-static_250ms1h39b_i75/exp_putnon_statconn-static_250ms1h39b_i75_20210302-091848_ll_pdr_sum_nrf52dk-1.json"
SRC_APPPDR = "exp_putnon_statconn-static_250ms1h39b_i75/exp_putnon_statconn-static_250ms1h39b_i75_20210302-091848_pdr_nrf52dk-1.json"

class Fig(Expbase):
    def __init__(self):
        super().__init__()

        base = os.path.splitext(os.path.basename(__file__))[0]
        os.makedirs(os.path.join(self.basedir, "results/figs"), exist_ok=True)
        self.out_pdf = os.path.join(self.basedir, "results/figs", f'{base}.pdf')
        self.out_png = os.path.join(self.basedir, "results/figs", f'{base}.png')
        print(self.out_pdf)

        self.chanpdr = self.load(SRC_LLCHAN)
        self.llpdr = self.load(SRC_LLPDR)
        self.apppdr = self.load(SRC_APPPDR)


    def make(self):
        fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]})
        fig.set_size_inches(5, 5)
        fig.set_figheight(3)

        chandata = self.chanpdr["data"][0:37]


        # build custom color map
        # tried maps: [RdBu, viridis, tab20_r]
        base = cm.get_cmap('viridis', 256)
        newcolors = base(np.linspace(0, 1, 256))
        newcolors[:1, :] = np.array([250/256, 250/256, 250/256, 1])
        cmap = ListedColormap(newcolors)

        ax[0].set_title("Link layer PDR per data channel for selected link", size=9)
        ax[0].set_xticklabels(self.apppdr["info"]["xtick_lbl"], size=8)

        im = ax[0].imshow(chandata, interpolation='none', cmap=cmap)
        cbar = ax[0].figure.colorbar(im, ax=ax[0], orientation="horizontal", shrink=0.6 , aspect=40, pad=0.03)
        # cbar = ax[0].figure.colorbar(im, ax=ax[0], pad=0.025)
        # cbar.ax.set_xticks([0, .25, .5, .75, 1.0])
        # cbar.ax.set_xticklabels([0, .25, .5, .75, 1.0], fontsize=8)
        for tick in cbar.ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(8)
        ax[0].set_aspect("auto")
        ax[0].set_yticks([0, 9, 18, 27, 36])
        ax[0].set_ylabel("Channel #", size=9)
        ax[0].set_xticks(self.chanpdr["info"]["xticks"])
        ax[0].set_xticklabels([])

        # Plot LL PDR
        # ax[1].set_title("Average link layer PDR for selected link", size=9)
        # ax[1].set_ylim([.4, 1.05])
        # ax[1].set_yticks([.5, .75, 1])
        # ax[1].set_ylabel("PDR [0:1.0]", size=9)
        # ax[1].yaxis.grid(True)
        # ax[1].set_xlim([1800, 3600])
        # ax[1].set_xticks(self.llpdr["info"]["xticks"])
        # ax[1].set_xticklabels([])
        # ax[1].plot(self.llpdr["data"][0]["x"], self.llpdr["data"][0]["y"], color="C0", label="average link layer PDR for selected link")
        # ax[1].legend(fontsize=8, loc="lower left")

        # Plot App PDR
        # ax[2].set_title("CoAP PDR for the producer node at the selected link", size=9)
        ax[1].set_ylim([.4, 1.05])
        ax[1].set_yticks([.5, .75, 1])
        ax[1].set_ylabel("PDR [0:1.0]", size=9)
        ax[1].yaxis.grid(True)
        ax[1].set_xlim([1800, 3600])
        ax[1].set_xticks(self.apppdr["info"]["xticks"])
        ax[1].set_xticklabels(self.apppdr["info"]["xtick_lbl"], size=8)
        ax[1].plot(self.llpdr["data"][0]["x"], self.llpdr["data"][0]["y"], color="C0", label="average link layer PDR for selected link")
        ax[1].plot(self.apppdr["data"][0]["x"], self.apppdr["data"][0]["y"], color="C1", label="CoAP PDR for producer node at selected link")
        ax[1].legend(fontsize=8, loc="lower left")

        for a in ax:
            for tick in a.yaxis.get_major_ticks():
                tick.label.set_fontsize(8)


        fig.text(0.5, 0.00, 'Experiment runtime [s]', ha='center', va='center', size=9)

        fig.tight_layout()

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
