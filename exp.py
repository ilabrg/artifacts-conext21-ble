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
# sys.path.append(os.path.join(SCRIPTBASE, "tools"))

import re
import time
import yaml
import logging
import argparse
import subprocess
import multiprocessing

from tools.exputil.expbase import Expbase

from iotlab_controller.common import get_default_api, get_uri
from iotlab_controller.constants import IOTLAB_DOMAIN
from iotlab_controller.experiment.base import ExperimentError
from iotlab_controller.experiment.tmux import TmuxExperiment
from iotlab_controller.riot import RIOTFirmware
from iotlab_controller.nodes import BaseNodes

SCRIPTBASE = os.path.dirname(os.path.realpath(__file__))
VER_CMD = ["git", "rev-parse", "--verify", "HEAD"]
CFG_DFLT_SITE = "saclay"
CFG_DFLT_DURATION = 60
CFG_DFLT_MAKEEXP = "Makefile.exp.include"

CFG_EXPPREFIX = 'exp: '

class DepError(Exception):
    pass

class Myexp(Expbase):

    def __init__(self, expfile):
        # setup environment
        super().__init__()
        self.setup_exp(expfile)

        self.duration = 0
        self.site = ""

        self.setups = {}
        self.used_nodes = set()
        self.cmds = []
        self.cmds_raw = []
        self.fwlist = {}
        self.env = {}
        self.cflags = {}
        self.expvars = {}
        self.exp = None
        self.topo = {}

        # read experiment configuration
        exp = self.loadyml(self.expfile)

        # read SETUP
        setup = self.loadyml_rel(exp["setup"])
        # TODO: rework precheck to use ifconfig
        self.precheck = setup['precheck'] if 'precheck' in setup else "ble"
        self.site = setup['site'] if 'site' in setup else CFG_DFLT_SITE
        self.get_nodecfg(self.site)
        self.setups = self.read_setup(setup['setup'])
        if "expvars" in setup:
            self.expvars = setup["expvars"]
        # read topology (if applicable)
        if "topologies" in setup:
            for name, file in setup["topologies"].items():
                self.topo_parse(name, self.loadyml_rel(file))

        # read ENV
        if "env" in exp:
            self.env.update(exp["env"])

        # update EXPVARS
        if "expvars" in exp:
            for file in exp["expvars"]:
                tmp = self.loadyml_rel(file)
                dups = set(tmp).intersection(self.expvars)
                if dups:
                    sys.exit("Error: expvars duplication in {}: {}".format(file, dups))
                self.expvars.update(tmp)

        # read COMMANDS (exp)
        if "exp_setup" in setup:
            self.cmds_raw.extend(setup["exp_setup"])
        if "exp" in exp and exp["exp"] != None:
            cmds = self.loadyml_rel(exp["exp"])
            self.cmds_raw.extend(cmds["exp"])
        if "exp_teardown" in setup:
            self.cmds_raw.extend(setup["exp_teardown"])
        self.cmd_parse()
        self.duration = int(self.duration * 1.2 / 60) + 5

        # try go get some information on RIOT and specified packages
        expmkfile = os.path.join(SCRIPTBASE, CFG_DFLT_MAKEEXP)
        self.sw_ver = {}
        if os.path.exists(expmkfile):
            with open(expmkfile, 'r', encoding="utf-8") as f:
                for line in f:
                    m = re.search(r'RIOTBASE \?= (?P<cwd>[-/a-zA-Z0-9]+)', line)
                    if m:
                        v = subprocess.check_output(VER_CMD, cwd=m.group("cwd"))
                        self.sw_ver['riot'] = v.decode("utf-8").replace("\n", "")
                    m = re.search(r'PKG_SOURCE_LOCAL_NIMBLE \?= (?P<cwd>[-/a-zA-Z0-9]+)', line)
                    if m:
                        v = subprocess.check_output(VER_CMD, cwd=m.group("cwd"))
                        self.sw_ver['nimble'] = v.decode("utf-8").replace("\n", "")

        self.init_logfile()


    def init_logfile(self):
        # open logfile and write experiment context
        with open(self.logfile, 'w', encoding="utf-8") as f:
            self.logwrite(f, 'name', self.expname)
            self.logwrite(f, 'logfile', "{}.dump".format(self.outname))
            self.logwrite(f, 'duration', self.duration)
            self.logwrite(f, 'site', self.site)
            self.logwrite(f, 'used_nodes', self.nsort(self.used_nodes))
            for mod in ('riot', 'nimble'):
                self.logwrite(f, 'version.{}'.format(mod), self.sw_ver[mod] if mod in self.sw_ver else 'n/a')
            for opt in self.env:
                self.logwrite(f, 'env.{}'.format(opt), self.env[opt])
            for opt in self.cflags:
                self.logwrite(f, "cflags.{}".format(opt), self.cflags[opt])
            for setup in self.setups:
                pre = "setup.{}".format(setup['name'])
                self.logwrite(f, "{}.fwpath".format(pre), setup['fwpath'])
                self.logwrite(f, "{}.node".format(pre), self.nsort(setup['nodes']))

            for name in self.topo:
                for n in self.topo[name]:
                    if self.topo[name][n]["parent"] == None:
                        self.logtopo(f, "topo.{}".format(name), name, n)

            for var in self.expvars:
                self.logwrite(f, "expvars.{}".format(var), self.expvars[var])
            self.logwrite(f, "exp", "---BEGIN---")
            for cmd in self.cmds:
                for inst in sorted(cmd):
                    self.logwrite(f, "exp.{}".format(inst), cmd[inst])
            self.logwrite(f, "exp", "---END---")
            f.write("\n----\n\n");


    def logwrite(self, f, cat, data):
        f.write("{}{}: {}\n".format(CFG_EXPPREFIX, cat, data))
        if data:
            logging.warning("{}{}: {}".format(CFG_EXPPREFIX, cat, data))
        else:
            logging.warning("{}{}".format(CFG_EXPPREFIX, cat))


    def logtopo(self, f, pos, name, node):
        pos += ".{}".format(node)
        self.logwrite(f, pos, None)
        for c in self.topo[name][node]["c"]:
            self.logtopo(f, pos, name, c)


    def read_setup(self, setup):
        res = []

        for s in setup:
            # parse and verify node list
            nodes = self.read_nodes(s['nodes'])
            overused = self.used_nodes.intersection(nodes)
            if overused:
                raise Exception("Nodes {} are assigned to multiple setups".format(overused))
            self.used_nodes = self.used_nodes.union(nodes)

            # verify firmware location and application name
            fwpath = self.getdir(s['fwpath'], self.expdir)

            res.append({
                'name': s['name'],
                'fwpath': fwpath,
                'nodes': nodes
                })

        return res;


    def read_nodes(self, nodes_str):
        nodes = set()

        parts = nodes_str.split("+")
        for p in parts:
            m = re.match("([a-z0-9]+(-[a-z]+)?-)([\,\d-]*)", p)
            if not m:
                raise Exception("Unable to parse nodelist: {}".format(p))
            else:
                node = m.group(1)
                ranges = m.group(3).split(",")
                for r in ranges:
                    minmax = [int(v) for v in r.split("-")]
                    if len(minmax) < 2:
                        minmax.append(minmax[0])
                    new_nodes = set([node + str(i) for i in range(minmax[0], minmax[1] + 1)])

                    # verify nodes
                    valid = new_nodes.intersection(self.nodecfg.keys())
                    if valid != new_nodes:
                        raise Exception("Node {} not available in the iotlab".format(new_nodes - valid))

                    nodes = nodes.union(new_nodes)

        # verify that all nodes exist
        for node in nodes:
            if node not in self.nodecfg:
                raise Exception("Node {} not available in the iotlab".format(node))

        return nodes


    def topo_parse_getcs(self, nodes, root, child):
        for c in nodes[child]["c"]:
            if c not in nodes[root]["allcs"]:
                nodes[root]["allcs"].append(c)
                self.topo_parse_getcs(nodes, root, c)


    def topo_parse(self, name, nodes):
        self.topo[name] = {}
        self.topo[name].update(nodes)
        for n in nodes:
            if "parent" not in nodes[n]:
                nodes[n]["parent"] = None
            if "c" in nodes[n]:
                for c in nodes[n]["c"]:
                    nodes[c]["parent"] = n
            else:
                nodes[n]["c"] = []

        # 2. iteration: collect list of all children in a nodes sub-tree
        for n in nodes:
            if "allcs" not in nodes[n]:
                nodes[n]["allcs"] = []
            self.topo_parse_getcs(nodes, n, n)


    def eval_math(self, exp):
        res = 0
        for add in exp.replace(" ", "").split("+"):
            tmp = 1
            for mul in add.split("*"):
                tmp *= float(mul)
            res += tmp
        return res


    def cmd_parse(self):
        for step in self.cmds_raw:
            if 'cmd' in step:
                cmd = step['cmd'].format(**self.expvars).split(";")
                if len(cmd) > 1:
                    for node in self.nsort(self.read_nodes(cmd[0])):
                        self.cmds.append({'cmd': "{};{}".format(node, cmd[1])})
                else:
                    self.cmds.append({'cmd': cmd[0]})
            if 'topo_ble' in step:
                for param in step["topo_ble"]:
                    step["topo_ble"][param] = step["topo_ble"][param].format(**self.expvars)
                self.cmd_topo_ble(step["topo_ble"]["name"])
            if 'topo_ip_tree' in step:
                for param in step["topo_ip_tree"]:
                    step["topo_ip_tree"][param] = step["topo_ip_tree"][param].format(**self.expvars)
                self.cmd_topo_ip_tree(step["topo_ip_tree"])

            if "statconn" in step:
                if "->" in step["statconn"]:
                    nodes = [n.strip() for n in step["statconn"].format(**self.expvars).split("->")]
                    self.cmd_add("{};statconn adds {}".format(nodes[1], self.nodecfg[nodes[0]]["addr_mac"]))
                    self.cmd_add("{};statconn addm {}".format(nodes[0], self.nodecfg[nodes[1]]["addr_mac"]))
                if "<-" in step["statconn"]:
                    nodes = [n.strip() for n in step["statconn"].format(**self.expvars).split("<-")]
                    self.cmd_add("{};statconn adds {}".format(nodes[0], self.nodecfg[nodes[1]]["addr_mac"]))
                    self.cmd_add("{};statconn addm {}".format(nodes[1], self.nodecfg[nodes[0]]["addr_mac"]))

            if 'autoid' in step:
                sleep = None

                if 'sleep' in step:
                    sleep = {"sleep": self.eval_math(step['sleep'].format(**self.expvars))}
                    self.duration += self.eval_math(step['sleep'].format(**self.expvars))

                cstr = step['autoid'].split(";")
                if "{" in cstr[0]:
                    cstr[0] = cstr[0].format(**self.expvars)
                for node in self.nsort(self.read_nodes(cstr[0])):
                    foo = cstr[1]
                    self.expvars["AUTOID"] = self.nodecfg[node]["id"]
                    foo = foo.format(**self.expvars)
                    self.cmds.append({"cmd": "{};{}".format(node, foo)})
                    if sleep:
                        self.cmds.append(sleep)

            if 'scon' in step:
                # "scon": "nrf52dk-1 -> nrf52dk-7"
                # results in
                # - nrf52dk-1;statconn adds [MAC of nrf52dk-7]
                # - nrf52dk-7;statconn addm [MAC of nrf52dk-1]
                conn = step["scon"].split(" -> ")
                if len(conn) != 2:
                    sys.exit("cmd_parse: error parsing scon ({})".format(step))
                self.cmd_add("{};statconn adds {}".format(conn[0], self.nodecfg[conn[1]]["addr_mac"]), .1)
                self.cmd_add("{};statconn addm {}".format(conn[1], self.nodecfg[conn[0]]["addr_mac"]), .1)

            if 'sleep' in step:
                dur = self.eval_math(step['sleep'].format(**self.expvars))
                self.duration += dur
                self.cmds.append({'sleep': dur})


    def cmd_add(self, cmd, delay=0):
        self.cmds.append({'cmd': cmd})
        if delay > 0:
            self.cmds.append({'sleep': delay})


    def cmd_topo_ble(self, name):
        topo = self.topo[name]
        for n in self.nsort(topo):
            if topo[n]["parent"] is not None:
                self.cmd_add("{};statconn adds {}".format(n, self.nodecfg[topo[n]["parent"]]["addr_mac"]), 0.2)
            for c in self.nsort(topo[n]["c"]):
                self.cmd_add("{};statconn addm {}".format(n, self.nodecfg[c]["addr_mac"]), 0.2)


    def cmd_topo_ip_tree(self, ctx):
        topo = self.topo[ctx["name"]]
        for n in self.nsort(topo):
            self.cmd_add("{};ifconfig {} add {}::{}".format(n, ctx["if"], ctx["prefix"], topo[n]["addr"]), 0.2)

            for c in self.nsort(topo[n]["c"]):
                self.cmd_add("{};nib route add {} {}::{}/128 {}".format(
                                    n, ctx["if"], ctx["prefix"],
                                    topo[c]["addr"],
                                    self.nodecfg[c]["addr_l2"]), 0.2)
                for cc in self.nsort(topo[c]["allcs"]):
                    self.cmd_add("{};nib route add {} {}::{}/128 {}".format(
                                    n, ctx["if"], ctx["prefix"],
                                    topo[cc]["addr"],
                                    self.nodecfg[c]["addr_l2"]), 0.2)

            if topo[n]["parent"] is not None:
                self.cmd_add("{};nib route add {} default {}".format(n, ctx["if"], self.nodecfg[topo[n]["parent"]]["addr_l2"]), 0.2)

    def precheck_ble(self, exp):

        # verify that all nodes have the addresses that we expect
        # exp.cmd("this_will_not_work")
        # time.sleep(1)
        # for i in range(3):
        #     for n in self.nsort(self.used_nodes):
        #         exp.cmd(f"{n};dummy")
        #         time.sleep(.5)
        # for i in range(3):
        # exp.cmd("gammel")
        # time.sleep(1)

        active = {}
        for n in self.nsort(self.used_nodes):
            exp.cmd("{};ble info".format(n))
            time.sleep(.25)
        with open(self.logfile, "r", encoding="utf-8") as f:
            for line in f:
                m = re.search(r'(?P<node>[a-zA-Z0-9-]+);'
                              r'Own Address: (?P<mac>[:a-zA-Z0-9]+)'
                              r' -> \[(?P<ip>[:a-zA-Z0-9]+)\]', line)
                if m:
                    active[m.group("node")] = {
                        'mac': m.group("mac").lower(),
                        'ip': m.group("ip").lower(),
                    }

        missing = self.used_nodes.difference(active.keys())
        addrerr = {}
        for n in active:
            if (self.nodecfg[n]['addr_mac'] != active[n]['mac'] or
                self.nodecfg[n]['addr_l2'] != active[n]['ip']):
                addrerr[n] = "is {}/{} vs nodecfg {}/{}".format(
                    active[n]['mac'], active[n]['ip'],
                    self.nodecfg[n]['addr_mac'], self.nodecfg[n]['addr_l2'])
        if len(missing) > 0 or len(addrerr) > 0:
            if len(missing) > 0:
                logging.warning("- Error: nodes missing in log: {}".format(self.nsort(missing)))
            for n in addrerr:
                logging.warning("- Error: bad address(es): {}".format(addrerr[n]))
            self.exp.stop()
            raise DepError("# Experiment aborted - no log written")
        else:
            logging.warning("- Deployment OK: all nodes responding properly:")
            for n in self.nsort(active):
                logging.warning("  {}: {}/{}".format(n, active[n]['mac'], active[n]['ip']))


    def cmd_feeder(self, exp):
        if self.precheck == "ble":
            self.precheck_ble(exp)

        # run the actual experiment
        for step in self.cmds:
            if 'cmd' in step:
                logging.warning("- CMD: {}".format(step['cmd']))
                self.exp.cmd(step['cmd'])
            if 'sleep' in step:
                logging.warning("- sleeping for {}".format(step['sleep']))
                time.sleep(step['sleep'])


    def node_uri(self, node):
        return "{}.{}.{}".format(node, self.site, IOTLAB_DOMAIN)


    def prepare(self):
        # build firmware binaries
        logging.warning("# STEP 1: build firmware images")

        # compile list for app config params
        benv = {'CFLAGS': ""}
        benv.update(self.env)
        for flag in self.cflags:
            benv['CFLAGS'] += "-D{}={} ".format(flag, self.cflags[flag])

        self.uris_all = []
        fwpath_all = set()
        for setup in self.setups:
            fwpath_all.add(setup['fwpath'])
            for node in setup['nodes']:
                uri = self.node_uri(node)
                self.uris_all.append(uri)
                board = self.nodecfg[node]['board']
                name = "{}-{}".format(setup['name'], board)
                if not name in self.fwlist:
                    self.fwlist[name] = {
                        'fw': RIOTFirmware(setup['fwpath'], board, setup['name']),
                        'uris': []
                    }
                self.fwlist[name]['uris'].append(uri)

        for path in fwpath_all:
            logging.warning("- distclean: {}".format(path))
            # dummy = RIOTFirmware(path, "nrf52dk")
            # dummy.clean(distclean=True)
        for name in self.fwlist:
            logging.warning("- build: {}".format(name))
            self.fwlist[name]['fw'].clean()
            self.fwlist[name]['fw'].build(build_env=benv, threads=multiprocessing.cpu_count())


    def run(self):
        # prepare node objects and start experiment
        logging.warning("# STEP 2: initialize and allocate experiment")

        self.exp = TmuxExperiment(name=self.expname, nodes=BaseNodes(self.uris_all), target=self.cmd_feeder)
        self.exp.schedule(self.duration)
        logging.warning("- Experiment ID: {}".format(self.exp.exp_id))
        logging.warning("- ... waiting for experiment to start")
        self.exp.wait()
        logging.warning("- Experiment was started")

        # flash nodes
        logging.warning("# STEP 3: flashing nodes")
        for name in self.fwlist:
            n = self.exp.nodes.select(self.fwlist[name]['uris'])
            n.flash(self.exp.exp_id, self.fwlist[name]['fw'])

        # run actual experiment
        logging.warning("# STEP 4: run experiment")

        tmux_session = self.exp.initialize_tmux_session("em0sess", "helmut")
        assert tmux_session
        self.exp.hit_ctrl_c()

        # power cycle nodes to prevent serial aggregator fuckups */
        logging.warning("- power cycling nodes")
        self.exp.nodes.stop(self.exp.exp_id)
        time.sleep(1)
        self.exp.nodes.start(self.exp.exp_id)
        time.sleep(1)

        logging.warning("- running the serial aggregator now")
        self.exp.start_serial_aggregator(site=self.site, logname=self.logfile)
        time.sleep(2)
        self.exp.nodes.reset(self.exp.exp_id)
        time.sleep(2)
        self.exp.run()

        # cleanup
        logging.warning("# STEP 5: experiment finished, cleaning up now")
        self.exp.stop()
        self.logfile_finalize()
        logging.warning("- all done, goodbye")


    def cleanlog(self, run_number):
        with open(self.logfile, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(self.logfile, "w", encoding="utf-8") as f:
            for line in lines:
                if re.match("^exp:", line):
                    f.write(line)
            f.write("\n---- Try #{}\n\n".format(run_number))


def run_exp(expfile):
    print("# Running experiment file {}".format(expfile))
    limit = 8
    exp = Myexp(expfile)
    exp.prepare()

    while limit > 0:
        try:
            logging.warning("#### TRY #{} ####".format(9 - limit))
            exp.cleanlog(9 - limit)
            exp.run()
            break
        except DepError as e:
            limit -= 1
            logging.warning("# Exp run failed:")
            logging.warning(e)
            logging.warning("# Re-running the experiment, wish me luck ;-)\n")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("expfile", help="Experiment description")
    args = p.parse_args()

    logging.basicConfig(format='%(asctime)s %(message)s',
                        level=logging.WARNING)
    logging.warning("### IoT-Lab experiment launcher V0.23 ###")


    if ".suite" in args.expfile:
        print("running a complete suite")
        with open(args.expfile, "r", encoding="utf-8") as f:
            explist = yaml.load(f, Loader=yaml.BaseLoader)
            for expfile in explist:
                run_exp(expfile)

    else:
        run_exp(args.expfile)


if __name__ == "__main__":
    main()
