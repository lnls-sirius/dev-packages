#!/usr/bin/env python-sirius

"""Module for WfmRef tests."""

# import time
import matplotlib.pyplot as plt

from siriuspy.search import PSSearch
from siriuspy.pwrsupply.udc import UDC
from siriuspy.pwrsupply.pru import PRU
# from siriuspy.pwrsupply.bsmp import FBP
from siriuspy.pwrsupply.status import PSCStatus


BBBNAME = 'IA-08RaCtrl:CO-PSCtrl-SI5'


def create_udc(bbbname):
    """Create UDC."""
    pru = PRU(bbbname=bbbname)
    bsmps = PSSearch.conv_bbbname_2_bsmps(bbbname)
    psnames, device_ids = zip(*bsmps)
    psmodel = PSSearch.conv_psname_2_psmodel(psnames[0])
    _udc = UDC(pru=pru, psmodel=psmodel, device_ids=device_ids)
    return _udc


def print_status(ps):
    """Print status."""
    _, ps_status = ps.read_variable(ps.CONST_PSBSMP.V_PS_STATUS, timeout=100)
    status = PSCStatus(ps_status=ps_status)
    print('{:<15}: {}'.format('ps_status', bin(ps_status)))
    print('{:<15}: {}'.format('status', status.state))
    print('{:<15}: {}'.format('open_loop', status.open_loop))
    print('{:<15}: {}'.format('interface', status.interface))
    print('{:<15}: {}'.format('active', status.active))
    print('{:<15}: {}'.format('model', status.model))
    print('{:<15}: {}'.format('unlocked', status.unlocked))


def print_wfmref(ps):
    """Print wfmref data."""
    print('{:<25}: {}'.format('wfmref_maxsize', ps.wfmref_maxsize))
    print('{:<25}: {}'.format('wfmref_selected', ps.wfmref_selected))
    print('{:<25}: {}'.format('wfmref_size', ps.wfmref_size))
    print('{:<25}: {}'.format('wfmref_idx', ps.wfmref_idx))
    wfmref_ptr_values = ps.wfmref_pointer_values
    print('{:<25}: {}'.format('wfmref_ptr_beg', wfmref_ptr_values[0]))
    print('{:<25}: {}'.format('wfmref_ptr_end', wfmref_ptr_values[1]))
    print('{:<25}: {}'.format('wfmref_ptr_idx', wfmref_ptr_values[2]))


def plot_wfmref(ps):
    """Plot wfmref."""
    curve = ps.wfmref_read()
    plt.plot(curve, label='WfmRef ({} points)'.format(len(curve)))
    plt.xlabel('Index')
    plt.ylabel('Current [A]')
    plt.legend()
    plt.show()


def print_basic_info(ps):
    """Print all info."""
    print('--- status ---')
    print_status(ps)
    print('--- wfmref ---')
    print_wfmref(ps)
    print()
    plot_wfmref(ps)


# --- create global objects ---

udc = create_udc(bbbname=BBBNAME)
ps1 = udc[1]
ps2 = udc[2]
ps3 = udc[3]
ps4 = udc[4]
