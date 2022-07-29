"""Reconstruction factories."""

from copy import deepcopy as _dcopy
import numpy as _np
from scipy.optimize import least_squares

from ..epics import PV as _PV
from ..search import PSSearch as _PSSearch, LLTimeSearch as _LLTimeSearch, \
    MASearch as _MASearch
from .ramp import BoosterRamp as _BORamp
from .waveform import Waveform as _Waveform, WaveformDipole as _WaveformDipole
from .magnet import get_magnet as _get_magnet


TIMEOUT_CONN = 0.05


class BODipRampFactory:
    """Class to rebuild Dipole energies from machine state."""

    _PSNAME_DIPOLES = ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2')
    _PSNAME_DIPOLE_REF = _PSNAME_DIPOLES[0]
    _ppties_2_fit = [
        'start_value',
        'rampup1_start_value',
        'rampup2_start_value',
        'rampdown_start_value',
        'rampup_smooth_value',
        'rampdown_stop_value',
        'rampdown_smooth_value',
    ]
    _ppties_2_use = [
        'duration',
        'rampup1_start_time',
        'rampup2_start_time',
        'rampdown_start_time',
        'rampdown_stop_time',
        'rampup_smooth_intvl',
        'rampdown_smooth_intvl',
    ]
    _PVs = dict()

    def __init__(self, ramp_config, waveform=None):
        """Init."""
        self._ramp_config = ramp_config
        self._duration = self._ramp_config.ps_ramp_duration
        self._magnet = _get_magnet(_MASearch.conv_psname_2_psmaname(
            BODipRampFactory._PSNAME_DIPOLE_REF))
        self._nrpoints = None
        self._times = None
        self.waveform = _np.array(waveform)
        self._create_pvs()

    @property
    def waveform(self):
        """Return waveform in current values."""
        return self._waveform

    @waveform.setter
    def waveform(self, waveform=None):
        """Set waveform in current values."""
        if waveform is None:
            waveform = _np.array([])
        self._waveform = waveform
        self._nrpoints = self._waveform.size
        self._times = _np.linspace(0, self._duration, self._nrpoints)

    def read_waveform(self):
        """Read waveform in current values from PVs."""
        if not BODipRampFactory._PVs:
            self._create_pvs()

        dipname = BODipRampFactory._PSNAME_DIPOLE_REF
        pvobj = BODipRampFactory._PVs[dipname]
        pvobj.wait_for_connection(10*TIMEOUT_CONN)
        if not pvobj.connected:
            raise ConnectionError('Dipole waveform PV is disconnected!')
        self._waveform = pvobj.get()
        self._nrpoints = self._waveform.size
        self._times = _np.linspace(0, self._duration, self._nrpoints)

    @property
    def dip_params(self):
        """Return dipole parameters rebuilt from PV values."""
        return self._generate_dip_params()

    # ----- private methods -----

    def _create_pvs(self):
        dipname = BODipRampFactory._PSNAME_DIPOLE_REF
        pvs = {dipname: _PV(
            dipname + ':Wfm-SP', connection_timeout=TIMEOUT_CONN)}
        BODipRampFactory._PVs = pvs

    def _generate_dip_params(self):
        if self._waveform is None:
            raise ValueError(
                'Waveform has None value. '
                'Set a valid value to waveform property '
                'or call read_waveform method.')

        init_params = self._get_initial_params()
        _x_init = [init_params[ppty] for ppty in
                   BODipRampFactory._ppties_2_fit]
        _x_final = least_squares(
            self._err_func, _x_init, method='lm').x
        final_params = {ppty: _x_final[i] for i, ppty in
                        enumerate(BODipRampFactory._ppties_2_fit)}

        result = dict()
        for ppty, value in final_params.items():
            energy_ppty = ppty.replace('value', 'energy')
            result[energy_ppty] = self._magnet.conv_current_2_strength(value)
        return result

    def _get_initial_params(self):
        params = dict()
        for ppty in BODipRampFactory._ppties_2_fit:
            if ppty in ['rampup2_start_value', 'rampdown_start_value',
                        'rampup_smooth_value', 'rampdown_smooth_value']:
                continue
            else:
                time_ppty_name = 'ps_ramp_'+ppty.replace('value', 'time')
                time = 0.0 if ppty == 'start_value' else getattr(
                    self._ramp_config, time_ppty_name)
                params[ppty] = _np.interp(time, self._times, self.waveform)

        def calc_intersection(s1_times, s2_times, time):
            slopes, offsets = list(), list()
            for s_times in [s1_times, s2_times]:
                ids = _np.arange(len(self._times))
                s_ids = _np.round(_np.interp(s_times, self._times, ids))
                slc = slice(int(s_ids[0]), int(s_ids[1]))
                s_x, s_y = self._times[slc], self.waveform[slc]
                s_off, s_slp = _np.polynomial.polynomial.polyfit(s_x, s_y, 1)
                offsets.append(s_off)
                slopes.append(s_slp)
            time_inter = -1 * _np.diff(offsets)/_np.diff(slopes)
            if not s1_times[-1] < time_inter < s2_times[0]:
                time_inter = time
            else:
                time_inter = time_inter[0]
            val_inter = slopes[0]*time_inter + offsets[0]
            return val_inter

        # calculate value for rampup2_start and rampdown_start
        ru1_times = [self._ramp_config.ps_ramp_rampup1_start_time,
                     (self._ramp_config.ps_ramp_rampup2_start_time -
                      self._ramp_config.ps_ramp_rampup_smooth_intvl/2)]
        ru2_times = [(self._ramp_config.ps_ramp_rampup2_start_time +
                      self._ramp_config.ps_ramp_rampup_smooth_intvl/2),
                     (self._ramp_config.ps_ramp_rampdown_start_time -
                      self._ramp_config.ps_ramp_rampdown_smooth_intvl/2)]
        rd_times = [(self._ramp_config.ps_ramp_rampdown_start_time +
                     self._ramp_config.ps_ramp_rampdown_smooth_intvl/2),
                    self._ramp_config.ps_ramp_rampdown_stop_time]

        ru_time = self._ramp_config.ps_ramp_rampup2_start_time
        params['rampup2_start_value'] = calc_intersection(
            ru1_times, ru2_times, ru_time)
        params['rampup_smooth_value'] = params['rampup2_start_value'] - \
            _np.interp(ru_time, self._times, self.waveform)

        rd_time = self._ramp_config.ps_ramp_rampdown_start_time
        params['rampdown_start_value'] = calc_intersection(
            ru2_times, rd_times, rd_time)
        params['rampdown_smooth_value'] = params['rampdown_start_value'] - \
            _np.interp(rd_time, self._times, self.waveform)

        return params

    def _err_func(self, params):
        new = _WaveformDipole()
        for ppty in BODipRampFactory._ppties_2_use:
            val = getattr(self._ramp_config, 'ps_ramp_' + ppty)
            setattr(new, ppty, val)
        for i, ppty in enumerate(BODipRampFactory._ppties_2_fit):
            setattr(new, ppty, params[i])
        error = self.waveform - new.currents
        return error


