"""ID feedforward App."""

import os as _os
import logging as _log
import time as _time

import epics as _epics
import numpy as _np

from ..util import update_bit as _updt_bit
from ..callbacks import Callback as _Callback
from ..clientconfigdb import ConfigDBException as _ConfigDBException
from ..devices import IDFF as _IDFF

from .csdev import IDFFConst as _Const, ETypes as _ETypes


class App(_Callback):
    """Main application for handling IDFF."""

    DEF_PS_TIMEOUT = 5  # [s]

    def __init__(self, idname):
        """Class constructor."""
        super().__init__()
        self._const = _Const(idname)
        self._pvs_prefix = self._const.idffname
        self._pvs_database = self._const.get_propty_database()

        self._loop_state = _Const.DEFAULT_LOOP_STATE
        self._loop_freq = _Const.DEFAULT_LOOP_FREQ
        self._control_qs = _Const.DEFAULT_CONTROL_QS
        self._polarization = 'none'
        self._config_name = ''
        self.read_autosave_file()

        # IDFF object with IDFF config
        self._idff = _IDFF(idname)

        # load idff in configdb
        self._load_config(self._config_name)

        # pvs to write methods
        self.map_pv2write = {
            'LoopState-Sel': self.set_loop_state,
            'LoopFreq-SP': self.set_loop_freq,
            'ControlQS-Sel': self.set_control_qs,
            'ConfigName-SP': self.set_config_name,
            'CorrConfig-Cmd': self.cmd_corrconfig,
        }

        self._quit = False
        self._corr_setpoints = None
        self._thread_ff = _epics.ca.CAThread(
            target=self.main_idff_loop, daemon=True)
        self._thread_ff.start()

    def init_database(self):
        """Set initial PV values."""
        pvn2vals = {
            'LoopState-Sel': self._loop_state,
            'LoopState-Sts': self._loop_state,
            'LoopFreq-SP': self._loop_freq,
            'LoopFreq-RB': self._loop_freq,
            'ConfigName-SP': self._config_name,
            'ConfigName-RB': self._config_name,
            'Polarization-Mon': self._polarization,
            'CorrConfig-Cmd': 0,
            'CorrStatus-Mon': _Const.DEFAULT_CORR_STATUS,
        }
        if self._const.has_qscorrs:
            pvn2vals.update({
                'ControlQS-Sel': self._control_qs,
                'ControlQS-Sts': self._control_qs,
                })
        for pvn, val in pvn2vals.items():
            self.run_callbacks(pvn, val)
        self._update_log('Started.')

    @property
    def pvs_prefix(self):
        """Return pvs_prefix."""
        return self._pvs_prefix

    @property
    def pvs_database(self):
        """Return pvs_database."""
        return self._pvs_database

    def process(self, interval):
        """Sleep."""
        # check correctors state periodically
        _t0 = _time.time()
        self._update_corr_status()
        self._update_corr_setpoints()
        dtime = _time.time() - _t0
        sleep_time = interval - dtime
        # sleep
        if sleep_time > 0:
            _time.sleep(sleep_time)
        else:
            _log.debug('process took {0:f}ms.'.format((dtime)*1000))

    def read(self, reason):
        """Read from IOC database."""
        value = None
        return value

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        _log.info('Write received for: %s --> %s', reason, str(value))
        if reason in self.map_pv2write.keys():
            status = self.map_pv2write[reason](value)
            _log.info('%s Write for: %s --> %s',
                      str(status).upper(), reason, str(value))
            return status
        _log.warning('PV %s does not have a set function.', reason)
        return False

    def set_loop_state(self, value):
        """Set loop state."""
        if not 0 <= value < len(_ETypes.OPEN_CLOSED):
            return False
        self._loop_state = value
        act = ('En' if value else 'Dis')
        self._update_log(f'Feedforward loop {act}abled.')
        self.run_callbacks('LoopState-Sts', value)
        return True

    def set_loop_freq(self, value):
        """Set loop frequency."""
        fmin, fmax = _Const.DEFAULT_LOOP_FREQ_MIN, _Const.DEFAULT_LOOP_FREQ_MAX
        if not fmin <= value < fmax:
            return False
        self._loop_freq = value
        self._update_log(f'Loop frequency updated to {value:.3f}Hz.')
        self.run_callbacks('LoopFreq-RB', value)
        return True

    def set_control_qs(self, value):
        """Set whether to include QS or not in feedforward."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False
        self._control_qs = value
        act = ('En' if value else 'Dis')
        self._update_log(f'{act}abled QS control.')
        self.run_callbacks('ControlQS-Sts', value)
        return True

    def set_config_name(self, value):
        """Set configuration name."""
        if self._loop_state == self._const.LoopState.Closed:
            self._update_log('ERR:Open loop before changing configuration.')
            return False

        if not self._load_config(value):
            return False

        self._config_name = value
        self.update_autosave_file()
        self.run_callbacks('ConfigName-RB', value)
        return True

    def cmd_corrconfig(self, _):
        """Command to reconfigure power supplies to desired state."""
        if self._loop_state == self._const.LoopState.Closed:
            self._update_log('ERR:Open loop before configure correctors.')
            return False

        corrdevs = self._idff.chdevs + self._idff.cvdevs + self._idff.qsdevs
        for dev in corrdevs:
            # turn on
            if not dev.cmd_turn_on():
                return False
            # opmode slowref
            if not dev.cmd_slowref():
                return False

        return True

    @property
    def quit(self):
        """Quit and shutdown threads."""
        return self._quit

    @quit.setter
    def quit(self, value):
        if value:
            self._quit = value

    def main_idff_loop(self):
        """Main IDFF loop."""
        while not self._quit:
            # updating interval
            tplanned = 1.0/self._loop_freq

            # initial time
            _t0 = _time.time()

            # check IDFF device connection
            if not self._idff.connected:
                self._do_sleep(_t0, tplanned)
                continue

            # update polarization state
            self._do_update_polarization()

            # correctors value calculation
            self._do_update_correctors()

            # return if loop is not closed
            if not self._loop_state:
                self._do_sleep(_t0, tplanned)
                continue

            # setpoints implementation
            if self._corr_setpoints:
                self._do_implement_correctors()

            # sleep unused time or signal overtime to stdout
            self._do_sleep(_t0, tplanned)

    #  ----- log auxiliary methods -----

    def _update_log(self, msg):
        if 'ERR' in msg:
            _log.error(msg[4:])
        elif 'FATAL' in msg:
            _log.error(msg[6:])
        elif 'WARN' in msg:
            _log.warning(msg[5:])
        else:
            _log.info(msg)
        self.run_callbacks('Log-Mon', msg)

    # ----- auto save methods -----

    def read_autosave_file(self):
        """Read autosave file."""
        filename = self._const.autosave_fname
        config_name = None
        if _os.path.isfile(filename):
            with open(filename, 'r') as fil:
                config_name = fil.read().strip('\n')
        if config_name is not None:
            self._config_name = config_name
        else:
            _log.info(
                'No backup file was found, default value '
                'was used for si_idff configuration name.')
            self._config_name = self._get_default_configname()
            self.update_autosave_file()
            _log.info('First autosave file was created.')

    def update_autosave_file(self):
        """Update autosave file."""
        path = _os.path.split(self._const.autosave_fname)[0]
        _os.makedirs(path, exist_ok=True)
        with open(self._const.autosave_fname, 'w+') as fil:
            fil.write(self._config_name)

    def _get_default_configname(self):
        if self._const.idname.dev == 'EPU50':
            return 'epu50_ref'
        elif self._const.idname.dev == 'PAPU50':
            return 'papu50_ref'
        elif self._const.idname.dev == 'DELTA52':
            return 'delta52_ref'
        return ''

    def _load_config(self, config_name):
        try:
            self._idff.load_config(config_name)
            self._update_log(f'Updated configuration: {config_name}.')
        except (ValueError, _ConfigDBException) as err:
            self._update_log('ERR:'+str(err))
            return False
        return True

    # ----- update pvs methods -----

    def _do_sleep(self, time0, tplanned):
        ttook = _time.time() - time0
        tsleep = tplanned - ttook
        if tsleep > 0:
            _time.sleep(tsleep)
        else:
            _log.warning(
                'Feedforward step took more than planned... '
                '{0:.3f}/{1:.3f} s'.format(ttook, tplanned))

    def _do_update_polarization(self):
        new_pol, *_ = self._idff.get_polarization_state()
        if new_pol is not None and new_pol != self._polarization:
            self._polarization = new_pol
            self.run_callbacks('Polarization-Mon', new_pol)

    def _do_update_correctors(self):
        try:
            self._corr_setpoints = self._idff.calculate_setpoints()
            # setpoints, polarization, *parameters = self._corr_setpoints
            # pparameter_value, kparameter_value = parameters
            # print('pparameter: ', pparameter_value)
            # print('kparameter: ', kparameter_value)
            # print('polarization: ', polarization)
            # print('setpoints: ', setpoints)
            # print()
        except ValueError as err:
            self._update_log('ERR:'+str(err))

    def _do_implement_correctors(self):
        corrdevs = None
        if self._control_qs == self._const.DsblEnbl.Dsbl:
            corrdevs = self._idff.chdevs + self._idff.cvdevs
        try:
            # use PS IOCs (IDFF) to implement setpoints
            setpoints, *_ = self._corr_setpoints
            self._idff.implement_setpoints(
                setpoints=setpoints, corrdevs=corrdevs)

        except ValueError as err:
            self._update_log('ERR:'+str(err))

    def _update_corr_status(self):
        """Update CorrStatus-Mon PV."""
        devs = self._idff.chdevs + self._idff.cvdevs
        if self._control_qs == self._const.DsblEnbl.Enbl:
            devs.extend(self._idff.qsdevs)

        status = 0
        if all(d.connected for d in devs):
            if any(d.pwrstate != d.PWRSTATE.On for d in devs):
                status = _updt_bit(status, 1, 1)
            if any(d.opmode != d.OPMODE_STS.SlowRef for d in devs):
                status = _updt_bit(status, 2, 1)
        else:
            status = _Const.DEFAULT_CORR_STATUS

        self.run_callbacks('CorrStatus-Mon', status)

    def _update_corr_setpoints(self):
        """Update corrector setpoint PVs."""
        if self._corr_setpoints is None:
            return
        setpoints, *_ = self._corr_setpoints
        idff = self._idff
        corrnames = idff.chnames + idff.cvnames + idff.qsnames
        corrlabels = ('CH1', 'CH2', 'CV1', 'CV2', 'QS1', 'QS2')
        for corrlabel, corrname in zip(corrlabels, corrnames):
            for corr_pvname in setpoints:
                if corrname in corr_pvname:
                    pvname = 'Corr' + corrlabel + 'Current-Mon'
                    value = setpoints[corr_pvname]
                    self.run_callbacks(pvname, value)

    # ----- idff preparation -----

    def _idff_prepare_corrs_state(self):
        """Configure PSSOFB mode state ."""
        if not self._idff.wait_for_connection():
            return False
        corrdevs = self._idff.chdevs + self._idff.cvdevs + self._idff.qsdevs
        for dev in corrdevs:
            if not dev.cmd_sofbmode_disable(timeout=App.DEF_PS_TIMEOUT):
                return False
        return True
