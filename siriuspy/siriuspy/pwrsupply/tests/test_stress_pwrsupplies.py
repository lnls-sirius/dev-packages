#!/usr/bin/env python-sirius

import time
from importlib.util import find_spec as _find_spec

import numpy as np
import matplotlib.pyplot as plt

from siriuspy.epics import PV
# from siriuspy.search import PSSearch
from siriuspy.pwrsupply.pssofb import PSSOFB, PSConnSOFB
if _find_spec('PRUserial485') is not None:
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


class Cmd:
    def __init__(self, devs):
        self.devs = devs
        self.sofbmode_sp = PVGroup(devs, 'SOFBMode-Sel')
        self.sofbmode_rb = PVGroup(devs, 'SOFBMode-Sts')
        self.idffmode_sp = PVGroup(devs, 'IDFFMode-Sel')
        self.idffmode_rb = PVGroup(devs, 'IDFFMode-Sts')
        self.opmode_sp = PVGroup(devs, 'OpMode-Sel')
        self.opmode_rb = PVGroup(devs, 'OpMode-Sts')


def wait_for_connection(cmd):
    cmd.sofbmode_sp.wait_for_connection()
    cmd.sofbmode_rb.wait_for_connection()
    cmd.idffmode_sp.wait_for_connection()
    cmd.idffmode_rb.wait_for_connection()
    cmd.opmode_sp.wait_for_connection()
    cmd.opmode_rb.wait_for_connection()


def connected(cmd):
    conn = True
    conn &= cmd.sofbmode_sp.connected
    conn &= cmd.sofbmode_rb.connected
    conn &= cmd.idffmode_sp.connected
    conn &= cmd.idffmode_rb.connected
    conn &= cmd.opmode_sp.connected
    conn &= cmd.opmode_rb.connected
    return conn


def is_stressed_sofb(cmd):
    values = cmd.sofbmode_rb.value
    for i in range(len(values)):
        if values[i] != 0:
            print(cmd.devs[i])
    return not all(map(lambda x: x == 0, values))


def is_stressed_idff(cmd):
    values = cmd.idffmode_rb.value
    for i in range(len(values)):
        if values[i] != 0:
            print(cmd.devs[i])
    return not all(map(lambda x: x == 0, values))


def get_current():
    curr = np.random.rand(280)
    curr -= 0.5
    return curr


def try_to_stress(pssofb, cmd, nr_iters=100, rate=25.14):
    # cmd.update_cmd.put(1, wait=False)
    factor = 0.0
    cmd.opmode_sp.value = 1
    # time.sleep(1)

    curr = factor * get_current()
    # plt.plot(curr)
    # plt.show()

    pssofb.bsmp_sofb_current_set(curr)
    time.sleep(0.1)
    cmd.sofbmode_sp.value = 1
    cmd.idffmode_sp.value = 1
    time.sleep(1)

    for i in range(nr_iters):
        print(i)
        pssofb.bsmp_sofb_current_set(factor*get_current())
        # time.sleep(0.1)
        # update_cmd.put(1, wait=False)
        time.sleep(1/rate)

    time.sleep(1)
    cmd.sofbmode_sp.value = 0
    cmd.idffmode_sp.value = 0
    cmd.opmode_sp.value = 0
    time.sleep(1)
    return is_stressed_sofb(cmd) or is_stressed_idff(cmd)


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
# pssofb.processes_start()

# pssofb = PSConnSOFB(EthBridgeClient, sofb_update_iocs=True)

devs = pssofb.sofb_psnames
# print(devs)
# print(len(devs))

cmd = Cmd(devs)
wait_for_connection(cmd)
time.sleep(2)
# print(connected(cmd))

# cmd.sofbmode_sp.value = 0
# cmd.opmode_sp.value = 0

print(is_stressed_sofb(cmd))

print(is_stressed_idff(cmd))

# for i in range(1):
#     try_to_stress(pssofb, cmd, nr_iters=1)
#     time.sleep(1)
#     if is_stressed(cmd):
#         break
#     time.sleep(1.0)
#     print()
