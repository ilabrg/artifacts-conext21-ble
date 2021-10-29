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
import argparse
import json
from datetime import datetime
from tools.exputil.ana import Ana
from tools.exputil.topo import Topo
from tools.exputil.expstats import Expstats
from tools.exputil.alive import Alive
from tools.exputil.connitvl import Connitvl
# from tools.exputil.ifconfigval import Ifconfigval
from tools.exputil.llstats import LLStats


class Results(Ana):
    def __init__(self, logfile):
        super().__init__(logfile)

        self.ips = {}

        self.alive = Alive(self)
        self.connitvl = Connitvl(self)
        # self.ifconfigval = Ifconfigval(self)

        self.expstats = Expstats(self)
        self.topo = Topo(self)
        self.llstats = LLStats(self)

        self.parse_log(self.on_logline)


        self.expstats.finish()
        self.llstats.finish()
        self.topo.finish()

        # export overview
        self.write_overview(self.llstats, self.expstats, self.topo)

        print("\nRESULTS")
        self.llstats.summary()
        self.alive.summary()
        self.connitvl.summary()
        # self.ifconfigval.summary()
        self.expstats.summary()
        self.topo.summary()

        print("\nRESULTS")

        # export raw data
        # expfile = f"{self.plotbase}_raw.json"

        # raw = {}
        # raw["t"] = self.t
        # raw["alive"] = self.alive.getraw()
        # raw["expstats"] = self.expstats.getraw()
        # raw["llstats"] = self.llstats.getraw()

        # with open(expfile, "w", encoding="utf-8") as f:
        #     json.dump(raw, f)
        # print("RAW data has been written to {}".format(expfile))



    def on_logline(self, time, node, output):
        self.alive.update(time, node, output)
        self.connitvl.update(time, node, output)
        # self.ifconfigval.update(time, node, output)
        self.expstats.update(time, node, output)
        self.topo.update(time, node, output)
        self.llstats.update(time, node, output)

        # get global IPv6 addresses
        m = re.search(r'inet6 addr: (?P<ip>(2001\:)?affe\:\:[\:a-z0-9]+)', output.lower())
        if m:
            if not "addr_ip" in self.nodecfg[node]:
                self.nodecfg[node]["addr_ip"] = m.group("ip")
                self.ips[m.group("ip")] = node
            elif self.nodecfg[node]["addr_ip"] != m.group("ip"):
                print("Warning: IPv6 addr for {} is deviating: {} vs {}".format(
                      node, self.nodecfg[node]["addr_ip"], m.group("ip")))


    def plotme(self):
        producers = copy.copy(self.desc["used_nodes"])
        if "expvars.SINK" in self.desc:
            producers.remove(self.desc["expvars.SINK"])
        prod = ["nrf52dk-1", "nrf52dk-8", "nrf52840dk-7",
                "nrf52dk-7", "nrf52840dk-8", "nrf52dk-4", "nrf52dk-9", "nrf52dk-2", "nrf52dk-3",
                "nrf52840dk-10", "nrf52dk-5", "nrf52840dk-6", "nrf52dk-10", "nrf52840dk-9"]
        styles = ["-", "-", "-",
                  "--", "--", "--", "--", "-", "--", "--",
                  ":", ":", ":", ":", ":"]

        # self.llstats.plot_rateline(binsize=10, ylim=[.0, 1.01], timespan=[None, None])

        # self.topo.plot_hopcnt(timespan=[None, 0])
        # self.topo.plot_hopcnt2(timespan=[None, 0])
        # self.expstats.plot_of_pn()

        # self.llstats.plot_phy_verify()
        # self.llstats.plot_bufusage()
        # self.llstats.plot_phy_usage_sum()
        # self.llstats.plot_phy_cnt_sum()
        # self.llstats.plot_phy_usage(stat="tx")
        # self.llstats.plot_phy_usage(stat="rx")
        # self.llstats.plot_phy_cnt("rx")
        # self.llstats.plot_phy_cnt("tx")

        self.llstats.plot_rateline(binsize=10, ylim=[.0, 1.01])
        self.llstats.plot_rateline_pn(binsize=5)
        self.llstats.plot_bufusage()


        self.expstats.plot_flow_pdr([["t_rx", "Pkts received by Consumer"],
                                     ["t_ack", "ACKs received by Producers"]], ylim=[.0, 1.01])
        self.expstats.plot_flow_pdr_pn("t_ack")

        self.expstats.plot_latency_box()
        # self.expstats.plot_cdf(xlim=[0, 1])
        self.expstats.plot_cdf()
        # self.expstats.plot_cdf_pn(styles=styles, stat="rx", xlim=[0, 1])
        self.expstats.plot_cdf_pn(styles=styles, stat="rx")
        # self.expstats.plot_cdf_pn(styles=styles, stat="ack", xlim=[0, 1])
        self.expstats.plot_cdf_pn(styles=styles, stat="ack")
        # self.expstats.plot_cdf_pn(prod, styles=styles, stat="rx", xlim=[0, 1])
        # self.expstats.plot_cdf_pn(prod, styles=styles, stat="rx")
        # self.expstats.plot_cdf_pn(prod, styles=styles, stat="ack", xlim=[0, 1])
        # self.expstats.plot_cdf_pn(prod, styles=styles, stat="ack")

        if len(self.llstats.events) > 0:
            # self.llstats.plot_chanrate(binsize=15)
            self.llstats.plot_chanrate(binsize=15, timespan=[0, 3600])

        self.expstats.plot_delay_heatmap(binsize=15, aggr="avg", nodes=prod)
        self.expstats.plot_delay_heatmap(binsize=15, aggr="min", nodes=prod)
        self.expstats.plot_delay_heatmap(binsize=15, aggr="max", nodes=prod)

        self.llstats.plot_rateline(binsize=10, ylim=[.0, 1.01], nodes=["nrf52dk-1"])
        self.expstats.plot_flow_pdr([["t_rx", "Pkts received by Consumer"],
                                     ["t_ack", "ACKs received by Producers"]], ylim=[.0, 1.01], nodes=["nrf52dk-1"])



        # self.llstats.plot_txcnt()
        # self.llstats.plot_txcnt(binsize=10)
        # self.llstats.plot_txcnt(binsize=30)
        # sys.exit("foo")

        # self.expstats.plot_evtcnt_boxes_pn(["N_RX", "N_TX"], ylim=(0, 450))
        # self.expstats.plot_evtcnt_boxes_pn(["A_TX", "A_RX", "A_ACK"], fulltime=True, ylim=(0, 450))
        # self.llstats.plot_anchor_offset()
        # self.llstats.plot_anchors()

        # nodesel = ["nrf52dk-2", "nrf52dk-10", "nrf52840dk-9"]
        # self.llstats.plot_chanrate(nodes=nodesel + ["nrf52840dk-7"], binsize=5)
        # self.expstats.plot_delay_heatmap(binsize=30, aggr="avg", nodes=nodesel + ["nrf52840dk-7"])

        # self.expstats.plot_stats(["A_TX", "A_RX", "A_ACK", "N_TX", "N_RX"], nodes=producers)
        # self.expstats.plot_stats_pn(["A_TX", "A_RX", "A_ACK", "N_TX", "N_RX"], nodes=producers)

        # self.expstats.plot_stats(["A_TX", "A_RX", "A_ACK", "N_TX", "N_RX"], timespan=[350,1000])
        # self.expstats.plot_stats_pn(["A_TX", "A_RX", "A_ACK", "N_TX", "N_RX"], timespan=[350,1000])

        # self.expstats.plot_stats(["A_TX", "A_RX", "A_ACK", "N_TX", "N_RX"], timespan=[350,1000],
                    # nodes=["nrf52dk-2", "nrf52dk-10", "nrf52840dk-9"])

        # self.expstats.plot_stats_pn(["A_TX", "A_ACK", "N_TX", "N_RX"], timespan=[350,1000], nodes=nodesel)








        # self.expstats.plot_stats(["A_TX", "A_RX", "A_ACK", "A_TX_RE", "A_TX_ER"])
        # self.expstats.plot_stats_pn(["A_TX", "A_RX", "A_ACK", "A_TX_RE", "A_TX_ER"], nodes=producers)

        # # self.expstats.plot_cdf_pn()

        # self.expstats.plot_stats(["I_D", "B_PL", "R_E_PTO", "F_DD", "F_AD"])
        # self.expstats.plot_stats_pn(["I_D", "B_PL", "R_E_PTO", "F_DD", "F_AD"])

        # self.expstats.plot_stats(["N_RX_ER", "N_RX_NPB", "N_TX_NC", "N_TX_ER", "N_TX_NNB"])
        # self.expstats.plot_stats_pn(["N_RX_ER", "N_RX_NPB", "N_TX_NC", "N_TX_ER", "N_TX_NNB"])
        # self.expstats.plot_stats(["A_TX_F", "A_TX_ER", "A_ACK_ER", "A_ACK_TO"])
        # self.expstats.plot_stats(["N_RX", "N_TX", "N_TX_M"])
        # self.expstats.plot_stats_pn(["N_RX", "N_TX", "N_TX_M"])


def main(args):
    res = Results(args.logfile)
    res.plotme()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("logfile", default="", help="output dump")
    args = p.parse_args()
    main(args)
