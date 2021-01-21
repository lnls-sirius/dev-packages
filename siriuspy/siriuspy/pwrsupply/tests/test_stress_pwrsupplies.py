#!/usr/bin/env python-sirius

import time

import numpy as np

from siriuspy.epics import PV
# from siriuspy.search import PSSearch
from siriuspy.pwrsupply.pssofb import PSSOFB
from PRUserial485 import EthBridgeClient


class PVGroup:

    def __init__(self, devlist, prop):
        self.pvs = [PV(dev + ':' + prop) for dev in devlist]

    def wait_for_connection(self):
        for pv in self.pvs:
            pv.wait_for_connection()

    @property
    def connected(self):
        return all(map(lambda x: x.connected, self.pvs))

    @property
    def value(self):
        return list(map(lambda x: x.value, self.pvs))

    @value.setter
    def value(self, value):
        for pv in self.pvs:
            pv.put(value, wait=False)


def wait_for_connection():
    # update_cmd.wait_for_connection()
    sofbmode_sp.wait_for_connection()
    sofbmode_rb.wait_for_connection()
    opmode_sp.wait_for_connection()
    opmode_rb.wait_for_connection()


def connected():
    conn = True
    # conn = update_cmd.connected
    conn &= sofbmode_sp.connected
    conn &= sofbmode_rb.connected
    conn &= opmode_sp.connected
    conn &= opmode_rb.connected
    return conn


def is_stressed():
    return not all(map(lambda x: x == 0, sofbmode_rb.value))


def get_current():
    curr = np.random.rand(280)
    curr -= 0.5
    return curr


def try_to_stress(nr_iters=100, rate=25.14):
    # update_cmd.put(1, wait=False)
    opmode_sp.value = 1
    pssofb.bsmp_sofb_current_set(get_current())
    sofbmode_sp.value = 1

    time.sleep(1)

    for _ in range(nr_iters):
        # update_cmd.put(1, wait=False)
        pssofb.bsmp_sofb_current_set(get_current())
        time.sleep(1/rate)

    time.sleep(1)
    sofbmode_sp.value = 0
    opmode_sp.value = 0
    time.sleep(1)
    return is_stressed()



# Next Steps 2020-01-18
# =====================
#
# 0. Check how we can test without using correctors setpoint. (look code)
#
# Using correctors setpoint:
#
# 1. try to replicate problem by runnig 'try_to_stress' again (using 40 BBBs)
# 2. if succeeds:
#        substitute PSSOFB with PSConnSOFB.
#        if suceeds:
#            try using < 40 BBBs
#        else:
#            problem prop. in PSSOFB mproc. then ?
#    else:
#        try to replicate problem somehow.
# 3. try script (or SOFB ioc) with differente setpoint rates < 25.14 Hz.


# bbbname = 'IA-01RaCtrl:CO-PSCtrl-SI2'
# devs = PSSearch.conv_bbbname_2_bsmps(bbbname)
# devs, _ = zip(*devs)

pssofb = PSSOFB(
    EthBridgeClient, nr_procs=8, asynchronous=True,
    sofb_update_iocs=True)
pssofb.processes_start()

devs = pssofb.sofb_psnames

# update_cmd = PV(devs[0] + ':SOFBUpdate-Cmd')
sofbmode_sp = PVGroup(devs, 'SOFBMode-Sel')
sofbmode_rb = PVGroup(devs, 'SOFBMode-Sts')
opmode_sp = PVGroup(devs, 'OpMode-Sel')
opmode_rb = PVGroup(devs, 'OpMode-Sts')
