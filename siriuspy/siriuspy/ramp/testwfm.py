#!/usr/bin/env python-sirius


# TODO: is this module deprecated?

import numpy as _np
import matplotlib.pyplot as plt
from waveform import WaveformParam


# ------------------
# Tabela da Liu
# ------------------
# T(ms) 	I(A)
# 0 	30 	cubo
# 10 	40 	reta
# 100 	175 	cubo
# 110 	195 	reta
# 370 	1027 	cubo
# 385 	1000 	reta
# 485 	40 	cubo
# 490 	30
# ------------------


current_3gev = 1013.2431  # [A]
current_130mev = 43.9658  # [A]
current_150mev = 50.625127792833354  # [A]


nrpts = 15000

duration = 490.0
start_energy = 35

rampup1_start_energy = 42.0
rampup2_start_energy = 199.7
rampdown_start_energy = 1140.7
rampdown_stop_energy = 42.0

rampup1_start_time = 10.0
rampup2_start_time = 140.0
rampdown_start_time = 378.0
rampdown_stop_time = 488.0

rampup_delta = 1*5.7
rampup_range = 60
rampdown_delta = 1*91.3
rampdown_range = 60


wfm1 = WaveformParam(
    duration=duration,
    start_energy=start_energy,
    rampup1_start_time=rampup1_start_time,
    rampup1_start_energy=rampup1_start_energy,
    rampup_delta=rampup_delta,
    rampup_range=rampup_range,
    rampup2_start_time=rampup2_start_time,
    rampup2_start_energy=rampup2_start_energy,
    rampdown_start_time=rampdown_start_time,
    rampdown_start_energy=rampdown_start_energy,
    rampdown_stop_time=rampdown_stop_time,
    rampdown_stop_energy=rampdown_stop_energy,
    rampdown_delta=rampdown_delta,
    rampdown_range=rampdown_range,
)


def waveform_info(nrpts):
    """Info."""
    time = _np.linspace(0, duration, nrpts)
    wfm = wfm1.eval_at(time)
    print('============= Waveform Info =============')
    print('waveform minimum value       : {:+10.4f}'.format(min(wfm)))
    print('waveform start value         : {:+10.4f}'.format(wfm1.start_energy))
    print('waveform rampdown start value: {:+10.4f}'.format(wfm1.rampdown_start_energy))
    print('waveform maximum value       : {:+10.4f}'.format(max(wfm)))
    print('waveform rampup1_slope       : {:+10.4f}'.format(wfm1.rampup1_slope))
    print('waveform rampup2_slope       : {:+10.4f}'.format(wfm1.rampup2_slope))
    print('waveform ramdown_slope       : {:+10.4f}'.format(wfm1.rampdown_slope))


def waveform_plot(nrpts, slope=False, selected_values=[]):
    """Plot waveform."""
    time = _np.linspace(0, duration, nrpts)
    wfm = wfm1.eval_at(time)
    if slope:
        dt = (time[-1] - time[0])/(len(time)-1)
        wfm = (wfm[2:] - wfm[:-2])/2/dt
        wfm = _np.append(wfm, 0.0)
        wfm = _np.insert(wfm, 0, 0.0)
        wfm = 1000*wfm  # [ms -> s]
    minv, maxv = min(wfm), max(wfm)
    time1 = wfm1.rampup1_start_time
    dt1 = wfm1.rampup_range/2
    dt2 = wfm1.rampdown_range/2
    time2 = wfm1.rampup2_start_time
    time3 = wfm1.rampdown_start_time
    time4 = wfm1.rampdown_stop_time
    plt.plot([time1, time1], [minv, maxv], '-.', color='orange')
    plt.plot([time2-dt1, time2-dt1], [minv, maxv], '-.', color='orchid')
    plt.plot([time2, time2], [minv, maxv], '-.', color='orange')
    plt.plot([time2+dt1, time2+dt1], [minv, maxv], '-.', color='orchid')
    plt.plot([time3-dt2, time3-dt2], [minv, maxv], '-.', color='orchid')
    plt.plot([time3, time3], [minv, maxv], '-.', color='orange')
    plt.plot([time3+dt2, time3+dt2], [minv, maxv], '-.', color='orchid')
    plt.plot([time4, time4], [minv, maxv], '-.', color='orange')
    for e in selected_values:
        plt.plot([min(time), max(time)], [e, e], '--', color='red')
    plt.plot(time, wfm, '-b')
    plt.plot()
    plt.xlabel('Time [ms]')
    if slope:
        plt.title('Energy|Current Ramp')
        plt.ylabel('Energy/time|Current/time [GeV/s|A/s]')
    else:
        plt.title('Energy|Current Ramp Slope')
        plt.ylabel('Energy|Current [GeV|A]')
    plt.grid()
    plt.show()


def waveform_print(nrpts):
    """Print waveform."""
    time = _np.linspace(0, duration, nrpts)
    wfm = wfm1.eval_at(time)
    for _time, _wfm in zip(time, wfm):
        print('{:.16e} {:.16e}'.format(_time, _wfm))


waveform_info(nrpts)
waveform_plot(nrpts, slope=False,
              selected_values=[current_150mev, current_3gev])
waveform_plot(nrpts, slope=True, selected_values=[4000, -10000])
# waveform_print(nrpts)
