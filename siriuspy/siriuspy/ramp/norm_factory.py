import numpy as _np
from epics import PV as _PV
from siriuspy.search import MASearch as _MASearch, PSSearch as _PSSearch
from .ramp import BoosterRamp as _BORamp, BoosterNormalized as _BONormalized
from .waveform import Waveform as _Waveform

TIMEOUT_CONN = 0.05


class BONormFactory:

    _MANAME_DIPOLE = 'BO-Fam:MA-B'
    _PVs = dict()

    def __init__(self, ramp_config, waveforms=dict()):
        """Init."""
        self._ramp_config = ramp_config
        self._dipole = ramp_config.ps_waveform_get(self._MANAME_DIPOLE)
        self._duration = ramp_config.ps_ramp_duration
        self._nrpoints_fams = ramp_config.ps_ramp_wfm_nrpoints_fams
        self._nrpoints_corrs = ramp_config.ps_ramp_wfm_nrpoints_corrs
        self._manames = _MASearch.get_manames({'sec': 'BO', 'dis': 'MA'})
        self._manames.remove(self._MANAME_DIPOLE)

        self._wfms_current = waveforms
        self._norm_configs_list = list()
        if waveforms:
            self._create_waveform_objects()
            self._generate_nconf_list()

    @property
    def manames(self):
        return self._manames

    @property
    def waveforms(self):
        """Return a dict of maname: waveform in current values."""
        return self._wfms_current

    @waveforms.setter
    def waveforms(self, waveforms=dict()):
        """Set a dict of maname: waveform in current values."""
        self._wfms_current = waveforms
        if waveforms:
            self._create_waveform_objects()
            self._generate_nconf_list()

    def read_waveforms(self):
        """Read waveform in current values from PVs."""
        if not BONormFactory._PVs:
            self._create_pvs()

        self._waveforms = dict()
        for ma in self.manames:
            pv = BONormFactory._PVs[ma]
            pv.wait_for_connection(10*TIMEOUT_CONN)
            self._wfms_current[ma] = pv.get()

        self._create_waveform_objects()
        self._generate_nconf_list()

    @property
    def normalized_configs(self):
        """Return list of [time, normalized configuration]."""
        return self._norm_configs_list

    @property
    def precision_reached(self):
        """Precision reached.

        Return if the reconstructed normalized configuration list
        reached the precision of 1.e-5.
        """
        if not self._norm_configs_list:
            return False

        max_error = self._check_waveforms_error()
        if max_error < 1e-5:
            return True, max_error
        return False, max_error

    # ----- auxiliar methods -----

    def _create_pvs(self):
        pvs = dict()
        for ma in self.manames:
            pvs[ma] = _PV(ma + ':Wfm-SP', connection_timeout=TIMEOUT_CONN)
        BONormFactory._PVs = pvs

    def _create_waveform_objects(self):
        self._ma2wfms = dict()
        for ma, wfm_curr in self._wfms_current.items():
            self._ma2wfms[ma] = _Waveform(
                ma, self._dipole, currents=wfm_curr,
                wfm_nrpoints=self._get_appropriate_wfmnrpoints(ma))

    def _get_appropriate_wfmnrpoints(self, maname):
        """Return appropriate number of points for maname."""
        psname = _MASearch.conv_maname_2_psnames(maname)
        if _PSSearch.conv_psname_2_psmodel(psname[0]) == 'FBP':
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
        for time, nconf in self._norm_configs_list:
            r_new.ps_normalized_configs_insert(time, nconf.name, nconf.value)

        max_error = 0.0
        for ma in self.manames:
            error = self._ma2wfms[ma].currents - \
                r_new.ps_waveform_get_currents(ma)
            max_error = max(max_error, max(error))
        return max_error

    def _generate_nconf_list(self):
        oversampling_factor = 1
        while not self.precision_reached:
            # get time instants and normalized strengths where there are
            # normalized configurations
            problems = False
            ma2time2strg = dict()
            times = set()
            for ma, wfm in self._ma2wfms.items():
                nrpts_orig = wfm.wfm_nrpoints
                ind_orig = _np.arange(0, nrpts_orig)
                t_orig = wfm.times
                w_orig = wfm.strengths

                nrpts = nrpts_orig*oversampling_factor
                ind = _np.linspace(0, ind_orig[-1], nrpts)
                t = _np.interp(ind, ind_orig, t_orig)
                w = _np.interp(ind, ind_orig, w_orig)

                time_inter, w_inter = self._calc_nconf_times(t, w)
                ma2time2strg[ma] = {i: w for i, w in zip(time_inter, w_inter)}
                times.update(time_inter)
                if not all(time_inter == sorted(time_inter)):
                    problems = True
                    break
            if problems:
                oversampling_factor *= 4
                continue

            # sort and verify times
            times = sorted(times)
            if _np.any([t > self._duration for t in times]) or \
                    _np.any([t < 0 for t in times]):
                raise Exception(
                    'Could not generate normalized configuration list!')
            if not times:
                times = {0.0, }

            # generate list of normalized configs
            self._norm_configs_list = list()
            for t in times:
                energy = self._dipole.get_strength_from_time(t)
                nconf = _BONormalized()
                nconf.name += ' {:.4f}GeV'.format(energy)
                for ma in self.manames:
                    if t in ma2time2strg[ma].keys():
                        nconf[ma] = ma2time2strg[ma][t]
                    else:
                        wfm = self._ma2wfms[ma]
                        nconf[ma] = wfm.get_strength_from_time(t)
                self._norm_configs_list.append([t, nconf])

            # TODO: verify case of oversampling_factor > 1
            # oversampling_factor *= 4
            break
