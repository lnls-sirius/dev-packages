"""Tests with BeagleBone."""

import time
# import epics
import sys

from siriuspy.bsmp import BSMP
from siriuspy.pwrsupply.pru import PRU
from siriuspy.pwrsupply.pru import PRUSim
from siriuspy.pwrsupply.bsmp import ConstBSMP
from siriuspy.pwrsupply.bsmp import EntitiesFBP
from siriuspy.pwrsupply.bsmp_sim import BSMPSim_FBP
from siriuspy.pwrsupply.prucontroller import PRUCQueue
from siriuspy.pwrsupply.prucontroller import PRUController
from siriuspy.pwrsupply.model_factory import ModelFactory

P = 'T'

BBB1_device_ids = (1, 2)
BBB2_device_ids = (5, 6)
BBB3_device_ids = (20, )


siggen_config = [
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
]

curve1 = [i*2.0/(4000.0-1.0) for i in range(4000)]


def calc_siggen_duration():
    """Calc duration for Sine or DampedSine siggens."""
    num_cycles = siggen_config[1]
    freq = siggen_config[2]
    return num_cycles/freq


def bsmp_create(device_id, simulate=False):
    """Create BSMP object."""
    if simulate is True:
        pru = PRUSim()
        bsmp = BSMPSim_FBP(pru, device_id, EntitiesFBP())
    else:
        pru = PRU()
        bsmp = BSMP(pru, device_id, EntitiesFBP())
    return bsmp


def bsmp_read_variable(bsmp, variable_id):
    """Read BSMP variable."""
    ret = bsmp.read_variable(variable_id, 1000)
    return ret


def bsmp_reset_interlock(bsmp):
    """Reset interlocks."""
    resp, value = bsmp.execute_function(ConstBSMP.F_RESET_INTERLOCKS)
    # print('response: ', resp)
    # print('value   : ', value)


def bbb_pru_and_prucqueue(simulate=False):
    """Return PRU and PRUCQUEUE."""
    if simulate:
        pru = PRUSim()
    else:
        pru = PRU()
    prucqueue = PRUCQueue()
    return pru, prucqueue


def pruc_create(udcmodel, device_ids, simulate=False):
    """Method."""
    # create BBB controller
    pru, prucqueue = bbb_pru_and_prucqueue(simulate=simulate)
    pruc = PRUController(pru=pru,
                         prucqueue=prucqueue,
                         udcmodel=ModelFactory.get(udcmodel),
                         device_ids=device_ids,
                         processing=True,
                         scanning=True)
    return pruc


def bbb1_pruc_create(simulate=False):
    """Method."""
    # create BBB controller
    pruc = pruc_create('FBP', BBB1_device_ids, simulate=simulate)
    return pruc


def bbb2_pruc_create(simulate=False):
    """Method."""
    # create BBB controller
    pruc = pruc_create('FBP', BBB2_device_ids, simulate=simulate)
    return pruc


def bbb3_pruc_create(simulate=False):
    """Method."""
    # create BBB controller
    pruc = pruc_create('FBP_DCLink', BBB3_device_ids, simulate=simulate)
    return pruc


def bbbs_mix_pruc_create(simulate=False):
    """Method."""
    pru, prucqueue = bbb_pru_and_prucqueue(simulate=simulate)

    pruc1 = PRUController(pru=pru,
                          prucqueue=prucqueue,
                          udcmodel=ModelFactory.get('FBP_DCLink'),
                          device_ids=(20, ),
                          processing=True,
                          scanning=True)
    pruc2 = PRUController(pru=pru,
                          prucqueue=prucqueue,
                          udcmodel=ModelFactory.get('FBP'),
                          device_ids=BBB1_device_ids + BBB2_device_ids,
                          processing=True,
                          scanning=True)
    return pruc1, pruc2


def bbbs_mix_print_state(pruc1, pruc2):
    """Print."""
    # dclink
    for id in pruc1.device_ids:
        v = pruc1.read_variables(id, pruc1.params.ConstBSMP.V_V_OUT)
        print('dclink v_out dev_id={} [V]: {}'.format(id, v))
    # power supplies
    for id in pruc2.device_ids:
        v = pruc2.read_variables(id, pruc2.params.ConstBSMP.V_I_LOAD)
        print('pwrsupply i_load dev_id={} [A]: {}'.format(id, v))


def pruc_reset_interlocks(pruc):
    """Reset interlocks."""
    # try to reset and then check interlocks
    ids = pruc.device_ids
    pruc.exec_functions(ids, pruc.BSMP.F_RESET_INTERLOCKS)
    intlck = 0
    for id in ids:
        intlck |= pruc.read_variables(id, pruc.BSMP.V_PS_HARD_INTERLOCKS)
        intlck |= pruc.read_variables(id, pruc.BSMP.V_PS_SOFT_INTERLOCKS)
    if intlck:
        raise ValueError('could not reset interlocks!')


