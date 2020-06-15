#!/usr/bin/env python-sirius
"""."""

import time
import numpy as np


TINY_CURRENT = (1e-3/400)*100


def benchmark(pssofb, print_flag=False):
    """."""
    value = pssofb.current
    setpoint = np.random.randint(0, 100, len(value))/1000
    pssofb.current = setpoint
    t0_ = time.time()
    while not np.allclose(pssofb.current, setpoint, TINY_CURRENT):
        pass
    t1_ = time.time()
    dt_ = 1e3*(t1_ - t0_)
    if print_flag:
        print('elapsed time: {:.3f} ms'.format(dt_))
    return dt_


def turn_on_pwrsupplies(psnames):
    """."""
    from siriuspy.devices import PowerSupply

    psupplies = [PowerSupply(psname) for psname in psnames]

    # set slowref
    print('--- psupplies slowref')
    for psupply in psupplies:
        print('psupply slowref: ', psupply.devname)
        psupply.cmd_slowref()
    time.sleep(1.0)
    for psupply in psupplies:
        while not psupply.connected:
            time.sleep(0.1)
        print('{} : {}'.format(psupply.devname, psupply.opmode))

    # turn power supplies on
    print('--- psupplies on')
    for psupply in psupplies:
        print('psupply on: ', psupply.devname)
        psupply.cmd_turn_on()
    time.sleep(1.0)
    for psupply in psupplies:
        print('{} : {}'.format(psupply.devname, psupply.pwrstate))


def turn_off_pwrsupplies(psnames):
    """."""

    from siriuspy.devices import PowerSupply

    psupplies = [PowerSupply(psname) for psname in psnames]

    # turn power supplies off
    print('--- psupplies off')
    for psupply in psupplies:
        psupply.cmd_turn_off()


def test_pscorrsofb(acc, psnames):
    """."""
    from siriuspy.devices import PSCorrSOFB
    import matplotlib.pyplot as plt

    # prepare power supplies
    turn_on_pwrsupplies(psnames)

    # wait for connection
    print('--- create device and wait for connection')
    pssofb = PSCorrSOFB(psnames[0])
    while not pssofb.connected:
        time.sleep(0.1)

    # check why PVs are connected but values are being returned None
    time.sleep(1.0)

    # neglect first setppoint in stats
    for _ in range(10):
        benchmark(pssofb, print_flag=False)

    # do benchmark
    stats = list()
    for _ in range(5000):
        stats.append(benchmark(pssofb, print_flag=True))
    stats = np.array(stats)

    # turn power supplies off
    turn_off_pwrsupplies(psnames)

    print('--- benchmarks ---')
    print('avg: {:08.3f} ms'.format(np.mean(stats)))
    print('std: {:08.3f} ms'.format(np.std(stats)))
    print('min: {:08.3f} ms'.format(np.min(stats)))
    print('max: {:08.3f} ms'.format(np.max(stats)))

    plt.hist(stats, 100, log=True)
    plt.title(
        acc + ' - SOFB setpoint benchmark ({} operations)'.format(len(stats)))
    plt.xlabel('Excetution time [ms]')
    plt.ylabel('Number of realizations')
    plt.show()


def test_bo_pscorrsofb():
    """."""
    psnames = (
        'BO-03U:PS-CH',
        'BO-03U:PS-CV',
        'BO-05U:PS-CH',
        'BO-05U:PS-CV',
    )
    test_pscorrsofb('BO', psnames)


def test_si_pscorrsofb():
    """."""
    psnames = (
        'SI-01M1:PS-CH',
        'SI-01M1:PS-CV',
        'SI-01M2:PS-CH',
        'SI-01M2:PS-CV',
        'SI-01C2:PS-CH',
        'SI-01C2:PS-CV-1',
        'SI-01C2:PS-CV-2',
        )
    test_pscorrsofb('SI', psnames)


def test_si_psapplysofb():
    """."""
    from siriuspy.devices import PowerSupply
    from siriuspy.devices import PSApplySOFB

    pssofb = PSApplySOFB(PSApplySOFB.DEVICES.SI, auto_mon=True)

    pssofb.wait_for_connection()
    value = pssofb.current
    setpoint = np.random.randint(0, 100, len(value))/1000
    pssofb.current = setpoint
    time.sleep(0.1)
    readback = pssofb.current
    psnames = pssofb.psnames_ch + pssofb.psnames_cv
    for i in range(len(readback)):
        error = readback[i] - setpoint[i]
        print('{:<16s}: {:+09.5f} {:+09.5f}  {:+09.5f} [A]'.format(psnames[i], setpoint[i], readback[i], error))


    # pssofb.current = curr

    # for i in range(10):
    #     value = pssofb.current
    #     setpoint = np.random.randint(0, 100, len(value))/1000
    #     pssofb.current = setpoint
    #     t0_ = time.time()
    #     time.sleep(0.1)
    #     curr = pssofb.current
    #     # while not np.allclose(pssofb.current, setpoint, TINY_CURRENT):
    #     #     pass
    #     t1_ = time.time()
    #     dt_ = 1e3*(t1_ - t0_)
    #     print('elapsed time: {:.3f} ms'.format(dt_))
    #     print('max diff: {}'.format(max(abs(curr - setpoint))))
    #     print()

    # for i in range(100):
    #     benchmark(psapply, True)


    # psnames = psapply.psnames_ch + psapply.psnames_cv
    # turn_on_pwrsupplies(psnames)



# test_bo_pscorrsofb()
# test_si_pscorrsofb()
test_si_psapplysofb()
