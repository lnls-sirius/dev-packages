#!/usr/bin/env python-sirius

"""Module for WfmRef tests."""

import time
import matplotlib.pyplot as plt
import numpy as np

from siriuspy.search import PSSearch
from siriuspy.pwrsupply.udc import UDC
from siriuspy.pwrsupply.pru import PRU
# from siriuspy.pwrsupply.bsmp import FBP
from siriuspy.pwrsupply.status import PSCStatus


BBBNAME = 'IA-08RaCtrl:CO-PSCtrl-SI5'


def create_udc(bbbname=BBBNAME):
    """Create UDC."""
    pru = PRU(bbbname=bbbname)
    bsmps = PSSearch.conv_bbbname_2_bsmps(bbbname)
    psnames, device_ids = zip(*bsmps)
    psmodel = PSSearch.conv_psname_2_psmodel(psnames[0])
    udc = UDC(pru=pru, psmodel=psmodel, device_ids=device_ids)
    return udc


def print_status(ps_list):
    """Print status."""

    st1, st2, st3, st4, st5, st6 = ['{:<15}:'] * 6
    va1, va2, va3, va4, va5, va6 = \
        [['status'], ['open_loop'], ['interface'],
         ['interface'], ['model'], ['unlock']]
    for ps in ps_list:
        _, ps_status = ps.read_variable(
            ps.CONST_PSBSMP.V_PS_STATUS, timeout=100)
        status = PSCStatus(ps_status=ps_status)
        st1 += ' {:6d}'
        va1.append(status.state)
        st2 += ' {:6d}'
        va2.append(status.open_loop)
        st3 += ' {:6d}'
        va3.append(status.interface)
        st4 += ' {:6d}'
        va4.append(status.active)
        st5 += ' {:6d}'
        va5.append(status.active)
        st6 += ' {:6d}'
        va6.append(status.unlocked)
    sts = [st1, st2, st3, st4, st5, st6]
    vas = [va1, va2, va3, va4, va5, va6]
    for st, va in zip(sts, vas):
        print(st.format(*va))


def print_wfmref(ps_list):
    """Print wfmref data."""
    st1, st2, st3, st4, st5, st6, st7 = ['{:<15}:'] * 7
    va1, va2, va3, va4, va5, va6, va7 = \
        [['wfmref_maxsize'],
         ['wfmref_select'],
         ['wfmref_size'],
         ['wfmref_idx'],
         ['wfmref_ptr_beg'],
         ['wfmref_ptr_end'],
         ['wfmref_ptr_idx']]
    for ps in ps_list:
        wfmref_ptr_values = ps.wfmref_pointer_values
        st1 += ' {:6d}'
        va1.append(ps.wfmref_maxsize)
        st2 += ' {:6d}'
        va2.append(ps.wfmref_select)
        st3 += ' {:6d}'
        va3.append(ps.wfmref_size)
        st4 += ' {:6d}'
        va4.append(ps.wfmref_idx)
        st5 += ' {:6d}'
        va5.append(wfmref_ptr_values[0])
        st6 += ' {:6d}'
        va6.append(wfmref_ptr_values[1])
        st7 += ' {:6d}'
        va7.append(wfmref_ptr_values[2])
    sts = [st1, st2, st3, st4, st5, st6, st7]
    vas = [va1, va2, va3, va4, va5, va6, va7]
    for st, va in zip(sts, vas):
        print(st.format(*va))


def plot_wfmref(ps_list):
    """Plot wfmref."""
    for i, ps in enumerate(ps_list):
        curve = ps.wfmref_read()
        plt.plot(curve, label='WfmRef {} ({} points)'.format(i, len(curve)))
    plt.xlabel('Index')
    plt.ylabel('Current [A]')
    plt.legend()
    plt.show()


def print_basic_info(ps_list):
    """Print all info."""
    print('--- power supply status ---')
    print_status(ps_list)
    # print('--- wfmref ---')
    print_wfmref(ps_list)
    # print()
    # plot_wfmref(ps)


def reset_powersupplies(udc, ps_list, opmode='SlowRef'):
    """."""
    # reset UDC
    udc.reset()

    ps = ps_list[0]
    if opmode == 'SlowRef':
        opmode = ps.CONST_PSBSMP.E_STATE_SLOWREF
    elif opmode == 'RmpWfm':
        opmode = ps.CONST_PSBSMP.E_STATE_RMPWFM
    else:
        print('Invalid opmode.')
        return
    for ps in ps_list:
        # turn power supply on
        ps.execute_function(
            func_id=ps.CONST_PSBSMP.F_TURN_ON,
            input_val=None,
            timeout=100)
        # change mode to RmpWfm
        ps.execute_function(
            func_id=ps.CONST_PSBSMP.F_SELECT_OP_MODE,
            input_val=opmode,
            timeout=100)
        time.sleep(0.010)  # needed?


def wfmref_flip(ps):
    id1 = ps.wfmref_select
    c1 = ps.wfmref_read()
    c_new = c1[::-1]
    # c_new = [i/1023 for i in range(1024)] # c_new[:500]
    # c_new = c1[:500]
    ps.wfmref_write(c_new)
    id2 = ps.wfmref_select
    c2 = ps.wfmref_read()
    plt.plot(c1, label='prev (id:{})'.format(id1))
    plt.plot(c2, label='next (id:{})'.format(id2))
    plt.legend()
    plt.show()


def test_wfmref_write_slowref():
    udc = create_udc('IA-08RaCtrl:CO-PSCtrl-SI5')
    all_ps = [udc[5], udc[6], udc[7]]
    ps5 = all_ps[0]
    reset_powersupplies(udc, all_ps, 'SlowRef')
    print_basic_info(all_ps)
    wfmref_flip(ps5)
    print_basic_info(all_ps)
    wfmref_flip(ps5)
    return udc, all_ps


def test_wfmref_write_rmpwfm():
    udc = create_udc('IA-08RaCtrl:CO-PSCtrl-SI5')
    all_ps = [udc[5], udc[6], udc[7]]
    ps5 = all_ps[0]
    reset_powersupplies(udc, all_ps, 'RmpWfm')
    print_basic_info(all_ps)
    wfmref_flip(ps5)
    print_basic_info(all_ps)
    wfmref_flip(ps5)
    return udc, all_ps
