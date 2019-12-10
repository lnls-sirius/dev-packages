"""Module with BO ramp and SI mig classes."""

import numpy as _np
from copy import deepcopy as _dcopy

from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE as _MAX_WFMSIZE
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.namesys import SiriusPVName
from siriuspy.clientconfigdb import ConfigDBDocument as _ConfigDBDocument
from siriuspy.magnet.util import \
    get_magnet_family_name as _get_magnet_family_name
from siriuspy.ramp.exceptions import RampError as _RampError, \
    RampInvalidDipoleWfmParms as _RampInvalidDipoleWfmParms, \
    RampInvalidNormConfig as _RampInvalidNormConfig, \
    RampInvalidRFParms as _RampInvalidRFParms
from siriuspy.ramp.util import MAX_RF_RAMP_DURATION as _MAX_RF_RAMP_DURATION
from siriuspy.ramp.waveform import \
    WaveformDipole as _WaveformDipole, \
    Waveform as _Waveform


class BoosterNormalized(_ConfigDBDocument):
    """Booster normalized configuration."""

    psnames = _PSSearch.get_psnames({'sec': 'BO', 'dis': 'PS'})

    def __init__(self, name=None):
        """Constructor."""
        super().__init__('bo_normalized', name=name)
        self._value = self.get_value_template()

        self._psnames2index = dict()
        for index, data in enumerate(self._value['pvs']):
            psname = SiriusPVName(data[0]).device_name
            self._psnames2index[psname] = index

    def _get_item(self, psname):
        index = self._psnames2index[psname]
        value = self._value['pvs'][index][1]
        return float(value)

    def _set_item(self, psname, value):
        index = self._psnames2index[psname]
        self._value['pvs'][index][1] = value

    def verify_syncronized(self):
        oconfig = BoosterNormalized(name=self.name)
        oconfig.load()

        modified = False
        for mag in oconfig.psnames:
            if oconfig[mag] != self[mag]:
                modified = True
                break
        self._synchronized = not modified

    def __str__(self):
        """Return string representation of configuration."""
        if not self._value:
            st = 'name: {}'.format(self.name)
            return st
        st = ''
        k = [data[0] for data in self._value['pvs']]
        v1 = [data[1] for data in self._value['pvs']]
        v2 = [data[2] for data in self._value['pvs']]
        maxlen = max(tuple(len(ky) for ky in k) + (len('name'),))
        fmtstr1 = '{:<'+str(maxlen)+'}, {:+.6f}, {:+.6f}\n'
        fmtstr2 = '{:<'+str(maxlen)+'}: {}\n'
        st = fmtstr2.format('name', self.name)
        for i in range(len(k)):
            st += fmtstr1.format(k[i], v1[i], v2[i])
        return st

    def __eq__(self, value):
        for ma in self.manames:
            if ma == 'BO-Fam:MA-B':
                continue
            if not _np.isclose(self[ma], value[ma], atol=1e-5):
                return False
        return True


