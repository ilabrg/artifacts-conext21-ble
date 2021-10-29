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
from mpl_toolkits.axes_grid1.inset_locator import inset_axes



SRC = {
    # "100ms": "em6_putnon_statconn-static_100ms1h39b_i75/em6_putnon_statconn-static_100ms1h39b_i75_20210301-164004",
    # "100ms": "em6_putnon_statconn-static_100ms1h39b_i75/em6_putnon_statconn-static_100ms1h39b_i75_20210914-101545",
    "100ms": "exp_putnon_statconn-static_100ms1h39b_i75/exp_putnon_statconn-static_100ms1h39b_i75_20210923-132758",
}
SUFFIX = "_pdr_pn.json"
SUFFIX2 = "_pdr.json"

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
        print(self.out_pdf)

        self.pdr_pn = self.load(f'{SRC["100ms"]}{SUFFIX}')
        self.pdrsum = self.load(f'{SRC["100ms"]}{SUFFIX2}')


    def make(self):

        fixer = {
            "nrf52dk-1": 14,
            "nrf52dk-2": 13,
            "nrf52dk-3": 12,
            "nrf52dk-4": 11,
            "nrf52dk-5": 10,
            "nrf52dk-7": 8,
            "nrf52dk-8": 7,
            "nrf52dk-9": 6,
            "nrf52dk-10": 5,
            "nrf52840dk-6": 4,
            "nrf52840dk-7": 3,
            "nrf52840dk-8": 2,
            "nrf52840dk-9": 1,
            "nrf52840dk-10": 0,
        }

        # compose data for heatmap
        data = []
        yticks = []
        for row, n in enumerate(self.pdr_pn["data"]):
            tmp = []
            yticks.append(NODEIDS[n["label"]])
            for i, v in enumerate(n["x"]):
                if v <= 3600:
                    tmp.append(n["y"][i] - fixer[n["label"]])
            data.append(tmp)

        # build custom color map
        base = cm.get_cmap('viridis', 256)
        newcolors = base(np.linspace(0, 1, 256))
        # newcolors[:1, :] = np.array([250/256, 250/256, 250/256, 1])
        cmap = ListedColormap(newcolors)


        fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]})
        fig.set_size_inches(5, 5)
        fig.set_figheight(3.2)


        im = ax[0].imshow(data, interpolation='none', cmap=cmap)
        ax[0].set_aspect("auto")
        ax[0].set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
        ax[0].set_yticklabels(yticks)
        ax[0].set_xticks(range(0, 780, 60)) #[0, 60, 120, 180, 240,  360, 480, 600, 720])
        # ax.set_xticklabels([0, 600, 1200, 1800, 2400, 3000, 3600])
        ax[0].set_xticklabels([])

        axins = inset_axes(ax[0],
                   width="100%",  # width = 5% of parent_bbox width
                   height="100%",  # height : 50%
                   loc='lower left',
                   bbox_to_anchor=(0, 1.1, 0.79, .048),
                   bbox_transform=ax[0].transAxes,
                   borderpad=0,
                   )
        cbar = ax[0].figure.colorbar(im, cax=axins, orientation="horizontal", shrink=0.6 , aspect=10, pad=0.01)
        axins.xaxis.set_ticks_position('top')
        cbar.set_ticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        for tick in cbar.ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(TICKLBLSIZE)
        fig.text(.915, 1.022, 'PDR [0:1.0]', ha='center', va='center', size=AXISLBLSIZE)


        # for tick in cbar.ax.xaxis.get_major_ticks():
            # tick.label.set_fontsize(8)

        # Plot App PDR
        ax[1].set_xlim([1800, 3600])
        ax[1].set_xticks(self.pdrsum["info"]["xticks"])
        ax[1].set_xticklabels(self.pdrsum["info"]["xtick_lbl"])

        yt = [0.0, .25, .5, .75, 1.0]
        ax[1].set_ylim([0.0, 1.05])
        ax[1].set_yticks(yt)
        ax[1].set_yticklabels([f'{l:.1f}' for l in yt])
        ax[1].yaxis.grid(True)
        ax[1].xaxis.grid(True)

        for index, label in enumerate(ax[1].xaxis.get_ticklabels()):
            if index % 2 != 0:
                label.set_visible(False)
        for index, label in enumerate(ax[1].yaxis.get_ticklabels()):
            if index % 2 != 0:
                label.set_visible(False)

        ax[1].plot(self.pdrsum["data"][0]["x"], self.pdrsum["data"][0]["y"], color="C0", label="Average CoAP PDR")
        ax[1].legend(fontsize=LEGENDSIZE, loc="lower right")


        for a in ax:
            for tick in a.yaxis.get_major_ticks():
                tick.label.set_fontsize(TICKLBLSIZE)
            for tick in a.xaxis.get_major_ticks():
                tick.label.set_fontsize(TICKLBLSIZE)


        fig.text(0.0, 0.65, 'Node ID', ha='center', va='center', size=AXISLBLSIZE, rotation='vertical')
        fig.text(0.0, 0.24, 'PDR [0:1.0]', ha='center', va='center', size=AXISLBLSIZE, rotation='vertical')
        fig.text(0.552, 0.000, 'Experiment runtime [s]', ha='center', va='center', size=AXISLBLSIZE)


        fig.tight_layout()
        plt.subplots_adjust(left=0.1, right=1.0, hspace=0.15)

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