def pruc_init_slowref(pruc, current_sp=2.5):
    """Method."""
    ids = pruc.device_ids

    # set bbb to sync off
    pruc.pru_sync_stop()

    # try to reset and then check interlocks
    pruc_reset_interlocks(pruc)

    # turn power supplies on
    pruc.exec_functions(ids, pruc.BSMP.F_TURN_ON)
    # time.sleep(0.3)  # implemented within PRUController now

    # close loop
    pruc.exec_functions(ids, pruc.BSMP.F_CLOSE_LOOP)
    # time.sleep(0.3) # implemented within PRUController now

    # disable siggen
    pruc.exec_functions(ids, pruc.BSMP.F_DISABLE_SIGGEN)

    # set slowref
    pruc.exec_functions(ids,
                        pruc.BSMP.F_SELECT_OP_MODE,
                        pruc.BSMP.E_STATE_SLOWREF)

    # current setpoint
    pruc.exec_functions(ids, pruc.BSMP.F_SET_SLOWREF, current_sp)


def pruc_config_cycle_mode(pruc):
    """Config siggen and set power supplies to cycle mode."""
    ids = pruc.device_ids

    # set bbb to sync off
    pruc.pru_sync_stop()

    # disable siggen
    pruc.exec_functions(ids, pruc.BSMP.F_DISABLE_SIGGEN)

    # configure siggen parameters (needs disabled siggen!)
    pruc.exec_functions(ids,
                        pruc.BSMP.F_CFG_SIGGEN,
                        siggen_config)

    # set ps to cycle mode
    pruc.exec_functions(ids,
                        pruc.BSMP.F_SELECT_OP_MODE,
                        pruc.BSMP.E_STATE_CYCLE)


def pruc_run_cycle(pruc):
    """Run cycle mode.

    This function prepares PRU and devices so that timing trigger can
    be received and the duration of BSMP command 'sync_pulse', generated by
    PRU upon receiving the timing trigger, can be measured in the oscilloscope.
    """
    id = 1

    # get signal duration
    duration = calc_siggen_duration()

    # create pruc in deafault config
    pruc_init_slowref(pruc)

    # read siggen offset and use it as setpoint
    setpoint = pruc.read_variables(id, pruc.BSMP.V_SIGGEN_OFFSET)
    pruc.exec_functions(id, pruc.BSMP.F_SET_SLOWREF, setpoint)

    # configure cycle mode
    pruc_config_cycle_mode(pruc)

    # enters cycle mode
    pruc.pru_sync_start(sync_mode=pruc.PRU.SYNC_MODE.BRDCST)

    # loops until timing trigger is received
    print('waiting for trigger from EVR...', end='')
    sys.stdout.flush()
    while pruc.pru_sync_status == pruc.PRU.SYNC_STATE.ON:
        t0 = time.time()
        time.sleep(0.1)
    print('arrived.')

    # makes sure power supply is in enable_siggen
    print('waiting for siggen to be enabled...', end='')
    sys.stdout.flush()
    while pruc.read_variables(id, pruc.BSMP.V_SIGGEN_ENABLE) == 0:
        time.sleep(0.1)
    print('enabled.')

    # loops while cycling
    while time.time() - t0 < duration + 2.0:
        # read iload and siggen
        iload, siggen_enable = {}, {}
        for id2 in pruc.device_ids:
            siggen_enable[id2] = \
                pruc.read_variables(id2, pruc.BSMP.V_SIGGEN_ENABLE)
            iload[id2] = pruc.read_variables(id2, pruc.BSMP.V_I_LOAD)

        # print
        print('dtime:{:06.2f}'.format(time.time()-t0), end='')
        print('  -  ', end='')
        print('iload:', end='')
        for id2 in pruc.device_ids:
            print('{:+08.4f} '.format(iload[id2]), end='')
        print('  -  ', end='')
        print('sigge:', end='')
        for id2 in pruc.device_ids:
            print('{} '.format(siggen_enable[id2]), end='')
        print()

        time.sleep(0.1)

    # return to SlowRef mode
    pruc.exec_functions(id,
                        pruc.BSMP.F_SELECT_OP_MODE,
                        pruc.BSMP.E_STATE_SLOWREF)


def pruc_run_rmpwfm(pruc):
    """Run rmpwfm."""
    # create pruc in deafault config
    pruc_init_slowref(pruc)

    # write curve1 to PRu
    pruc.pru_curve_write(1, curve1)

    # enters cycle mode
    pruc.pru_sync_start(sync_mode=pruc.PRU.SYNC_MODE.RMPEND)

    print('power supply in rmpwfm mode, waiting for sync signal...')
