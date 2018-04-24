"""Tests with BeagleBone."""

import time
import epics

# from siriuspy.bsmp import BSMP
from siriuspy.csdevice.pwrsupply import Const as PSConst
# from siriuspy.pwrsupply.pru import PRU
from siriuspy.pwrsupply.bsmp import BSMPConst
from siriuspy.pwrsupply.bsmp import FBPEntities
from siriuspy.pwrsupply.prucontroller import PRUController

TPREFIX = ''

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


def configure_timing_modules(cycle=True):
    """Configure timing system."""
    print('Configuring Timing Modules to ' + ('cycle' if cycle else 'ramp'))
    epics.caput(TPREFIX + 'AS-Glob:TI-EVG:Evt01Mode-Sel', 'External')
    epics.caput(TPREFIX + 'AS-Glob:TI-EVG:DevEnbl-Sel', 1)
    epics.caput(TPREFIX + 'AS-Glob:TU-EVG:RFDiv-SP', 4)
    epics.caput(TPREFIX + 'AS-Glob:TI-EVR-1:DevEnbl-Sel', 1)
    epics.caput(TPREFIX + 'AS-Glob:TI-EVR-1:OTP00Width-SP', 7000)
    epics.caput(TPREFIX + 'AS-Glob:TI-EVR-1:OTP00State-Sel', 1)
    epics.caput(TPREFIX + 'AS-Glob:TI-EVR-1:OTP00Evt-SP', 1)
    epics.caput(TPREFIX + 'AS-Glob:TI-EVR-1:OTP00Pulses-SP',
                1 if cycle else 4000)


def calc_siggen_duration():
    """Calc duration for Sine or DampedSine siggens."""
    num_cycles = siggen_config[1]
    freq = siggen_config[2]
    return num_cycles/freq


def reset_interlocks(pruc):
    """Reset interlocks."""
    # try to reset and then check interlocks
    ids = pruc.device_ids
    pruc.exec_function(ids, BSMPConst.F_RESET_INTERLOCKS)
    intlck = 0
    for id in ids:
        intlck |= pruc.read_variable(ids[0], BSMPConst.V_PS_HARD_INTERLOCK)
        intlck |= pruc.read_variable(ids[0], BSMPConst.V_PS_SOFT_INTERLOCK)
    if intlck:
        raise ValueError('could not reset interlocks!')


def create_pruc(self):
    """Method."""
    # create BBB controller
    pruc = PRUController(bsmp_entities=FBPEntities(),
                         device_ids=BBB1_device_ids,
                         simulate=False,
                         processing=True,
                         scanning=True)
    return pruc


def init_slowref(pruc):
    """Method."""
    ids = pruc.device_ids

    # set bbb to sync off
    pruc.pru_sync_stop()

    # try to reset and then check interlocks
    reset_interlocks(pruc)

    # turn power supplies on
    pruc.exec_function(ids, BSMPConst.F_TURN_ON)
    # time.sleep(0.3)  # implemented within PRUController now

    # close loop
    pruc.exec_function(ids, BSMPConst.F_CLOSE_LOOP)
    # time.sleep(0.3) # implemented within PRUController now

    # disable siggen
    pruc.exec_function(ids, BSMPConst.F_DISABLE_SIGGEN)

    # set slowref
    pruc.exec_function(ids, BSMPConst.F_SELECT_OP_MODE, args=(3,))

    # current setpoint
    current_sp = 2.5
    pruc.exec_function(ids, BSMPConst.F_SET_SLOWREF, args=(current_sp))


def config_cycle_mode(pruc):
    """Config siggen and set power supplies to cycle mode."""
    ids = pruc.device_ids

    # set bbb to sync off
    pruc.pru_sync_stop()

    # disable siggen
    pruc.exec_function(ids, BSMPConst.F_DISABLE_SIGGEN)

    # configure siggen parameters (needs disabled siggen!)
    pruc.exec_function(ids, BSMPConst.F_CFG_SIGGEN, siggen_config)

    # set ps to cycle mode
    pruc.exec_function(ids, BSMPConst.F_SELECT_OP_MODE,
                       args=(PSConst.States.Cycle,))


