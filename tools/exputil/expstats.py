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
import math
import numpy as np

FLOW = {
    "seq": None,        # ID of the flow -> seq number without direction char (a-bbb)
    "src": None,        # filled by A_TX event
    "dst": None,        # filled by A_RX event
    "ack": None,        # filled by A_ACK event -> MUST be same as src
    "path": [],         # list of nodes that mark the packets path (by logtime)
    "events": [],       # list of events regarding this flow
    "t_tx": [],         # timestamp when pkt was sent ->    on A_TX
    "t_tx_er": [],      # timestamp when pkt send error occured -> on A_TX_ER
    "t_tx_re": [],      # timestamp when pkt was resent ->    on A_TX_RE
    "t_rx": [],         # timestamp when pkt was received -> on A_RX
    "t_ack": [],        # timestamp when pkt was acked -> on A_ACK
    "drop_tx": [],      # DROP tuple for packet drops on request path
    "drop_ack": [],     # DROP tuple for packet drops on reply path
    "drop_nc_tx": [],   # DROP tuple for packets dropped when not connected, dir TX
    "drop_nc_ack": [],  # DROP tuple for packets dropped when not connected, dir ACK
}

EVT = {
    "node": None,       # node that triggered the event
    "time": 0,          # timestamp when the event happened
    "type": None,       # type of the event -> e.g. A_TX
    "seq": None,        # sequence number given with that event
}

DROP = {
    "node": None,       # node that dropped the packet
    "time": 0,          # time when the drop happened
}

FLOW_CNT = {
    "all": 0,
    "tx": 0,
    "tx_re": 0,
    "tx_er": 0,
    "rx": 0,
    "ack": 0,
    "rate_rx": 0,
    "rate_ack": 0,
    "tx_dups": 0,
    "rx_dups": 0,
    "tx_re_dups": 0,
    "ack_dups": 0,
    "drop_tx": 0,
    "drop_ack": 0,
    "drop_nc_tx": 0,
    "drop_nc_ack": 0,
}

COLORMAP_TYPES = {
    "N_TX": "mediumblue",
    "N_RX": "red",
    "A_TX": "darkorange",
    "A_RX": "greenyellow",
    "A_ACK": "darkgreen",
    "A_ACK_TO": "violet",
    "A_TX_ER": "purple",
    # more here
}

