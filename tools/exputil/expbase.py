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
import shutil
from pathlib import Path
from datetime import datetime


SCRIPTBASE = os.path.dirname(os.path.realpath(__file__))
CFG_FILE = "config.yml"
NODE_FILE = "nodes.yml"


class Expbase:

    def __init__(self):
        self.nodecfg = {}
        self.hostcfg = {}

        self.basedir = str(Path(SCRIPTBASE).parent.parent)
        self.logdir = None
        self.tmpdir = None
        self.plotdir = None
        self.expdir = None

        self.expbase = None     # e.g. em2
        self.expname = None     # e.g. em2_rpble_1s_long
        self.outname = None     # e.g. em2_rpble_1s_long_20200101_121223

        self.expfile = None     # e.g. BASDIR/EXPNAME.yml
        self.logfile = None     # e.g. LOGDIR/EXPNAME/OUTNAME.dump
        self.plotbase = None    # e.g. PLOTDIR/EXPNAME/OUTNAME

        # read host configuration
        self.hostcfg = self.loadyml(os.path.join(self.basedir, CFG_FILE))

        self.logdir = self.getdir(self.hostcfg['DIR_LOGS'])
        self.tmpdir = self.getdir(self.hostcfg['DIR_TEMP'])
        self.plotdir = self.getdir(self.hostcfg['DIR_PLOT'])

        self.checkpath(self.basedir)
        self.checkpath(self.logdir)
        self.checkpath(self.tmpdir)
        self.checkpath(self.plotdir)


    def setup_exp(self, expfile):
        self.expname = os.path.splitext(os.path.basename(expfile))[0]
        self.expbase = self.expname.split("_")[0]
        self.outname = "{}_{}".format(self.expname, datetime.now().strftime("%Y%m%d-%H%M%S"))
        self.expdir = os.path.join(self.basedir, self.expbase);
        self.expfile = os.path.join(self.expdir, "{}.yml".format(self.expname))
        self.logfile = os.path.join(self.tmpdir, self.expname,
                                    "{}.dump".format(self.outname))
        self.plotbase = os.path.join(self.plotdir, self.expname, self.outname)

        self.checkpath(self.expfile)
        self.mkdir(self.logfile)


    def setup_ana(self, logfile):
        self.logfile = logfile
        self.outname = os.path.splitext(os.path.basename(logfile))[0]

        m = re.search(r'.+_\d+-\d+.dump$', logfile)
        if m:
            self.expname = self.outname[:-16]
            self.expbase = self.expname.split("_")[0]
            self.expdir = os.path.join(self.basedir, self.expbase);
            self.expfile = os.path.join(self.expdir, "{}.yml".format(self.expname))
            self.plotbase = os.path.join(self.plotdir, self.expname, self.outname)
        else:
            self.expname = self.outname
            self.expbase = None
            self.expdir = None
            self.expfile = None
            self.plotbase = os.path.join(self.plotdir, self.expname, self.outname)

        self.checkpath(self.logfile)
        self.mkdir(self.plotbase)


    def loadyml(self, file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return  yaml.load(f, Loader=yaml.BaseLoader)
        except Exception as e:
            sys.exit("Error: unable to load file {}: {}".format(file, e))


    def loadyml_rel(self, path):
        return self.loadyml(os.path.join(self.basedir, path))


    def getdir(self, src, base=None):
        if not base:
            base = self.basedir
        src = os.path.expanduser(src)
        if not os.path.isabs(src):
            src = os.path.normpath(os.path.join(base, src))

        if not os.path.exists(src):
             os.mkdir(src)
        return src


    def checkpath(self, path):
        if not os.path.exists(path):
            sys.exit("Error: file {} not found".format(path))


    def mkdir(self, file):
        # print(str(Path(file).parent))
        Path(file).parent.mkdir(exist_ok=True)
        # sys.exit("lslsl")


    def get_nodecfg(self, site):
        tmp = self.loadyml(os.path.join(self.basedir, NODE_FILE))
        self.nodecfg.update(tmp[site])


    def logfile_finalize(self):
        if self.tmpdir in self.logfile:
            final = os.path.join(self.logdir, self.expname,
                                 "{}.dump".format(self.outname))
            self.mkdir(final)
            shutil.move(self.logfile, final)


    def nsort(self, obj):
        return sorted(obj, key=self.nodes_sort)


    def nodes_sort(self, name):
        if "-" in name:
            return (len(name) * 100) + int(name.split("-")[-1])
        else:
            return (len(name) * 10000)