def measure_duration_bsmp_sync_pulse(pruc):
    """Measure BSMP command sync_pulse.

    This function prepares PRU and devices so that timing trigger can
    be received and the duration of BSMP command 'sync_pulse', generated by
    PRU upon receiving the timing trigger, can be measured in the oscilloscope.
    """
    # get signal duration
    duration = calc_siggen_duration()

    # create pruc in deafault config
    init_slowref(pruc)

    # enters cycle mode
    pruc.pru_sync_start(sync_mode=pruc.SYNC.RMPEND)

    # loops until timing trigger is received
    print('waiting for trigger from EVR...', end='')
    while pruc.pru_sync_status == pruc.SYNC.ON:
        t0 = time.time()
        time.sleep(0.1)
    print('arrived.')

    # makes sure power supply is in enable_siggen
    print('waiting for siggen to be enabled...', end='')
    while pruc.read_variable(id, BSMPConst.V_SIGGEN_ENABLE) == 0:
        time.sleep(0.1)
    print('enabled.')

    # loops while cycling
    while time.time() - t0 < duration + 2.0:
        # read iload and siggen
        iload, siggen_enable = {}, {}
        for id in pruc.device_ids:
            siggen_enable[id] = \
                pruc.read_variable(id, BSMPConst.V_SIGGEN_ENABLE)
            iload[id] = pruc.read_variable(id, BSMPConst.V_I_LOAD)

        # print
        print('dtime:{:06.2f}'.format(time.time()-t0), end='')
        print('  -  ', end='')
        print('iload:', end='')
        for id in pruc.device_ids:
            print('{:+08.4f} '.format(iload[id]), end='')
        print('  -  ', end='')
        print('sigge:', end='')
        for id in pruc.device_ids:
            print('{} '.format(siggen_enable[id]), end='')
        print()

        time.sleep(0.1)


# @staticmethod
# def basic_tests():
#     """Basic."""
#     pru, bsmp = create_bsmp()
#
#
# @staticmethod
# def create_bbb_controller(simulate=False, running=True,
#                           device_ids=BBB1_device_ids):
#     """Return a BBB controller."""
#     pruc = PRUController(bsmp_entities=FBPEntities(),
#                          device_ids=BBB1_device_ids,
#                          simulate=simulate,
#                          processing=running,
#                          scanning=running)
#     return pruc
#
#
# @staticmethod
# def set_rmpwfm_mode_in_power_supplies(pruc):
#     """Config rmpwfm and set power supplies to rmpwfm mode."""
#     ids = pruc.device_ids
#
#     # configure siggen parameters
#     pruc.exec_function(ids, BSMPConst.F_CFG_SIGGEN, siggen_config)
#
#     # disable siggen
#     pruc.exec_function(ids, BSMPConst.F_DISABLE_SIGGEN)
#
#     # set ps to cycle mode
#     pruc.exec_function(ids, BSMPConst.F_SELECT_OP_MODE,
#                        args=(PSConst.States.Cycle,))
#
#
# @staticmethod
# def run_cycle(pruc):
#     """Set cycle_mode in bbb controller."""
#     # get signal duration
#     duration = calc_siggen_duration()
#
#     # set sync on in cycle mode
#     pruc.pru_sync_start(pruc.SYNC.CYCLE)
#     print('waiting to enter cycle mode...')
#     while pruc.pru_sync_status != pruc.SYNC.ON:
#         pass
#
#     # print message
#     print('wainting for timing trigger...')
#
#     # loop until siggen is active
#     not_finished, trigg_not_rcvd = [pruc.pru_sync_status] * 2
#     while not_finished:
#         if pruc.pru_sync_status == 0 and trigg_not_rcvd:
#             trigg_not_rcvd = 0
#             t0 = time.time()
#             print('timing signal arrived!')
#
#         # read iload and siggen
#         iload, siggen_enable = {}, {}
#         for id in pruc.device_ids:
#             siggen_enable[id] = \
#                 pruc.read_variable(id, BSMPConst.V_SIGGEN_ENABLE)
#             iload[id] = pruc.read_variable(id, BSMPConst.V_I_LOAD)
#
#         # print info
#         if not trigg_not_rcvd:
#             # print
#             print('dtime:{:06.2f}'.format(time.time()-t0), end='')
#             print('    -    ', end='')
#             print('iload:', end='')
#             for id in pruc.device_ids:
#                 print('{:+08.4f} '.format(iload[id]), end='')
#             print('    -    ', end='')
#             print('sigge:', end='')
#             for id in pruc.device_ids:
#                 print('{} '.format(siggen_enable[id]), end='')
#             print()
#
#         # test if finished
#         if not trigg_not_rcvd and time.time() - t0 > duration + 2:
#             not_finished = 0
#
#         # sleep a little
#         time.sleep(0.1)
#
#
# @staticmethod
# def run_rmpwfm():
#     """Example of testing rmp mode."""
#     # Example of testing cycle mode for powr supplies in BBB1
#
#     # create BBB1 controller
#     pruc = create_pruc()
#
#     # configure power supplies rmpwfm and set them to run it
#     pruc.exec_function(pruc.device_ids, BSMPConst.F_SELECT_OP_MODE,
#                        args=(PSConst.States.RmpWfm,))
#
#     # set PRU sync mode
#     pruc.pru_sync_start(pruc.SYNC.RMPEND)
#
#
# @staticmethod
# def test_cycle():
#     """Example of testing cycle mode."""
#     # Example of testing cycle mode for powr supplies in BBB1
#
#     # create BBB1 controller
#     pruc = create_bbb_controller()
#
#     # initialized power supplies
#     init_power_supplies(pruc)
#
#     # configure power supplies siggen and set them to run it
#     set_cycle_mode_in_power_supplies(pruc)
#
#     # run cycle
#     run_cycle(pruc)
