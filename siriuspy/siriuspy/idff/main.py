"""ID feedforward App."""

import os as _os
import logging as _log
import time as _time
import epics as _epics
import numpy as _np

from PRUserial485 import EthBridgeClient as _EthBridgeClient

from ..util import update_bit as _updt_bit
from ..callbacks import Callback as _Callback
from ..devices import IDFF as _IDFF
from ..pwrsupply.pssofb import PSConnSOFB as _PSConnSOFB
from ..pwrsupply.pssofb import PSNamesSOFB as _PSNamesSOFB

from .csdev import IDFFConst as _Const, ETypes as _ETypes


class App(_Callback):
    """Main application for handling machine shift."""

    DEF_PS_TIMEOUT = 5  # [s]

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

        self._pssofb_isused = self._pvs_database['SOFBMode-Sts']['value']
        self._pssofb, self._bsmp_devs = self._pssofb_init(idname)

        # load idff in configdb
        self._load_config(self._config_name)

        # pvs to write methods
        self.map_pv2write = {
            'LoopState-Sel': self.set_loop_state,
            'LoopFreq-SP': self.set_loop_freq,
            'ControlQS-Sel': self.set_control_qs,
            'ConfigName-SP': self.set_config_name,
            'SOFBMode-Sel': self.set_sofb_mode,
            'CorrConfig-Cmd': self.cmd_corrconfig,
        }

        self._quit = False
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
            'SOFBMode-Sel': self._pssofb_isused,
            'SOFBMode-Sts': self._pssofb_isused,
            'CorrConfig-Cmd': 0,
            'CorrStatus-Mon': 0b1111,
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
        # check correctors state periodically
        _t0 = _time.time()
        self._update_corr_status()
        dtime = _time.time() - _t0
        # sleep
        if dtime > 0:
            _time.sleep(interval - dtime)
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

    def set_sofb_mode(self, value):
        """Set whether to use SOFBMode."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False

        if self._loop_state == self._const.LoopState.Closed:
            self._update_log('ERR:Open loop before changing configuration.')
            return False

        if not self._idff_prepare_corrs_state(value):
            self._update_log(
                ('ERR:Could not configure IDFF correctors '
                 'when changing SOFBMode.'))
            return False

        self._pssofb_isused = bool(value)
        status = 'enabled' if self._pssofb_isused else 'disabled'
        self._update_log(f'SOFBMode {status}.')
        self.run_callbacks('SOFBMode-Sts', value)

        return True

    def cmd_corrconfig(self, _):
        """Command to reconfigure power supplies to desired state."""
        if self._loop_state == self._const.LoopState.Closed:
            self._update_log('ERR:Open loop before configure correctors.')
            return False
        if self._pssofb_isused:
            self._update_log('ERR:Turn off PSSOFB mode before configure.')
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

    def _load_config(self, config_name):
        try:
            self._idff.load_config(config_name)
            self._update_log(f'Updated configuration: {config_name}.')
        except ValueError as err:
            self._update_log('ERR:'+str(err))
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
            self._pssofb.threads_shutdown()

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
        if new_pol is not None and new_pol != self._polarization:
            self._polarization = new_pol
            self.run_callbacks('Polarization-Mon', new_pol)

    def _do_update_correctors(self):
        corrdevs = None
        if self._control_qs == self._const.DsblEnbl.Dsbl:
            corrdevs = self._idff.chdevs + self._idff.cvdevs
        try:
            # ret = self._idff.calculate_setpoints()
            # setpoints, polarization, *parameters = ret
            # pparameter_value, kparameter_value = parameters
            # print('pparameter: ', pparameter_value)
            # print('kparameter: ', kparameter_value)
            # print('polarization: ', polarization)
            # print('setpoints: ', setpoints)
            # print()
            if self._pssofb_isused:
                # calc setpoints
                ret = self._idff.calculate_setpoints()
                setpoints, *_ = ret

                # built curr_sp vector
                curr_sp = self._pssfob_current_setpoint(setpoints, corrdevs)

                # apply curr_sp to pssofb
                self._pssofb.bsmp_sofb_current_set_update((curr_sp, ))
            else:
                # use PS IOCs (IDFF) to implement setpoints
                self._idff.implement_setpoints(corrdevs=corrdevs)

        except ValueError as err:
            self._update_log('ERR:'+str(err))

    def _do_ff(self):
        # updating loop
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

            # return if loop is not closed
            if not self._loop_state:
                self._do_sleep(_t0, tplanned)
                continue

            # correctors setpoint implementation
            self._do_update_correctors()

            # sleep unused time or signal overtime to stdout
            self._do_sleep(_t0, tplanned)

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
            if any(d.sofbmode != self._pssofb_isused for d in devs):
                status = _updt_bit(status, 3, 1)
        else:
            status = 0b111

        self.run_callbacks('CorrStatus-Mon', status)

    # ----- idff -----

    def _idff_prepare_corrs_state(self, pssofb_isused):
        """Configure PSSOFB mode state ."""
        if not self._idff.wait_for_connection():
            return False
        corrdevs = self._idff.chdevs + self._idff.cvdevs + self._idff.qsdevs
        for dev in corrdevs:
            if pssofb_isused:
                if not dev.cmd_sofbmode_enable(timeout=App.DEF_PS_TIMEOUT):
                    return False
            else:
                if not dev.cmd_sofbmode_disable(timeout=App.DEF_PS_TIMEOUT):
                    return False
        return True

    # ----- pssofb -----

    def _pssofb_init(self, idname):
        """Create PSSOFB connections to control correctors."""
        # bbbnames
        bbbnames = _PSNamesSOFB.get_bbbnames(idname)

        # create pssofb object
        pssofb = _PSConnSOFB(
            ethbridgeclnt_class=_EthBridgeClient,
            bbbnames=bbbnames,
            sofb_update_iocs=True,
            acc=idname)

        # build bsmpid -> psname dict
        bsmp_devs = dict()
        for devices in pssofb.bbb2devs.values():
            for devname, bsmpid in devices:
                bsmp_devs[bsmpid] = devname

        return pssofb, bsmp_devs

    def _pssfob_get_current_setpoint(self, setpoints, corrdevs):
        """Convert IDFF dict setpoints to PSSOFB list setpoints."""
        current_sp = _np.ones(len(setpoints)) * _np.nan
        devnames = [dev.devname for dev in corrdevs]
        for bsmpid, devname in self._bsmp_devs.items():
            if devname in devnames:
                current_sp[bsmpid - 1] = setpoints[devname]
        return current_sp
