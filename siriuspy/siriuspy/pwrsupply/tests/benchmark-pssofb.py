#!/usr/bin/env python-sirius
"""."""

import time
import numpy as np


TINY_CURRENT = (1e-3/400)*10


def benchmark(sofb, print_flag=False):
    """."""
    value = sofb.current
    setpoint = np.random.randint(0, 100, len(value))/1000
    sofb.current = setpoint
    t0_ = time.time()
    while not np.allclose(sofb.current, setpoint, TINY_CURRENT):
        pass
    t1_ = time.time()
    dt_ = 1e3*(t1_ - t0_)
    if print_flag:
        print('elapsed time: {:.3f} ms'.format(dt_))
    return dt_


def test_pvs(acc, psnames):
    """."""
    from siriuspy.devices import PowerSupply
    from siriuspy.devices import PSCorrSOFB
    import matplotlib.pyplot as plt

    psupplies = [PowerSupply(psname) for psname in psnames]

    # set slowref
    print('--- psupplies slowref')
    for psupply in psupplies:
        psupply.cmd_slowref()
    time.sleep(1.0)
    for psupply in psupplies:
        while not psupply.connected:
            time.sleep(0.1)
        print('{} : {}'.format(psupply.devname, psupply.opmode))

    # turn power supplies on
    print('--- psupplies on')
    for psupply in psupplies:
        psupply.cmd_turn_on()
    time.sleep(1.0)
    for psupply in psupplies:
        print('{} : {}'.format(psupply.devname, psupply.pwrstate))

    # wait for connection
    print('--- create device and wait for connection')
    sofb = PSCorrSOFB(psnames[0])
    while not sofb.connected:
        time.sleep(0.1)

    # check why PVs are connected but values are being returned None
    time.sleep(1.0)

    # neglect first setppoint in stats
    for _ in range(10):
        benchmark(sofb, print_flag=False)

    # do benchmark
    stats = list()
    for _ in range(5000):
        stats.append(benchmark(sofb, print_flag=True))
    stats = np.array(stats)

    # turn power supplies off
    print('--- psupplies off')
    for psupply in psupplies:
        psupply.cmd_turn_off()

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


def test_bo_pvs():
    """."""
    psnames = (
        'BO-03U:PS-CH',
        'BO-03U:PS-CV',
        'BO-05U:PS-CH',
        'BO-05U:PS-CV',
    )
    test_pvs('BO', psnames)


def test_si_pvs():
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
    test_pvs('SI', psnames)


test_bo_pvs()
# test_si_pvs()
