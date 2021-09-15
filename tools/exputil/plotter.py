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
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

class Plotter:

    def __init__(self, plotbase):
        self.plotbase = plotbase


    def init_plot(self, info):
        if "dim" in info:
            fig, ax = plt.subplots(info["dim"][0], info["dim"][1])
        else:
            fig, ax = plt.subplots()
        fig.set_size_inches(11.7, 8.3)
        return fig, ax


    def saveraw(self, suffix, info, data):
        file = "{}_{}.json".format(self.plotbase, suffix)

        plotdat = {
            "info": info,
            "data": data,
        }

        with open(file, "w", encoding="utf-8") as f:
            json.dump(plotdat, f)


    def get_lim(self, xvals, yvals, xlim, ylim):
        if xlim == None and xvals != None:
            xlim = [0, 0]
            xlim[0] = min([x[0] for x in xvals])
            xlim[1] = max([x[-1] for x in xvals])
        if ylim == None and yvals != None:
            ylim = [0, 0]
            ylim[0] = min([min(row) for row in yvals])
            ylim[1] = max([max(row) for row in yvals]) * 1.01

        return [xlim, ylim]


    def get_ticks(self, xvals, xlim, binsize=None, num=25):
        NUM = 20
        res = {}
        lim = self.get_lim(xvals, None, xlim, None)[0]

        # calc xticks
        step = (lim[1] - lim[0]) / num
        if binsize:
            step += step % binsize
        else:
            for s in (0.001, 0.005, 0.010, 0.05, 0.1, 0.25, 0.5, 1.0, 5.0, 10, 30, 60, 120, 300, 600, 1800, 3600, 7200):
                if step <= s:
                    step = s
                    break

        tickmin = int(lim[0] / step) * step
        tickmax = (int(lim[1] / step) + 1) * step

        res["ticks"] = np.arange(tickmin, tickmax, step).tolist()
        res["lim"] = lim
        res["ticklim"] = [tickmin, tickmax]
        return res


    def get_xticks_from_binnum(self, binvals, num=25):
        pass


    def filter(self, cfg, node, time):
        if node != None and node not in cfg["nodes"]:
            return True
        if time != None and (time < cfg["first"] or time > cfg["last"]):
            return True
        return False

    # def finish_plot(self, plt, title, suffix, grid=True):
    #     outfile = "{}_{}.pdf".format(self.plotbase, suffix)
    #     pngfile = "{}_{}.png".format(self.plotbase, suffix)
    #     if os.path.isfile(outfile):
    #         os.remove(outfile)
    #     if title != None:
    #         plt.title(title)
    #     # plt.grid(grid)

    #     plt.tight_layout()

    #     plt.savefig(outfile, dpi=300, format='pdf', bbox_inches='tight')
    #     plt.savefig(pngfile, dpi=300, format='png', bbox_inches='tight', pad_inches=0.01)
    #     plt.show()
    #     plt.close()


    def finish_plot2(self, fig, ax, info, data):
        # apply labels and axis decoration
        for i, axis in enumerate(ax):
            if "grid" in info:
                axis.xaxis.grid(info["grid"][0])
                axis.yaxis.grid(info["grid"][1])
            else:
                axis.xaxis.grid(True)
                axis.yaxis.grid(True)

            if "xticks" in info:
                axis.set_xticks(info["xticks"])

            if "xtick_lbl" in info:
                if "xtick_lbl_rot" in info:
                    axis.set_xticklabels(info["xtick_lbl"], **info["xtick_lbl_rot"])
                else:
                    axis.set_xticklabels(info["xtick_lbl"])
            if "xtick_nth" in info:
                for index, label in enumerate(axis.xaxis.get_ticklabels()):
                    if index % info["xtick_nth"] != 0:
                        label.set_visible(False)

            if "yticks" in info:
                axis.set_yticks(info["yticks"])
                if "ytick_lbl" in info:
                    if "ytick_lbl_rot" in info:
                        axis.set_yticklabels(info["ytick_lbl"], **info["ytick_lbl_rot"])
                    else:
                        axis.set_yticklabels(info["ytick_lbl"])
                if "ytick_nth" in info:
                    for index, label in enumerate(axis.yaxis.get_ticklabels()):
                        if index % info["ytick_nth"] != 0:
                            label.set_visible(False)

        if "title" in info:
            if len(ax) == 1:
                ax[0].set_title(info["title"])
            else:
                fig.suptitle(info["title"])

        if "xlim" in info:
            plt.xlim(info["xlim"])
        if "ylim" in info:
            plt.ylim(info["ylim"])

        if "xlabel" in info:
            plt.xlabel(info["xlabel"])
        if "ylabel" in info:
            plt.ylabel(info["ylabel"])

        if "ylog" in info and info["ylog"]:
            plt.yscale('log')


        # if "title" in info:
        #     if len(ax) == 1:
        #         plt.title(info["title"])
        #     else:
        #         fig.suptitle(info["title"])

        if "nolegend" not in info:
            plt.legend(fontsize=8)
        plt.tight_layout()

        suffix = "" if "suffix" not in info else info["suffix"]
        pdffile = "{}_{}.pdf".format(self.plotbase, suffix)
        pngfile = "{}_{}.png".format(self.plotbase, suffix)
        plt.savefig(pdffile, dpi=300, format='pdf', bbox_inches='tight')
        plt.savefig(pngfile, dpi=300, format='png', bbox_inches='tight', pad_inches=0.01)
        self.saveraw(suffix, info, data)
        plt.show()
        plt.close()



    # def linechart(self, title, labels, x, y_data, y_labels, suffix):
    #     fig, ax = self.init_plot()

    #     for i, line in enumerate(y_data):
    #         axis.plot(x, line, label=y_labels[i])

    #     plt.xlabel(labels['x'])
    #     plt.ylabel(labels['y'])
    #     plt.legend(fontsize=8)
    #     plt.margins(x=0)
    #     self.finish_plot(plt, title, suffix)


    # def linechart2(self, info, data, xticks=None, grid=None):
    #     '''
    #     info: title, labels, suffix...
    #     data: {y: [[]] one array for each line to display
    #            x: [] ticks for x-axis
    #            label: [] label for each line
    #            ylim: [opt] limiter for y axis
    #     }
    #     '''
    #     fig, ax = self.init_plot()

    #     for i, y in enumerate(data['y']):
    #         label = data["label"][i] if "label" in data else None
    #         ax.plot(data['x'], y, label=label)

    #     plt.xlabel(info['xlabel'])
    #     plt.ylabel(info['ylabel'])
    #     plt.legend(fontsize=8)

    #     if grid and "x" in grid:
    #         ax.xaxis.grid(grid["x"])
    #     if grid and "y" in grid:
    #         ax.yaxis.grid(grid["y"])

    #     if "ylim" in data:
    #         plt.ylim(data["ylim"])
    #     if "xlim" in data:
    #         plt.xlim(data["xlim"])
    #     self.finish_plot(plt, info["title"], info["suffix"])


    # def linechart3(self, info, data, xticks=None, grid=None, step=True, lbl_nth_tick=None):
    #     '''
    #     info: title, labels, suffix, ylim:[min,max], ...,
    #     data: list of axes defs:
    #           -> [{x: [], y: [], label: "", style:"-"}, ...]
    #     '''

    #     fig, ax = self.init_plot()

    #     for i, line in enumerate(data):
    #         style = "-"
    #         if "style" in line:
    #             style = line["style"]
    #         else:
    #             if i > 8:
    #                 style = ":"
    #         color = line["color"] if "color" in line else None
    #         if step:
    #             ax.step(line["x"], line["y"], where="post", label=line["label"], linestyle=style, color=color)
    #         else:
    #             ax.plot(line["x"], line["y"], label=line["label"], linestyle=style, color=color)
    #         # plt.plot(line["x"], line["y"], 'C2o', alpha=0.5) # for verification...

    #     if xticks:
    #         ax.set_xticks(xticks["ticks"])
    #         ax.set_xticklabels(xticks["labels"])

    #     if grid and "x" in grid:
    #         ax.xaxis.grid(grid["x"])
    #     if grid and "y" in grid:
    #         ax.yaxis.grid(grid["y"])

    #     if lbl_nth_tick != None:
    #         if "x" in lbl_nth_tick:
    #             for index, label in enumerate(ax.xaxis.get_ticklabels()):
    #                 if index % lbl_nth_tick["x"] != 0:
    #                     label.set_visible(False)
    #         if "y" in lbl_nth_tick:
    #             for index, label in enumerate(ax.yaxix.get_ticklabels()):
    #                 if index % lbl_nth_tick["y"] != 0:
    #                     label.set_visible(False)

    #     plt.xlabel(info["xlabel"])
    #     plt.ylabel(info["ylabel"])
    #     plt.legend(fontsize=8)
    #     if "ylim" in info:
    #         plt.ylim(info["ylim"])
    #     if "xlim" in info:
    #         plt.xlim(info["xlim"])
    #     self.finish_plot(plt, info["title"], info["suffix"])

    def plot(self, plotter, info, data):
        mapping = {
            "linechart4": self.linechart4,
            "step_multi": self.step_multi,
            "heatmap": self.heatmap,
        }

        if plotter not in mapping:
            sys.exit("Plotter error: type of plot is not defined")

        mapping[plotter](info, data)


    def linechart4(self, info, data):
        '''
        info:
            title: Plot title
            suffix: added to output file name
            step: True|False, default: false
            grid: [x, y]
            xlabel: label for x-axis
            ylabel: label for y axis
            xlim: [min, max]
            ylim: [min, max]
            xticks: []
            xtick_lbl: []
            xtick_nth: 1-n
            yticks: []
            ytick_lbl: []
            yticks_nth: 1-n
        data: [] of which:
            x: [] - x coordinates
            y: [] - y coordinates
            label: label of line [opt]
            style: "" [opt]
            color: "" [opt]
        '''
        info["plotter"] = "linechart4"

        fig, ax = self.init_plot(info)
        for i, line in enumerate(data):
            label = None if "label" not in line else line["label"]
            style = None if "style" not in line else line["style"]
            color = None if "color" not in line else line["color"]
            if "step" in info and info["step"]:
                ax.step(line["x"], line["y"], where="post", label=label, linestyle=style, color=color)
            else:
                ax.plot(line["x"], line["y"], label=label, linestyle=style, color=color)
        self.finish_plot2(fig, [ax], info, data)



    def step_multi(self, info, data):
        '''
        info: title, suffix, x-axix-label, y-axis-label, grid:[x, y], ylim:[min, max], xlim[min,max]
              xticks, xtick_label,
        data: [line0, line1, line2] with line:{"x":[], "y":[], label,}
        '''
        info["plotter"] = "step_multi"

        fig, ax = self.init_plot(info)

        for i, line in enumerate(data):
            ax[i].step(line["x"], line["y"], where="post", label=line["label"])
            if "xticks" in info:
                ax[i].set_xticks(info["xticks"])
            if "xtick_label" in info:
                ax[i].set_xticklabels(info["xtick_label"])
            if "yticks" in info:
                ax[i].set_yticks(info["yticks"])
            if "grid" in info:
                ax[i].xaxis.grid(info["grid"][0])
                ax[i].yaxix.grid(info["grid"][1])
            if "ylim" in info:
                ax[i].set_ylim(bottom=info["ylim"][0], top=info["ylim"][1])
            if "xlim" in info:
                ax[i].set_xlim(left=info["xlim"][0], right=info["xlim"][1])
            if "label" in line:
                ax[i].set_ylabel(line["label"], rotation="horizontal", fontsize=8)
                ax[i].yaxis.set_label_coords(-.1, .50)

        ax[0].set_title(info["title"])
        ax[-1].set_xlabel(info["xlabel"])

        # plt.xlabel(info["xlabel"])
        # plt.ylabel(info["ylabel"])
        if "ylim" in info:
            plt.ylim(info["ylim"])
        if "xlim" in info:
            plt.xlim(info["xlim"])
        # plt.legend(fontsize=8)
        self.finish_plot(plt, None, info["suffix"])




    def linechart3_pn(self, info, data):
        '''
        info: title, labels, suffix, ylim:[min,max], ...,
        data: list of plots: each a list of lines:
              -> [[{x: [], y: [], label: ""}, ...], [{},{}]]
        '''
        info["plotter"] = "linechart3_pn"

        fig, ax = self.init_plot(info)

        for line in data:
            ax.step(line["x"], line["y"], where="post", label=line["label"])
            # plt.plot(line["x"], line["y"], 'C2o', alpha=0.5) # for verification...

        plt.xlabel(info["xlabel"])
        plt.ylabel(info["ylabel"])
        plt.legend(fontsize=8)
        if "ylim" in info:
            plt.ylim(info["ylim"])
        self.finish_plot(plt, info["title"], info["suffix"])


    def timechart(self, info, data):
        info["plotter"] = "timechart"

        fig, ax = plt.subplots(len(data), 1)
        fig.set_size_inches(11.7, 50)

        plt.title(info['title'])

        xmin = min([data[x]['x'][-1] for x in range(len(data))])
        xmax = max([data[x]['x'][-1] for x in range(len(data))])

        for i, line in enumerate(data):
            ax[i].step(line['x'], line['y'], where='post', label=line['label'])
            # ax.plot(line['x'], line['y'], label=line['label'], alpha=0.5)
            ax[i].set_xlim(left=xmin, right=xmax)

        plt.xlabel(info['xlabel'])
        plt.ylabel(info['ylabel'])
        plt.legend(fontsize=8)
        self.finish_plot(plt, info['title'], info['suffix'])


    def boxplot2(self, info, data):
        '''
        info: usual, but MUST contain bar_lbl
        data: list of sequences -> [[..], [...], ...]
        '''
        info["plotter"] = "boxplot2"

        fig, ax = self.init_plot(info)

        ax.boxplot(data, labels=info["bar_lbl"], whis="range")

        # plt.xlabel(info["xlabel"])
        # plt.ylabel(info["ylabel"])
        plt.xticks(rotation="vertical")
        self.finish_plot2(fig, [ax], info, data)


    def barchart(self, info, tick_labels, data, data_labels):
        info["plotter"] = "barchart"

        fig, ax = self.init_plot(info)

        x = np.arange(len(tick_labels))
        width = 0.8 / len(data)
        offset = 0.8 / len(data) / 2

        for i, val in enumerate(data):
            ax.bar(x - 0.4 + ((2 * i + 1) * offset), data[i], width,
                   label=data_labels[i])

        plt.xlabel(info['xlabel'])
        plt.ylabel(info['ylabel'])
        plt.xticks(x, tick_labels, rotation='vertical')
        ax.legend()
        # ax.yaxis.grid(True)

        self.finish_plot(plt, info['title'], info['suffix'])

    # def linechart_pn(self, info, tick_labels, data):
    #     '''
    #     info: title, labels (x, y), file name suffix
    #     tick_labels: [] for x-axis ticks
    #     '''
    def barchart2(self, info, data):
        '''
        info: [title, xlabel, ylabel, suffix, grid[True,False]]
        data: [{
            x: tick labels for x axis -> len(data["x"]) == len(data["y"][0])
            label: [] -> label for each bar group -> len(data["label"]) == len(data["y"])
            y: [[1, 2, 3,4], [4, 5, 6, 7], ...] one array for each bar group
            [opt] ylim: limit for y axix
            ylim: maximum y axis value
        }, ...]
        '''
        info["plotter"] = "barchart2"

        fig, ax = self.init_plot(info)
        self._bar(ax, info, data)
        self.finish_plot2(fig, [ax], info, data)


    def barchart_muldim(self, info, data):
        '''
        info: [title, labels, ticks, ...]
            + 'title' field for sub-titles
            + 'dim': [num rows, num cols] -> row * cols := len(data)
        data: list of line lists ->
            [[{x, y, label, ...}, {}], [{x, y, label, ...}, {}, ...]]
        '''
        info["plotter"] = "barchart_muldim"

        fig, ax = self.init_plot(info)
        for i, bar in enumerate(data):
            self._bar(ax[i], info, bar)
        self.finish_plot2(fig, ax, info, data)


    # def barchart_multi(self, info, data):
    #     '''
    #     info: [title, xlabel, ylabel, suffix, grid, rows, cols]
    #     data: [data, data, data, ...] -> each holding data object as in barchart2
    #     '''
    #     fig, ax = plt.subplots(info["rows"], info["cols"])

    #     for i, bar in enumerate(data):
    #         # print(ax)
    #         r = int(i / 4)
    #         c = i - (r * 4)
    #         self._bar(ax[r][c], bar["title"], bar["x"], bar["y"], bar["label"], bar["ylim"])


    #     fig.set_size_inches(11.7, 50)
    #     plt.xlabel(info['xlabel'])
    #     plt.ylabel(info['ylabel'])
    #     # if "grid" in info and info["grid"]:
    #     # if info["grid"]:
    #         # ax.yaxis.grid(True)

    #     self.finish_plot(plt, info['title'], info['suffix'])


    def barchart_per_node(self, info, tick_labels, data):
        '''
        info: title, labels, suffix...
        tick_labels: []
        data: [{label: name, data: [[1,2,3,...][1,2,3,...]]}
        nodeA: ([bar1...][bar2...]), nodeB: ([bar1...][bar2...])]
        '''
        info["plotter"] = "barchart_per_node"

        fig, ax = plt.subplots(len(data), 1)
        fig.set_size_inches(11.7, 50)

        ym = []
        for bar in data:
            ym.append(max([max(bar['data'][x]) for x in range(len(bar['data']))]))
        ytop = max(ym)

        x = np.arange(len(tick_labels))

        for i, bar in enumerate(data):
            d = bar["data"]
            width = 0.8 / len(d)
            offset = 0.8 / len(d) / 2
            ax[i].set_title(bar["label"], fontsize=9)
            ax[i].set_ylim(bottom=0, top=ytop)
            ax[i].set_xticks(x)
            ax[i].set_xticklabels([])
            # ax[i].set_xticklabels(tick_labels)
            ax[i].tick_params(labelrotation=90)
            # ax[i].yaxis.grid(True)
            for j, val in enumerate(d):
                ax[i].bar(x - 0.4 + ((2 * j + 1) * offset), val, width, label=bar["barlab"][j])

        ax[len(data) - 1].set_xticklabels(tick_labels)

        plt.xlabel(info['xlabel'])
        plt.ylabel(info['ylabel'])
        plt.legend(fontsize=8)
        # plt.xticks(x, tick_labels, rotation='vertical')
        # plt.setp(ax, xticks=x, xticklabels=tick_labels, rotation=90)
        plt.subplots_adjust(hspace=.4)
        # plt.title(info["title"])

        self.finish_plot(plt, ax, info)


    # def heatmap(self, info, xticks, ylab, data):
    def heatmap(self, info, data):
        '''
        info: title, suffix, xlabel, ylabel, colors?, cbarlabel
        data: [{label: name, val:[...]}, ...]
        '''
        info["plotter"] = "heatmap"

        # build custom color map
        # tried maps: [RdBu, viridis, tab20_r]
        base = cm.get_cmap('viridis', 256)
        newcolors = base(np.linspace(0, 1, 256))
        newcolors[:1, :] = np.array([250/256, 250/256, 250/256, 1])
        cmap = ListedColormap(newcolors)

        cbar_kw = {}
        fig, ax = self.init_plot(info)

        if len(data) > 40:
            fig.set_size_inches(11.7, 28.3)

        im = ax.imshow(data, interpolation='none', cmap=cmap)
        # im = ax.pcolor(data, linewidths=1)
        # im = ax.pcolormesh(data) #, cmap=cok)
        cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
        cbar.ax.set_ylabel(info["cbarlabel"], rotation=-90, va="bottom")

        # ax.set_yticks(np.arange(len(data)))
        # ax.set_yticklabels(info["ytick_lbl"])

        ax.set_aspect("auto")

        # if "xticks" in info:
        #     ax.set_xticks(info["xticks"])
        # if "xtick_label" in info:
        #     ax.set_xticklabels(info["xtick_label"])

        # plt.xlabel(info["xlabel"])
        # plt.ylabel(info["ylabel"])
        # fig.tight_layout()
        self.finish_plot2(fig, [ax], info, data)


    def evt_type_boxes(self, info, bins, data, colors):
        '''
        info: ...
        bins: []
        data: [ { label: "", y: [[], [], ...],  } ]
        colors: []
        '''
        info["plotter"] = "evt_type_boxes"

        fig, ax = plt.subplots(len(data), 1)
        fig.set_size_inches(11.7, 50)
        plt.subplots_adjust(hspace=1.4)


        for i, line, in enumerate(data):
            ax[i].set_aspect("auto")
            res, bins, patches = ax[i].hist(data[i]["y"], bins=bins, stacked=True)
            ax[i].set_xlabel(info["xlabel"])
            ax[i].set_ylabel(info["ylabel"])

            ax[i].legend(patches, info["types"], fontsize=8, bbox_to_anchor=(1, 1.2), loc="upper left")
            ax[i].set_title(data[i]["label"], fontsize=9)

            if "xlim" in info:
                ax[i].set_xlim(info["xlim"])
            if "ylim" in info:
                ax[i].set_ylim(info["ylim"])



        # plt.xlabel(info["xlabel"])
        # plt.ylabel(info["ylabel"])
        figheight = 9 if len(data) == 2 else 9 / 2.145 * 3
        plt.rcParams["figure.figsize"] = (36, figheight)
        self.finish_plot(plt, None, info["suffix"])

        pass


    def _bar(self, ax, info, data):
        x = np.arange(len(data["x"]))
        width = 0.8 / len(data["y"])
        offset = width / 2

        # ax.tick_params(axis='both', which='major', labelsize=8)

        if "title" in data:
            ax.set_title(data["title"], fontsize=9)

        # if "ylim" in info:
        #     ax.set_ylim(bottom=ylim[0], top=ylim[1])
        # -> add to finish_plot2()

        # ax.set_xticks(x)
        # ax.set_xticklabels(ticks)
        # ax.tick_params(labelrotation=90)

        for i, y in enumerate(data["y"]):
            label = data["label"][i] if "label" in data else None
            ax.bar(x - 0.4 + ((2 * i + 1) * offset), y, width, label=label)

        # if "label" in data:
            # ax.legend(fontsize=14)
