"""."""

from copy import deepcopy as _dcopy
import numpy as _np
from epics import PV as _PV

from ..search import PSSearch as _PSSearch, LLTimeSearch as _LLTimeSearch
from .ramp import BoosterRamp as _BORamp
from .waveform import Waveform as _Waveform


TIMEOUT_CONN = 0.05


class BONormListFactory:
    """Class to rebuild Norm. Config. List from machine state."""

    _PSNAME_DIPOLES = ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2')
    _PSNAME_DIPOLE_REF = _PSNAME_DIPOLES[0]
    _PVs = dict()

    def __init__(self, ramp_config, waveforms=None):
        """Init."""
        if waveforms is None:
            waveforms = dict()

        # declaration of attributes (as pylint requires)
        self._wfms_current = None
        self._waveforms = None

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

    # ----- private methods -----

    def _create_pvs(self):
        pvs = dict()
        for psname in self.psnames:
            pvs[psname] = _PV(
                psname + ':Wfm-SP', connection_timeout=TIMEOUT_CONN)
        BONormListFactory._PVs = pvs

    def _create_waveform_objects(self):
        self._ps2wfms = dict()
        for psname, wfm_curr in self._wfms_current.items():
            self._ps2wfms[psname] = _Waveform(
                psname, self._dipole, currents=wfm_curr,
                wfm_nrpoints=self._get_appropriate_wfmnrpoints(psname))

    def _get_appropriate_wfmnrpoints(self, psname):
        """Return appropriate number of points for psname."""
        if _PSSearch.conv_psname_2_psmodel(psname) == 'FBP':
            return self._nrpoints_corrs
        return self._nrpoints_fams

    def _calc_nconf_times(self, times, wfm):
        diff1 = _np.diff(wfm)
        diff2 = _np.diff(diff1)
        ind = _np.where(_np.abs(diff2) < 1e-10)[0]
        dind = _np.diff(ind)
        ind2 = _np.where(dind > 1)[0]

        idd2 = _np.ones(ind2.size+1, dtype=int)*(len(diff2)-1)
        idd2[:ind2.size] = ind[ind2]
        idd1 = idd2 + 1
        idw = idd1 + 1

        diffa = diff1[idd1]
        diffb = wfm[idw] - diffa*idw
        ind_inter = -_np.diff(diffb)/_np.diff(diffa)
        w_inter = diffa[:-1]*ind_inter + diffb[:-1]

        ind_orig = _np.arange(0, len(wfm))
        time_inter = _np.interp(ind_inter, ind_orig, times)
        if time_inter.size:
            time_inter2 = _np.round(time_inter, decimals=3)
            w_inter2 = _np.interp(time_inter2, time_inter, w_inter)
            return time_inter2, w_inter2
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
        for psname in self.psnames:
            error = self._ps2wfms[psname].currents - \
                r_new.ps_waveform_get_currents(psname)
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
            for psname, wfm in self._ps2wfms.items():
                nrpts_orig = wfm.wfm_nrpoints
                ind_orig = _np.arange(0, nrpts_orig)
                t_orig = wfm.times
                w_orig = wfm.strengths

                nrpts = nrpts_orig*oversampling_factor
                ind = _np.linspace(0, ind_orig[-1], nrpts)
                time = _np.interp(ind, ind_orig, t_orig)
                wfm = _np.interp(ind, ind_orig, w_orig)

                time_inter, w_inter = self._calc_nconf_times(time, wfm)
                ps2time2strg[psname] = {i: w for i, w in zip(time_inter, w_inter)}
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
            if _np.any([time > self._duration for time in times]) or \
                    _np.any([time < 0 for time in times]):
                raise Exception(
                    'Could not generate normalized configurations!')
            if not times:
                times = {0.0, }

            # generate dict of normalized configs
            self._norm_configs_dict = dict()
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
                self._norm_configs_dict['{:.3f}'.format(time)] = nconf

            # TODO: verify case of precision not reached
            break


class BORFRampFactory:
    """Class to rebuild RF ramp parameters from machine state."""

    _DevName = 'BR-RF-DLLRF-01'
    _ppties = {
        'bottom_duration': _DevName+':RmpTs1-RB',
        'rampup_duration': _DevName+':RmpTs2-RB',
        'top_duration': _DevName+':RmpTs3-RB',
        'rampdown_duration': _DevName+':RmpTs4-RB',
        'bottom_voltage': _DevName+':RmpVoltBot-RB',
        'top_voltage': _DevName+':RmpVoltTop-RB',
        'bottom_phase': _DevName+':RmpPhsBot-RB',
        'top_phase': _DevName+':RmpPhsTop-RB',
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
            rf_params[param] = BORFRampFactory._PVs[param].value
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
        _EVG+':DigLI', _EVG+':DigTB', _EVG+':DigBO', _EVG+':DigTS',
        _EVG+':DigSI', _EVG+':Study',
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

        for ev in BOTIRampFactory._events:
            pvname = ev + 'Delay-RB'
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
