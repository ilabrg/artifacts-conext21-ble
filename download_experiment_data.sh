#!/bin/sh

BASEDIR=$(dirname "${0}")
SRCLOGS="https://zenodo.org/record/5635607/files/logs.tar.gz?download=1"
SRCPLOTS="https://zenodo.org/record/5635607/files/plots.tar.gz?download=1"
TMPLOGS="logs.tar.gz"
TMPPLOTS="plots.tar.gz"

[ ! -e results ] && mkdir results

wget -O results/${TMPLOGS} ${SRCLOGS}
tar xfvz results/${TMPLOGS} -C results/

wget -O results/${TMPPLOTS} ${SRCPLOTS}
tar xfvz results/${TMPPLOTS} -C results/
