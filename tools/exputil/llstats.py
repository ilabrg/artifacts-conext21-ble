#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2020 Hauke Petersen <hauke.petersen@fu-berlin.de>
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
import re
import sys
import copy
import math
import statistics
import numpy as np

CHAN_NUMOF = 40
CONN_MAX   = 10

CHANSTAT = {
    "time": 0,
    "foo": "bar",
}

EVENT = {
    "time": 0,
    "node": "",
    "conn": 0,
    "tx": [-1.0] * CHAN_NUMOF,
    "ok": [-1.0] * CHAN_NUMOF,
}

CHARMAP = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

class LLStats:

    def __init__(self, ana):
        self.ana = ana

        self.events = []
        self.pn = {n: [] for n in self.ana.desc["used_nodes"]}
        self.sums = {"ok": 0, "tx": 0, "rate": 0.0}
        self.sums_pc = {n: {"ok": [0] * CHAN_NUMOF, "tx": [0] * CHAN_NUMOF} for n in self.ana.desc["used_nodes"] + ["sum"]}
        self.anchors = {n: [[] for _ in range(CONN_MAX)] for n in self.ana.desc["used_nodes"]}
        self.buf = {n: [] for n in self.ana.desc["used_nodes"]}
        self.conn_offset = {n: [] for n in self.ana.desc["used_nodes"]}

        self.phy = {n: [] for n in self.ana.desc["used_nodes"]}
        self.phy_all = []


        self.re_txstats = re.compile(r'^>? *ll(?P<conn>\d+),(?P<stats>[0-9a-zA-Z]{80})')
        self.re_supstats = re.compile(r'^>? *ll,(?P<dur>\d+),'
                                      r'(?P<rx_cnt>\d+),(?P<rx>\d+),'
                                      r'(?P<tx_cnt>\d+),(?P<tx>\d+),(?P<free>\d+)'
                                      r'(,(?P<rx_cnt_off>\d+),(?P<tx_cnt_off>\d+))?')
        self.re_buf = re.compile(r'^>? *buf(?P<free>\d+)')


    def getraw(self):
        return {
            "events": self.events,
            "pn": self.pn,
            "sums": self.sums,
            "sums_pc": self.sums_pc,
            "anchors": self.anchors,
            "buf": self.buf,
            "conn_offset": self.conn_offset,
        }


    def readraw(self, raw):
        self.events = raw["events"]
        self.pn = raw["pn"]
        self.sums = raw["sums"]
        self.sums_pc = raw["sums_pc"]
        self.anchors = raw["anchors"]
        self.buf = raw["buf"]
        self.conn_offset = raw["conn_offset"]


    def update(self, time, node, line):
        m = self.re_txstats.search(line)
        if m:
            evt = {
                "time": time,
                "node": node,
                "conn": int(m.group("conn")),
                "tx": [-1.0] * CHAN_NUMOF,
                "ok": [-1.0] * CHAN_NUMOF,
            }

            txsum = 0
            oksum = 0
            for i, char in enumerate(m.group("stats")):
                chan = int(i / 2)
                if not i & 1:
                    txsum += CHARMAP.find(char)
                    evt["tx"][chan] = CHARMAP.find(char)
                else:
                    oksum += CHARMAP.find(char)
                    evt["ok"][chan] = CHARMAP.find(char)
            evt["sum_tx"] = txsum
            evt["sum_ok"] = oksum

            self.events.append(evt)
            self.pn[node].append(evt)
            return

        m = self.re_supstats.search(line)
        if m:
            self.buf[node].append({"time": time, "free": int(m.group("free"))})
            phy_evt = {
                "time": time,
                "node": node,
                "dur": int(m.group("dur")),
                "rx_cnt": int(m.group("rx_cnt")),
                "rx_tim": int(m.group("rx")),
                "tx_cnt": int(m.group("tx_cnt")),
                "tx_tim": int(m.group("tx")),
                "rx_cnt_off": int(m.group("rx_cnt_off")) if m.group("rx_cnt_off") else 0,
                "tx_cnt_off": int(m.group("tx_cnt_off")) if m.group("tx_cnt_off") else 0,
            }
            self.phy[node].append(phy_evt)
            self.phy_all.append(phy_evt)


        m = self.re_buf.search(line)
        if m:
            self.buf[node].append({"time": time, "free": int(m.group("free"))})


    def get_rate(self, tx, ok):
        rate = -.005
        if tx > 0:
            rate = ok / tx
        if rate > 1.0:
            rate = 1.0
        return rate


    def finish(self):
        for e in self.events:
            for c in range(CHAN_NUMOF):
                self.sums_pc[e["node"]]["tx"][c] += e["tx"][c]
                self.sums_pc[e["node"]]["ok"][c] += e["ok"][c]
                self.sums_pc["sum"]["tx"][c] += e["tx"][c]
                self.sums_pc["sum"]["ok"][c] += e["ok"][c]

                self.sums["tx"] += e["tx"][c]
                self.sums["ok"] += e["ok"][c]

        for n in self.sums_pc:
            self.sums_pc[n]["rate"] = [-1.0] * CHAN_NUMOF
            for c in range(CHAN_NUMOF):
                self.sums_pc[n]["rate"][c] = self.get_rate(self.sums_pc[n]["tx"][c], self.sums_pc[n]["ok"][c])
        self.sums["rate"] = self.get_rate(self.sums["tx"], self.sums["ok"])


    def summary(self):
        # find max packets send per interval:
        maxc = 0
        maxe = {}

        self.ana.statwrite("{:>15} {:>4}".format("NODE", "type"), end=False)
        for c in range(CHAN_NUMOF):
            self.ana.statwrite(" {:>5}".format("CH{}".format(c)), end=False)
        self.ana.statwrite("")

        for n in self.ana.nsort(self.sums_pc):
            for stat in ["tx", "ok", "rate"]:
                self.ana.statwrite("{:>15} {:>4}".format(n, stat), end=False)
                for c in range(CHAN_NUMOF):
                    if stat == "rate":
                        self.ana.statwrite(" {:>4}%".format(int(self.sums_pc[n]["rate"][c] * 100)), end=False)
                    else:
                        self.ana.statwrite(" {:>5}".format(self.sums_pc[n][stat][c]), end=False)
                self.ana.statwrite("")

        self.ana.statwrite("llstats: Buffer state (free mbufs in MSYS pool)")
        self.ana.statwrite("{:>15}  min/avg/max".format("node"))
        for n in self.ana.nsort(self.buf):
            if len(self.buf[n]) > 0:
                self.ana.statwrite("{:>15} {:>3}/{:>3}/{:>3}".format(n,
                    min([e["free"] for e in self.buf[n]]),
                    int(sum([e["free"] for e in self.buf[n]]) / len(self.buf[n])),
                    max([e["free"] for e in self.buf[n]])))

        # sum up the link layer stats
        self.ana.statwrite("\nMaster TX counts per node")
        self.ana.statwrite(f'{"node":>15} {"TX sent":>8} {"TX OK":>8} {"TX rate":>8}')
        for n in self.ana.nsort(self.sums_pc):
            tx_sum = 0
            tx_ok = 0
            for c in range(CHAN_NUMOF):
                tx_sum += self.sums_pc[n]["tx"][c]
                tx_ok += self.sums_pc[n]["ok"][c]
            rate = 0.0 if tx_sum == 0 else tx_ok / tx_sum
            self.ana.statwrite(f'{n:>15} {tx_sum:>8} {tx_ok:>8} {(rate * 100):>5.2f}%')

        if len(self.phy_all) == 0:
            return
        print("\nPHY stats - RX/TX on/off counts")
        self.ana.statwrite(f'{" ":>15} '
                           f'{"rx_on":>8} {"rx_off":>8} {"rx_diff":>8} |'
                           f'{"tx_on":>8} {"tx_off":>8} {"tx_diff":>8} | '
                           f'{"sum_on":>8} {"sum_off":>8} {"sum_diff":>8}')
        for n in self.ana.nsort(self.phy):
            sums = {"rx_on": 0, "rx_off": 0, "tx_on": 0, "tx_off": 0}
            for evt in self.phy[n]:
                sums["rx_on"] += evt["rx_cnt"]
                sums["tx_on"] += evt["tx_cnt"]
                sums["rx_off"] += evt["rx_cnt_off"]
                sums["tx_off"] += evt["tx_cnt_off"]
            all_on = sums["rx_on"] + sums["tx_on"]
            all_off = sums["rx_off"] + sums["tx_off"]
            self.ana.statwrite(f'{n:>15} '
                               f'{sums["rx_on"]:>8} {sums["rx_off"]:>8} {sums["rx_on"] - sums["rx_off"]:>8} |'
                               f'{sums["tx_on"]:>8} {sums["tx_off"]:>8} {sums["tx_on"] - sums["tx_off"]:>8} |'
                               f'{all_on:>8} {all_off:>8} {all_on - all_off:>8}')




    def buf_usage_summery(self, exponly=True, bufnum=40, bufsize=264):
        free = []
        size = bufnum * bufsize
        for n in self.buf:
            free.extend([k["free"] * bufsize for k in self.buf[n] if k["time"] >= self.ana.t["start"] and k["time"] <= self.ana.t["end"]])

        return {
            "min": size - max(free),
            "max": size - min(free),
            "avg": size - statistics.mean(free),
            "med": size - statistics.median(free),
            "size": size,
        }


    def plot_anchors(self, tstart=None, tend=None):

        tstart = 0
        tend = self.ana.t["end"] - self.ana.t["start"]

        data = []
        xlim = [None, None]
        ylim = [0.0, None]

        for n in self.anchors:
            for conn in range(len(self.anchors[n])):
                if len(self.anchors[n][conn]) == 0:
                    continue
                line = {"x": [], "y": [], "label": "{}_conn-{}".format(n, conn)}

                itvl = self.anchors[n][conn][1]["anchor"] - self.anchors[n][conn][0]["anchor"]
                offset = self.anchors[n][conn][0]["anchor"] % itvl
                last = 0
                for i, e in enumerate(self.anchors[n][conn]):
                    if tstart != None and (e["time"] - self.ana.t["start"]) < tstart:
                        continue
                    if tend != None and tend < (e["time"] - self.ana.t["start"]):
                        continue
                    if last == 0:
                        last = e["anchor"]
                        continue
                    val = (e["anchor"] - last) * (1 / 32768) * 1000
                    last = e["anchor"]
                    line["y"].append(val)
                    if val > 5000:
                        print("bad val {} -> line")

                    line["x"].append(e["time"] - self.ana.t["start"])
                    if xlim[0] == None or xlim[0] > line["x"][-1]:
                        xlim[0] = line["x"][-1]
                    if xlim[1] == None or xlim[1] < line["x"][-1]:
                        xlim[1] = line["x"][-1]
                    if ylim[0] == None or ylim[0] > line["y"][-1]:
                        ylim[0] = line["y"][-1]
                    if ylim[1] == None or ylim[1] < line["y"][-1]:
                        ylim[1] = line["y"][-1]

                data.append(line)

        if len(data) == 0:
            print("Warning: not printing anchors: no exp output found")
            return

        info = {
            "title": "RAW anchors for connection events",
            "xlabel": "Experiment Runtime [s]",
            "ylabel": "RAW connection anchor [ticks]",
            "suffix": "anchors_raw_mul",
            "dim": [len(data), 1],
            "xlim": xlim,
            "ylim": [0.0, ylim[1] * 1.1],
            "yticks": np.arange(0, ylim[1] * 1.1, 50)
        }
        # self.ana.plotter.linechart3(info, data)
        self.ana.plotter.step_multi(info, data)


    def plot_chanrate(self, all_chan=False, binsize=30, nodes=None, excl_nodes=None, timespan=None):
        if not nodes:
            nodes = self.ana.desc["used_nodes"]
        if excl_nodes:
            nodes = [n for n in nodes if n not in excl_nodes]

        chan_num = CHAN_NUMOF if all_chan else (CHAN_NUMOF - 3)
        if timespan == None:
            curbin = self.ana.t["start"]
        else:
            curbin = self.ana.t["start"] + timespan[0]

        # get ids
        tx = {n: [] for n in nodes}
        ok = {n: [] for n in nodes}
        labels = []
        for n in self.ana.nsort(tx):
            if n not in nodes:
                continue

            for c in range(chan_num):
                tx[n].append([])
                ok[n].append([])
                if len(nodes) < 3:
                    labels.append("{} - CH{}".format(n, c))
                else:
                    if c == 18:
                        labels.append("{}".format(n))
                    else:
                        labels.append("")

        xbin = []
        for e in self.events:
            if e["node"] not in nodes:
                continue

            if timespan != None:
                if e["time"] < (self.ana.t["start"] + timespan[0]) or e["time"] > (self.ana.t["start"] + timespan[1]):
                    continue
            elif e["time"] <= self.ana.t["start"]:
                continue


            if e["time"] > curbin:
                curbin += binsize
                xbin.append(curbin)

                for n in tx:
                    for i in range(len(tx[n])):
                        tx[n][i].append(0)
                        ok[n][i].append(0)

            for c in range(chan_num):
                tx[e["node"]][c][-1] += e["tx"][c]
                ok[e["node"]][c][-1] += e["ok"][c]

        data = []
        for n in self.ana.nsort(tx):
            for chan in range(len(tx[n])):        # channels
                row = []
                for b in range(len(tx[n][chan])):
                    row.append(self.get_rate(tx[n][chan][b], ok[n][chan][b]))
                data.append(row)

        xticks = np.arange(0, len(data[0]) + 1, 600 / binsize).tolist()
        xtick_lbl = ["{:.0f}".format(t * binsize) for t in xticks]
        info = {
            "title": "Link Layer Reliability of Data Channels (binsize {}s)".format(binsize),
            "cbarlabel": "Packet delivery rate [0-1]",
            "xlabel": "Experiment runtime [s]",
            "ylabel": "Node and channel",
            "suffix": "ll_pdr_pc",
            "grid": [False, False],
            "xticks": xticks,
            "xtick_lbl": xtick_lbl,
            "xtick_lbl_rot":  {"rotation": 45, "ha": "right"},
            "yticks": np.arange(len(data)).tolist(),
            "ytick_lbl": labels,
            "binsize": binsize,
            "plotter": "heatmap",
        }
        self.ana.plotter.heatmap(info, data)


    def get_rateline(self, nodes=None, binsize=5.0, timespan=None, ylim=None):
        cfg = self.ana.plotsetup(nodes, binsize, timespan)
        curbin = cfg["first"]

        line = {
            "x": [],
            "y": [],
            "label": "Link Layer Delivery Rate",
        }

        curdat = [0, 0]
        for e in self.events:
            if self.ana.plotter.filter(cfg, e["node"], e["time"]):
                continue

            if e["time"] >= (curbin + cfg["binsize"]):
                line["x"].append(self.ana.t_norm(curbin))
                line["y"].append(self.get_rate(curdat[0], curdat[1]))
                curbin += cfg["binsize"]
                curdat = [0, 0]
            curdat[0] += e["sum_tx"]
            curdat[1] += e["sum_ok"]

        if curdat[0] > 0:
            line["x"].append(self.ana.t_norm(curbin))
            line["y"].append(self.get_rate(curdat[0], curdat[1]))

        return line


    def plot_rateline(self, nodes=None, binsize=5.0, timespan=None, ylim=None):
        if len(self.events) == 0:
            print("llstats: skipping plot_rateliine(), no LL events in log")
            return

        line = self.get_rateline(nodes, binsize, timespan, ylim)

        if nodes == None:
            suffix = "ll_pdr_sum"
        else:
            suffix = "ll_pdr_sum_{}".format("-".join(nodes))

        xt = self.ana.plotter.get_ticks([line["x"]], None)
        info = {
            "title": "Link layer Packet Delivery Rate (binsize {}s)".format(binsize),
            "xlabel": "Experiment runtime [s]",
            "ylabel": "Packet Delivery Rate [0-1.0]",
            "suffix": suffix,
            "xlim": xt["lim"],
            "xticks": xt["ticks"],
            "xtick_lbl": xt["ticks"],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            "ylim": ylim,
            "binsize": binsize,
            "plotter": "line",
        }
        self.ana.plotter.linechart4(info, [line])


    def plot_rateline_pn(self, nodes=None, binsize=5.0, timespan=None, ylim=None):
        if len(self.events) == 0:
            print("llstats: skipping plot_rateliine_pn(), no LL events in log")
            return

        cfg = self.ana.plotsetup(nodes, binsize, timespan)

        done = set()
        data = {}
        for i, n in enumerate(cfg["nodes"]):
            curbin = cfg["first"]
            data[n] = {"x": [], "y": [], "label": n}

            curdat = [0, 0]
            for e in self.pn[n]:
                if self.ana.plotter.filter(cfg, None, e["time"]):
                    continue

                # pull curbin to first entry for the node in question
                if n not in done:
                    while e["time"] > (curbin + cfg["binsize"]):
                        curbin += cfg["binsize"]
                    done.add(n)

                if e["time"] >= (curbin + cfg["binsize"]):
                    data[n]["x"].append(self.ana.t_norm(curbin))
                    data[n]["y"].append(self.get_rate(curdat[0], curdat[1]) + ((len(cfg["nodes"]) - i) * 1.0))
                    curbin += cfg["binsize"]
                    curdat = [0, 0]
                curdat[0] += e["sum_tx"]
                curdat[1] += e["sum_ok"]

            if curdat[0] > 0:
                data[n]["x"].append(self.ana.t_norm(curbin))
                data[n]["y"].append(self.get_rate(curdat[0], curdat[1]) + ((len(cfg["nodes"]) - i) * 1.0))

        lines = []
        for n in self.ana.nsort(data):
            if len(data[n]["x"]) > 0:
                lines.append(data[n])

        xt = self.ana.plotter.get_ticks([l["x"] for l in lines], None)
        info = {
            "title": "Link layer Packet Delivery Rate (binsize {}s)".format(binsize),
            "xlabel": "Experiment runtime [s]",
            "ylabel": "Packet Delivery Rate [0-1.0]",
            "suffix": "ll_pdr_sum_pn",
            "xlim": xt["lim"],
            "xticks": xt["ticks"],
            "xtick_lbl": xt["ticks"],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            "ylim": ylim,
            "binsize": binsize,
            "plotter": "line",
        }

        self.ana.plotter.linechart4(info, lines)


    def plot_txcnt(self, all_chan=False, binsize=5, nodes=None, excl_nodes=None):
        if not nodes:
            nodes = self.ana.desc["used_nodes"]
        if excl_nodes:
            nodes = [n for n in nodes if n not in excl_nodes]

        chan_num = CHAN_NUMOF if all_chan else (CHAN_NUMOF - 3)
        curbin = self.ana.t["start"]

        # get ids
        tx = {n: [] for n in nodes}
        ok = {n: [] for n in nodes}
        labels = []
        for n in self.ana.nsort(tx):
            if n not in nodes:
                continue

            for c in range(chan_num):
                tx[n].append([])
                ok[n].append([])
                if len(nodes) < 3:
                    labels.append("{} - CH{}".format(n, c))
                else:
                    if c == 18:
                        labels.append("{}".format(n))
                    else:
                        labels.append("")

        for e in self.events:
            if e["node"] not in nodes:
                continue
            if e["time"] <= self.ana.t["start"]:
                continue
            if e["time"] > curbin:
                curbin += binsize

                for n in tx:
                    for i in range(len(tx[n])):
                        tx[n][i].append(0)
                        ok[n][i].append(0)

            for c in range(chan_num):
                tx[e["node"]][c][-1] += e["tx"][c]
                ok[e["node"]][c][-1] += e["ok"][c]

        data = []
        for n in self.ana.nsort(tx):
            for chan in range(len(tx[n])):        # channels
                row = []
                for b in range(len(tx[n][chan])):
                    cnt = tx[n][chan][b]

                    if cnt <= 1:
                        row.append(0.0)
                    elif cnt == 2:
                        row.append(10.0)
                    else:
                        row.append(20.0)
                data.append(row)

        xticks = np.arange(0, len(data[0]) + 1, 600 / binsize)
        xtick_lbl = ["{:.0f}s".format(t * binsize) for t in xticks]

        info = {
            "title": "Link Layer Reliability of Data Channels",
            "cbarlabel": "Packet delivery rate [0-1]",
            "xlabel": "Experiment runtime - binsize:{}s".format(binsize),
            "ylabel": "Node and channel",
            "suffix": "ll_pdr_pc-bin{}".format(binsize),
            "xticks": xticks,
            "xtick_label": xtick_lbl,
            "plotter": "heatmap",
        }
        self.ana.plotter.heatmap(info, [], labels, data)


    def plot_conn_offset(self, nodes=None, fulltime=False, ylim=None):
        if nodes == None:
            nodes = self.ana.desc["used_nodes"]

        data = []

        styles = ["-", ":", "--"]

        for n in self.conn_offset:

            if n not in nodes:
                continue


            conns = max([len(a["anchors"]) for a in self.conn_offset[n]])
            if conns < 2:
                print("not enough conns -> {}".format(conns))
                continue

            style = styles.pop(0)
            styles.append(style)

            lines = {}
            for i in range(conns):
                for ip in range(i + 1, conns):
                    lines["{}-{}".format(i, ip)] = {"x": [], "y": [],
                         "style": style,
                         "label": "{}: h{} to h{}".format(n, ip, i)}

            # print("conns", conns)
            # print(lines)

            for offevt in self.conn_offset[n]:
                if len(offevt["anchors"]) != conns:
                    continue

                if fulltime == False and (offevt["time"] < self.ana.t["start"] or offevt["time"] > self.ana.t["end"]):
                    continue

                for i in range(conns):
                    for ip in range(i + 1, conns):
                        diff = (offevt["anchors"][ip]["anchor"] - offevt["anchors"][i]["anchor"]) * 1000 / 32768
                        if diff > 0:
                            lines["{}-{}".format(i, ip)]["x"].append(offevt["time"] - self.ana.t["start"])
                            lines["{}-{}".format(i, ip)]["y"].append(diff)

            data.extend([lines[l] for l in lines])

        if len(data) == 0:
            print("no data")
            return

        xticks = np.arange(0, data[0]["x"][-1] * 0.01, (data[0]["x"][-1] - 0) / 10)
        xtick_lbl = ["{:.0f}s".format(t) for t in xticks]

        suff = "".join(["{}".format(n[-1]) for n in nodes])

        info = {
            "title": "Connection event anchor offset for {}".format(nodes),
            "xlabel": "Experiment runtime [s]",
            "ylabel": "Offset between anchors [in ms]",
            "suffix": "connevt_offset_{}".format(suff),
            "xticks": xticks,
            "xtick_lbl": xtick_lbl,
            "ylim": ylim,
            "plotter": "line",
        }

        self.ana.plotter.linechart4(info, data)


    def plot_bufusage(self, nodes=None, timespan=[None, None], xlim=None):
        if len(self.events) == 0:
            print("llstats: skipping plot_bufusage(), no LL events in log")
            return

        cfg = self.ana.plotsetup(nodes, None, timespan)

        data = []
        numof = max([max([e["free"] for e in self.buf[n]]) for n in self.buf])

        for n in self.ana.nsort(self.buf):
            if self.ana.plotter.filter(cfg, n, None):
                continue

            data.append({
                "x": [e["time"] - self.ana.t["start"] for e in self.buf[n]],
                "y": [numof - e["free"] for e in self.buf[n]],
                "label": n,
            })

        data.append({
            "x": data[0]["x"],
            "y": [numof] * len(data[0]["x"]),
            "label": "limit",
        })

        xt = self.ana.plotter.get_ticks([l["x"] for l in data], xlim)
        info = {
            "title": "NimBLE Buffer Usage",
            "xlabel": "Experiment runtime [s]",
            "ylabel": "Number of used mbufs",
            "suffix": "buf_msys",
            "xlim": xt["lim"],
            "xticks": xt["ticks"],
            "xtick_lbl": xt["ticks"],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            "plotter": "line",
        }

        self.ana.plotter.linechart4(info, data)


    def plot_phy_usage(self, stat="rx", nodes=None, timespan=[None, None], xlim=None):
        cfg = self.ana.plotsetup(nodes, None, timespan)

        data = []

        for n in self.ana.nsort(self.phy):
            if self.ana.plotter.filter(cfg, n, None):
                continue

            line = {"x": [], "y": [], "label": f'{n}-{stat}'}
            for evt in self.phy[n]:
                # if self.ana.plotter.filter(cfg, None, evt["time"]):
                #     continue
                line["x"].append(self.ana.t_norm(evt["time"]))
                line["y"].append(evt[f'{stat}_tim'] / evt["dur"] * 100)
            data.append(line)

            # self.phy[node].append({
            #     "time": time,
            #     "dur": int(m.group("dur")),
            #     "rx_cnt": int(m.group("rx_cnt")),
            #     "rx_tim": int(m.group("rx")),
            #     "tx_cnt": int(m.group("tx_cnt")),
            #     "tx_tim": int(m.group("tx")),
            # })

        xt = self.ana.plotter.get_ticks([l["x"] for l in data], xlim)
        info = {
            "title": "Radio Utilization per Node - {} (Binsize 5s)".format(stat.upper()),
            "xlabel": "Experiment runtime [s]",
            "ylabel": "Relative time in {} [%]".format(stat.upper()),
            "suffix": "phy_usage",
            "xlim": xt["lim"],
            "xticks": xt["ticks"],
            "xtick_lbl": xt["ticks"],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            # "ylim": [0, 3],
            "plotter": "line",
        }

        self.ana.plotter.linechart4(info, data)


    def plot_phy_usage_sum(self, stat=["rx", "tx", "aggr"], nodes=None, binsize=15.0, timespan=[None, None]):
        cfg = self.ana.plotsetup(nodes, binsize, timespan)

        data = []
        for s in stat:
            data.append({"x": [], "y": [], "label": f'{s.upper()}'})

        curbin = cfg["first"]
        cnt = [[] for _ in range(len(stat))]
        for evt in self.phy_all:
            if self.ana.plotter.filter(cfg, evt["node"], evt["time"]):
                continue

            if evt["time"] >= curbin + cfg["binsize"]:
                for i, s in enumerate(stat):
                    data[i]["x"].append(self.ana.t_norm(curbin))
                    if len(cnt[i]) > 0:
                        data[i]["y"].append((sum(cnt[i]) / len(cnt[i])) * 100)
                    else:
                        data[i]["y"].append(0.0)
                    cnt[i] = []
                curbin += cfg["binsize"]

            for i, s in enumerate(stat):
                if s == "aggr":
                    cnt[i].append((evt["rx_tim"] + evt["tx_tim"]) / evt["dur"])
                else:
                    cnt[i].append(evt[f'{s}_tim'] / evt["dur"])

        for i, s in enumerate(stat):
            data[i]["x"].append(self.ana.t_norm(curbin))
            if len(cnt[i]) > 0:
                data[i]["y"].append((sum(cnt[i]) / len(cnt[i])) * 100)
            else:
                data[i]["y"].append(0.0)

        xt = self.ana.plotter.get_ticks([l["x"] for l in data], None)
        info = {
            "title": "Average PHY Utilization (Binsize {}s)".format(cfg["binsize"]),
            "xlabel": "Experiment runtime [s]",
            "ylabel": "PHY Utilization [%]",
            "suffix": "phy_usage_sum",
            "xlim": xt["lim"],
            "xticks": xt["ticks"],
            "xtick_lbl": xt["ticks"],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            # "ylim": [0, 3],''
            "plotter": "line",
        }
        self.ana.plotter.linechart4(info, data)


    def plot_phy_cnt(self, stat="tx", nodes=None, timespan=[None, None], xlim=None):
        cfg = self.ana.plotsetup(nodes, None, timespan)

        data = []

        for n in self.ana.nsort(self.phy):
            if self.ana.plotter.filter(cfg, n, None):
                continue
            line = {"x": [], "y": [], "label": f'{n}-{stat}'}
            for evt in self.phy[n]:
                # if self.ana.plotter.filter(cfg, None, evt["time"]):
                #     continue
                line["x"].append(self.ana.t_norm(evt["time"]))
                line["y"].append(evt[f'{stat}_cnt'] * 1000000 / evt["dur"])
            data.append(line)

        xt = self.ana.plotter.get_ticks([l["x"] for l in data], xlim)
        info = {
            "title": "Radio Activity Count - {} (Binsize 5s)".format(stat.upper()),
            "xlabel": "Experiment runtime [s]",
            "ylabel": "Events per second",
            "suffix": "phy_cnt_pn",
            "xlim": xt["lim"],
            "xticks": xt["ticks"],
            "xtick_lbl": xt["ticks"],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            # "ylim": [0, 3],''
            "plotter": "line",
        }
        self.ana.plotter.linechart4(info, data)


    def plot_phy_cnt_sum(self, stat=["rx", "tx", "aggr"], nodes=None, binsize=15.0, timespan=[None, None]):
        cfg = self.ana.plotsetup(nodes, binsize, timespan)

        data = []
        for s in stat:
            data.append({"x": [], "y": [], "label": f'{s.upper()}'})

        curbin = cfg["first"]
        cnt = [0 for _ in range(len(stat))]
        for evt in self.phy_all:
            if self.ana.plotter.filter(cfg, evt["node"], evt["time"]):
                continue

            if evt["time"] >= curbin + cfg["binsize"]:
                for i, s in enumerate(stat):
                    data[i]["x"].append(self.ana.t_norm(curbin))
                    data[i]["y"].append(cnt[i])
                    cnt[i] = 0
                curbin += cfg["binsize"]
            for i, s in enumerate(stat):
                if s == "aggr":
                    cnt[i] += (evt["rx_cnt"] + evt["tx_cnt"]) * 1000000 / evt["dur"]
                else:
                    cnt[i] += evt[f'{s}_cnt'] * 1000000 / evt["dur"]

        for i, s in enumerate(stat):
            data[i]["x"].append(self.ana.t_norm(curbin))
            data[i]["y"].append(cnt[i])

        xt = self.ana.plotter.get_ticks([l["x"] for l in data], None)
        info = {
            "title": "PHY Events (Binsize {}s)".format(cfg["binsize"]),
            "xlabel": "Experiment runtime [s]",
            "ylabel": "Events per second",
            "suffix": "phy_cnt_sum",
            "xlim": xt["lim"],
            "xticks": xt["ticks"],
            "xtick_lbl": xt["ticks"],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            # "ylim": [0, 3],''
            "plotter": "line",
        }
        self.ana.plotter.linechart4(info, data)


    def plot_phy_verify(self):
        for n in self.ana.nsort(self.phy):
            data = [
                {"x": [], "y": [], "label": "Diff RX"},
                {"x": [], "y": [], "label": "Diff TX"},
            ]

            for evt in self.phy[n]:
                data[0]["x"].append(self.ana.t_norm(evt["time"]))
                data[0]["y"].append(evt["rx_cnt"] - evt["rx_cnt_off"])
                data[1]["x"].append(self.ana.t_norm(evt["time"]))
                data[1]["y"].append(evt["tx_cnt"] - evt["tx_cnt_off"])

            xt = self.ana.plotter.get_ticks([l["x"] for l in data], None)
            info = {
                "title": "PHY Count Diff(Node: {})".format(n),
                "xlabel": "Experiment runtime [s]",
                "ylabel": "Event Difference",
                "suffix": "phy_cnt_verify",
                "xlim": xt["lim"],
                "xticks": xt["ticks"],
                "xtick_lbl": xt["ticks"],
                "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
                # "ylim": [0, 3],''
                "plotter": "line",
            }
            self.ana.plotter.linechart4(info, data)



        # sys.exit("dMUHH")
