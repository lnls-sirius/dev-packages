#!/usr/bin/env python-sirius
"""."""

import time as _time
from threading import Thread as _Thread

import numpy as _np
import matplotlib.pyplot as _plt
import matplotlib.gridspec as _mgs

from PRUserial485 import EthBrigdeClient as _EthBrigdeClient

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.bsmp.serial import Channel as _Channel

from siriuspy.pwrsupply.pructrl.pru import PRU as _PRU
from siriuspy.pwrsupply.pructrl.udc import UDC as _UDC


class SOFB2BSMP:
    """."""

    BBBNAMES = (
        'IA-01RaCtrl:CO-PSCtrl-SI2',
        'IA-02RaCtrl:CO-PSCtrl-SI2',
        'IA-03RaCtrl:CO-PSCtrl-SI2',
        'IA-04RaCtrl:CO-PSCtrl-SI2',
        'IA-05RaCtrl:CO-PSCtrl-SI2',
        'IA-06RaCtrl:CO-PSCtrl-SI2',
        'IA-07RaCtrl:CO-PSCtrl-SI2',
        'IA-08RaCtrl:CO-PSCtrl-SI2',
        'IA-09RaCtrl:CO-PSCtrl-SI2',
        'IA-10RaCtrl:CO-PSCtrl-SI2',
        'IA-12RaCtrl:CO-PSCtrl-SI2',
        'IA-13RaCtrl:CO-PSCtrl-SI2',
        'IA-14RaCtrl:CO-PSCtrl-SI2',
        'IA-15RaCtrl:CO-PSCtrl-SI2',
        'IA-16RaCtrl:CO-PSCtrl-SI2',
        'IA-17RaCtrl:CO-PSCtrl-SI2',
        'IA-18RaCtrl:CO-PSCtrl-SI2',
        'IA-19RaCtrl:CO-PSCtrl-SI2',
        'IA-20RaCtrl:CO-PSCtrl-SI2',
        'IA-01RaCtrl:CO-PSCtrl-SI4',
        'IA-02RaCtrl:CO-PSCtrl-SI4',
        'IA-03RaCtrl:CO-PSCtrl-SI4',
        'IA-04RaCtrl:CO-PSCtrl-SI4',
        'IA-05RaCtrl:CO-PSCtrl-SI4',
        'IA-06RaCtrl:CO-PSCtrl-SI4',
        'IA-07RaCtrl:CO-PSCtrl-SI4',
        'IA-08RaCtrl:CO-PSCtrl-SI4',
        'IA-09RaCtrl:CO-PSCtrl-SI4',
        'IA-10RaCtrl:CO-PSCtrl-SI4',
        'IA-12RaCtrl:CO-PSCtrl-SI4',
        'IA-13RaCtrl:CO-PSCtrl-SI4',
        'IA-14RaCtrl:CO-PSCtrl-SI4',
        'IA-15RaCtrl:CO-PSCtrl-SI4',
        'IA-16RaCtrl:CO-PSCtrl-SI4',
        'IA-17RaCtrl:CO-PSCtrl-SI4',
        'IA-18RaCtrl:CO-PSCtrl-SI4',
        'IA-19RaCtrl:CO-PSCtrl-SI4',
        'IA-20RaCtrl:CO-PSCtrl-SI4',
    )

    BBB2DEVS = dict()

    def __init__(self):
        """."""
        self.pru = None
        self.udc = None
        self._init_connectors()

    def update(self):
        """."""
        for bbbname in SOFB2BSMP.BBBNAMES:
            udc = self.udc[bbbname]
            udc.sofb_update()

    def current_sp_set(self):
        """."""
        # benchmark: 83 us without access to UDC
        threads = dict()

        # run threads
        t0 = _time.time()
        for bbbname in SOFB2BSMP.BBBNAMES:
            threads[bbbname] = _Thread(
                target=self._udc_current_sp_set, args=(bbbname, ), daemon=True)
            threads[bbbname].start()
        t1 = _time.time()
        # print('start {:.6f} ms'.format(1e3*(t1-t0)))

        # join threads
        t0 = _time.time()
        for thread in threads.values():
            thread.join()
        t1 = _time.time()
        # print('join {:.6f} ms'.format(1e3*(t1-t0)))

    def current_rb_get(self):
        """."""
        # benchmark: 6 us without access to UDC
        readbacks = list()
        for bbbname in SOFB2BSMP.BBBNAMES:
            udc = self.udc[bbbname]
            readback = udc.sofb_current_rb_get()
            readbacks += list(readback)
        return _np.array(readbacks)

    def current_mon_get(self):
        """."""
        # benchmark: 6 us without access to UDC
        readbacks = list()
        for bbbname in SOFB2BSMP.BBBNAMES:
            udc = self.udc[bbbname]
            readback = udc.sofb_current_mon_get()
            readbacks += list(readback)
        return _np.array(readbacks)

    # --- private methods ---

    def _udc_current_sp_set(self, bbbname):
        """."""
        setpoint = list(_np.random.uniform(-0.1, 0.1, 8))
        udc = self.udc[bbbname]
        # TODO: embed try catch in order to deal with exceptions
        udc.sofb_current_set(setpoint)
        udc.sofb_update()

    @staticmethod
    def _create_pru():
        """."""
        pru = dict()
        for bbbname in SOFB2BSMP.BBBNAMES:
            pru[bbbname] = _PRU(_EthBrigdeClient, bbbname)
        return pru

    def _create_udc(self):
        """."""
        udc = dict()
        for bbbname, bsmpdevs in SOFB2BSMP.BBB2DEVS.items():
            pru = self.pru[bbbname]
            devids = [bsmp[1] for bsmp in bsmpdevs]
            udc[bbbname] = _UDC(pru=pru, psmodel='FBP', device_ids=devids)
        return udc

    def _init_connectors(self):
        """."""
        # NOTE: This is necessary for the threads to interact with
        # corresponding beaglebones in parallel
        _Channel.LOCK = None

        time0 = _time.time()
        SOFB2BSMP._update_bbb2devs()
        self.pru = SOFB2BSMP._create_pru()
        self.udc = self._create_udc()
        self._add_groups_of_variables()
        time1 = _time.time()
        print('_init_connectors: {:.5f} ms'.format(1e3*(time1 - time0)))

    @staticmethod
    def _update_bbb2devs():
        """."""
        for bbbname in SOFB2BSMP.BBBNAMES:
            devs = _PSSearch.conv_bbbname_2_bsmps(bbbname)
            SOFB2BSMP.BBB2DEVS[bbbname] = devs

    def _add_groups_of_variables(self):
        """."""
        for udc in self.udc.values():
            udc.add_groups_of_variables()