class BONormListFactory:
    """Class to rebuild Norm. Config. List from machine state."""

    _PSNAME_DIPOLES = ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2')
    _PSNAME_DIPOLE_REF = _PSNAME_DIPOLES[0]
    _PVs = dict()

    # desired reconstruction precision
    _DESIRED_PRECISION = 1e-5

    # thersholds to norm. configs time detection
    _THRESHOLD_DEFAULT = 1e-10
    _THRESHOLD_PROBLEM = 1e-4

    # loss factors consider that a change of 1e-1urad in a corrector is
    # comparable to a change of 1e-4 in tune fraction and 1e-2 in chromaticity
    _LOSS_FACTOR_CORRS = 1
    _LOSS_FACTOR_QUADS = 2e-5
    _LOSS_FACTOR_SEXTS = 1e-2

    # if considering only beam interval
    _BEAM_INTERVAL = [0.0, 300.0]

    def __init__(self, ramp_config, waveforms=None, opt_metric='strength',
                 opt_global=False, opt_times=False, use_config_times=False,
                 use_straigth_estim=True, consider_beam_interval=False):
        """Init."""
        if waveforms is None:
            waveforms = dict()
        self._opt_metric = opt_metric
        self._opt_global = opt_global
        self._opt_times = opt_times
        self._use_rampconfig_times = use_config_times
        self._use_straigth_estim = use_straigth_estim
        self._consider_beam_interval = consider_beam_interval

        # declaration of attributes (as pylint requires)
        self._wfms_strength = None
        self._waveforms = None

        self._ramp_config = ramp_config
        self._dipole = ramp_config.ps_waveform_get(self._PSNAME_DIPOLE_REF)
        self._duration = ramp_config.ps_ramp_duration
        self._nrpoints_fams = ramp_config.ps_ramp_wfm_nrpoints_fams
        self._times_fams = self._dipole.times
        self._dipstrgs_fams = self._dipole.strengths
        self._nrpoints_corrs = ramp_config.ps_ramp_wfm_nrpoints_corrs
        self._times_corrs = _np.linspace(
            0.0, self._duration, self._nrpoints_corrs)
        self._dipstrgs_corrs = _np.interp(
            self._times_corrs, self._dipole.times, self._dipole.strengths)

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
        """."""
        return self._psnames

    @property
    def waveforms(self):
        """Return a dict of psname: waveform in current values."""
        return self._wfms_current

    @waveforms.setter
    def waveforms(self, waveforms=None):
        """Set a dict of psname: waveform in current values."""
        if waveforms is None:
            waveforms = dict()
        self._wfms_current = waveforms
        if waveforms:
            self._create_waveform_objects()
            self._generate_nconf_dict()

    def read_waveforms(self):
        """Read waveform in current values from PVs."""
        if not BONormListFactory._PVs:
            self._create_pvs()

        self._waveforms = dict()
        for psname in self.psnames:
            pvobj = BONormListFactory._PVs[psname]
            pvobj.wait_for_connection(10*TIMEOUT_CONN)
            if not pvobj.connected:
                raise ConnectionError('There are disconnected PVs!')
            self._wfms_current[psname] = pvobj.get()

        self._create_waveform_objects()
        self._generate_nconf_dict()

    @property
    def normalized_configs(self):
        """Return dict of [time: normalized configuration]."""
        return _dcopy(self._norm_configs_dict)

    @property
    def desired_reconstr_precision(self):
        """Desired reconstruction precision."""
        return BONormListFactory._DESIRED_PRECISION

    @property
    def precision_reached(self):
        """Precision reached.

        Return if the reconstructed normalized configuration dict
        reached the desired  precision.
        """
        if not self._norm_configs_dict:
            return False

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
        for psname in self.psnames:
            error = _np.abs(
                self._ps2wfms[psname].currents -
                r_new.ps_waveform_get_currents(psname))
            max_error = max(max_error, max(error))
        if max_error < self.desired_reconstr_precision:
            return True, max_error
        return False, max_error

    def calc_psname_current_error(self, psname, nc_times, nc_strengths):
        """Calculate error vector in current.

        Calculate reconstruction error vector in current units for
        psname given normalized configurations times and strengths."""
        if 'Fam' in psname:
            wfm_times = self._times_fams
            dip_strgs = self._dipstrgs_fams
        else:
            wfm_times = self._times_corrs
            dip_strgs = self._dipstrgs_corrs
        wfm_strengths = _np.interp(wfm_times, nc_times, nc_strengths)
        magnet = _get_magnet(_MASearch.conv_psname_2_psmaname(psname))
        wfm_currents = magnet.conv_strength_2_current(
            strengths=wfm_strengths, strengths_dipole=dip_strgs)
        error = self._wfms_current[psname] - wfm_currents
        if self._consider_beam_interval:
            ini, end = _np.round(_np.interp(
                BONormListFactory._BEAM_INTERVAL,
                wfm_times, _np.arange(len(wfm_times))))
            error = error[int(ini):int(end)]
        return error

    def calc_psname_strength_error(self, psname, nc_times, nc_strengths):
        """Calculate error vector in strength.

        Calculate reconstruction error vector in strengths units for
        psname given normalized configurations times and strengths."""
        wfm_times = self._times_fams if 'Fam' in psname else self._times_corrs
        wfm_strengths = _np.interp(wfm_times, nc_times, nc_strengths)
        error = self._wfms_strength[psname] - wfm_strengths
        if self._consider_beam_interval:
            ini, end = _np.round(_np.interp(
                BONormListFactory._BEAM_INTERVAL,
                wfm_times, _np.arange(len(wfm_times))))
            error = error[int(ini):int(end)]
        return error

    # ----- private methods -----

    def _create_pvs(self):
        pvs = dict()
        for psname in self.psnames:
            pvs[psname] = _PV(
                psname + ':Wfm-SP', connection_timeout=TIMEOUT_CONN)
        BONormListFactory._PVs = pvs

    def _create_waveform_objects(self):
        self._ps2wfms = dict()
        self._wfms_strength = dict()
        for psname, wfm_curr in self._wfms_current.items():
            wfm_nrpoints = self._nrpoints_fams if 'Fam' in psname \
                else self._nrpoints_corrs
            self._ps2wfms[psname] = _Waveform(
                psname, self._dipole, currents=wfm_curr,
                wfm_nrpoints=wfm_nrpoints)
            self._wfms_strength[psname] = self._ps2wfms[psname].strengths

    def _calc_nconf_times(self, times, wfm, thres):
        if self._use_rampconfig_times:
            nconf_times = sorted(self._ramp_config.ps_normalized_configs_times)
            nconf_indcs = list()
            for tim in nconf_times:
                atol = self._duration/wfm.size
                idx = _np.where(_np.isclose(times, tim, atol=atol))[0]
                nconf_indcs.append(idx[-1])
            nconf_times = _np.array(nconf_times)
            nconf_indcs = _np.array(nconf_indcs)

            idd_bef = _np.r_[nconf_indcs, times.size-3]
            idd_aft = _np.r_[0, nconf_indcs]
        else:
            # calculate 1 e 2 derivatives
            diff1 = _np.diff(wfm)
            diff2 = _np.diff(diff1)

            # change threshold, if necessary
            maxi = _np.max(_np.abs(diff2))
            thres = maxi*1e-2 if maxi < thres else thres

            # identify zeros in 2 derivative and norm. configs indices
            ind = _np.where(_np.abs(diff2) < thres)[0]
            dind = _np.diff(ind)
            ind2 = _np.where(dind > 1)[0]
            idd_bef = _np.r_[ind[ind2], diff2.size-1]
            idd_aft = _np.r_[0, ind[ind2+1]]

        # calculate slopes, offsets and interceptions to interpolations
        slopes, offsets = list(), list()
        for beg, fin in zip(idd_aft, idd_bef):
            _x, _y = times[beg:fin], wfm[beg:fin]
            if not _x.size:
                continue
            off, slp = _np.polynomial.polynomial.polyfit(_x, _y, 1)
            slopes.append(slp)
            offsets.append(off)
        time_inter = -1 * _np.diff(offsets)/_np.diff(slopes)
        w_inter = slopes[:-1]*time_inter + offsets[:-1]
        if time_inter.size:
            time_inter2 = _np.round(time_inter, decimals=3)
            w_inter2 = _np.interp(time_inter2, time_inter, w_inter)
            time_inter, w_inter = time_inter2, w_inter2

        if self._use_rampconfig_times:
            if self._use_straigth_estim:
                w1_inter = slopes[1:]*nconf_times + offsets[1:]
                w2_inter = slopes[:-1]*nconf_times + offsets[:-1]
                w_inter = (w1_inter + w2_inter)/2
            else:
                w_inter = _np.interp(nconf_times, times, wfm)

            aux_t, aux_w = time_inter, w_inter
            val1 = _np.where(_np.logical_and(
                ~_np.isnan(aux_t), ~_np.isnan(aux_w)))[0]
            val2 = _np.where(_np.logical_and(
                _np.diff(-aux_t[val1]) <= 0,
                _np.diff(aux_t[val1]) >= 0))[0]
            time_inter = nconf_times[val1[val2]]
            w_inter = aux_w[val1[val2]]
            if aux_w.size and ~_np.isnan(aux_w[-1]):
                time_inter = _np.r_[time_inter, nconf_times[-1]]
                w_inter = _np.r_[w_inter, aux_w[-1]]
        return time_inter, w_inter

    def _get_initial_guess(self, threshold):
        # get time instants and normalized strengths where there are
        # normalized configurations
        problems = False
        ps2time2strg = dict()
        times = set()
        for psname, wfm in self._ps2wfms.items():
            time = wfm.times
            wfm = wfm.strengths

            time_inter, w_inter = self._calc_nconf_times(
                time, wfm, threshold)
            ps2time2strg[psname] = {
                i: w for i, w in zip(time_inter, w_inter)}
            times.update(time_inter)
            if not all(time_inter == sorted(time_inter)) or \
                    (time_inter.size == 1 and time_inter[0] == _np.nan):
                problems = True
                break
        if problems and threshold == BONormListFactory._THRESHOLD_DEFAULT:
            return False
        if problems:
            raise Exception(
                'Could not generate normalized configurations!')

        # sort and verify times
        times = sorted(times)
        if _np.any([time > self._duration for time in times]) or \
                _np.any([time < 0 for time in times]):
            raise Exception(
                'Could not generate normalized configurations!')
        if not times:
            times = {0.0, }

        # generate dict of normalized configs
        norm_configs_dict = dict()
        for time in times:
            energy = self._dipole.get_strength_from_time(time)
            nconf = dict()
            nconf['label'] = ' {:.4f}GeV'.format(energy)
            for dip in self._PSNAME_DIPOLES:
                nconf[dip] = energy
            for psname in self.psnames:
                if time in ps2time2strg[psname].keys():
                    nconf[psname] = ps2time2strg[psname][time]
                else:
                    wfm = self._ps2wfms[psname]
                    nconf[psname] = wfm.get_strength_from_time(time)
            norm_configs_dict['{:.3f}'.format(time)] = nconf
        return norm_configs_dict

    def _generate_nconf_dict(self):
        init_guess = self._get_initial_guess(
            BONormListFactory._THRESHOLD_DEFAULT)
        if not init_guess:
            init_guess = self._get_initial_guess(
                BONormListFactory._THRESHOLD_PROBLEM)

        self._norm_configs_dict = init_guess

        if self.precision_reached[0]:
            return

        self._order = list(init_guess.keys())

        if self._opt_global:
            nrows = len(self._psnames)+1 if self._opt_times else \
                len(self._psnames)
            ncols = len(self._order)

            init_params = _np.zeros((nrows, ncols))
            if self._opt_times:
                init_params[-1] = [float(t) for t in self._order]
            for row, psname in enumerate(self._psnames):
                for col, str_time in enumerate(self._order):
                    init_params[row][col] = init_guess[str_time][psname]

            final_params = least_squares(
                self._err_func_global, init_params.flatten(), method='lm').x
            final_params = _np.reshape(final_params, (nrows, ncols))

            final_times = final_params[-1] if self._opt_times else \
                [float(t) for t in self._order]

            nconfs = dict()
            for col, str_time_orig in enumerate(self._order):
                str_time = '{:.3f}'.format(final_times[col])
                nconfs[str_time] = dict()
                nconfs[str_time]['label'] = init_guess[str_time_orig]['label']
                for dip in self._PSNAME_DIPOLES:
                    energy = init_guess[str_time_orig][dip]
                    nconfs[str_time][dip] = energy
                for row, psname in enumerate(self._psnames):
                    nconfs[str_time][psname] = final_params[row][col]
        else:
            nconfs = dict()
            for psn in self._psnames:
                init_params = [init_guess[st][psn] for st in self._order]
                final_params = least_squares(
                    self._err_func_individual, init_params,
                    args=(psn,), method='lm').x
                for i, str_time in enumerate(self._order):
                    if str_time not in nconfs:
                        nconfs[str_time] = dict()
                        nconfs[str_time]['label'] = \
                            init_guess[str_time]['label']
                        for dip in self._PSNAME_DIPOLES:
                            energy = init_guess[str_time][dip]
                            nconfs[str_time][dip] = energy
                    nconfs[str_time][psn] = final_params[i]
        self._norm_configs_dict = nconfs

    def _err_func_individual(self, params, psname):
        nc_strengths = params
        nc_times = [float(t) for t in self._order]
        error = self._get_err_vector(psname, nc_times, nc_strengths)
        return error

    def _err_func_global(self, params):
        nrows = len(self._psnames)+1 if self._opt_times else \
            len(self._psnames)
        ncols = len(self._order)
        aux_params = _np.reshape(params, (nrows, ncols))
        if self._opt_times:
            aux_params = aux_params[:, _np.argsort(aux_params[-1, :])]
        nc_times = aux_params[-1] if self._opt_times else \
            [float(t) for t in self._order]

        error = list()
        for psn in self._psnames:
            nc_strengths = aux_params[self._psnames.index(psn)]
            ind_error = self._get_err_vector(psn, nc_times, nc_strengths)
            error.extend(list(ind_error))
        error = _np.array(error)
        return error

    def _get_err_vector(self, psname, nc_times, nc_strengths):
        if self._opt_metric == 'strength':
            error = self.calc_psname_strength_error(
                psname, nc_times, nc_strengths)
            loss_factor = self._get_loss_factor(psname)
            error /= loss_factor
        else:
            error = self.calc_psname_current_error(
                psname, nc_times, nc_strengths)
        return error

    def _get_loss_factor(self, psname):
        if psname.dev in ('QF', 'QD'):
            return BONormListFactory._LOSS_FACTOR_QUADS
        if psname.dev in ('SF', 'SD'):
            return BONormListFactory._LOSS_FACTOR_SEXTS
        return BONormListFactory._LOSS_FACTOR_CORRS


