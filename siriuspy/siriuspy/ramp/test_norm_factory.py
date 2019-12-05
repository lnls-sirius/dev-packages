#!/usr/bin/env python-sirius

import numpy as _np
import matplotlib.pyplot as plt
from siriuspy.ramp.ramp import BoosterRamp
from siriuspy.ramp.norm_factory import BONormFactory
from siriuspy.search import MASearch


manames = MASearch.get_manames({'sec': 'BO', 'dis': 'MA'})

r_orig = BoosterRamp('mb_eje500mev_bpm01si_withoutSI')
r_orig.load()

ma2wfm = dict()
for ma in manames:
    if ma == 'BO-Fam:MA-B':
        continue
    ma2wfm[ma] = r_orig.ps_waveform_get_currents(ma)

fac = BONormFactory(ramp_config=r_orig, waveforms=ma2wfm)
# fac.read_waveforms()

r_built = BoosterRamp('testing')
attrs = [
    'ps_ramp_wfm_nrpoints_fams',
    'ps_ramp_wfm_nrpoints_corrs',
    'ps_ramp_duration',
    'ps_ramp_start_energy',
    'ps_ramp_rampup1_start_time',
    'ps_ramp_rampup1_start_energy',
    'ps_ramp_rampup2_start_time',
    'ps_ramp_rampup2_start_energy',
    'ps_ramp_rampup_smooth_intvl',
    'ps_ramp_rampup_smooth_energy',
    'ps_ramp_rampdown_start_time',
    'ps_ramp_rampdown_start_energy',
    'ps_ramp_rampdown_stop_time',
    'ps_ramp_rampdown_stop_energy',
    'ps_ramp_rampdown_smooth_intvl',
    'ps_ramp_rampdown_smooth_energy',
    'rf_ramp_rampup_start_time',
    'rf_ramp_rampup_stop_time',
    'rf_ramp_rampdown_start_time',
    'rf_ramp_rampdown_stop_time',
    'rf_ramp_bottom_voltage',
    'rf_ramp_top_voltage',
    'rf_ramp_bottom_phase',
    'rf_ramp_top_phase',
    'ti_params_injection_time',
    'ti_params_ejection_time',
    'ti_params_ps_ramp_delay',
    'ti_params_rf_ramp_delay',
]
for attr in attrs:
    setattr(r_built, attr, getattr(r_orig, attr))

for time, nconf in fac.normalized_configs:
    r_built.ps_normalized_configs_insert(time, nconf.name, nconf.value)
times = r_built.ps_normalized_configs_times
names = r_built.ps_normalized_configs_names

print(r_built)
# for name in r_built.ps_normalized_configs_names:
#     print(r_built[name])

f = plt.figure()
ax = plt.gca()
ax.grid()
for ma in manames:
    strgs = list()
    for n in names:
        strgs.append(r_built[n][ma])
    strgs = _np.array(strgs)

    dif = r_orig.ps_waveform_get_currents(ma) - \
        r_built.ps_waveform_get_currents(ma)
    if not _np.allclose(dif, 0, atol=1e-5):
        # ax.plot(r_orig.ps_waveform_get_times(ma),
        #         r_orig.ps_waveform_get_strengths(ma),
        #         'r.-', label=ma)
        # ax.plot(r_built.ps_waveform_get_times(ma),
        #         r_built.ps_waveform_get_strengths(ma),
        #         'k.-', label=ma)
        # ax.plot(times, strgs, 'b.')
        # ax.plot(times, _np.zeros((len(times), 1)).flatten(), 'b.')
        ax.plot(r_built.ps_waveform_get_times(ma), dif, 'g-')
ax.legend()
plt.show()
