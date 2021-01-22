#!/usr/bin/env python-sirius

import argparse as _argparse
import numpy as _np
import matplotlib.pyplot as plt
from copy import deepcopy as _dcopy

from siriuspy.ramp.ramp import BoosterRamp
from siriuspy.ramp.reconst_factory import BONormListFactory, BORFRampFactory, \
    BOTIRampFactory, BODipRampFactory

from siriuspy.search import PSSearch


parser = _argparse.ArgumentParser(description="Test BORamp Rebuild Factories.")
parser.add_argument(
    "factory", type=str, default='', help="Define which factory to test.")
args = parser.parse_args()


psnames = PSSearch.get_psnames({'sec': 'BO', 'dis': 'PS'})

r_orig = BoosterRamp('testing')
r_orig.load()


def run():
    if args.factory == 'BONormListFactory':
        ps2wfm = dict()
        for ps in psnames:
            if ps in ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2'):
                continue
            ps2wfm[ps] = r_orig.ps_waveform_get_currents(ps)

        fac = BONormListFactory(ramp_config=r_orig, waveforms=ps2wfm)
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

        r_built.ps_normalized_configs_set(fac.normalized_configs)
        times = r_built.ps_normalized_configs_times
        labels = r_built.ps_normalized_configs_labels

        print(r_built)
        # for name in r_built.ps_normalized_configs_names:
        #     print(r_built[name])

        f = plt.figure()
        ax = plt.gca()
        ax.grid()
        for ps in psnames:
            strgs = list()
            for t in times:
                strgs.append(r_built[t][ps])
            strgs = _np.array(strgs)

            dif = r_orig.ps_waveform_get_currents(ps) - \
                r_built.ps_waveform_get_currents(ps)
            if not _np.allclose(dif, 0, atol=1e-5):
                # ax.plot(r_orig.ps_waveform_get_times(ps),
                #         r_orig.ps_waveform_get_strengths(ps),
                #         'r.-', label=ps)
                # ax.plot(r_built.ps_waveform_get_times(ps),
                #         r_built.ps_waveform_get_strengths(ps),
                #         'k.-', label=ps)
                # ax.plot(times, strgs, 'b.')
                # ax.plot(times, _np.zeros((len(times), 1)).flatten(), 'b.')
                ax.plot(r_built.ps_waveform_get_times(ps), dif, 'g-')
        ax.legend()
        plt.show()

    elif args.factory == 'BORFRampFactory':
        fac = BORFRampFactory()
        params = fac.rf_params
        _print_param_dict(params)

    elif args.factory == 'BOTIRampFactory':
        fac = BOTIRampFactory()
        params = fac.ti_params
        _print_param_dict(params)

    elif args.factory == 'BODipRampFactory':
        wav = r_orig.ps_waveform_get_currents('BO-Fam:PS-B-1')
        fac = BODipRampFactory(ramp_config=r_orig, waveform=wav)
        params_init = fac._get_initial_params()
        # fac.read_waveforms()
        params_final = fac.dip_params
        print('initial')
        _print_param_dict(params_init)
        print('final')
        _print_param_dict(params_final)

        r_built_init = _dcopy(r_orig)
        for name, value in params_init.items():
            setattr(r_built_init, 'ps_ramp_' + name, value)
        wav_new_init = r_built_init.ps_waveform_get_currents('BO-Fam:PS-B-1')
        wav_err_init = wav - wav_new_init

        r_built_final = _dcopy(r_orig)
        for name, value in params_final.items():
            setattr(r_built_final, 'ps_ramp_' + name, value)
        wav_new_final = r_built_final.ps_waveform_get_currents('BO-Fam:PS-B-1')
        wav_err_final = wav - wav_new_final

        axis = plt.gca()
        axis.plot(_np.arange(len(wav)), wav_err_init, 'k', label='initial')
        axis.plot(_np.arange(len(wav)), wav_err_final, 'r--', label='final')
        axis.grid()
        plt.title('Fit errors')
        plt.legend()
        plt.show()


def _print_param_dict(params):
    string = ''
    fmtstr = '{:<'+str(25)+'}: {}\n'
    for key in sorted(params):
        string += fmtstr.format(key, params[key])
    print(string)


if __name__ == "__main__":
    run()