class BORFRampFactory:
    """Class to rebuild RF ramp parameters from machine state."""

    V_2_KV = 1e-3
    _DevName = 'BR-RF-DLLRF-01'
    _ppties = {
        'bottom_duration': _DevName+':RmpTs1-SP',
        'rampup_duration': _DevName+':RmpTs2-SP',
        'top_duration': _DevName+':RmpTs3-SP',
        'rampdown_duration': _DevName+':RmpTs4-SP',
        'bottom_voltage': 'RA-RaBO01:RF-LLRF:RmpAmpVCavBot-SP',
        'top_voltage': 'RA-RaBO01:RF-LLRF:RmpAmpVCavTop-SP',
        'bottom_phase': _DevName+':RmpPhsBot-SP',
        'top_phase': _DevName+':RmpPhsTop-SP',
    }
    _PVs = dict()

    def __init__(self):
        """."""
        self._rf_params = None
        self._create_pvs()

    @property
    def rf_params(self):
        """Return RF parameters rebuilt from PV values."""
        self._rf_params = self._generate_rf_params()
        return self._rf_params

    # ----- private methods -----

    def _create_pvs(self):
        pvs = dict()
        for param, pvname in BORFRampFactory._ppties.items():
            pvs[param] = _PV(pvname, connection_timeout=TIMEOUT_CONN)
        BORFRampFactory._PVs = pvs

    def _generate_rf_params(self):
        for pvobj in BORFRampFactory._PVs.values():
            pvobj.wait_for_connection()
            if not pvobj.connected:
                raise Exception('There are not connected PVs!')

        rf_params = dict()
        for param in BORFRampFactory._ppties:
            val = BORFRampFactory._PVs[param].value
            if 'voltage' in param:
                val = val*BORFRampFactory.V_2_KV
            rf_params[param] = val
        return rf_params


