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
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

SRC = "exp_putnon_statconn-static_250ms1h39b_i75/exp_putnon_statconn-static_250ms1h39b_i75_20210302-091848"

LLPDR_PN = "_ll_pdr_sum_pn.json"
LLCHAN = "_ll_pdr_pc.json"
LLPDR =  "_ll_pdr_sum_nrf52dk-1.json"
APPPDR = "_pdr_nrf52dk-1.json"

TICKLBLSIZE = 9
LEGENDSIZE = 9
AXISLBLSIZE = 11

NODEIDS = {
    "nrf52dk-1": 1,
    "nrf52dk-2": 2,
    "nrf52dk-3": 3,
    "nrf52dk-4": 4,
    "nrf52dk-5": 5,
    "nrf52dk-6": 6,
    "nrf52dk-7": 7,
    "nrf52dk-8": 8,
    "nrf52dk-9": 9,
    "nrf52dk-10": 10,
    "nrf52840dk-6": 11,
    "nrf52840dk-7": 12,
    "nrf52840dk-8": 13,
    "nrf52840dk-9": 14,
    "nrf52840dk-10": 15,
}

class Fig(Expbase):
    def __init__(self):
        super().__init__()

        base = os.path.splitext(os.path.basename(__file__))[0]
        self.out_pdf = os.path.join(self.basedir, "results/figs", f'{base}.pdf')
        self.out_png = os.path.join(self.basedir, "results/figs", f'{base}.png')
        print(f'Output PDF file: {self.out_pdf}')
        print(f'Output PNG file: {self.out_png}')

        self.pdr_pn = self.load(f'{SRC}{LLPDR_PN}')
        self.chanpdr = self.load(f'{SRC}{LLCHAN}')
        self.llpdr = self.load(f'{SRC}{LLPDR}')
        self.apppdr = self.load(f'{SRC}{APPPDR}')
        self.apppdr_sum = self.load(f'{SRC}_pdr.json')


    def make(self):

        fixer = {
            "nrf52dk-1": 15,
            "nrf52dk-2": 14,
            "nrf52dk-3": 13,
            "nrf52dk-4": 12,
            "nrf52dk-5": 11,
            "nrf52dk-7": 9,
            "nrf52dk-8": 8,
            "nrf52dk-9": 7,
            "nrf52dk-10": 6,
            "nrf52840dk-6": 5,
            "nrf52840dk-7": 4,
            "nrf52840dk-8": 3,
            "nrf52840dk-9": 2,
            "nrf52840dk-10": 1,
        }

        chandata = self.chanpdr["data"][0:37]

        llpdr_map = []
        llpdr_yticks = []
        for row, n in enumerate(self.pdr_pn["data"]):
            tmp = []
            llpdr_yticks.append(str(NODEIDS[n["label"]]))
            for i, v in enumerate(n["x"]):
                if v <= 3600:
                    tmp.append(n["y"][i] - fixer[n["label"]])
            llpdr_map.append(tmp)

        llpdr_map[0][0] = 0.0
        print(llpdr_map[0][0])


        fig, ax = plt.subplots(3, 1, gridspec_kw={'height_ratios': [2, 1.5, 1]})
        fig.set_size_inches(5, 5)
        fig.set_figheight(5)

        # build custom color map
        # tried maps: [RdBu, viridis, tab20_r]
        base = cm.get_cmap('viridis', 256)
        newcolors = base(np.linspace(0, 1, 256))
        newcolors[:1, :] = np.array([250/256, 250/256, 250/256, 1])
        cmap = ListedColormap(newcolors)

        im_ll = ax[0].imshow(llpdr_map, interpolation='none', cmap=cmap)
        ax[0].set_title("Link layer PDR for each nodes upstream link", size=LEGENDSIZE)
        ax[0].set_aspect("auto")
        ax[0].set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
        ax[0].set_yticklabels(llpdr_yticks)
        ax[0].set_xticks(range(0, 780, 60))
        ax[0].set_xticklabels([])


        # Plot LL PDR per channel for node 1 (nrf52dk-1)
        im = ax[1].imshow(chandata, interpolation='none', cmap=cmap)


        axins = inset_axes(ax[0],
                   width="100%",  # width = 5% of parent_bbox width
                   height="100%",  # height : 50%
                   loc='lower left',
                   bbox_to_anchor=(0, 1.2, 0.79, .05),
                   bbox_transform=ax[0].transAxes,
                   borderpad=0,
                   )
        cbar = fig.colorbar(im, cax=axins, orientation="horizontal", shrink=0.6 , aspect=10, pad=0.01)
        # cbar.ax.tick_params(labelsize=TICKLBLSIZE)
        axins.xaxis.set_ticks_position('top')
        cbar.set_ticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        fig.text(.83, 1.01, 'PDR [0:1.0]', ha='left', va='center', size=AXISLBLSIZE)
        for tick in cbar.ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(TICKLBLSIZE)

        ax[1].set_title("Link layer PDR per data channel for upstream link of node 1", size=LEGENDSIZE)
        ax[1].set_aspect("auto")
        ax[1].set_yticks([0, 9, 18, 27, 36])
        ax[1].set_xticks([t / 15 for t in self.apppdr["info"]["xticks"]])
        ax[1].set_xticklabels([])

        # Plot App PDR
        ax[2].set_title("PDRs", size=LEGENDSIZE)
        ax[2].set_ylim([.4, 1.05])
        yt2 = [.5, .75, 1]
        ax[2].set_yticks(yt2)
        ax[2].set_yticklabels([f'{l:.2f}' for l in yt2])
        ax[2].yaxis.grid(True)
        ax[2].xaxis.grid(True)
        ax[2].set_xlim([1800, 3600])
        ax[2].set_xticks(self.apppdr["info"]["xticks"])
        ax[2].set_xticklabels(self.apppdr["info"]["xtick_lbl"], size=TICKLBLSIZE)
        ax[2].plot(self.llpdr["data"][0]["x"], self.llpdr["data"][0]["y"], color="C0", label="Link layer PDR for upstream link for node 1")
        ax[2].plot(self.apppdr["data"][0]["x"], self.apppdr["data"][0]["y"], color="C1", label="CoAP PDR for node 1")
        ax[2].plot(self.apppdr_sum["data"][0]["x"], self.apppdr_sum["data"][0]["y"], color="C2", label="Average CoAP PDR", linewidth=1)
        ax[2].legend(fontsize=LEGENDSIZE, loc="lower left")
        for index, label in enumerate(ax[2].xaxis.get_ticklabels()):
            if index % 2 != 0:
                label.set_visible(False)


        for a in ax:
            for tick in a.yaxis.get_major_ticks():
                tick.label.set_fontsize(TICKLBLSIZE)
            for tick in a.xaxis.get_major_ticks():
                tick.label.set_fontsize(TICKLBLSIZE)

        fig.text(0.0, 0.750, 'Node ID', ha='center', va='center', size=AXISLBLSIZE, rotation='vertical')
        fig.text(0.0, 0.425, 'Channel #', ha='center', va='center', size=AXISLBLSIZE, rotation='vertical')
        fig.text(0.0, 0.155, 'PDR [0:1.0]', ha='center', va='center', size=AXISLBLSIZE, rotation='vertical')
        fig.text(0.552, 0.00, 'Experiment runtime [s]', ha='center', va='center', size=AXISLBLSIZE)

        fig.tight_layout()
        plt.subplots_adjust(left=0.1, right=1.0, hspace=0.25)

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
