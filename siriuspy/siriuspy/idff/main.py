"""ID feedforward App."""

import os as _os
import logging as _log
import time as _time
import epics as _epics

from ..callbacks import Callback as _Callback
from ..devices import IDFF as _IDFF

from .csdev import IDFFConst as _Const, ETypes as _ETypes


class App(_Callback):
    """Main application for handling machine shift."""

    def __init__(self, idname):
        """Class constructor."""
        super().__init__()
        self._const = _Const(idname)
        self._pvs_prefix = self._const.idffname
        self._pvs_database = self._const.get_propty_database()

        self._loop_state = _Const.DsblEnbl.Dsbl
        self._loop_freq = _Const.DEFAULT_LOOP_FREQ
        self._control_qs = _Const.DsblEnbl.Dsbl
        self._polarization = 'none'
        self._config_name = ''
        self.read_autosave_file()

        self._idff = _IDFF(idname)

        self._load_config(self._config_name)

        # pvs to write methods
        self.map_pv2write = {
            'LoopState-Sel': self.set_loop_state,
            'LoopFreq-SP': self.set_loop_freq,
            'ControlQS-Sel': self.set_control_qs,
            'ConfigName-SP': self.set_config_name,
        }

        self.quit = False
        self._thread_ff = _epics.ca.CAThread(
            target=self._do_ff, daemon=True)
        self._thread_ff.start()

    def init_database(self):
        """Set initial PV values."""
        pvn2vals = {
            'LoopState-Sel': self._loop_state,
            'LoopState-Sts': self._loop_state,
            'LoopFreq-SP': self._loop_freq,
            'LoopFreq-RB': self._loop_freq,
            'ControlQS-Sel': self._control_qs,
            'ControlQS-Sts': self._control_qs,
            'ConfigName-SP': self._config_name,
            'ConfigName-RB': self._config_name,
            'Polarization-Mon': self._polarization,
        }
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
        _time.sleep(interval)

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
        if not 1e-3 <= value < 60:
            return False
        self._loop_freq = value
        self._update_log(f'Loop frequency updated to {value:.2f}Hz.')
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
        self.run_callbacks('ConfigName-RB', value)
        return True

    def _load_config(self, config_name):
        try:
            self._idff.load_config(config_name)
            self._update_log(f'Updated configuration: {config_name}.')
        except ValueError as err:
            self._update_log('ERR:'+str(err))
            return False
        return True

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
        return ''

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
        if new_pol != self._polarization:
            self._polarization = new_pol
            self.run_callbacks('Polarization-Mon', new_pol)

    def _do_update_correctors(self):
        corrs = None
        if self._control_qs == self._const.DsblEnbl.Dsbl:
            corrs = self._idff.chdevs + self._idff.cvdevs
        try:
            # ret = self._idff.calculate_setpoints()
            # setpoints, polarization, *parameters = ret
            # pparameter_value, kparameter_value = parameters
            # print('pparameter: ', pparameter_value)
            # print('kparameter: ', kparameter_value)
            # print('polarization: ', polarization)
            # print('setpoints: ', setpoints)
            # print()
            self._idff.implement_setpoints(corrdevs=corrs)
        except ValueError as err:
            self._update_log('ERR:'+str(err))

    def _do_ff(self):
        # updating loop
        while not self.quit:
            # updating interval
            tplanned = 1.0/self._loop_freq

            # initial time
            _t0 = _time.time()

            # check IDFF device connection
            if not self._idff.connected:
                self._update_log('ERR: IDFF device is disconnected.')
                self._do_sleep(_t0, tplanned)
                continue

            # update polarization state
            self._do_update_polarization()

            # return if loop is not closed
            if not self._loop_state:
                self._do_sleep(_t0, tplanned)
                continue

            # correctors setpoint implementation
            self._do_update_correctors()

            # sleep unused time or signal overtime to stdout
            self._do_sleep(_t0, tplanned)