class BoosterRamp(_ConfigDBDocument):
    """Booster ramp class."""

    # Dipole psname
    PSNAME_DIPOLES = ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2')
    PSNAME_DIPOLE_REF = PSNAME_DIPOLES[0]

    def __init__(self, name=None, auto_update=False):
        """Constructor."""
        super().__init__('bo_ramp', name=name)
        self._auto_update = auto_update
        self._ps_nconfigs = dict()
        self._ps_waveforms = dict()
        self.value = self.get_value_template()

    # --- ConfigSrv API ---

    @property
    def synchronized(self):
        """Return synchronization state between object and config in server."""
        if not self._synchronized:
            return False
        for config in self._ps_nconfigs.values():
            if not config.synchronized:
                return False
        return True

    def load(self):
        """Load configuration from config server."""
        # load booster ramp configuration
        super().load()
        self._synchronized = False  # in case cannot load ps norm config
        # update ps normalized configs
        self._update_ps_normalized_configs_objects()
        # load ps normalized configurations one by one
        for config in self._ps_nconfigs.values():
            config.load()
        self._synchronized = True  # all went well
        self._invalidate_ps_waveforms(True)

    def load_normalized_configs(self):
        """Load ps normalized configurations from config server."""
        # load ps normalized configurations one by one
        for config in self._ps_nconfigs.values():
            config.load()
        self._invalidate_ps_waveforms()

    def save(self, new_name=None):
        """Save configuration to config server."""
        # save each ps normalized configuration
        nconfig_sub_dict = dict()
        for config in self._ps_nconfigs.values():
            if config.exist():
                if self._check_ps_normalized_modified(config):
                    # save changes in an existing normalized config
                    old = config.name
                    new = config.generate_config_name(old)
                    config.save(new)

                    # replace old config from normalized configs dict
                    del(self._ps_nconfigs[old])
                    self._ps_nconfigs[new] = config

                    # replace old name in normalized configs list
                    nconfigs = self.ps_normalized_configs
                    for i in range(len(nconfigs)):
                        if nconfigs[i][1] == old:
                            nconfigs[i][1] = new
                    self._value['ps_normalized_configs*'] = nconfigs
                    nconfig_sub_dict[old] = new
                else:
                    config._synchronized = True
            else:
                config.save()

        # save booster ramp
        super().save(new_name)

        self._synchronized = True  # all went well

        return nconfig_sub_dict

    # ---- ps_normalized_configs ----

    @property
    def ps_normalized_configs(self):
        """List of ps normalized config."""
        return _dcopy(self._value['ps_normalized_configs*'])

    def ps_normalized_configs_set(self, value):
        """Receive a list of [time, BoosterNormalized]."""
        self._ps_nconfigs = dict()
        nconfigs = list()
        for time, nconfig in value:
            nconfigs.append([time, nconfig.name])
            self._ps_nconfigs[nconfig.name] = nconfig
        self._set_ps_normalized_configs(nconfigs)
        self._synchronized = False
        self._invalidate_ps_waveforms()

    @property
    def ps_normalized_configs_times(self):
        """Return time instants corresponding to ps normalized configs."""
        if not self._value['ps_normalized_configs*']:
            return list()
        else:
            time, _ = zip(*self._value['ps_normalized_configs*'])
            return list(time)

    @property
    def ps_normalized_configs_names(self):
        """Return names corresponding to ps normalized configs."""
        if not self._value['ps_normalized_configs*']:
            return list()
        else:
            _, name = zip(*self._value['ps_normalized_configs*'])
            return list(name)

    def ps_normalized_configs_delete(self, index):
        """Delete a ps normalized config either by its index or its name."""
        names = self.ps_normalized_configs_names
        if isinstance(index, str):
            index = names.index(index)
        times = self.ps_normalized_configs_times
        names.pop(index)
        times.pop(index)
        nconfigs = [[times[i], names[i]] for i in range(len(times))]
        self._set_ps_normalized_configs(nconfigs)
        self._synchronized = False
        self._invalidate_ps_waveforms()

    def ps_normalized_configs_insert(self, time, name=None, nconfig=None):
        """Insert a ps normalized configuration."""
        # process ps normalized config name
        if not isinstance(name, str) or len(name) == 0:
            name = self.generate_config_name()

        # add new entry to list with ps normalized configs metadata
        otimes = self.ps_normalized_configs_times
        onames = self.ps_normalized_configs_names
        times = otimes.copy()
        names = onames.copy()
        if time in times:
            if nconfig is not None:
                index = times.index(time)
                names[index] = name
            else:
                raise _RampInvalidNormConfig(
                    'There is already a configuration at this time.')
        else:
            times.append(time)
            names.append(name)
        times, names = \
            [list(x) for x in zip(*sorted(zip(times, names),
             key=lambda pair: pair[0]))]  # sort by time
        nconfigs = [[times[i], names[i]] for i in range(len(times))]

        # triggers updates for new ps normalized configs table
        self._set_ps_normalized_configs(nconfigs)

        # interpolate nconfig, if necessary
        if nconfig is None:
            if otimes:
                for ps in self._ps_nconfigs[name].psnames:
                    if ps in self.PSNAME_DIPOLES:
                        continue
                    ovalues = [self._ps_nconfigs[n][ps] for n in onames]
                    self._ps_nconfigs[name][ps] = _np.interp(
                        time, otimes, ovalues)
            else:
                self._ps_nconfigs[name].value = \
                    BoosterNormalized().get_value_template()

            self._update_ps_normalized_config_energy(
                self._ps_nconfigs[name], time)
        else:
            self._ps_nconfigs[name].value = nconfig

        return name

    def ps_normalized_configs_change_time(self, index, new_time,
                                          change_energy=False):
        """Change the time of an existing config either by index or name."""
        names = self.ps_normalized_configs_names
        if isinstance(index, str):
            name = index
            index = names.index(name)
        else:
            name = names[index]
        times = self.ps_normalized_configs_times
        if times[index] == new_time:
            return
        times[index] = new_time

        # set config energy appropriately if needed
        if change_energy:
            self._update_ps_normalized_config_energy(
                self._ps_nconfigs[name], new_time)

        nconfigs = [[times[i], names[i]] for i in range(len(times))]
        nconfigs = sorted(nconfigs, key=lambda x: x[0])
        self._set_ps_normalized_configs(nconfigs)
        self._synchronized = False
        self._invalidate_ps_waveforms()

    # ---- ps ramp parameters ----

    @property
    def ps_ramp_duration(self):
        """Power supplies ramp duration."""
        return self._value['ps_ramp']['duration']

    @ps_ramp_duration.setter
    def ps_ramp_duration(self, value):
        """Set power supplies duration."""
        value = float(value)
        if value != self._value['ps_ramp']['duration']:
            if not self.ps_ramp_rampdown_stop_time < value:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid duration for waveforms.')
            self._value['ps_ramp']['duration'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_wfm_nrpoints_fams(self):
        """Power supplies waveform number of points."""
        rdip = self._value['ps_ramp']
        return rdip['wfm_nrpoints_fams']

    @ps_ramp_wfm_nrpoints_fams.setter
    def ps_ramp_wfm_nrpoints_fams(self, value):
        """Set power supplies waveform number of points for families."""
        value = int(value)
        rdip = self._value['ps_ramp']
        if value != rdip['wfm_nrpoints_fams']:
            if not 1 <= value <= _MAX_WFMSIZE:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid number of points for waveforms.')
            rdip['wfm_nrpoints_fams'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_wfm_nrpoints_corrs(self):
        """Power supplies waveform number of points for correctors."""
        rdip = self._value['ps_ramp']
        return rdip['wfm_nrpoints_corrs']

    @ps_ramp_wfm_nrpoints_corrs.setter
    def ps_ramp_wfm_nrpoints_corrs(self, value):
        """Set power supplies waveform number of points for correctors."""
        value = int(value)
        rdip = self._value['ps_ramp']
        if value != rdip['wfm_nrpoints_corrs']:
            if not 1 <= value <= _MAX_WFMSIZE:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid number of points for waveforms.')
            rdip['wfm_nrpoints_corrs'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_times(self):
        """Return ps ramp times."""
        v = (self.ps_ramp_rampup1_start_time,
             self.ps_ramp_rampup2_start_time,
             self.ps_ramp_rampdown_start_time,
             self.ps_ramp_rampdown_stop_time)
        return v

    @property
    def ps_ramp_energies(self):
        """Return ps ramp times."""
        v = (self.ps_ramp_rampup1_start_energy,
             self.ps_ramp_rampup2_start_energy,
             self.ps_ramp_rampdown_start_energy,
             self.ps_ramp_rampdown_stop_energy)
        return v

    @property
    def ps_ramp_start_energy(self):
        """Return."""
        return self._value['ps_ramp']['start_energy']

    @ps_ramp_start_energy.setter
    def ps_ramp_start_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['start_energy']:
            w = self._create_new_ps_waveform_dipole()
            w.start_energy = value
            rdip['start_energy'] = w.start_energy
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampup1_start_energy(self):
        """Return."""
        return self._value['ps_ramp']['rampup1_start_energy']

    @ps_ramp_rampup1_start_energy.setter
    def ps_ramp_rampup1_start_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampup1_start_energy']:
            w = self._create_new_ps_waveform_dipole()
            w.rampup1_start_energy = value
            rdip['rampup1_start_energy'] = w.rampup1_start_energy
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampup1_start_time(self):
        """Return."""
        return self._value['ps_ramp']['rampup1_start_time']

    @ps_ramp_rampup1_start_time.setter
    def ps_ramp_rampup1_start_time(self, value):
        """Return."""
        self._check_valid_time(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampup1_start_time']:
            rdip['rampup1_start_energy'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampup1_slope(self):
        """Return rampup1 slope."""
        self._update_ps_waveform(self.PSNAME_DIPOLE_REF)
        return self._ps_waveforms[self.PSNAME_DIPOLE_REF].rampup1_slope

    @property
    def ps_ramp_rampup2_start_energy(self):
        """Return."""
        return self._value['ps_ramp']['rampup2_start_energy']

    @ps_ramp_rampup2_start_energy.setter
    def ps_ramp_rampup2_start_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampup2_start_energy']:
            w = self._create_new_ps_waveform_dipole()
            w.rampup2_start_energy = value
            rdip['rampup2_start_energy'] = w.rampup2_start_energy
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampup2_start_time(self):
        """Return."""
        return self._value['ps_ramp']['rampup2_start_time']

    @ps_ramp_rampup2_start_time.setter
    def ps_ramp_rampup2_start_time(self, value):
        """Return."""
        self._check_valid_time(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampup2_start_time']:
            rdip['rampup2_start_time'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampup2_slope(self):
        """Return rampup2 slope."""
        self._update_ps_waveform(self.PSNAME_DIPOLE_REF)
        return self._ps_waveforms[self.PSNAME_DIPOLE_REF].rampup2_slope

    @property
    def ps_ramp_rampup_smooth_energy(self):
        """Return."""
        return self._value['ps_ramp']['rampup_smooth_energy']

    @ps_ramp_rampup_smooth_energy.setter
    def ps_ramp_rampup_smooth_energy(self, value):
        """Return."""
        rdip = self._value['ps_ramp']
        if value != rdip['rampup_smooth_energy']:
            rdip['rampup_smooth_energy'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampup_smooth_intvl(self):
        """Return."""
        return self._value['ps_ramp']['rampup_smooth_intvl']

    @ps_ramp_rampup_smooth_intvl.setter
    def ps_ramp_rampup_smooth_intvl(self, value):
        """Return."""
        rdip = self._value['ps_ramp']
        if value != rdip['rampup_smooth_intvl']:
            rdip['rampup_smooth_intvl'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampdown_start_energy(self):
        """Return."""
        return self._value['ps_ramp']['rampdown_start_energy']

    @ps_ramp_rampdown_start_energy.setter
    def ps_ramp_rampdown_start_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampdown_start_energy']:
            w = self._create_new_ps_waveform_dipole()
            w.rampdown_start_energy = value
            rdip['rampdown_start_energy'] = w.rampdown_start_energy
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampdown_start_time(self):
        """Return."""
        return self._value['ps_ramp']['rampdown_start_time']

    @ps_ramp_rampdown_start_time.setter
    def ps_ramp_rampdown_start_time(self, value):
        """Return."""
        self._check_valid_time(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampdown_start_time']:
            rdip['rampdown_start_time'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampdown_stop_energy(self):
        """Return."""
        return self._value['ps_ramp']['rampdown_stop_energy']

    @ps_ramp_rampdown_stop_energy.setter
    def ps_ramp_rampdown_stop_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampdown_stop_energy']:
            w = self._create_new_ps_waveform_dipole()
            w.rampdown_stop_energy = value
            rdip['rampdown_stop_energy'] = w.rampdown_stop_energy
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampdown_stop_time(self):
        """Return."""
        return self._value['ps_ramp']['rampdown_stop_time']

    @ps_ramp_rampdown_stop_time.setter
    def ps_ramp_rampdown_stop_time(self, value):
        """Return."""
        self._check_valid_time(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampdown_stop_time']:
            rdip['rampdown_stop_time'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampdown_slope(self):
        """Return rampup2 slope."""
        self._update_ps_waveform(self.PSNAME_DIPOLE_REF)
        return self._ps_waveforms[self.PSNAME_DIPOLE_REF].rampdown_slope

    @property
    def ps_ramp_rampdown_smooth_energy(self):
        """Return."""
        return self._value['ps_ramp']['rampdown_smooth_energy']

    @ps_ramp_rampdown_smooth_energy.setter
    def ps_ramp_rampdown_smooth_energy(self, value):
        """Return."""
        rdip = self._value['ps_ramp']
        if value != rdip['rampdown_smooth_energy']:
            rdip['rampdown_smooth_energy'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampdown_smooth_intvl(self):
        """Return."""
        return self._value['ps_ramp']['rampdown_smooth_intvl']

    @ps_ramp_rampdown_smooth_intvl.setter
    def ps_ramp_rampdown_smooth_intvl(self, value):
        """Return."""
        rdip = self._value['ps_ramp']
        if value != rdip['rampdown_smooth_intvl']:
            rdip['rampdown_smooth_intvl'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    # ---- rf ramp parameters ----

    @property
    def rf_ramp_duration(self):
        """RF ramp duration."""
        d = self.rf_ramp_bottom_duration + \
            self.rf_ramp_rampup_duration + \
            self.rf_ramp_top_duration + \
            self.rf_ramp_rampdown_duration
        return d

    @property
    def rf_ramp_times(self):
        """Time instants to define RF ramp."""
        t = (self.ti_params_rf_ramp_delay,      # = RF ramp start, bottom start
             self.rf_ramp_rampup_start_time,    # = RF bottom stop
             self.rf_ramp_rampup_stop_time,     # = RF top start
             self.rf_ramp_rampdown_start_time,  # = RF top stop
             self.rf_ramp_duration)             # = RF rampdown stop
        return t

    @property
    def rf_ramp_voltages(self):
        """List of voltages to define RF ramp."""
        v = (self.rf_ramp_bottom_voltage,
             self.rf_ramp_bottom_voltage,
             self.rf_ramp_top_voltage,
             self.rf_ramp_top_voltage,
             self.rf_ramp_bottom_voltage)
        return v

    @property
    def rf_ramp_phases(self):
        """List of phases to define RF ramp."""
        p = (self.rf_ramp_bottom_phase,
             self.rf_ramp_bottom_phase,
             self.rf_ramp_top_phase,
             self.rf_ramp_top_phase,
             self.rf_ramp_bottom_phase)
        return p

    def rf_ramp_interp_voltages(self, time):
        """Return voltages related to times."""
        v = _np.interp(time, self.rf_ramp_times, self.rf_ramp_voltages)
        return v

    @property
    def rf_ramp_rampup_start_time(self):
        """RF ramp rampup start time."""
        t = self.ti_params_rf_ramp_delay + \
            float(self._value['rf_ramp']['bottom_duration'])
        return t

    @rf_ramp_rampup_start_time.setter
    def rf_ramp_rampup_start_time(self, value):
        value = float(value)
        if value == self.rf_ramp_rampup_start_time:
            return
        if not self.ti_params_rf_ramp_delay <= value < \
                self.rf_ramp_rampup_stop_time:
            raise _RampInvalidRFParms('Invalid rampup start time.')

        delay = self.ti_params_rf_ramp_delay
        rampup_stop_time = self.rf_ramp_rampup_stop_time
        self._value['rf_ramp']['bottom_duration'] = \
            value - delay
        self._value['rf_ramp']['rampup_duration'] = \
            rampup_stop_time - value
        self._synchronized = False

    @property
    def rf_ramp_rampup_stop_time(self):
        """RF ramp rampup stop time."""
        t = self.ti_params_rf_ramp_delay + \
            float(self._value['rf_ramp']['bottom_duration']) + \
            float(self._value['rf_ramp']['rampup_duration'])
        return t

    @rf_ramp_rampup_stop_time.setter
    def rf_ramp_rampup_stop_time(self, value):
        value = float(value)
        if value == self.rf_ramp_rampup_stop_time:
            return
        if not self.rf_ramp_rampup_start_time < value <= \
                self.rf_ramp_rampdown_start_time:
            raise _RampInvalidRFParms('Invalid rampup stop time.')

        rampup_start_time = self.rf_ramp_rampup_start_time
        rampdown_start_time = self.rf_ramp_rampdown_start_time
        self._value['rf_ramp']['rampup_duration'] = \
            value - rampup_start_time
        self._value['rf_ramp']['top_duration'] = \
            rampdown_start_time - value
        self._synchronized = False

    @property
    def rf_ramp_rampdown_start_time(self):
        """RF ramp rampdown start time."""
        t = self.ti_params_rf_ramp_delay + \
            float(self._value['rf_ramp']['bottom_duration']) + \
            float(self._value['rf_ramp']['rampup_duration']) + \
            float(self._value['rf_ramp']['top_duration'])
        return t

    @rf_ramp_rampdown_start_time.setter
    def rf_ramp_rampdown_start_time(self, value):
        value = float(value)
        if value == self.rf_ramp_rampdown_start_time:
            return
        if not self.rf_ramp_rampup_stop_time <= value < \
                self.rf_ramp_rampdown_stop_time:
            raise _RampInvalidRFParms('Invalid rampdown start time.')

        rampup_stop_time = self.rf_ramp_rampup_stop_time
        rampdown_stop_time = self.rf_ramp_rampdown_stop_time
        self._value['rf_ramp']['top_duration'] = \
            value - rampup_stop_time
        self._value['rf_ramp']['rampdown_duration'] = \
            rampdown_stop_time - value
        self._synchronized = False

    @property
    def rf_ramp_rampdown_stop_time(self):
        """RF ramp rampdown start time."""
        t = self.ti_params_rf_ramp_delay + \
            float(self._value['rf_ramp']['bottom_duration']) + \
            float(self._value['rf_ramp']['rampup_duration']) + \
            float(self._value['rf_ramp']['top_duration']) + \
            float(self._value['rf_ramp']['rampdown_duration'])
        return t

    @rf_ramp_rampdown_stop_time.setter
    def rf_ramp_rampdown_stop_time(self, value):
        value = float(value)
        if value == self.rf_ramp_rampdown_stop_time:
            return
        if not self.rf_ramp_rampdown_start_time < value <= \
                self.ti_params_rf_ramp_delay + _MAX_RF_RAMP_DURATION:
            raise _RampInvalidRFParms('Invalid rampdown stop time.')

        rampdown_start_time = self.rf_ramp_rampdown_start_time
        self._value['rf_ramp']['rampdown_duration'] = \
            value - rampdown_start_time
        self._synchronized = False

    @property
    def rf_ramp_bottom_duration(self):
        """Bottom duration, in ms."""
        return self._value['rf_ramp']['bottom_duration']

    @property
    def rf_ramp_rampup_duration(self):
        """Rampup duration, in ms."""
        return self._value['rf_ramp']['rampup_duration']

    @property
    def rf_ramp_top_duration(self):
        """Top duration, in ms."""
        return self._value['rf_ramp']['top_duration']

    @property
    def rf_ramp_rampdown_duration(self):
        """Rampdown duration, in ms."""
        return self._value['rf_ramp']['rampdown_duration']

    @property
    def rf_ramp_bottom_voltage(self):
        """RF ramp bottom voltage, in kV."""
        return self._value['rf_ramp']['bottom_voltage']

    @rf_ramp_bottom_voltage.setter
    def rf_ramp_bottom_voltage(self, value):
        value = float(value)
        if value == self._value['rf_ramp']['bottom_voltage']:
            return
        if not 0 <= value <= self.rf_ramp_top_voltage:
            raise _RampInvalidRFParms('Invalid value to bottom voltage.')

        self._value['rf_ramp']['bottom_voltage'] = value
        self._synchronized = False

    @property
    def rf_ramp_top_voltage(self):
        """RF ramp top voltage, in kV."""
        return self._value['rf_ramp']['top_voltage']

    @rf_ramp_top_voltage.setter
    def rf_ramp_top_voltage(self, value):
        value = float(value)
        if value == self._value['rf_ramp']['top_voltage']:
            return
        if not value >= self._value['rf_ramp']['bottom_voltage']:
            raise _RampInvalidRFParms('Invalid value to top voltage.')

        self._value['rf_ramp']['top_voltage'] = value
        self._synchronized = False

    @property
    def rf_ramp_bottom_phase(self):
        """RF ramp bottom phase, in degrees."""
        return self._value['rf_ramp']['bottom_phase']

    @rf_ramp_bottom_phase.setter
    def rf_ramp_bottom_phase(self, value):
        value = float(value)
        if value == self._value['rf_ramp']['bottom_phase']:
            return
        if not -180 < value < 360:
            raise _RampInvalidRFParms('Invalid value to bottom phase.')

        self._value['rf_ramp']['bottom_phase'] = value
        self._synchronized = False

    @property
    def rf_ramp_top_phase(self):
        """RF ramp top phase, in degrees."""
        return self._value['rf_ramp']['top_phase']

    @rf_ramp_top_phase.setter
    def rf_ramp_top_phase(self, value):
        value = float(value)
        if value == self._value['rf_ramp']['top_phase']:
            return
        if not -180 < value < 360:
            raise _RampInvalidRFParms('Invalid value to top phase.')

        self._value['rf_ramp']['top_phase'] = value
        self._synchronized = False

    # --- timing parameters ---

    @property
    def ti_params_injection_time(self):
        """Injection time instant."""
        return float(self._value['ti_params']['injection_time'])

    @ti_params_injection_time.setter
    def ti_params_injection_time(self, value):
        """Set injection time instant."""
        # TODO: verify value
        if value == self._value['ti_params']['injection_time']:
            return
        self._value['ti_params']['injection_time'] = value
        self._synchronized = False

    @property
    def ti_params_ejection_time(self):
        """Ejection time instant."""
        return float(self._value['ti_params']['ejection_time'])

    @ti_params_ejection_time.setter
    def ti_params_ejection_time(self, value):
        """Set ejection time instant."""
        # TODO: verify value
        if value == self._value['ti_params']['ejection_time']:
            return
        self._value['ti_params']['ejection_time'] = value
        self._synchronized = False

    @property
    def ti_params_ps_ramp_delay(self):
        """PS ramp delay."""
        return float(self._value['ti_params']['ps_ramp_delay'])

    @ti_params_ps_ramp_delay.setter
    def ti_params_ps_ramp_delay(self, value):
        """Set ps ramp delay [us]."""
        value = float(value)
        if value == self._value['ti_params']['ps_ramp_delay']:
            return
        self._value['ti_params']['ps_ramp_delay'] = value
        self._synchronized = False

    @property
    def ti_params_rf_ramp_delay(self):
        """RF delay."""
        return float(self._value['ti_params']['rf_ramp_delay'])

    @ti_params_rf_ramp_delay.setter
    def ti_params_rf_ramp_delay(self, value):
        """Set RF ramp delay [us]."""
        # TODO: verify value
        if value == self._value['ti_params']['rf_ramp_delay']:
            return
        self._value['ti_params']['rf_ramp_delay'] = value
        self._synchronized = False

    # --- API for waveforms ---

    @property
    def ps_waveform_psnames_exclimits(self):
        """Return a list of psnames whose waveform exceeds current limits."""
        if not self._value['ps_normalized_configs*']:
            psnames = list(self.PSNAME_DIPOLES)
        else:
            psnames = BoosterNormalized.psnames
        psnames_exclimits = list()
        for psname in psnames:
            self._update_ps_waveform(psname)
            w_currents = self._ps_waveforms[psname].currents
            isNan = _np.any(_np.isnan(w_currents))
            isInf = _np.any(_np.isinf(w_currents))
            if isNan or isInf:
                continue
            limits = _PSSearch.conv_psname_2_splims(psname)
            highlim = limits['HOPR'] if psname not in self.PSNAME_DIPOLES \
                else 1072
            lowlim = limits['LOPR']
            if _np.any(w_currents > highlim) or _np.any(w_currents < lowlim):
                psnames_exclimits.append(psname)
        return psnames_exclimits

    def ps_waveform_get(self, psname):
        """Return ps waveform for a given power supply."""
        if psname not in self.PSNAME_DIPOLES and \
                not self._value['ps_normalized_configs*']:
            raise _RampError('There is no normalized cofiguration defined!')
        self._update_ps_waveform(psname)
        waveform = self._ps_waveforms[psname]
        return waveform

    def ps_waveform_set(self, psname, waveform):
        """Set ps waveform for a given power supply."""
        self._ps_waveforms[psname] = _dcopy(waveform)

    def ps_waveform_get_times(self, psname):
        """Return ramp energy at a given time."""
        self._update_ps_waveform(psname)
        times = self._ps_waveforms[psname].times
        return times

    def ps_waveform_get_currents(self, psname):
        """Return ps waveform current for a given power supply."""
        if not self._value['ps_normalized_configs*'] and \
                psname not in self.PSNAME_DIPOLES:
            raise _RampError('There is no normalized cofiguration defined!')
        self._update_ps_waveform(psname)
        waveform = self._ps_waveforms[psname]
        return waveform.currents.copy()

    def ps_waveform_get_strengths(self, psname):
        """Return ps waveform strength for a given power supply."""
        if not self._value['ps_normalized_configs*'] and \
                psname not in self.PSNAME_DIPOLES:
            raise _RampError('There is no normalized cofiguration defined!')
        self._update_ps_waveform(psname)
        waveform = self._ps_waveforms[psname]
        return waveform.strengths.copy()

    def ps_waveform_interp_time(self, energy):
        """Return ps ramp time at a given energy.
        Use only energies until rampdown-start time.
        """
        rampdown_start_time = self.ps_ramp_rampdown_start_time
        times = [t for t in self.ps_waveform_get_times(self.PSNAME_DIPOLE_REF)
                 if t < rampdown_start_time]
        energies = self._ps_waveforms[self.PSNAME_DIPOLE_REF].strengths[
                 0:len(times)]
        time = _np.interp(energy, energies, times)
        return time

    def ps_waveform_interp_strengths(self, psname, time):
        """Return ps ramp strength at a given time."""
        if not self._value['ps_normalized_configs*'] and \
                psname not in self.PSNAME_DIPOLES:
            raise _RampError('There is no normalized cofiguration defined!')
        self._update_ps_waveform(psname)
        times = self.ps_waveform_get_times(psname)
        strengths = self._ps_waveforms[psname].strengths
        strength = _np.interp(time, times, strengths)
        return strength

    def ps_waveform_interp_currents(self, psname, time):
        """Return ps ramp current at a given time."""
        if not self._value['ps_normalized_configs*'] and \
                psname not in self.PSNAME_DIPOLES:
            raise _RampError('There is no normalized cofiguration defined!')
        self._update_ps_waveform(psname)
        times = self.ps_waveform_get_times(psname)
        currents = self._ps_waveforms[psname].currents
        current = _np.interp(time, times, currents)
        return current

    def ps_waveform_interp_energy(self, time):
        """Return ps ramp energy at a given time."""
        return self.ps_waveform_interp_strengths(self.PSNAME_DIPOLE_REF, time)

    # --- private methods ---

    def __len__(self):
        """Return number of ps normalized configurations."""
        return len(self._ps_nconfigs)

    def __str__(self):
        """Return string representation of configuration."""
        if not self._value:
            st = 'name: {}'.format(self.name)
            return st
        labels = (
            'ti_params_rf_ramp_delay [us]',
            'ti_params_ps_ramp_delay [us]',
            'ti_params_injection_time [ms]',
            'ti_params_ejection_time [ms]',
            'ps_ramp_duration [ms]',
            'ps_ramp_time_energy [ms] [GeV]',
            'ps_ramp_slopes [GeV/s]',
            'ps_normalized_configs [ms] [name]',
        )
        st = ''
        maxlen = max(tuple(len(l) for l in labels) + (len('name'),))
        strfmt1 = '{:<' + str(maxlen) + 's}: {}\n'
        strfmt2 = strfmt1.replace('{}', '{:07.3f} {:+08.3f} {:<s}')
        strfmt3 = strfmt1.replace('{}', '{:07.3f} {}')
        strfmt4 = strfmt1.replace('{}', '{:07.3f}')
        st += strfmt1.format('name', self.name)
        st += strfmt1.format(labels[0], self.ti_params_rf_ramp_delay)
        st += strfmt1.format(labels[1], self.ti_params_ps_ramp_delay)
        st += strfmt4.format(labels[2], self.ti_params_injection_time)
        st += strfmt4.format(labels[3], self.ti_params_ejection_time)
        st += strfmt1.format(labels[4], self.ps_ramp_duration)
        st += strfmt1.format(labels[5], '')
        st += strfmt2.format('', 0.0,
                             self.ps_ramp_start_energy, '(start)')
        st += strfmt2.format('', self.ps_ramp_rampup1_start_time,
                             self.ps_ramp_rampup1_start_energy,
                             '(rampup1_start)')
        st += strfmt2.format('', self.ps_ramp_rampup2_start_time,
                             self.ps_ramp_rampup2_start_energy,
                             '(rampup2_start)')
        st += strfmt2.format('', self.ps_ramp_rampdown_start_time,
                             self.ps_ramp_rampdown_start_energy,
                             '(rampdown_start)')
        st += strfmt2.format('', self.ps_ramp_rampdown_stop_time,
                             self.ps_ramp_rampdown_stop_energy,
                             '(rampdown_stop)')
        st += strfmt2.format('', self.ps_ramp_duration,
                             self.ps_ramp_start_energy, '(stop)')
        st += strfmt1.format(labels[6], '')
        st += strfmt3.format('', self.ps_ramp_rampup1_slope,
                             '(rampup1)')
        st += strfmt3.format('', self.ps_ramp_rampup2_slope,
                             '(rampup2)')
        st += strfmt3.format('', self.ps_ramp_rampdown_slope,
                             '(rampdown)')
        st += strfmt1.format(labels[7], '')
        time = self.ps_normalized_configs_times
        name = self.ps_normalized_configs_names
        for i in range(len(time)):
            st += strfmt3.format('', time[i], name[i])
        return st

    def __setitem__(self, index, value):
        """Set configuration item."""
        self._set_item(index, value)

    def _get_item(self, name):
        return _dcopy(self._ps_nconfigs[name])

    def _set_item(self, name, value):
        if name in self._ps_nconfigs.keys() and \
                not self._check_ps_normalized_modified(value):
            return
        self._ps_nconfigs[name] = value
        self._synchronized = False
        self._invalidate_ps_waveforms()

    def _set_value(self, value):
        super()._set_value(value)
        self._update_ps_normalized_configs_objects()

    def _set_ps_normalized_configs(self, value):
        """Set ps normalized config list."""
        self._value['ps_normalized_configs*'] = _dcopy(value)
        self._update_ps_normalized_configs_objects()

    def _update_ps_normalized_configs_objects(self):
        norm_configs = dict()
        for _, name in self._value['ps_normalized_configs*']:
            if name in self._ps_nconfigs:
                norm_configs[name] = self._ps_nconfigs[name]
            else:
                norm_configs[name] = BoosterNormalized(name)
        self._synchronized = False
        self._invalidate_ps_waveforms()
        self._ps_nconfigs = norm_configs

    def _update_ps_normalized_config_energy(self, nconfig_obj, time):
        indices = self._conv_times_2_indices(self.PSNAME_DIPOLE_REF, [time])
        strengths = self.ps_waveform_get_strengths(self.PSNAME_DIPOLE_REF)
        strength = _np.interp(
            indices[0],
            list(range(self._get_appropriate_wfmnrpoints(
                self.PSNAME_DIPOLE_REF))),
            strengths)
        for psname in self.PSNAME_DIPOLES:
            nconfig_obj[psname] = strength
        return nconfig_obj

    def _update_ps_waveform(self, psname):

        # update dipole if necessary
        if self.PSNAME_DIPOLE_REF not in self._ps_waveforms:
            self._update_ps_waveform_dipole()

        # update family if necessary
        family = _get_magnet_family_name(psname)
        if family is not None and family not in self._ps_waveforms:
            self._update_ps_waveform(family)

        # update magnet waveform if it is not a dipole
        if psname not in self._ps_waveforms:
            self._update_ps_waveform_not_dipole(
                psname, self.PSNAME_DIPOLE_REF, family)

    def _update_ps_waveform_not_dipole(self, psname, dipole, family=None):
        # sort ps normalized configs
        nconf_times = self.ps_normalized_configs_times
        nconf_names = self.ps_normalized_configs_names
        nconf_times, nconf_names = \
            [list(x) for x in zip(*sorted(zip(nconf_times, nconf_names),
             key=lambda pair: pair[0]))]  # sort by time

        # build strength
        nconf_strength = []
        for i in range(len(nconf_times)):
            nconfig = self._ps_nconfigs[nconf_names[i]]
            if psname not in nconfig.psnames:
                raise _RampInvalidNormConfig()
            nconf_strength.append(nconfig[psname])

        # interpolate strengths
        wfm_nrpoints = self._get_appropriate_wfmnrpoints(psname)
        nconf_indices = self._conv_times_2_indices(psname, nconf_times)
        wfm_indices = [i for i in range(wfm_nrpoints)]
        wfm_strengths = _np.interp(wfm_indices, nconf_indices, nconf_strength)

        # create waveform object with given strengths
        dipole = self._ps_waveforms[dipole]
        if family is not None:
            family = self._ps_waveforms[family]
        self._ps_waveforms[psname] = _Waveform(
            psname=psname, dipole=dipole, family=family,
            strengths=wfm_strengths,
            wfm_nrpoints=self._get_appropriate_wfmnrpoints(psname))

    def _update_ps_waveform_dipole(self):
        for psname in self.PSNAME_DIPOLES:
            w = self._create_new_ps_waveform_dipole(psname)
            self._ps_waveforms[psname] = w

    def _create_new_ps_waveform_dipole(self, dipole=''):
        if not dipole:
            dipole = self.PSNAME_DIPOLE_REF
        rdip = self._value['ps_ramp']
        dipole = _WaveformDipole(
            psname=dipole,
            wfm_nrpoints=self._get_appropriate_wfmnrpoints(dipole),
            duration=rdip['duration'],
            start_energy=rdip['start_energy'],
            rampup1_start_time=rdip['rampup1_start_time'],
            rampup1_start_energy=rdip['rampup1_start_energy'],
            rampup2_start_time=rdip['rampup2_start_time'],
            rampup2_start_energy=rdip['rampup2_start_energy'],
            rampup_smooth_intvl=rdip['rampup_smooth_intvl'],
            rampup_smooth_energy=rdip['rampup_smooth_energy'],
            rampdown_start_time=rdip['rampdown_start_time'],
            rampdown_start_energy=rdip['rampdown_start_energy'],
            rampdown_stop_time=rdip['rampdown_stop_time'],
            rampdown_stop_energy=rdip['rampdown_stop_energy'],
            rampdown_smooth_intvl=rdip['rampdown_smooth_intvl'],
            rampdown_smooth_energy=rdip['rampdown_smooth_energy'])
        return dipole

    def _conv_times_2_indices(self, psname, times):
        rdip = self._value['ps_ramp']
        duration = rdip['duration']
        wfm_nrpoints = self._get_appropriate_wfmnrpoints(psname)
        interval = duration / (wfm_nrpoints - 1.0)
        indices = [t/interval for t in times]
        return indices

    def _invalidate_ps_waveforms(self, include_dipole=False):
        psnames = tuple(self._ps_waveforms.keys())
        for psname in psnames:
            if psname not in self.PSNAME_DIPOLES or include_dipole:
                del(self._ps_waveforms[psname])

    def _check_ps_normalized_modified(self, nconfig):
        # load original nconfig from server
        oconfig = BoosterNormalized(name=nconfig.name)
        oconfig.load()

        # compare values. If identical, return False
        for mag in oconfig.psnames:
            if oconfig[mag] != nconfig[mag]:
                return True
        return False

    def _check_valid_time(self, time):
        """Check if time is in valid interval."""
        d = self.ps_ramp_duration
        if 0 < time < d:
            return True
        else:
            raise _RampError(
                'Time value must be between 0 and {}!'.format(d))

    def _get_appropriate_wfmnrpoints(self, psname):
        """Return appropriate number of points for psname."""
        if _PSSearch.conv_psname_2_psmodel(psname) == 'FBP':
            return self.ps_ramp_wfm_nrpoints_corrs
        else:
            return self.ps_ramp_wfm_nrpoints_fams


class SiriusMig(BoosterRamp):
    """Sirius migration class."""

    PSNAME_DIPOLES = ('SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2')
