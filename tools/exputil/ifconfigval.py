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
import copy


PREFIX = "2001:affe"


IFCONFIG = {
    "time": 0,
    "l2_addr": None,
    "ip_addr": None,
}

BAD_PS = {
    "node": None,
    "time": 0,
    "pid": 0,
    "thread": None,
    "state": None,
    "should": None,
}

PS_GOODSTATE = {
    "nimble_host": "bl anyfl",
    "nimble_ctrl": "bl anyfl",
    "nimble_netif": "bl rx",
}


class Ifconfigval:

    def __init__(self, ana):
        self.ana = ana
        self.events = {n: [] for n in self.ana.desc["used_nodes"]}
        self.bad_ps = []


    def update(self, time, node, line):
        m = re.search(r'^>? *ifconfig$', line)
        if m:
            e = copy.deepcopy(IFCONFIG)
            e["time"] = time
            self.events[node].append(e)

        m = re.search(r'Iface +\d+ +HWaddr: +(?P<l2_addr>[a-fA-F0-9:]+)', line)
        if m:
            if not self.events[node] or self.events[node][-1]["l2_addr"]:
                self.ana.warn_blocking("Ifconfig: Node {} has output without call: {}".format(
                    node, self.events[node]))
                return
            self.events[node][-1]["l2_addr"] = str(m.group("l2_addr"))



        m = re.search(r' +inet6 addr: (?P<ip_addr>[a-fA-F0-9:]+) +scope: global', line)
        if m:
            if not self.events[node] or self.events[node][-1]["ip_addr"]:
                self.ana.warn_blocking("Ifconfig: Node {} has IP output without ifconfig call".format(
                    node, self.events[node]))
                return
            self.events[node][-1]["ip_addr"] = str(m.group("ip_addr"))

        m = re.search(r'.+(?P<pid>\d+) +\| (?P<name>.+) +\| (?P<state>.+) +_ \| +(?P<prio>\d+)', line)
        if m:
            name = m.group("name").strip()
            state = m.group("state").strip()
            if name in PS_GOODSTATE:
                if state != PS_GOODSTATE[name]:
                    bad = copy.deepcopy(BAD_PS)
                    bad["node"] = node
                    bad["time"] = time
                    bad["pid"] = int(m.group("pid"))
                    bad["thread"] = name
                    bad["state"] = state
                    bad["should"] = PS_GOODSTATE[name]
                    self.bad_ps.append(bad)


    def summary(self):
        self.ana.statwrite("\nThread State Validation:")
        for bad in self.bad_ps:
            self.ana.warn_blocking("PS: Node {} has broken thread {} (pid:{}) is:'{}'' should:'{}' @ {} ({})".format(
                bad["node"], bad["thread"], bad["pid"], bad["state"], bad["should"],
                bad["time"] - self.ana.t["start"], bad["time"]))

        self.ana.statwrite("\nIfconfig call summary:")
        for n in self.ana.nsort(self.events):
            for e in self.events[n]:
                t = e["time"] - self.ana.t["start"]

                if not e["l2_addr"]:
                    self.ana.warn_blocking("Ifconfig: Node {} is Stuck at {} ({}): {}".format(
                        n, t, e["time"], e))
                else:
                    if e["l2_addr"].lower() != self.ana.nodecfg[n]["addr_mac"].lower():
                        self.ana.warn_blocking("Ifconfig: Node {} has bad L2 Addr (is:{} should:{}) @ ifconfig {} ({})".format(
                            n, e["l2_addr"].lower(), self.ana.nodecfg[n]["addr_mac"].lower(),
                            t, e["time"]))

                # self.ana.statwrite("{:<15}: ifconfig {} ({}): l2addr:{} ipaddr:{}".format(
                #     n, t, e["time"], e["l2_addr"], e["ip_addr"]))

