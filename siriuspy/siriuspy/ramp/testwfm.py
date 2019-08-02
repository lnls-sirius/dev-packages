#!/usr/bin/env python-sirius

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

nrpts = 15000
duration = 490.0
start_energy = 30.0

rampup1_start_energy = 40.0
rampup2_start_energy = 175.0
rampdown_start_energy = 1000.0
rampdown_stop_energy = 40.0

rampup1_start_time = 10.0
rampup2_start_time = 130.0
rampdown_start_time = 380.0
rampdown_stop_time = 485.0

rampup_delta = 1*5.0
rampup_range = 60
rampdown_delta = 1*80.0
rampdown_range = 60


w1 = WaveformParam(
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
    wfm = w1.eval_at(time)
    print('============= Waveform Info =============')
    print('waveform minimum value       : {:+10.4f}'.format(min(wfm)))
    print('waveform start value         : {:+10.4f}'.format(w1.start_energy))
    print('waveform rampdown start value: {:+10.4f}'.format(w1.rampdown_start_energy))
    print('waveform maximum value       : {:+10.4f}'.format(max(wfm)))
    print('waveform rampup1_slope       : {:+10.4f}'.format(w1.rampup1_slope))
    print('waveform rampup2_slope       : {:+10.4f}'.format(w1.rampup2_slope))
    print('waveform ramdown_slope       : {:+10.4f}'.format(w1.rampdown_slope))


def waveform_plot(nrpts, slope=False, selected_values=[]):
    """Plot waveform."""
    time = _np.linspace(0, duration, nrpts)
    wfm = w1.eval_at(time)
    if slope:
        dt = (time[-1] - time[0])/(len(time)-1)
        wfm = (wfm[2:] - wfm[:-2])/2/dt
        wfm = _np.append(wfm, 0.0)
        wfm = _np.insert(wfm, 0, 0.0)
        wfm = 1000*wfm  # [ms -> s]
    minv, maxv = min(wfm), max(wfm)
    t1 = w1.rampup1_start_time
    dt1 = w1.rampup_range/2
    dt2 = w1.rampdown_range/2
    t2 = w1.rampup2_start_time
    t3 = w1.rampdown_start_time
    t4 = w1.rampdown_stop_time
    plt.plot([t1, t1], [minv, maxv], '-.', color='orange')
    plt.plot([t2-dt1, t2-dt1], [minv, maxv], '-.', color='orchid')
    plt.plot([t2, t2], [minv, maxv], '-.', color='orange')
    plt.plot([t2+dt1, t2+dt1], [minv, maxv], '-.', color='orchid')
    plt.plot([t3-dt2, t3-dt2], [minv, maxv], '-.', color='orchid')
    plt.plot([t3, t3], [minv, maxv], '-.', color='orange')
    plt.plot([t3+dt2, t3+dt2], [minv, maxv], '-.', color='orchid')
    plt.plot([t4, t4], [minv, maxv], '-.', color='orange')
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
    wfm = w1.eval_at(time)
    for _time, _wfm in zip(time, wfm):
        print('{:.16e} {:.16e}'.format(_time, _wfm))


waveform_info(nrpts)
waveform_plot(nrpts, slope=False, selected_values=[100, 890])
waveform_plot(nrpts, slope=True, selected_values=[-8000])
# waveform_print(nrpts)
