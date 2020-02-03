from copy import deepcopy as _dcopy
import numpy as _np
from epics import PV as _PV
from siriuspy.search import PSSearch as _PSSearch
from .ramp import BoosterRamp as _BORamp
from .waveform import Waveform as _Waveform

TIMEOUT_CONN = 0.05


class BONormFactory:

    _PSNAME_DIPOLES = ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2')
    _PSNAME_DIPOLE_REF = _PSNAME_DIPOLES[0]
    _PVs = dict()

    def __init__(self, ramp_config, waveforms=dict()):
        """Init."""
        self._ramp_config = ramp_config
        self._dipole = ramp_config.ps_waveform_get(self._PSNAME_DIPOLE_REF)
        self._duration = ramp_config.ps_ramp_duration
        self._nrpoints_fams = ramp_config.ps_ramp_wfm_nrpoints_fams
        self._nrpoints_corrs = ramp_config.ps_ramp_wfm_nrpoints_corrs
        self._psnames = _PSSearch.get_psnames({'sec': 'BO', 'dis': 'PS'})
        for dip in self._PSNAME_DIPOLES:
            self._psnames.remove(dip)

        self._wfms_current = waveforms
        self._norm_configs_dict = dict()
        if waveforms:
            self._create_waveform_objects()
            self._generate_nconf_dict()

    @property
    def psnames(self):
        return self._psnames

    @property
    def waveforms(self):
        """Return a dict of psname: waveform in current values."""
        return self._wfms_current

    @waveforms.setter
    def waveforms(self, waveforms=dict()):
        """Set a dict of psname: waveform in current values."""
        self._wfms_current = waveforms
        if waveforms:
            self._create_waveform_objects()
            self._generate_nconf_dict()

    def read_waveforms(self):
        """Read waveform in current values from PVs."""
        if not BONormFactory._PVs:
            self._create_pvs()

        self._waveforms = dict()
        for ps in self.psnames:
            pv = BONormFactory._PVs[ps]
            pv.wait_for_connection(10*TIMEOUT_CONN)
            if not pv.connected:
                raise ConnectionError('There are disconnected PVs!')
            self._wfms_current[ps] = pv.get()

        self._create_waveform_objects()
        self._generate_nconf_dict()

    @property
    def normalized_configs(self):
        """Return dict of [time: normalized configuration]."""
        return _dcopy(self._norm_configs_dict)

    @property
    def precision_reached(self):
        """Precision reached.

        Return if the reconstructed normalized configuration dict
        reached the precision of 1.e-5.
        """
        if not self._norm_configs_dict:
            return False

        max_error = self._check_waveforms_error()
        if max_error < 1e-5:
            return True, max_error
        return False, max_error

    # ----- auxiliar methods -----

    def _create_pvs(self):
        pvs = dict()
        for ps in self.psnames:
            pvs[ps] = _PV(ps + ':Wfm-SP', connection_timeout=TIMEOUT_CONN)
        BONormFactory._PVs = pvs

    def _create_waveform_objects(self):
        self._ps2wfms = dict()
        for ps, wfm_curr in self._wfms_current.items():
            self._ps2wfms[ps] = _Waveform(
                ps, self._dipole, currents=wfm_curr,
                wfm_nrpoints=self._get_appropriate_wfmnrpoints(ps))

    def _get_appropriate_wfmnrpoints(self, psname):
        """Return appropriate number of points for psname."""
        if _PSSearch.conv_psname_2_psmodel(psname) == 'FBP':
            return self._nrpoints_corrs
        else:
            return self._nrpoints_fams

    def _calc_nconf_times(self, times, wfm):
        d1 = _np.diff(wfm)
        d2 = _np.diff(d1)
        ind = _np.where(_np.abs(d2) < 1e-10)[0]
        dind = _np.diff(ind)
        ind2 = _np.where(dind > 1)[0]

        idd2 = _np.ones(ind2.size+1, dtype=int)*(len(d2)-1)
        idd2[:ind2.size] = ind[ind2]
        idd1 = idd2 + 1
        idw = idd1 + 1

        a = d1[idd1]
        b = wfm[idw] - a*idw
        ind_inter = -_np.diff(b)/_np.diff(a)
        w_inter = a[:-1]*ind_inter + b[:-1]

        ind_orig = _np.arange(0, len(wfm))
        time_inter = _np.interp(ind_inter, ind_orig, times)
        if time_inter.size:
            time_inter2 = _np.round(time_inter, decimals=3)
            w_inter2 = _np.interp(time_inter2, time_inter, w_inter)
            return time_inter2, w_inter2
        else:
            return time_inter, w_inter

    def _check_waveforms_error(self):
        r_new = _BORamp()
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
            setattr(r_new, attr, getattr(self._ramp_config, attr))
        r_new.ps_normalized_configs_set(self.normalized_configs)

        max_error = 0.0
        for ps in self.psnames:
            error = self._ps2wfms[ps].currents - \
                r_new.ps_waveform_get_currents(ps)
            max_error = max(max_error, max(error))
        return max_error

    def _generate_nconf_dict(self):
        oversampling_factor = 1
        while not self.precision_reached:
            # get time instants and normalized strengths where there are
            # normalized configurations
            problems = False
            ps2time2strg = dict()
            times = set()
            for ps, wfm in self._ps2wfms.items():
                nrpts_orig = wfm.wfm_nrpoints
                ind_orig = _np.arange(0, nrpts_orig)
                t_orig = wfm.times
                w_orig = wfm.strengths

                nrpts = nrpts_orig*oversampling_factor
                ind = _np.linspace(0, ind_orig[-1], nrpts)
                t = _np.interp(ind, ind_orig, t_orig)
                w = _np.interp(ind, ind_orig, w_orig)

                time_inter, w_inter = self._calc_nconf_times(t, w)
                ps2time2strg[ps] = {i: w for i, w in zip(time_inter, w_inter)}
                times.update(time_inter)
                if not all(time_inter == sorted(time_inter)):
                    problems = True
                    break
            if problems and oversampling_factor == 1:
                oversampling_factor *= 4
                continue
            elif problems:
                raise Exception(
                    'Could not generate normalized configurations!')

            # sort and verify times
            times = sorted(times)
            if _np.any([t > self._duration for t in times]) or \
                    _np.any([t < 0 for t in times]):
                raise Exception(
                    'Could not generate normalized configurations!')
            if not times:
                times = {0.0, }

            # generate dict of normalized configs
            self._norm_configs_dict = dict()
            for t in times:
                energy = self._dipole.get_strength_from_time(t)
                nconf = dict()
                nconf['label'] = ' {:.4f}GeV'.format(energy)
                for dip in self._PSNAME_DIPOLES:
                    nconf[dip] = energy
                for ps in self.psnames:
                    if t in ps2time2strg[ps].keys():
                        nconf[ps] = ps2time2strg[ps][t]
                    else:
                        wfm = self._ps2wfms[ps]
                        nconf[ps] = wfm.get_strength_from_time(t)
                self._norm_configs_dict['{:.3f}'.format(t)] = nconf

            # TODO: verify case of precision not reached
            break