class BOTIRampFactory:
    """Class to rebuild TI ramp parameters from machine state."""

    _EVG = _LLTimeSearch.get_evg_name()
    _triggers = {
        'BO-Glob:TI-Mags-Fams', 'BO-Glob:TI-Mags-Corrs',
        'BO-Glob:TI-LLRF-Rmp',
        'LI-01:TI-EGun-SglBun', 'LI-01:TI-EGun-MultBun',
        'BO-48D:TI-EjeKckr', 'SI-01SA:TI-InjDpKckr',
    }
    _events = {
        _EVG+':Linac', _EVG+':InjBO', _EVG+':RmpBO', _EVG+':InjSI',
        _EVG+':Study',
    }
    _PVs = dict()

    def __init__(self):
        """."""
        self._ti_params = None
        BOTIRampFactory._create_pvs()

    @property
    def ti_params(self):
        """Return TI parameters rebuilt from PV values."""
        self._ti_params = self._generate_ti_params()
        return self._ti_params

    # ----- private methods -----

    @staticmethod
    def _create_pvs():
        pvs = dict()
        for trig in BOTIRampFactory._triggers:
            for ppty in {'Src-Sts', 'Delay-RB'}:
                pvname = trig + ':' + ppty
                pvs[pvname] = _PV(pvname, connection_timeout=TIMEOUT_CONN)

        for event in BOTIRampFactory._events:
            pvname = event + 'Delay-RB'
            pvs[pvname] = _PV(pvname, connection_timeout=TIMEOUT_CONN)

        egun_sb_sts_pvname = 'LI-01:EG-PulsePS:singleselstatus'
        pvs[egun_sb_sts_pvname] = _PV(
            egun_sb_sts_pvname, connection_timeout=TIMEOUT_CONN)

        BOTIRampFactory._PVs = pvs

    def _generate_ti_params(self):
        _pvs = BOTIRampFactory._PVs
        for pvobj in _pvs.values():
            pvobj.wait_for_connection()
            if not pvobj.connected:
                raise Exception('There are not connected PVs!')

        ti_params = dict()

        # injection time
        egun_src_idx = _pvs['LI-01:TI-EGun-SglBun:Src-Sts'].value
        egun_src_strs = _pvs['LI-01:TI-EGun-SglBun:Src-Sts'].enum_strs
        egun_src_val = egun_src_strs[egun_src_idx]
        egun_src_dly_pvn = \
            BOTIRampFactory._EVG+':'+egun_src_val+'Delay-RB'
        egun_src_dly = _pvs[egun_src_dly_pvn].value
        egun_dly = _pvs['LI-01:TI-EGun-SglBun:Delay-RB'].value \
            if _pvs['LI-01:EG-PulsePS:singleselstatus'].value \
            else _pvs['LI-01:TI-EGun-MultBun:Delay-RB'].value
        ti_params['injection_time'] = (egun_src_dly + egun_dly)/1e3

        # ejection time
        ejekckr_src_idx = _pvs['BO-48D:TI-EjeKckr:Src-Sts'].value
        ejekckr_src_strs = _pvs['BO-48D:TI-EjeKckr:Src-Sts'].enum_strs
        ejekckr_src_val = ejekckr_src_strs[ejekckr_src_idx]
        ejekckr_src_dly_pvn = \
            BOTIRampFactory._EVG+':'+ejekckr_src_val+'Delay-RB'
        ejekckr_src_dly = _pvs[ejekckr_src_dly_pvn].value
        ejekckr_dly = _pvs['BO-48D:TI-EjeKckr:Delay-RB'].value
        ti_params['ejection_time'] = (ejekckr_src_dly + ejekckr_dly)/1e3

        # mags delay
        ps_rmp_dly_fam = _pvs['BO-Glob:TI-Mags-Fams:Delay-RB'].value
        ti_params['ps_ramp_delay'] = (ps_rmp_dly_fam)/1e3

        # rf delay
        rf_rmp_dly = _pvs['BO-Glob:TI-LLRF-Rmp:Delay-RB'].value
        ti_params['rf_ramp_delay'] = (rf_rmp_dly)/1e3

        return ti_params
