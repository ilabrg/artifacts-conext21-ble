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
import re
import sys
import yaml
import json
import math
from datetime import datetime
from tools.exputil.plotter import Plotter
from tools.exputil.expbase import Expbase

CFG_DFLT_SITE = "saclay"

class Ana(Expbase):

    def __init__(self, logfile):
        # read environment
        super().__init__()
        self.setup_ana(logfile)

        self.re_desc = re.compile(r'exp: (?P<cat>[-\.a-zA-Z0-9_]+): (?P<val>.+)')
        self.re_logline = re.compile(r'(?P<time>\d+\.\d+);'
                                     r'(?P<node>[a-zA-Z0-9-]+);'
                                     r'(?P<output>.*)')
        self.re_ownaddr = re.compile(r'Own Address: (?P<mac>[:a-zA-Z0-9]+)'
                                     r' -> \[(?P<l2addr>[:a-zA-Z0-9]+)\]')
        self.re_logline_pyterm = re.compile(r'^>? *(?P<time>\d+-\d+-\d+ \d+:\d+:\d+,\d+) # +'
                                            r'(?P<line>.+)')

        self.t = {
            "prep": 0,          # time of first entry in the log file, start of experiment
            "start": 0,         # time of first payload activity -> TIME 0
            "end": 0,           # time of last payload effecting event
            "finish": 0,        # time of last entry in log file
            "duration": 0,      # time span from start to end (end - start)
        }

        self.statfile = open("{}{}".format(self.plotbase, ".stat"), "w", encoding="utf-8", buffering=1)

        # setup the plotter
        self.plotter = Plotter(self.plotbase)

        # parse experiment description
        self.desc = {}
        self.parse_desc()


    def reltime(self, timestamp):
        return timestamp - self.t["start"]


    def nodename_from_mac(self, mac):
        node = self.nodename_from_mac2(mac)
        if node == None:
            sys.exit("error: unable to find node with addr {}".format(mac))
        return node


    def nodename_from_mac2(self, mac):
        mac = mac.lower()
        for n in sorted(self.nodecfg):
            if 'addr_mac' in self.nodecfg[n] and self.nodecfg[n]['addr_mac'] == mac:
                return n
        return None


    def nodename_from_l2addr(self, l2addr):
        l2addr = l2addr.lower()
        for node in sorted(self.nodecfg):
            if 'addr_l2' in self.nodecfg[node] and self.nodecfg[node]['addr_l2'] == l2addr:
                return node
        sys.exit("error: unable to find node with addr {}".format(l2addr))


    def nodes_mac(self, node):
        return self.nodecfg[node]['addr_mac'].lower()


    def parse_desc(self):
        with open(self.logfile, "r", encoding="utf-8") as f:
            for line in f:
                if line == "----\n":
                    return;
                m = self.re_desc.match(line)
                if m:
                    cat = m.group("cat")
                    if cat == "used_nodes":
                        self.desc[cat] = [n[1:-1] for n in m.group("val")[1:-1].split(", ")]
                    elif cat == "site":
                        self.get_nodecfg(m.group("val"))
                    elif m.group("cat") not in self.desc:
                        self.desc[cat] = m.group("val")
                    # TODO: do 'real' parsing of description


    def plotsetup(self, nodes, binsize, timespan):
        '''
        nodes: list of nodes or None for all nodes
        binsize: binsize in seconds
        timespan:
                  [0, 0] -> experiment runtime, from t[start] to t[end]
                  [None, None] -> full runtime, from t[prep] to t[finish]
                  [N, 0] -> from t[start] + N to t[end]
                  ...
        '''
        cfg = {"binsize": binsize}

        # set nodes
        if nodes == None:
            cfg["nodes"] = self.desc["used_nodes"]
        else:
            if nodes[0] == "ex":
                cfg["nodes"] = [n for n in self.desc["used_nodes"] if n not in nodes]
            else:
                cfg["nodes"] = nodes

        # set timespan
        if timespan == None:
            cfg["first"] = self.t["start"]
            cfg["last"] = self.t["end"]
        else:
            if timespan[0] == None:
                cfg["first"] = self.t["prep"]
            else:
                cfg["first"] = self.t["start"] + timespan[0]
            if timespan[1] == None:
                cfg["last"] = self.t["finish"]
            else:
                cfg["last"] = self.t["start"] + timespan[1]
        # make sure first point in time is a multiple of binsizes back
        if cfg["first"] < self.t["start"] and cfg["binsize"] != None:
            cfg["first"] = self.t["start"] - (math.ceil((self.t["start"] - cfg["first"]) / cfg["binsize"]) * cfg["binsize"])
        cfg["dur"] = cfg["last"] - cfg["first"]


        return cfg


    def t_norm(self, time):
        return time - self.t["start"]


    def t_init(self, t_first, t_last):
        self.t["prep"] = t_first
        self.t["start"] = t_first
        self.t["end"] = t_last
        self.t["finish"] = t_last
        self.t["duration"] = t_last - t_first


    def parse_log(self, cb):
        t_first = 0
        t_last = 0

        with open(self.logfile, "r", encoding="utf-8") as f:
            for line in f:
                m = self.re_logline.match(line)
                if m:
                    time = float(m.group('time'))
                    node = m.group("node")
                    output = m.group("output")

                    if t_first == 0:
                        t_first = time
                    if time > t_last:
                        t_last = time

                    m = self.re_ownaddr.search(output)
                    if m:
                        mac = m.group('mac').lower()
                        l2addr = m.group('l2addr').lower()
                        if self.nodecfg[node]['addr_mac'] != mac:
                            print("Warning: addr conf for {} broken "
                                  "(cfg {} but is {})".format(node,
                                                      self.nodecfg[node]['addr_mac'],
                                                      mac))
                            self.nodecfg[node]['addr_mac'] = mac
                            self.nodecfg[node]['addr_l2'] = l2addr

                    cb(time, node, output)

        self.t_init(t_first, t_last)


    def parse_log_pyterm(self, cb):
        t_first = 0
        t_last = 0

        if not self.node:
            self.node = "local-0"

        with open(self.logfile, "r", encoding="utf-8") as f:
            for line in f:
                m = self.re_logline_pyterm.match(line)
                if m:
                    t = datetime.strptime(m.group("time") + "000",
                                            "%Y-%m-%d %H:%M:%S,%f").timestamp()

                    if t_first == 0:
                        t_first = t
                    if t > t_last:
                        t_last = t

                    cb(t, self.node, m.group("line"))

        self.t_init(t_first, t_last)


    def statwrite(self, line, end=True):
        if end:
            self.statfile.write("{}\n".format(line))
            print(line)
        else:
            self.statfile.write("{}".format(line))
            print(line, end="")


    def warn_blocking(self, msg):
        print("\n@@@@@@@@@@ WARNING @@@@@@@@@@\n: {}".format(msg))
        print("Press any key to continue")
        sys.stdin.read(1)


    def write_overview(self, llstats, expstats, topo):
        outfile = f'{self.plotbase}_overview.json'
        stats = {
            "name": self.outname,
            "pdr_app": expstats.flows_cnt["sum"]["rate_ack"],
            "pdr_ll": llstats.sums["rate"] * 100,
            "reconns": topo.stats()["reconn"],
            "latency": expstats.stats(),
            # "latency":
            #   {"latency_avg": x,
            #    "latency_min": x,
            #    "latency_max": x,
            #    "latency_all": []
            #   }
        }
        with open(outfile, "w", encoding="utf-8") as f:
            json.dump(stats, f)


