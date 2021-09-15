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

import re
import os
import sys
import statistics

MAX_CONNS = 20

class Topo:

    def __init__(self, ana):
        self.ana = ana

        if "meshconn" in self.ana.desc["name"]:
            self.evt_map = {"conn": "conn_downlink", "close": "close_downlink"}
        else:
            self.evt_map = {"conn": "conn_s", "close": "close_s"}

        self.topo = {n: {"p": set(), "c": set(), "lost": [], "hops": -1} for n in ana.desc["used_nodes"]}
        self.conn_evt = []
        # self.evt_list = []
        # self.conns = {n: [None for _ in range(MAX_CONNS)] for n in self.ana.desc["used_nodes"]}
        # self.conn_on = []
        # self.drop_on = []

        self.meshconn = []


    def evt(self, time, evt, node, peer, handle):
        self.conn_evt.append({
            "t": time,
            "type": evt,
            "node": node,
            "peer": peer,
            "handle": handle,
        })

        if evt == self.evt_map["conn"]:
            self.topo[node]["c"].add(peer)
            self.topo[peer]["p"].add(node)

            # self.evt_list.append({"t": time, "e": "parent {} connected to child {}".format(node, peer)})


            # self.conns[node][handle] = {"peer": peer, "role": "S"}
            # self.conn_on.append(time)
        # elif "conn" in evt:
        #     self.conns[node][handle] = {"peer": peer, "role": "M"}

        if evt == self.evt_map["close"]:
            self.topo[peer]["lost"].append(float(time))
            self.topo[node]["c"].remove(peer)
            self.topo[peer]["p"].remove(node)
            self.topo[peer]["hops"] = -1
            # self.evt_list.append({"t": time, "e": "parent {} lost child {}".format(node, peer)})
            # self.conns[node][handle] = None
            # self.drop_on.append(time)
        # elif "close" in evt:
            # self.conns[node][handle] = None


    def parse_meshconn(self, time, evt, node, peer, handle):
        if evt in ("conn_uplink", "close_uplink", "conn_downlink", "close_downlink", "reconn"):
            self.meshconn.append({
                "time": time,
                "node": node,
                "evt": evt,
                "peer": peer,
                "handle": handle,
            })


    def update(self, time, node, output):
        m = re.search(r'ble: (?P<evt>[_a-z]+) '
                      r'\((?P<handle>\d+)\|'
                      r'(?P<addr>[0-9a-zA-Z:]+)\)', output)
        if m:
            peer = self.ana.nodename_from_mac(m.group('addr'))
            self.evt(time, m.group("evt"), node, peer, int(m.group("handle")))

        m = re.search(r'ble:(?P<evt>[_a-z]+) (?P<addr>[0-9a-zA-Z:]+) (?P<handle>\d+)', output)
        if m:
            peer = self.ana.nodename_from_mac(m.group('addr'))
            self.evt(time, m.group("evt"), node, peer, int(m.group("handle")))
            self.parse_meshconn(time, m.group("evt"), node, peer, int(m.group("handle")))


    def finish(self):
        # update hop count for final topology
        tmp = [n for n in self.topo if len(self.topo[n]["p"]) == 0 and len(self.topo[n]["c"]) > 0]
        for n in tmp:
            self.topo[n]["hops"] = 0

        while (len(tmp) > 0):
            c = []
            for n in tmp:
                c += self.topo[n]["c"]
            for n in c:
                self.topo[n]["hops"] = min([self.topo[p]["hops"] for p in self.topo[n]["p"]]) + 1
            tmp = c


    def summary(self):
        self.ana.statwrite("\nTOPO:")
        self.ana.statwrite("Topology effecting events:")
        for evt in self.conn_evt:
            if evt["type"] in self.evt_map.values():
                self.ana.statwrite(f'{self.ana.t_norm(evt["t"]):>9.2f} '
                                   f'{evt["node"]:>15} -> {evt["peer"]:>15} : {evt["type"]}')

        self.ana.statwrite("Topology at the end of experiment:")
        self.print_topo()

        hopcnt = [self.topo[n]["hops"] for n in self.topo if self.topo[n]["hops"] > 0]
        self.ana.statwrite(f'\nHopcnt max    {max(hopcnt):>7}')
        self.ana.statwrite(f'Hopcnt avg    {sum(hopcnt) / len(hopcnt):>7.3f}')
        self.ana.statwrite(f'Hopcnt mean   {statistics.mean(hopcnt):>7.3f}')
        self.ana.statwrite(f'Hopcnt median {statistics.median(hopcnt):>7.3f}\n')


    def get_conn_drops(self):
        # TODO: filter conn drops by going through self.conn_evt list
        cnt = 0
        for ts in self.drop_on:
            if ts >= self.ana.t["start"] and ts <= self.ana.t["end"]:
                cnt += 1

        return cnt


    def print_deep(self, fmt, node):
        for n in self.ana.nsort(self.topo[node]["c"]):
            recon = ""
            if len(self.topo[n]["lost"]) > 0:
                recon = "--> closed: "
                for ts in self.topo[n]["lost"]:
                    recon += "{:.2f}, ".format(self.ana.reltime(ts))
            self.ana.statwrite("{} {} {}".format(fmt, n, recon))
            self.print_deep("|   " + fmt, n)


    def print_topo(self):
        if "autoconn" not in self.ana.desc["name"]:
            for n in self.ana.nsort(self.topo):
                if len(self.topo[n]["p"]) == 0:
                    self.ana.statwrite(n)
                    self.print_deep("|--", n)
        else:
            for n in self.ana.nsort(self.topo):
                self.ana.statwrite("{:>15} p: {} c:{}".format(n, self.topo[n]["p"], self.topo[n]["c"]))


    def _cnt_hops(self, topo):
        hopcnt = []

        for n in topo:
            cnt = 0
            p = topo[n]
            while p != None:
                cnt += 1
                p = topo[p]
            if cnt > 0:
                hopcnt.append(cnt)

        return hopcnt


    def plot_hopcnt2(self, timespan=[None, None], xlim=None):
        cfg = self.ana.plotsetup(None, None, timespan)

        data = [
            {"x": [self.ana.t_norm(cfg["first"])], "y": [0], "label": "# of links"},
            {"x": [self.ana.t_norm(cfg["first"])], "y": [0], "label": "hop count: max"},
            {"x": [self.ana.t_norm(cfg["first"])], "y": [0], "label": "hop count: average"},
            # {"x": [self.ana.t_norm(cfg["first"])], "y": [0], "label": "hop count: median"},
        ]
        topo = {n: None for n in self.ana.desc["used_nodes"]}

        for evt in self.conn_evt:
            if self.ana.plotter.filter(cfg, None, evt["t"]):
                continue

            if evt["type"] == self.evt_map["conn"]:
                topo[evt["peer"]] = evt["node"]
            elif evt["type"] == self.evt_map["close"]:
                topo[evt["peer"]] = None
            else:
                continue

            hopcnt = self._cnt_hops(topo)

            for line in data:
                line["x"].append(self.ana.t_norm(evt["t"]))

            data[0]["y"].append(len(hopcnt))
            if len(hopcnt) > 0:
                data[1]["y"].append(max(hopcnt))
                data[2]["y"].append(statistics.mean(hopcnt))
            else:
                data[1]["y"].append(0)
                data[2]["y"].append(0)

        if len(timespan) == 2 and timespan[1] != None:
            for line in data:
                line["x"].append(timespan[1])
                line["y"].append(line["y"][-1])

        xt = self.ana.plotter.get_ticks([l["x"] for l in data], xlim)
        info = {
            "title": "Hop Count",
            "xlabel": "Experiment runtime [in s]",
            "ylabel": "Number of Hops/Links",
            "suffix": "hopcnt",
            "xlim": xt["lim"],
            "xticks": xt["ticks"],
            "xtick_lbl": xt["ticks"],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            "plotter": "line",
            "step": True,
        }
        self.ana.plotter.linechart4(info, data)


    def plot_hopcnt(self, timespan=[None, None], xlim=None):
        cfg = self.ana.plotsetup(None, None, timespan)

        # plot: min, max, avg, mean
        if len(self.meshconn) == 0:
            print("Plot Hopcount: SKIPPING -> node meshconn events")
            return

        data = [
            {"x": [self.ana.t_norm(cfg["first"])], "y": [0], "label": "# of links"},
            {"x": [self.ana.t_norm(cfg["first"])], "y": [0], "label": "hop count: max"},
            {"x": [self.ana.t_norm(cfg["first"])], "y": [0], "label": "hop count: average"},
            # {"x": [self.ana.t_norm(cfg["first"])], "y": [0], "label": "hop count: median"},
        ]
        hops = {n: 0.0 for n in self.ana.desc["used_nodes"]}

        for evt in self.meshconn:
            if self.ana.plotter.filter(cfg, None, evt["time"]):
                continue

            node = evt["node"]
            peer = evt["peer"]

            if evt["evt"] == "conn_uplink":
                hops[node] = hops[peer] + 1.0
            elif evt["evt"] == "close_uplink":
                hops[node] = 0

            hopnum = [hops[n] for n in hops if hops[n] > 0]

            data[0]["y"].append(len(hopnum))
            if len(hopnum) > 0:
                data[1]["y"].append(max(hopnum))
                data[2]["y"].append(statistics.mean(hopnum))
                # data[3]["y"].append(statistics.median(hopnum))
            else:
                data[1]["y"].append(0)
                data[2]["y"].append(0)
                # data[3]["y"].append(0)
            for line in data:
                line["x"].append(self.ana.t_norm(evt["time"]))

        if len(timespan) ==2 and timespan[1] != None:
            for line in data:
                line["x"].append(timespan[1])
                line["y"].append(line["y"][-1])

        xt = self.ana.plotter.get_ticks([l["x"] for l in data], xlim)
        info = {
            "title": "Hop Count",
            "xlabel": "Experiment runtime [in s]",
            "ylabel": "Number of Hops/Links",
            "suffix": "hopcnt",
            "xlim": xt["lim"],
            "xticks": xt["ticks"],
            "xtick_lbl": xt["ticks"],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            "plotter": "line",
            "step": True,
        }
        self.ana.plotter.linechart4(info, data)

