#!/usr/bin/env python-sirius

"""BeagleBone Controller.

This module implements classes that are used to do low level BeagleBone
communications, be it with PRU or BSMP requests to power supply controllers
at the other end of the serial line.
"""

import time

from siriuspy.pwrsupply.bsmp import FBPEntities
from siriuspy.pwrsupply.bsmp import Const
from siriuspy.pwrsupply.bbbcontroller import BBBController


BBB1_device_ids = (1, 2)
BBB2_device_ids = (5, 6)


siggen_config = (
    # --- siggen sine parameters ---
    0,       # type
    10,      # num_cycles
    0.5,     # freq
    2.0,     # amplitude
    0.0,     # offset
    0.0,     # aux_param[0]
    0.0,     # aux_param[1]
    0.0,     # aux_param[2]
    0.0,     # aux_param[3]
)


def create_bbb_controller(simulate=False, running=True,
                          device_ids=BBB1_device_ids):
    """Return a BBB controller."""
    bbbc = BBBController(bsmp_entities=FBPEntities(),
                         device_ids=BBB1_device_ids,
                         simulate=simulate,
                         processing=running,
                         scanning=running)
    return bbbc


def init_power_supplies(bbbc, current_sp=2.5):
    """Init power supplies linked to the bbb controller."""
    # set bbb to sync off
    bbbc.pru_sync_stop()

    # turn power supplies on
    for id in bbbc.device_ids:
        # turn power supply on
        bbbc.exec_function(id, Const.F_TURN_ON)
    time.sleep(0.3)

    # close loop
    for id in bbbc.device_ids:
        # turn power supply on
        bbbc.exec_function(id, Const.F_CLOSE_LOOP)
    time.sleep(0.3)

    # other initializations
    for id in bbbc.device_ids:

        # disable siggen
        bbbc.exec_function(id, Const.F_DISABLE_SIGGEN)

        # set slowref
        bbbc.exec_function(id, Const.F_SELECT_OP_MODE, args=(3,))

        # current setpoint
        bbbc.exec_function(id, Const.F_SET_SLOWREF, args=(current_sp))


def set_cycle_mode_in_power_supplies(bbbc):
    """Config siggen and set power supplies to cycle mode."""
    for id in bbbc.device_ids:
        # configure siggen parameters
        bbbc.exec_function(id, Const.F_CFG_SIGGEN, siggen_config)

        # disable siggen
        bbbc.exec_function(id, Const.F_DISABLE_SIGGEN)

        # set ps to cycle mode
        bbbc.exec_function(id, Const.F_SELECT_OP_MODE, args=(5,))


def calc_siggen_duration():
    """Calc duration for Sine or DampedSine siggens."""
    num_cycles = siggen_config[1]
    freq = siggen_config[2]
    return num_cycles/freq


def run_cycle(bbbc):
    """Set cycle_mode in bbb controller."""
    # get signal duration
    duration = calc_siggen_duration()

    # set sync on in cycle mode
    bbbc.pru_sync_start(bbbc.SYNC.CYCLE)
    print('waiting to enter cycle mode...')
    while bbbc.pru_get_sync_status() != bbbc.SYNC.ON:
        pass

    # print message
    print('wainting for timing trigger...')

    # loop until siggen is active
    not_finished, trigg_not_rcvd = [bbbc.pru_get_sync_status()] * 2
    while not_finished:
        if bbbc.pru_get_sync_status() == 0 and trigg_not_rcvd:
            trigg_not_rcvd = 0
            t0 = time.time()
            print('timing signal arrived!')

        # read iload and siggen
        iload, siggen_enable = {}, {}
        for id in bbbc.device_ids:
            siggen_enable[id] = bbbc.read_variable(id, Const.V_SIGGEN_ENABLE)
            iload[id] = bbbc.read_variable(id, Const.V_I_LOAD)

        # print info
        if not trigg_not_rcvd:
            # print
            print('dtime:{:06.2f}'.format(time.time()-t0), end='')
            print('    -    ', end='')
            print('iload:', end='')
            for id in bbbc.device_ids:
                print('{:+08.4f} '.format(iload[id]), end='')
            print('    -    ', end='')
            print('sigge:', end='')
            for id in bbbc.device_ids:
                print('{} '.format(siggen_enable[id]), end='')
            print()

        # test if finished
        if not trigg_not_rcvd and time.time() - t0 > duration + 2:
            not_finished = 0

        # sleep a little
        time.sleep(0.1)


def test_cycle():
    """Example of testing cycle mode."""
    # Example of testing cycle mode for powr supplies in BBB1

    # create BBB1 controller
    bbbc = create_bbb_controller()

    # initialized power supplies
    init_power_supplies(bbbc)

    # configure power supplies siggen and set them to run it
    set_cycle_mode_in_power_supplies(bbbc)

    # run cycle
    run_cycle(bbbc)
