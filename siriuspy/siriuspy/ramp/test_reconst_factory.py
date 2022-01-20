#!/usr/bin/env python-sirius

"""Test reconstrction factories."""

from copy import deepcopy as _dcopy
import argparse as _argparse
import numpy as _np
import matplotlib.pyplot as plt

from siriuspy.clientconfigdb import ConfigDBDocument
from siriuspy.ramp.ramp import BoosterRamp
from siriuspy.ramp.waveform import Waveform
from siriuspy.ramp.magnet import get_magnet
from siriuspy.ramp.reconst_factory import BONormListFactory, BORFRampFactory, \
    BOTIRampFactory, BODipRampFactory

from siriuspy.search import PSSearch


PARSER = _argparse.ArgumentParser(description="Test BORamp Rebuild Factories.")
PARSER.add_argument(
    "factory", type=str, default='', help="Define which factory to test.")
ARGS = PARSER.parse_args()


PSNAMES = PSSearch.get_psnames({'sec': 'BO', 'dis': 'PS'})

R_ORIG = BoosterRamp('testing')
R_ORIG.load()

GLOBAL_CONF = ConfigDBDocument(
    config_type='global_config', name='ref_config')
GLOBAL_CONF.load()


def run():
    if ARGS.factory == 'BONormListFactory':
        dip_wav = R_ORIG.ps_waveform_get('BO-Fam:PS-B-1')

        ps2wfm = dict()
        # for psn in PSNAMES:
        #     if psn in ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2'):
        #         continue
        #     ps2wfm[psn] = R_ORIG.ps_waveform_get_currents(psn)

        for psn in PSNAMES:
            if psn in ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2'):
                continue
            for row in GLOBAL_CONF.value['pvs']:
                pvname = psn + ':Wfm-SP'
                if row[0] == pvname:
                    ps2wfm[psn] = row[1]
                    break

        fac = BONormListFactory(
            ramp_config=R_ORIG, waveforms=ps2wfm,
            opt_global=False, opt_times=False,
            opt_metric='current', use_config_times=True,
            use_straigth_estim=True,
            consider_beam_interval=False)
        # fac.read_waveforms()

        r_built = BoosterRamp('config_test')
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

        r_built.ps_normalized_configs_set(fac.normalized_configs)
        ntimes = r_built.ps_normalized_configs_times
        print(r_built)

        des_prec = fac.desired_reconstr_precision
        prec_reached = fac.precision_reached
        print('Precision rechead?', prec_reached[0])
        print('Maximum abs.error:', prec_reached[1])

        max_error = 0.0

        axs = plt.gca()
        axs.grid()
        for psn in PSNAMES:
            if psn in ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2'):
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
                # axs.plot(built_times, dif_curr, label=psn)
                axs.plot(built_times, dif_strg, label=psn)

        # for tim in ntimes:
        #     axs.plot([tim, tim], [-max_error, max_error], 'k-.')
        plt.legend()
        plt.title('Curves with error > than desired ({})'.format(des_prec))
        plt.show()

    elif ARGS.factory == 'BORFRampFactory':
        fac = BORFRampFactory()
        params = fac.rf_params
        _print_param_dict(params)

    elif ARGS.factory == 'BOTIRampFactory':
        fac = BOTIRampFactory()
        params = fac.ti_params
        _print_param_dict(params)

    elif ARGS.factory == 'BODipRampFactory':
        dip_name = 'BO-Fam:PS-B-1'
        dip_mag = get_magnet('BO-Fam:MA-B')

        # wav_orig = R_ORIG.ps_waveform_get_currents(dip_name)

        for row in GLOBAL_CONF.value['pvs']:
            if row[0] == dip_name + ':Wfm-SP':
                wav_orig = row[1]
                break

        wav_energy = dip_mag.conv_current_2_strength(wav_orig)

        fac = BODipRampFactory(ramp_config=R_ORIG, waveform=wav_orig)
        # fac.read_waveforms()
        params_final = fac.dip_params
        _print_param_dict(params_final)

        w_built = _dcopy(R_ORIG.ps_waveform_get(dip_name))
        for name, value in params_final.items():
            setattr(w_built, name, value)
        wav_curr = w_built.currents
        err_curr = wav_orig - wav_curr
        wav_strgt = w_built.strengths
        err_strgt = wav_energy - wav_strgt

        success = _np.allclose(err_curr, 0, atol=1e-5)
        max_error = _np.max(_np.abs(err_curr))
        print('Precision rechead?', success)
        print('Maximum abs.error:', max_error)

        fig, axs = plt.subplots(1, 2)
        fig.set_size_inches(12, 6)
        axs[0].plot(err_curr)
        axs[0].grid()
        axs[0].set_title('Current error')
        axs[1].plot(err_strgt)
        axs[1].grid()
        axs[1].set_title('Strength error')
        plt.show()


def _print_param_dict(params):
    string = ''
    fmtstr = '{:<'+str(25)+'}: {}\n'
    for key in sorted(params):
        string += fmtstr.format(key, params[key])
    print(string)


if __name__ == "__main__":
    run()