class Expstats:

    def __init__(self, ana):
        self.ana = ana

        self.evt = []
        self.flows = []
        self.flows_cnt = {}
        self.flows_map = {}

        self.credits = {n: {} for n in self.ana.desc["used_nodes"]}
        self.of_evt = []


    def getraw(self):
        return {
            "evt": self.evt,
            "flows": self.flows,
            "flows_cnt": self.flows_cnt,
            "flows_map": self.flows_map,
            "credits": self.credits,
        }


    def readraw(self, raw):
        self.evt = raw["evt"]
        self.flows = raw["flows"]
        self.flows_cnt = raw["flows_cnt"]
        self.flows_map = raw["flows_map"]
        self.credits = raw["credits"]


    def update(self, time, node, line):
        m = re.search(r'^>? *~(?P<type>[A-Z]+(_[A-Z_]+)*)'
                       '(:(?P<info>.+))?', line)
        if m:
            evt = copy.deepcopy(EVT)
            evt["node"] = node
            evt["time"] = time
            evt["type"] = m.group("type")

            if m.group("info"):
                if ">" in m.group("info") or "<" in m.group("info"):
                    evt["seq"] = m.group("info")
                    self.update_flow(evt)
                elif evt["type"] == "OF":
                    self.of_evt.append({"node": node, "time": time, "of": int(m.group("info"))})
                else:
                    mm = re.match(r'(?P<chan>0x[a-f0-9]+);(?P<handle>\d+)'
                                  r';(?P<rx_credits>\d+);(?P<tx_credits>\d+);(?P<change>\d+)', m.group("info"))
                    if mm:
                        chan = mm.group("chan")
                        handle = mm.group("handle")
                        rx_credits = int(mm.group("rx_credits"))
                        tx_credits = int(mm.group("tx_credits"))
                        change = int(mm.group("change"))

                        if chan not in self.credits[node]:
                            self.credits[node][chan] = [{"handle": handle,
                                                         "init-rx": 0,
                                                         "init-tx": 0,
                                                         "min-rx": 0,
                                                         "max-rx": 0,
                                                         "min-tx": 0,
                                                         "max-tx": 0,
                                                         "sig-cnt": 0,
                                                         "upd-cnt": 0,}]
                        if evt["type"] == "H_CI" and self.credits[node][chan][-1]["init-rx"] == 0:
                            self.credits[node][chan][-1]["init-rx"] = rx_credits
                            self.credits[node][chan][-1]["init-tx"] = tx_credits
                        elif evt["type"] == "H_CI":
                            self.credits[node][chan].append({"handle": handle,
                                                              "init-rx": rx_credits,
                                                              "init-tx": tx_credits,
                                                              "min-rx": 0,
                                                              "max-rx": 0,
                                                              "min-tx": 0,
                                                              "max-tx": 0,
                                                              "sig-cnt": 0,
                                                              "upd-cnt": 0,})

                        if evt["type"] in ["H_CS", "H_CRR", "H_CU", "H_CTX"]:
                            if rx_credits > self.credits[node][chan][-1]["max-rx"]:
                                self.credits[node][chan][-1]["max-rx"] = rx_credits
                            if rx_credits < self.credits[node][chan][-1]["min-rx"]:
                                self.credits[node][chan][-1]["min-rx"] = rx_credits
                            if tx_credits > self.credits[node][chan][-1]["max-tx"]:
                                self.credits[node][chan][-1]["max-tx"] = tx_credits
                            if tx_credits < self.credits[node][chan][-1]["min-tx"]:
                                self.credits[node][chan][-1]["min-tx"] = tx_credits

                        if evt["type"] == "H_CS":
                            self.credits[node][chan][-1]["sig-cnt"] += change
                        if evt["type"] == "H_CU":
                            self.credits[node][chan][-1]["upd-cnt"] += change

            self.evt.append(evt)

    def _flowid(self, seq):
        return seq.replace("<", "-").replace(">", "-")

    def _flowprint(self, flow):
        self.ana.statwrite("FLOW {}: {} -> {} -> {}  | PATH:{}".format(
                flow["seq"], flow["src"], flow["dst"], flow["ack"], flow["path"]))
        for evt in flow["events"]:
            self.ana.statwrite("    {:>14}: {:>8} {} ({})".format(
                evt["node"], evt["type"], (evt["time"] - self.ana.t["start"]), evt["time"]))
        if flow["dst"] == None:
            self.ana.statwrite("    {:>14}   Designated next hop: {}".format("", self.ana.topo.topo[flow["path"][-1]]["p"]))


    def update_flow(self, evt): #
        sid = self._flowid(evt["seq"])
        flow = None
        if sid in self.flows_map:
            flow = self.flows_map[sid]
        else:
            flow = copy.deepcopy(FLOW)
            flow["seq"] = sid
            flow["path"].append(evt["node"])
            self.flows.append(flow)
            self.flows_map[sid] = flow

        flow["events"].append(evt)

        if flow["path"][-1] != evt["node"]:
            flow["path"].append(evt["node"])

        if evt["type"] == "A_TX_ER":
            if flow["src"] != None and flow["src"] != evt["node"]:
                print("Warning: duplicate SOURCE node for {}".format(sid))
            flow["src"] = evt["node"]
            flow["t_tx_er"].append(evt["time"])

        if evt["type"] == "A_TX":
            if flow["src"] != None and flow["src"] != evt["node"]:
                print("Warning: duplicate SOURCE node for {}".format(sid))
            flow["src"] = evt["node"]
            flow["t_tx"].append(evt["time"])

        if evt["type"] == "A_TX_RE":
            flow["t_tx_re"].append(evt["time"])

        elif evt["type"] == "A_RX":
            if flow["dst"] and flow["dst"] != evt["node"]:
                print("Warning: duplicate DEST node for {}".format(sid))
            flow["dst"] = evt["node"]
            flow["t_rx"].append(evt["time"])

        elif evt["type"] == "A_ACK":
            if flow["ack"] and flow["ack"] != evt["node"]:
                print("Warning: duplicate ACK node for {}".format(sid))
            flow["ack"] = evt["node"]
            flow["t_ack"].append(evt["time"])

        elif evt["type"] == "I_D" or evt["type"] == "N_TX_NC":
            drop = copy.deepcopy(DROP)
            drop["node"] = evt["node"]
            drop["time"] = evt["time"]

            if evt["type"] == "I_D":
                if ">" in evt["seq"]:
                    flow["drop_tx"].append(drop)
                else:
                    flow["drop_ack"].append(drop)
            else:
                if ">" in evt["seq"]:
                    flow["drop_nc_tx"].append(drop)
                else:
                    flow["drop_nc_ack"].append(drop)


    def finish(self):
        if len(self.evt) == 0:
            return

        self.ana.t["start"] = self.ana.t["finish"]
        self.ana.t["end"] = self.ana.t["prep"]

        for e in self.evt:
            if e["type"].find("A_") == 0:
                if e["time"] < self.ana.t["start"]:
                    self.ana.t["start"] = e["time"]
                if e["time"] > self.ana.t["end"]:
                    self.ana.t["end"] = e["time"]

        self.ana.t["duration"] = self.ana.t["end"] - self.ana.t["start"]

        # count flow events
        self.flows_cnt = {n: copy.deepcopy(FLOW_CNT) for n in self.ana.desc["used_nodes"]}
        self.flows_cnt["sum"] = copy.deepcopy(FLOW_CNT)
        for flow in self.flows:
            if flow["src"] == None:
                print("FLOW is broken {}".format(flow))
                continue

            self.flows_cnt["sum"]["all"] += 1
            self.flows_cnt[flow["src"]]["all"] += 1

            self.flows_cnt[flow["src"]]["tx_re"] += len(flow["t_tx_re"])
            self.flows_cnt["sum"]["tx_re"] += len(flow["t_tx_re"])
            self.flows_cnt[flow["src"]]["tx_er"] += len(flow["t_tx_er"])
            self.flows_cnt["sum"]["tx_er"] += len(flow["t_tx_er"])


            for feat in ["tx", "rx", "ack"]:
                numof = len(flow["t_{}".format(feat)])

                if feat == "tx" and numof > 1:
                    print(flow)

                if numof > 0:
                    self.flows_cnt["sum"][feat] += 1
                    self.flows_cnt[flow["src"]][feat] += 1
                if numof > 1:
                    self.flows_cnt["sum"]["{}_dups".format(feat)] += (numof - 1)
                    self.flows_cnt[flow["src"]]["{}_dups".format(feat)] += (numof - 1)
            for field in ["drop_tx", "drop_ack", "drop_nc_tx", "drop_nc_ack"]:
                if len(flow[field]) > 0:
                    # if len(flow[field]) > 1:
                    #     self.ana.warn_blocking("flow {}: dropped multiple times {}".format(field, flow))

                    self.flows_cnt["sum"][field] += 1
                    self.flows_cnt[flow[field][0]["node"]][field] += 1


            # if len(flow["drop_tx"]) > 0:
            #     for drop in flow["drop_tx"]
            #     self.flows_cnt["sum"]["drop_tx"] += 1
            #     self.flows_cnt[flow["src"]]["drop_tx"] += 1
            # if len(flow["drop_ack"]) > 0:
            #     self.flows_cnt["sum"]["drop_ack"] += 1
            #     self.flows_cnt[flow["src"]]["drop_ack"] += 1
            # if len(flow["drop_nc_tx"]) > 0:
            #     self.flows_cnt["sum"]["drop_nc_tx"] += 1
            #     self.flows_cnt[flow["src"]]["drop_nc_tx"] += 1
            # if len(flow["drop_nc_ack"]) > 0:
            #     self.flows_cnt["sum"]["drop_nc_ack"] += 1
            #     self.flows_cnt[flow["src"]]["drop_nc_ack"] += 1

        self.flows_cnt["sum"]["rate_rx"] = self.flows_cnt["sum"]["rx"] / self.flows_cnt["sum"]["tx"] * 100.0
        self.flows_cnt["sum"]["rate_ack"] = self.flows_cnt["sum"]["ack"] / self.flows_cnt["sum"]["tx"] * 100.0
        for n in self.flows_cnt:
            if self.flows_cnt[n]["tx"] > 0:
                self.flows_cnt[n]["rate_rx"] = self.flows_cnt[n]["rx"] / self.flows_cnt[n]["tx"] * 100.0
                self.flows_cnt[n]["rate_ack"] = self.flows_cnt[n]["ack"] / self.flows_cnt[n]["tx"] * 100.0


    def summary(self):
        stats = {n: {} for n in self.ana.desc["used_nodes"]}
        stats["sum"] = {}
        # stats[node][type] = ['sum', 'data_traffic', 'ctrl_traffic', 'data_req', 'data_resp']

        for n in stats:
            for t in  ["A_RX", "A_TX", "A_TX_RE", "A_ACK", "A_TX_ER",
                       "N_RX", "N_TX", "N_TX_NC", "N_TX_A", "I_D", "C_RXER", "N_RX_NPB"]:
                stats[n][t] = [0, 0, 0, 0, 0]
        for evt in self.evt:
            if evt["type"] not in stats["sum"]:
                for n in stats:
                    stats[n][evt["type"]] = [0, 0, 0, 0, 0]

            addto = [0]
            if evt["seq"] != None:
                addto.append(1)
                if ">" in evt["seq"]:
                    addto.append(3)
                else:
                    addto.append(4)
            else:
                addto.append(2)

            for i in addto:
                stats["sum"][evt["type"]][i] += 1
                stats[evt["node"]][evt["type"]][i] += 1


        self.ana.statwrite("Expstats summary:")
        self.ana.statwrite("Experiement timestamps: {}".format(self.ana.t))
        self.ana.statwrite("Experiement duration: {}s".format(self.ana.t["duration"]))

        self.ana.statwrite("\nExpstats: Summary of last link layer packet sent per node:")
        last = {n: 0.0 for n in self.ana.desc["used_nodes"]}
        for evt in self.evt:
            if evt["type"] == "N_TX" and evt["time"] > last[evt["node"]]:
                last[evt["node"]] = evt["time"]
        for n in self.ana.nsort(last):
            self.ana.statwrite("{:>13}  n_tx:{} ({})".format(n, last[n] - self.ana.t["start"], last[n]))

        self.ana.statwrite("\nExpstats: Summary of events:")

        for stat in sorted(stats["sum"]):
            self.ana.statwrite("{:<15}: {:>6}   (data:{:>6}, ctrl:{:>6})".format(stat,
                                                          stats["sum"][stat][0],
                                                          stats["sum"][stat][1],
                                                          stats["sum"][stat][2]))

        self.ana.statwrite("\nExpstats: Count of selected events per node, DATA TRAFFIC only")
        self.ana.statwrite("{:<15}: {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8}".format(
                            "node", "A_TX", "A_TX_RE", "A_TX_ER", "A_RX", "A_ACK", "N_TX", "N_TX_NC", "N_TX_A", "N_RX", "N_RX_NPB", "I_D"))
        for n in self.ana.nsort(stats):
            self.ana.statwrite("{:<15}: {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8}".format(
                                n,
                                stats[n]["A_TX"][1],
                                stats[n]["A_TX_RE"][1],
                                stats[n]["A_TX_ER"][1],
                                stats[n]["A_RX"][1],
                                stats[n]["A_ACK"][1],
                                stats[n]["N_TX"][1],
                                stats[n]["N_TX_NC"][1],
                                stats[n]["N_TX_A"][1],
                                stats[n]["N_RX"][1],
                                stats[n]["N_RX_NPB"][2],
                                stats[n]["I_D"][1]))

        self.ana.statwrite("\nExpstats: Count of selected events per node, ALL TRAFFIC")
        self.ana.statwrite("{:<15}: {:>6} {:>6} {:>7} {:>6} {:>6}  {:>8} {:>6} {:>6} {:>6}".format(
                            "node", "A_RX", "A_TX", "A_TX_RE", "N_RX", "N_TX", "A_TX_ER", "N_NC", "I_D", "C_RXER"))
        for n in self.ana.nsort(stats):
            self.ana.statwrite("{:<15}: {:>6} {:>6} {:>7} {:>6} {:>6} {:>8} {:>6} {:>6} {:>6}".format(
                                n,
                                stats[n]["A_RX"][0],
                                stats[n]["A_TX"][0],
                                stats[n]["A_TX_RE"][0],
                                stats[n]["N_RX"][0],
                                stats[n]["N_TX"][0],
                                stats[n]["A_TX_ER"][0],
                                stats[n]["N_TX_NC"][0],
                                stats[n]["I_D"][0],
                                stats[n]["C_RXER"][0]))


        self.ana.statwrite("\n#### Data traffic packet count verification ####")

        # Verify global link layer packet counts
        n_tx_sum = stats["sum"]["N_TX"][1]
        n_rx_sum = stats["sum"]["N_RX"][1]
        n_loss = n_tx_sum - n_rx_sum
        state = "OK" if n_tx_sum == n_rx_sum else "ER"
        self.ana.statwrite("---- Link layer Packets -> N_RX == N_TX")
        self.ana.statwrite("[{}] {} == {} --> DIFF: {}".format(state, n_rx_sum, n_tx_sum, n_loss))

        # Verify application layer packet count
        a_rx = stats["sum"]["A_RX"][1]
        a_tx = stats["sum"]["A_TX"][1]
        a_tx_re = stats["sum"]["A_TX_RE"][1]
        a_tx_er = stats["sum"]["A_TX_ER"][1]
        i_d = stats["sum"]["I_D"][3]
        n_nc = stats["sum"]["N_TX_NC"][3]
        a_rx_sum = a_tx + a_tx_re - a_tx_er - i_d - n_nc
        state = "OK" if a_rx == a_rx_sum else "ER"
        self.ana.statwrite("---- App packet count REQ -> A_RX = A_TX + A_TX_RE - A_TX_ER - I_D_req - N_NC_req")
        self.ana.statwrite("[{}] {} == {} ({} + {} - {} - {} - {})".format(
                            state, a_rx, a_rx_sum,
                            a_tx, a_tx_re, a_tx_er, i_d, n_nc))

        a_ack = stats["sum"]["A_ACK"][1]
        a_rx = stats["sum"]["A_RX"][1]
        i_d = stats["sum"]["I_D"][4]
        n_nc = stats["sum"]["N_TX_NC"][4]
        a_ack_sum = a_rx - i_d - n_nc
        state = "OK" if a_ack == a_ack_sum else "ER"
        self.ana.statwrite("---- App packet count RESP -> A_ACK = A_RX - I_D_resp - N_NC_resp")
        self.ana.statwrite("[{}] {} == {} ({} - {} - {})".format(
                            state, a_ack, a_ack_sum,
                            a_rx, i_d, n_nc))

        for n in self.ana.nsort(stats):
            print("n {}: {}".format(n, stats[n]["N_RX_NPB"]))

        self.ana.statwrite("---- Link layer data packets per Node -> N_TX == N_RX + A_TX + A_TX_RE - A_ACK - A_TX_ER - I_D - N_NC - N_RX_NPB")
        for n in self.ana.nsort(stats):
            n_tx = stats[n]["N_TX"][1]
            n_rx = stats[n]["N_RX"][1]
            a_tx = stats[n]["A_TX"][1]
            a_tx_re = stats[n]["A_TX_RE"][1]
            a_tx_er = stats[n]["A_TX_ER"][1]
            a_ack = stats[n]["A_ACK"][1]
            i_d = stats[n]["I_D"][1]
            n_nc = stats[n]["N_TX_NC"][1]
            n_rx_npb = stats[n]["N_RX_NPB"][0]
            n_tx_calc = n_rx + a_tx + a_tx_re - a_tx_er - a_ack - i_d - n_nc - n_rx_npb;
            state = "OK" if n_tx == n_tx_calc else "ER"
            self.ana.statwrite("[{}] {:<15}: {} == {} ({} + {} + {} - {} - {} - {} - {} - {})".format(
                                state, n, n_tx, n_tx_calc,
                                n_rx, a_tx, a_tx_re, a_ack, a_tx_er, i_d, n_nc, n_rx_npb))

        # self.ana.statwrite("---- Link layer data packets per Node -> N_RX_req = N_TX_req of each child node")
        # for n in self.ana.nsort(self.ana.desc["used_nodes"]):
        #     n_rx = stats[n]["N_RX"][3]
        #     n_rx_calc = 0
        #     for c in self.ana.topo.topo[n]["c"]:
        #         n_rx_calc += stats[c]["N_TX"][3]
        #     state = "OK" if n_rx == n_rx_calc else "ER"
        #     self.ana.statwrite("[{}] {:<15}: {} == {})".format(n, state, n_rx, n_rx_calc, n_rx_calc - n_rx))

        # self.ana.statwrite("\nLink layer losses:")
        # loss_list = {}
        # for evt in self.evt:
        #     if evt["type"] in ["N_TX", "N_RX"]:
        #         if evt["seq"] not in loss_list:
        #             loss_list[evt["seq"]] = 0
        #         if evt["type"] == "N_TX":
        #             loss_list[evt["seq"]] += 1
        #         if evt["type"] == "N_RX":
        #             loss_list[evt["seq"]] -= 1
        # for seq in loss_list:
        #     if loss_list[seq] > 0:
        #         self.ana.statwrite("{} ({}:{})".format(seq, self._flowid(seq), loss_list[seq]))
        #         self._flowprint(self.flows_map[self._flowid(seq)])


        self.ana.statwrite("Credits:")
        self.ana.statwrite("{:<15} {:10} {:1} {:8} {:8} {:8} {:8} {:8} {:8} {:8} {:8}".format(
                "node", "chan", "h",
                "init-rx", "init-tx", "min-rx", "max-rx", "min-tx", "max-tx", "sig", "upd"))
        for n in self.ana.nsort(self.credits):
            s = {"sig-cnt": 0, "upd-cnt": 0}
            for c in sorted(self.credits[n]):
                for con in self.credits[n][c]:
                    for f in con:
                        if f in s:
                            s[f] += con[f]
                    self.ana.statwrite("{:<15} {:10} {:1} {:8} {:8} {:8} {:8} {:8} {:8} {:8} {:8}".format(
                          n, c, con["handle"],
                          con["init-rx"], con["init-tx"], con["min-rx"], con["max-rx"],
                          con["min-tx"], con["max-tx"], con["sig-cnt"], con["upd-cnt"]))
            self.ana.statwrite("{:<15} {:10} {:1} {:8} {:8} {:8} {:8} {:8} {:8} {:8} {:8}".format(
                    n, "sum", "-", "-", "-", "-", "-", "-", "-", s["sig-cnt"], s["upd-cnt"]))



        self.ana.statwrite("\nExpstats summary of flows:")
        unack = []
        incomp = []
        drops = []
        dups = []
        for flow in self.flows:
            if flow["dst"] == None:
                incomp.append(flow)
            if flow["ack"] == None:
                unack.append(flow)
            if len(flow["t_tx"]) > 1 or len(flow["t_rx"]) > 1 or len(flow["t_ack"]) > 1:
                dups.append(flow)
            if len(flow["drop_tx"]) > 0 or len(flow["drop_ack"]) > 0:
                drops.append(flow)

            if flow["src"] == None:
                self.ana.statwrite("Warning: flow summary: flow without a SRC node")
                continue

        self.ana.statwrite("{:>13}  {:>6} {:>6} {:>6} {:>6} {:>6}  {:>7}  {:>7}  {:>6} {:>6} {:>6} {:>7} {:>8} {:>10} {:>11}".format(
              "node", "tx", "tx_re", "tx_er", "rx", "ack", "rate_rx", "rate_ack",
              "tx_dup", "rx_dup", "ack_du", "drop_tx", "drop_ack", "drop_nc_tx", "drop_nc_ack"))
        for n in self.ana.nsort(self.flows_cnt):
            self.ana.statwrite("{:>13}: {:>6} {:>6} {:>6} {:>6} {:>6} ({:>7.3f}%/{:>7.3f}%) {:>6} {:>6} {:>6} {:>7} {:>8} {:>10} {:>11}".format(
                  n, self.flows_cnt[n]["tx"], self.flows_cnt[n]["tx_re"], self.flows_cnt[n]["tx_er"],
                  self.flows_cnt[n]["rx"], self.flows_cnt[n]["ack"],
                  self.flows_cnt[n]["rate_rx"], self.flows_cnt[n]["rate_ack"],
                  self.flows_cnt[n]["tx_dups"], self.flows_cnt[n]["rx_dups"], self.flows_cnt[n]["ack_dups"],
                  self.flows_cnt[n]["drop_tx"], self.flows_cnt[n]["drop_ack"],
                  self.flows_cnt[n]["drop_nc_tx"], self.flows_cnt[n]["drop_nc_ack"]))

        # self.ana.statwrite("Flows - Duplicated packets")
        # for flow in dups:
        #     print("seq:{} src:{} dst:{} ack:{}".format(flow["seq"], flow["src"], flow["dst"], flow["ack"]))
        #     print("path: {}".format(flow["path"]))
        #     print("t_tx: {}".format(flow["t_tx"]))
        #     print("t_rx: {}".format(flow["t_rx"]))
        #     print("events:")
        #     for e in flow["events"]:
        #         print("- ", e)

        # self.ana.statwrite("Incomplete packets (count: {})".format(len(incomp)))
        # for flow in incomp:
        #     # self.ana.statwrite(flow)
        #     tmp = [t - self.ana.t["start"] for t in flow["t_tx"]]
        #     print("{:>7}: a_tx:{} ({})".format(flow["seq"], tmp, flow["t_tx"]))
        #     tmp = [t["time"] - self.ana.t["start"] for t in flow["drop_nc_tx"]]
        #     print("{:>7}  drop_nc_tx:{} ({})".format("", tmp, flow["drop_nc_tx"]))
        #     for e in flow["events"]:
        #         print("{:>14} {}".format("", e))

        # if len(unack) < 100:
        #     self.ana.statwrite("Unacked packets (count:{})".format(len(unack)))
        #     for flow in unack:
        #         self.ana.statwrite(flow)

        # self.ana.statwrite("Dropped packets (count: {})".format(len(drops)))
        # for flow in drops:
        #     self.ana.statwrite(flow)
        # self.ana.statwrite("Duplicated packets (count: {})".format(len(dups)))
        # for flow in dups:
        #     self.ana.statwrite(flow)


    def _bininit(self, bincnt, timespan, fulltime):
        cfg = {"first": 0, "last": 0, "cnt": bincnt, "size": 0, "initial": 0}

        if timespan == None:
            if fulltime:
                cfg["first"] = self.ana.t["prep"]
                cfg["last"] = self.ana.t["finish"]
            else:
                cfg["first"] = self.ana.t["start"]
                cfg["last"] = self.ana.t["end"]
        else:
            cfg["first"] = timespan[0] + self.ana.t["start"]
            cfg["last"] = timespan[1] + self.ana.t["start"]

        cfg["size"] = (cfg["last"] - cfg["first"]) / cfg["cnt"]

        # if we use the full time, make sure we go full binsizes in the past...
        if cfg["first"] < self.ana.t["start"]:
            cfg["initial"] = self.ana.t["start"] - (math.ceil((self.ana.t["start"] - cfg["first"]) / cfg["size"]) * cfg["size"])
        else:
            cfg["initial"] = cfg["first"]

        return cfg


    def _bininit2(self, binsize, timespan, fulltime, maxbins=150):
        cfg = {"first": 0, "last": 0, "dur": 0, "size": binsize, "cnt": 0, "initial": 0}

        if timespan == None:
            if fulltime:
                cfg["first"] = self.ana.t["prep"]
                cfg["last"] = self.ana.t["finish"]
            else:
                cfg["first"] = self.ana.t["start"]
                cfg["last"] = self.ana.t["end"]
        else:
            cfg["first"] = timespan[0] + self.ana.t["start"]
            cfg["last"] = timespan[1] + self.ana.t["start"]

        cfg["dur"] = cfg["last"] - cfg["first"]


        if not binsize:
            for size in [1, 10, 30, 60, 300, 600, 3600, 36000]:
                if (cfg["dur"] / size) <= maxbins:
                    cfg["size"] = size
                    break
        cfg["cnt"] = cfg["dur"] / cfg["size"]

                    # if we use the full time, make sure we go full binsizes in the past...
        if cfg["first"] < self.ana.t["start"]:
            cfg["initial"] = self.ana.t["start"] - (math.ceil((self.ana.t["start"] - cfg["first"]) / cfg["size"]) * cfg["size"])
        else:
            cfg["initial"] = cfg["first"]

        return cfg


    def _dump_flow(self, flow):
        print("FLOW {} src:{} dst:{} ack:{} - path:{}".format(flow["seq"], flow["src"], flow["dst"], flow["ack"], flow["path"]))
        print("     t_tx:{}".format(flow["t_tx"]))
        print("  t_tx_re:{}".format(flow["t_tx"]))
        print("     t_rx:{}".format(flow["t_tx"]))
        print("    t_ack:{}".format(flow["t_tx"]))
        for e in flow["events"]:
            print("   - {}".format(e))


    def plot_stats(self, types, nodes=None, binsize=90, timespan=None):
        cfg = self.ana.plotsetup(nodes, binsize, timespan)
        curbin = cfg["first"]

        cnt = {t: [] for t in types}
        ticks = []
        for evt in self.evt:
            if self.ana.plotter.filter(cfg, evt["node"], evt["time"]):
                continue

            if evt["time"] >= curbin:
                ticks.append("{:.0f}".format(self.ana.t_norm(curbin + cfg["binsize"])))
                for t in cnt:
                    cnt[t].append(0)
                curbin += cfg["binsize"]

            if evt["type"] in types:
                cnt[evt["type"]][-1] += 1

        data = {"x": ticks, "y": [cnt[t] for t in types], "label": types}
        suffix = "-".join([a[1:] for a in types]).lower()
        print(ticks)
        info = {"title": "Accumulated # of Events",
                "xlabel": "Experiment duration, binsize {:.0f}s".format(cfg["binsize"]),
                "ylabel": "# of Events",
                "suffix": "stats-{}".format(suffix),
                # "xticks": ticks,
                "xtick_lbl": ticks,
                # "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
                "binsize": binsize,
                "plotter": "barchart",
        }
        self.ana.plotter.barchart2(info, data)


    def plot_stats_pn(self, types, nodes=None, binsize=90, timespan=None):
        cfg = self.ana.plotsetup(nodes, binsize, timespan)
        curbin = cfg["first"]

        cnt = {n: {t: [] for t in types} for n in cfg["nodes"]}
        ticks = []

        for evt in self.evt:
            if self.ana.plotter.filter(cfg, evt["node"], evt["time"]):
                continue

            if evt["time"] >= curbin:
                ticks.append("{:.0f}".format(self.ana.t_norm(curbin + cfg["binsize"])))
                for n in cnt:
                    for t in cnt[n]:
                        cnt[n][t].append(0)
                curbin += cfg["binsize"]

            if evt["type"] in types:
                cnt[evt["node"]][evt["type"]][-1] += 1

        data = []
        for n in self.ana.nsort(cnt):
            data.append({"x": ticks,
                         "y": [cnt[n][t] for t in types],
                         "label": types,
                         "title": n})
        suffix = "-".join([a[1:] for a in types]).lower()
        info = {
            'title': "# of Packets Sent and Received per Node (binsize {}s)".format(cfg["binsize"]),
            'xlabel': "Experiment duration [in s]",
            'ylabel': "# packets sent/received",
            'suffix': "stats_pn-{}".format(suffix),
            'dim': [len(data), 1],
            'binsize': binsize,
            'plotter': "barchart_muldim",
        }
        self.ana.plotter.barchart_muldim(info, data)


    def get_flow_pdr(self, rels, nodes=None, binsize=5.0, timespan=None, ylim=[0.5, 1.01]):
        cfg = self.ana.plotsetup(nodes, binsize, timespan)

        lines = []
        for rel in rels:
            lines.append({"x": [], "y": [], "label": rel[1]})

        curbin = [cfg["first"] for _ in range(len(rels))]
        cnt = [[0, 0] for _ in range(len(rels))]
        for flow in self.flows:
            if len(flow["t_tx"]) == 0:
                print("Warning: currupt flow: {}".format(flow))
                continue
            if self.ana.plotter.filter(cfg, flow["src"], flow["t_tx"][0]):
                continue

            for i, rel in enumerate(rels):
                if flow["t_tx"][0] >= (curbin[i] + cfg["binsize"]):
                    lines[i]["x"].append(self.ana.t_norm(curbin[i]))
                    lines[i]["y"].append(cnt[i][1] / cnt[i][0])
                    cnt[i] = [0, 0]
                    curbin[i] += cfg["binsize"]
                cnt[i][0] += 1
                cnt[i][1] += 1 if len(flow[rel[0]]) > 0 else 0

        for i, rel in enumerate(rels):
            if cnt[i][0] > 0:
                lines[i]["x"].append(self.ana.t_norm(curbin[i]))
                lines[i]["y"].append(cnt[i][1] / cnt[i][0])

        return lines, cfg;


    def plot_flow_pdr(self, rels, nodes=None, binsize=5.0, timespan=None, ylim=[0.5, 1.01]):
        lines, cfg = self.get_flow_pdr(rels, nodes, binsize, timespan, ylim)

        xt = self.ana.plotter.get_ticks([l["x"] for l in lines], None)
        yt = self.ana.plotter.get_ticks([l["y"] for l in lines], ylim)

        if nodes == None:
            suffix = "pdr"
        else:
            suffix = "pdr_{}".format("-".join(nodes))

        info = {
            "title": "Packet Delivery Rate (binsize: {:.1f}s)".format(cfg["binsize"]),
            "xlabel": "Experiment duration [s]",
            "ylabel": "Packet delivery rate [0, 1.0]",
            "suffix": suffix,
            "grid": [False, True],
            "xlim": xt["lim"],
            "xticks": xt["ticks"],
            "xtick_lbl": xt["ticks"],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            "ylim": yt["lim"],
        }
        self.ana.plotter.linechart4(info, lines)


    def plot_flow_pdr_pn(self, rel, nodes=None, binsize=5.0, timespan=None, ylim=[0.0, 15.05]):
        cfg = self.ana.plotsetup(nodes, binsize, timespan)

        data = {n: {"x": [], "y": [], "label": f'{n}'} for n in cfg["nodes"]}

        curbin = cfg["first"]
        cnt = {n: [0, 0] for n in cfg["nodes"]}
        for flow in self.flows:
            if self.ana.plotter.filter(cfg, flow["src"], flow["t_tx"][0]):
                continue

            if (flow["t_tx"][0] >= curbin + cfg["binsize"]):
                for n in cnt:
                    if cnt[n][0] > 0:
                        data[n]["x"].append(self.ana.t_norm(curbin))
                        data[n]["y"].append(cnt[n][1] / cnt[n][0])
                    cnt[n] = [0, 0]
                curbin += cfg["binsize"]
            cnt[flow["src"]][0] += 1
            if len(flow[rel]) > 0:
                cnt[flow["src"]][1] += 1

        for n in cnt:
            if cnt[n][0] > 0:
                data[n]["x"].append(self.ana.t_norm(curbin))
                data[n]["y"].append(cnt[n][1] / cnt[n][0])

        lines = []
        for i, n in enumerate(self.ana.nsort(data)):
            if len(data[n]["x"]) > 0:
                for p in range(len(data[n]["y"])):
                    data[n]["y"][p] += (len(cfg["nodes"]) - i - 1)
                lines.append(data[n])

        xt = self.ana.plotter.get_ticks([l["x"] for l in lines], None)
        yt = self.ana.plotter.get_ticks([l["y"] for l in lines], ylim)

        info = {
            "title": "Packet Delivery Rate per Node (binsize: {:.1f}s)".format(cfg["binsize"]),
            "xlabel": "Experiment duration [s]",
            "ylabel": "Packet delivery rate [0, 1.0] TODO: ytick labels",
            "suffix": "pdr_pn",
            "grid": [True, False],
            "xlim": xt["lim"],
            "xticks": xt["ticks"],
            "xtick_lbl": xt["ticks"],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            "ylim": yt["lim"],
        }
        self.ana.plotter.linechart4(info, lines)



    def plot_cdf(self, nodes=None, timespan=None, xlim=None):
        cfg = self.ana.plotsetup(nodes, None, timespan)

        data_rx = {"x": [0.0], "y": [0.0], "label": "Packets Received"}
        data_ack = {"x": [0.0], "y": [0.0], "label": "Packets Acknowledged"}
        ttc_rx = []
        ttc_ack = []

        for flow in self.flows:
            if len(flow["t_tx"]) == 0:
                print("Warning: CDF: currupt flow: {}".format(flow))
                continue
            if self.ana.plotter.filter(cfg, flow["src"], None):
                continue

            if len(flow["t_rx"]) > 0:
                if flow["t_rx"][0] < flow["t_tx"][0]:
                    ttc_rx.append(0.0)
                else:
                    ttc_rx.append(flow["t_rx"][0] - flow["t_tx"][0])
            if len(flow["t_ack"]) > 0:
                ttc_ack.append(flow["t_ack"][0] - flow["t_tx"][0])

        cnt_rx = 0.0
        for ttc in sorted(ttc_rx):
            cnt_rx += 1.0
            data_rx["x"].append(ttc)
            data_rx["y"].append(cnt_rx / self.flows_cnt["sum"]["tx"])
        cnt_ack = 0.0
        for ttc in sorted(ttc_ack):
            cnt_ack += 1.0
            data_ack["x"].append(ttc)
            data_ack["y"].append(cnt_ack / self.flows_cnt["sum"]["tx"])

        xt = self.ana.plotter.get_ticks([data_rx["x"], data_ack["x"]], xlim, num=25)
        info = {
            "title": "CDF of Packet Delivery Rate to Time to Completion",
            "xlabel": "Packet Delivery Time [in ms]",
            "ylabel": "Packet Delivery Rate",
            "suffix": "cdf",
            "xlim": xt["ticklim"],
            "xticks": xt["ticks"],
            "xtick_lbl": ["{:.0f}".format(n * 1000) for n in xt["ticks"]],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            "ylim": [0, 1.05],
        }
        self.ana.plotter.linechart4(info, [data_rx, data_ack])


    def plot_cdf_pn(self, nodes=None, styles=None, stat="ack", xlim=None):
        if not nodes:
            nodes = self.ana.desc["used_nodes"]

        fstat = "t_{}".format(stat)

        data = [{"x": [0.0], "y": [0.0], "label": n} for n in nodes]
        cnt = dict(zip(nodes, [0.0] * len(nodes)))
        ttc = {}
        for n in nodes:
            ttc[n] = []

        for flow in self.flows:
            if flow["src"] in nodes:
                if len(flow["t_tx"]) == 0:
                    print("Warning: CDF: currupt flow: {}".format(flow))
                    continue
                if len(flow[fstat]) > 0:
                    diff = flow[fstat][0] - flow["t_tx"][0]
                    ttc[flow["src"]].append(diff)

        for i, n in enumerate(nodes):
            if styles:
                data[i]["style"] = styles[i]
            for ct in sorted(ttc[n]):
                cnt[n] += 1.0
                data[i]["x"].append(ct)
                data[i]["y"].append(cnt[n] / self.flows_cnt[n]["tx"])


        xt = self.ana.plotter.get_ticks([l["x"] for l in data], xlim)
        info = {
            "title": "CDF of Packet Delivery Rate to Time to Completion ({})".format(stat.upper()),
            "xlabel": "Packet Delivery Time [in ms]",
            "ylabel": "Packet Delivery Rate",
            "suffix": "cdf_{}_pn".format(stat),
            "xlim": xt["ticklim"],
            "xticks": xt["ticks"],
            "xtick_lbl": ["{:.0f}".format(n * 1000) for n in xt["ticks"]],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            "ylim": [0.0, 1.05],
        }

        self.ana.plotter.linechart4(info, data)


    def plot_delay_heatmap(self, stat="ack", nodes=None, excl_nodes=None, range=None, binsize=60, aggr="avg"):
        to = "t_{}".format(stat)
        if not nodes:
            nodes = self.ana.desc["used_nodes"]
        if excl_nodes:
            nodes = [n for n in nodes if n not in excl_nodes]


        curbin = self.flows[0]["t_tx"][0] + binsize

        pn = {n: [[]] for n in nodes}
        for flow in self.flows:
            if len(flow["t_tx"]) == 0:
                print("Warning: Delay: corrupt flow: {}".format(flow))
                continue

            if flow["src"] not in nodes:
                continue

            if flow["t_tx"][0] > curbin:
                curbin += binsize
                for n in pn:
                    pn[n].append([])

            if len(flow[to]) > 0:
                pn[flow["src"]][-1].append(flow[to][0] - flow["t_tx"][0])

        yticklab = []
        data = []
        for n in self.ana.nsort(pn):
            row = []
            for delays in pn[n]:
                if len(delays) > 0:
                    if aggr == "min":
                        row.append(min(delays) * 1000)
                    elif aggr == "max":
                        row.append(max(delays) * 1000)
                    else:
                        row.append(sum(delays) / len(delays) * 1000)
                else:
                    row.append(-1.0)
            data.append(row)
            yticklab.append("{}".format(n))

        # calc xticks
        xticks = np.arange(0, len(data[0]) + 1, 600 / binsize).tolist()
        xtick_lbl = ["{:.0f}".format(t * binsize) for t in xticks]
        info = {
            "title": "Time to Completion for {} - {} (binsize {}s)".format(stat.upper(), aggr.upper(), binsize),
            "cbarlabel": "Time to Completion [ms]",
            "xlabel": "Experiment runtime [in s]",
            "ylabel": "Node",
            "suffix": "ttc_heatmap_{}".format(aggr),
            "grid": [False, False],
            "xticks": xticks,
            "xtick_lbl": xtick_lbl,
            "xtick_lbl_rot":  {"rotation": 45, "ha": "right"},
            "yticks": np.arange(len(data)).tolist(),
            "ytick_lbl": yticklab,
        }
        self.ana.plotter.heatmap(info, data)


    def plot_latency_box(self, stat="ack", nodes=None, ylim=0):
        tim = "t_{}".format(stat)
        cfg = self.ana.plotsetup(nodes, None, None)

        lat = {n: [] for n in cfg["nodes"]}

        for flow in self.flows:
            # skip incomplete and broken packets
            if len(flow["t_tx"]) == 0 or len(flow[tim]) == 0:
                continue

            lat[flow["src"]].append((flow[tim][0] - flow["t_tx"][0]) * 1000)


        data = [lat[n] for n in self.ana.nsort(cfg["nodes"])]
        info = {
            "title": "Packet Latency ({})".format(stat),
            "xlabel": "Node",
            "ylabel": "Latency [ms]",
            "suffix": "lat_box",
            "grid": [False, True],
            "bar_lbl": ["{}".format(n) for n in self.ana.nsort(cfg["nodes"])],
            "ylim": ylim,
        }
        self.ana.plotter.boxplot2(info, data)


    def plot_evtcnt_boxes_pn(self, types, nodes=None, binsize=None, timespan=None, fulltime=False, ylim=None):
        if not nodes or nodes != "sum":
            nodes = self.ana.desc["used_nodes"]

        cfg = self._bininit2(binsize, timespan, fulltime, maxbins=400)

        pn = {n: {t: [] for t in types} for n in nodes}
        for e in self.evt:
            if (e["node"] not in nodes or
                e["type"] not in types or
                e["time"] < cfg["first"] or
                e["time"] > cfg["last"]):
                continue

            pn[e["node"]][e["type"]].append(e["time"] - self.ana.t["start"])

        bins = np.arange(cfg["initial"] - self.ana.t["start"], cfg["dur"] + cfg["size"], cfg["size"])

        data = []
        for n in self.ana.nsort(pn):
            y = []
            for t in sorted(pn[n]):
                y.append(pn[n][t])

            data.append({
                "label": n,
                "y": y,
            })


        colors = []
        for t in types:
            colors.append(COLORMAP_TYPES[t])

        info = {
            "title": "Number of events packets - binsize: {}s".format(cfg["size"]),
            "xlabel": "Time",
            "ylabel": "# of events",
            "suffix": "hist",
            "xlim": (bins[0], bins[-1]),
            "ylim": ylim,
            "types": types,
        }
        self.ana.plotter.evt_type_boxes(info, bins, data, colors)


    def plot_of_pn(self, nodes=None, timespan=[None, None], xlim=None):
        if len(self.of_evt) == 0:
            print("Expstats: Skipping OF Plot, no OF events")
            return

        cfg = self.ana.plotsetup(nodes, None, timespan)

        data = []
        of_pn = {n: [{"time": cfg["first"], "of": 0}] for n in cfg["nodes"]}

        for of_evt in self.of_evt:
            if self.ana.plotter.filter(cfg, of_evt["node"], of_evt["time"]):
                continue
            of_pn[of_evt["node"]].append(of_evt)

        for n in of_pn:
            data.append({
                "x": [self.ana.t_norm(e["time"]) for e in of_pn[n]],
                "y": [e["of"] for e in of_pn[n]],
                "label": n,
            })
        for line in data:
            line["x"].append(self.ana.t_norm(cfg["last"]))
            line["y"].append(line["y"][-1])


        xt = self.ana.plotter.get_ticks([l["x"] for l in data], xlim)
        info = {
            "title": "Objective Function (OF) History",
            "xlabel": "Experiment runtime [in s]",
            "ylabel": "Object Function Value",
            "suffix": "of_pn",
            "xlim": xt["lim"],
            "xticks": xt["ticks"],
            "xtick_lbl": xt["ticks"],
            "xtick_lbl_rot": {"rotation": 45, "ha": "right"},
            "plotter": "line",
            "step": True,
        }

        self.ana.plotter.linechart4(info, data)
