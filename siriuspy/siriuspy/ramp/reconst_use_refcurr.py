#!/usr/bin/env python-sirius

"""Test reconstrction factories."""

import json
from copy import deepcopy as _dcopy
import numpy as _np
import matplotlib.pyplot as plt

from siriuspy.search import PSSearch, MASearch
from siriuspy.clientconfigdb import ConfigDBDocument
from siriuspy.ramp.ramp import BoosterRamp
from siriuspy.ramp.waveform import Waveform
from siriuspy.ramp.magnet import get_magnet


PSNAMES = PSSearch.get_psnames({'sec': 'BO', 'dis': 'PS'})

# R_ORIG = BoosterRamp('testing')
R_ORIG = BoosterRamp('testing_newexc_dip')
R_ORIG.load()

GLOBAL_CONF = ConfigDBDocument(
    config_type='global_config', name='ref_config')
GLOBAL_CONF.load()


def run():
    nconf = json.load(open("nconf_currents.txt"))

    nconf_strg = _dcopy(nconf)
    for strt in nconf_strg.keys():
        nct = float(strt)
        for psn in PSNAMES:
            mag = get_magnet(MASearch.conv_psname_2_psmaname(psn))
            curr = nconf[strt][psn]
            if psn in ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2'):
                nconf_strg[strt][psn] = mag.conv_current_2_strength(curr)
            else:
                energy = R_ORIG.ps_waveform_interp_energy(nct)
                strg = mag.conv_current_2_strength(
                    curr, strengths_dipole=energy)
                nconf_strg[strt][psn] = strg

    dip_wav = R_ORIG.ps_waveform_get('BO-Fam:PS-B-1')

    ps2wfm = dict()
    for psn in PSNAMES:
        if psn in ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2'):
            continue
        for row in GLOBAL_CONF.value['pvs']:
            pvname = psn + ':Wfm-SP'
            if row[0] == pvname:
                ps2wfm[psn] = row[1]
                break

    r_built = BoosterRamp('testing_newexc5_norm')
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
        setattr(r_built, attr, getattr(R_ORIG, attr))
    r_built.ps_normalized_configs_set(nconf_strg)
    ntimes = r_built.ps_normalized_configs_times
    # r_built.save()

    print(r_built)

    des_prec = 1e-5
    max_error = 0.0

    axs = plt.gca()
    axs.grid()
    for psn in PSNAMES:
        if psn in ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2'):
            continue
        # if psn not in [PSNAMES[-1], PSNAMES[-2]]:
        # if psn not in [PSNAMES[-3], PSNAMES[-4]]:
        # if psn not in [PSNAMES[1], ]:
        if psn in [PSNAMES[1], PSNAMES[-1], PSNAMES[-2], PSNAMES[-3], PSNAMES[-4]]:
            continue
        strgs = list()
        for tim in ntimes:
            strgs.append(r_built[tim][psn])
        strgs = _np.array(strgs)

        nr_pts = R_ORIG.ps_ramp_wfm_nrpoints_fams if 'Fam' in psn \
            else R_ORIG.ps_ramp_wfm_nrpoints_corrs
        orig_times = R_ORIG.ps_waveform_get_times(psn)
        orig_currs = ps2wfm[psn]
        orig_strgs = Waveform(
            psn, dipole=dip_wav, currents=orig_currs,
            wfm_nrpoints=nr_pts).strengths
        built_times = r_built.ps_waveform_get_times(psn)
        built_currs = r_built.ps_waveform_get_currents(psn)
        built_strgs = r_built.ps_waveform_get_strengths(psn)
        dif_curr = orig_currs - built_currs
        dif_strg = orig_strgs - built_strgs
        max_error = max(max_error, max(dif_curr))
        if not _np.allclose(dif_curr, 0, atol=des_prec):
            # axs.plot(orig_times, orig_strgs, 'r.-', label=psn)
            # axs.plot(built_times, built_strgs, 'k.-')
            # axs.plot(ntimes, strgs, 'b.')
            axs.plot(built_times, dif_curr, label=psn)
            # axs.plot(built_times, dif_strg, label=psn)

    for tim in ntimes:
        axs.plot([tim, tim], [-max_error, max_error], 'k-.')
    # plt.legend()
    plt.title('Curves with error > than desired ({})'.format(des_prec))
    print('Precision rechead?', max_error < des_prec)
    print('Maximum abs.error:', max_error)
    plt.show()


if __name__ == "__main__":
    run()
