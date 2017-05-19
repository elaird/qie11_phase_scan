#!/usr/bin/env python

import qie11_phase_scan as qps

for s in qps.settings(nCycles=2):
    print s

for c in qps.commands():
    print c