def run_test():
    """."""
    conn = SOFB2BSMP()
    exectimes = [0] * 5000
    for i in range(len(exectimes)):
        time0 = _time.time()
        conn.current_sp_set()
        time1 = _time.time()
        exectimes[i] = 1000*(time1 - time0)
    for exectime in exectimes:
        print(exectime)


def plot_result(fname):
    """."""
    data = _np.loadtxt(fname, skiprows=77)
    fig = _plt.figure(figsize=(8, 10))
    gs = _mgs.GridSpec(1, 1)
    gs.update(
        left=0.12, right=0.97, top=0.95, bottom=0.10,
        hspace=0.2, wspace=0.25)

    asp = _plt.subplot(gs[0, 0])
    asp.hist(data, bins=100)

    avg = data.mean()
    std = data.std()
    minv = data.min()
    maxv = data.max()
    stg = f'avg = {avg:05.1f} ms\n'
    stg += f'std = {std:05.1f} ms\n'
    stg += f'min = {minv:05.1f} ms\n'
    stg += f'max = {maxv:05.1f} ms'
    asp.text(
        0.8, 0.8, stg, horizontalalignment='center',
        fontsize='xx-small',
        verticalalignment='center', transform=asp.transAxes,
        bbox=dict(edgecolor='k', facecolor='w', alpha=1.0))
    asp.set_xlabel('time [ms]')
    asp.set_ylabel('# total apply')
    asp.set_title('SOFB2BSMP @ lnls561-linux ({} points)'.format(len(data)))
    _plt.show()


if __name__ == '__main__':
    run_test()
