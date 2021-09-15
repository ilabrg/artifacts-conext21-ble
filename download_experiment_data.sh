#!/bin/sh

BASEDIR=$(dirname "${0}")
SRCLOGS="https://box.fu-berlin.de/s/engt3MkibQQbpTg/download"
SRCPLOTS="https://box.fu-berlin.de/s/Qg6fqLcGxcsQR6L/download"
TMPDIR=$(mktemp -d -t)
TMPLOGS="logs.zip"
TMPPLOTS="plots.zip"

wget -O ${TMPDIR}/${TMPLOGS} ${SRCLOGS}
unzip ${TMPDIR}/${TMPLOGS} -d ${TMPDIR}
cp -R ${TMPDIR}/logs ${BASEDIR}/results/

wget -O ${TMPDIR}/${TMPPLOTS} ${SRCPLOTS}
unzip ${TMPDIR}/${TMPPLOTS} -d ${TMPDIR}
cp -R ${TMPDIR}/plots ${BASEDIR}/results/

rm -rf ${TMPDIR}
