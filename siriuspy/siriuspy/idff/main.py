"""ID feedforward App."""

import logging as _log
import os as _os
import time as _time

import epics as _epics

from ..callbacks import Callback as _Callback
from ..clientconfigdb import ConfigDBException as _ConfigDBException
from ..devices import IDFF as _IDFF
from ..util import update_bit as _updt_bit
from .csdev import ETypes as _ETypes, IDFFConst as _Const


class App(_Callback):
    """Main application for ID feedforward."""

    def __init__(self, idname,
                 enbl_chcorrs, enbl_cvcorrs,
                 enbl_qscorrs, enbl_lccorrs,
                 enbl_qncorrs, enbl_cccorrs):
        """Class constructor."""
        super().__init__()
        self.const = _Const(
            idname,
            enbl_chcorrs, enbl_cvcorrs,
            enbl_qscorrs, enbl_lccorrs,
            enbl_qncorrs, enbl_cccorrs)
        self.pvs_prefix = self.const.idffname
        self.pvs_database = self.const.get_propty_database()

        self.loop_state = _Const.DEFAULT_LOOP_STATE
        self.loop_freq = _Const.DEFAULT_LOOP_FREQ
        self.control_ch = self.const.enbl_chcorrs
        self.control_cv = self.const.enbl_cvcorrs
        self.control_qs = self.const.enbl_qscorrs
        self.control_lc = self.const.enbl_lccorrs
        self.control_qn = self.const.enbl_qncorrs
        self.control_cc = self.const.enbl_cccorrs
        self.polarization = 'none'

        # IDFF object with IDFF config
        idffname_soft = self.const.idffname
        self.idff = _IDFF(idffname_soft, with_devctrl=False)

        self.config_name = ''  # stored in autosave file
        self.read_autosave_file()

        # load idff in configdb
        self.load_config(self.config_name)

        # pvs to write methods
        self.map_pv2write = {
            'LoopState-Sel': self.write_loop_state,
            'LoopFreq-SP': self.write_loop_freq,
            'ConfigName-SP': self.write_config_name,
            'CorrConfig-Cmd': self.write_cmd_corr_config,
            'CorrSaveOffsets-Cmd': self.write_cmd_save_offsets,
            # following mappings are only used if
            # corresponding correctors are in IDFF
            'ControlCH-Sel': self.write_control_ch,
            'ControlCV-Sel': self.write_control_cv,
            'ControlQS-Sel': self.write_control_qs,
            'ControlLC-Sel': self.write_control_lc,
            'ControlQN-Sel': self.write_control_qn,
            'ControlCC-Sel': self.write_control_cc,
        }

        self._thread_quit = False
        self._corr_setpoints = None
        self._thread_ff = _epics.ca.CAThread(
            target=self.feedforward_loop, daemon=True)
        self._thread_ff.start()

    def init_database(self):
        """Set initial PV values."""
        pvn2vals = {
            'LoopState-Sel': self.loop_state,
            'LoopState-Sts': self.loop_state,
            'LoopFreq-SP': self.loop_freq,
            'LoopFreq-RB': self.loop_freq,
            'ConfigName-SP': self.config_name,
            'ConfigName-RB': self.config_name,
            'Polarization-Mon': self.polarization,
            'CorrConfig-Cmd': 0,
            'CorrStatus-Mon': _Const.DEFAULT_CORR_STATUS,
        }
        if self.const.enbl_chcorrs:
            pvn2vals.update({
                'ControlCH-Sel': self.control_ch,
                'ControlCH-Sts': self.control_ch,
                })
        if self.const.enbl_cvcorrs:
            pvn2vals.update({
                'ControlCV-Sel': self.control_cv,
                'ControlCV-Sts': self.control_cv,
                })
        if self.const.enbl_qscorrs:
            pvn2vals.update({
                'ControlQS-Sel': self.control_qs,
                'ControlQS-Sts': self.control_qs,
                })
        if self.const.enbl_lccorrs:
            pvn2vals.update({
                'ControlLC-Sel': self.control_lc,
                'ControlLC-Sts': self.control_lc,
                })
        if self.const.enbl_qncorrs:
            pvn2vals.update({
                'ControlQN-Sel': self.control_qn,
                'ControlQN-Sts': self.control_qn,
                })
        if self.const.enbl_cccorrs:
            pvn2vals.update({
                'ControlCC-Sel': self.control_cc,
                'ControlCC-Sts': self.control_cc,
                })
        for pvn, val in pvn2vals.items():
            self.run_callbacks(pvn, val)
        self.update_log('Started.')

    def process(self, interval):
        """Sleep."""
        # check correctors state periodically
        _t0 = _time.time()
        self.update_corr_status()
        self.update_corr_pvs()
        dtime = _time.time() - _t0
        sleep_time = interval - dtime
        # sleep
        if sleep_time > 0:
            _time.sleep(sleep_time)
        else:
            strf = f'process took {(dtime)*1000:f}ms.'
            _log.debug(strf)

    def read(self, reason):
        """Read from IOC database."""
        _ = reason
        value = None
        return value

    # ----- write methods -----

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

    def write_loop_state(self, value):
        """Set loop state."""
        if not 0 <= value < len(_ETypes.OPEN_CLOSED):
            return False
        self.loop_state = value
        act = ('En' if value else 'Dis')
        self.update_log(f'Feedforward loop {act}abled.')
        self.run_callbacks('LoopState-Sts', value)
        return True

    def write_loop_freq(self, value):
        """Set loop frequency."""
        fmin, fmax = _Const.DEFAULT_LOOP_FREQ_MIN, _Const.DEFAULT_LOOP_FREQ_MAX
        if not fmin <= value < fmax:
            return False
        self.loop_freq = value
        self.update_log(f'Loop frequency updated to {value:.3f}Hz.')
        self.run_callbacks('LoopFreq-RB', value)
        return True

    def write_control_ch(self, value):
        """Set whether to include CH or not in feedforward."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False
        self.control_ch = value
        act = ('En' if value else 'Dis')
        self.update_log(f'{act}abled CH control.')
        self.run_callbacks('ControlCH-Sts', value)
        return True

    def write_control_cv(self, value):
        """Set whether to include CV or not in feedforward."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False
        self.control_cv = value
        act = ('En' if value else 'Dis')
        self.update_log(f'{act}abled CV control.')
        self.run_callbacks('ControlCV-Sts', value)
        return True

    def write_control_qs(self, value):
        """Set whether to include QS or not in feedforward."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False
        self.control_qs = value
        act = ('En' if value else 'Dis')
        self.update_log(f'{act}abled QS control.')
        self.run_callbacks('ControlQS-Sts', value)
        return True

    def write_control_lc(self, value):
        """Set whether to include LC or not in feedforward."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False
        self.control_lc = value
        act = ('En' if value else 'Dis')
        self.update_log(f'{act}abled LC control.')
        self.run_callbacks('ControlLC-Sts', value)
        return True

    def write_control_qn(self, value):
        """Set whether to include QN or not in feedforward."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False
        self.control_qn = value
        act = ('En' if value else 'Dis')
        self.update_log(f'{act}abled QN control.')
        self.run_callbacks('ControlQN-Sts', value)
        return True

    def write_control_cc(self, value):
        """Set whether to include CC or not in feedforward."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False
        self.control_cc = value
        act = ('En' if value else 'Dis')
        self.update_log(f'{act}abled CC control.')
        self.run_callbacks('ControlCC-Sts', value)
        return True

    def write_config_name(self, value, save_autoconfig=True):
        """Set configuration name."""
        if self.loop_state == self.const.LoopState.Closed:
            self.update_log('ERR:Open loop before changing configuration.')
            return False

        if not self.load_config(value):
            return False
        self.config_name = value
        self.run_callbacks('ConfigName-RB', value)

        if save_autoconfig:
            self.update_autosave_file()

        return True

    def write_cmd_corr_config(self, _):
        """Command to reconfigure power supplies to desired state."""
        if self.loop_state == self.const.LoopState.Closed:
            self.update_log('ERR:Open loop before configure correctors.')
            return False

        corrdevs = self.get_control_corrdevs()
        for dev in corrdevs:
            # turn on
            if not dev.cmd_turn_on():
                return False
            # opmode slowref
            if not dev.cmd_slowref():
                return False

        return True

    def write_cmd_save_offsets(self, _):
        """Save current values of correctors' currents to si_idff configdb."""
        if self.loop_state == self.const.LoopState.Closed:
            self.update_log('ERR:Open loop before saving correctors offsets.')
            return False

        return self.save_config_offsets()

    # ----- feedforward loop methods -----

    @property
    def thread_is_alive(self):
        """Return if thread is alive."""
        return self._thread_ff.is_alive()

    @property
    def thread_quit(self):
        """Quit and shutdown threads."""
        return self._thread_quit

    @thread_quit.setter
    def thread_quit(self, value):
        if value:
            self._thread_quit = value

    def feedforward_loop(self):
        """Main IDFF loop."""
        self.idff.wait_for_connection(timeout=2)

        while not self._thread_quit:
            # updating interval
            tplanned = 1.0/self.loop_freq

            # initial time
            _t0 = _time.time()

            # check IDFF device connection
            if not self.idff.connected:
                self.update_log('WARN: IDFF device disconnected!')
                self._do_sleep(_t0, tplanned)
                continue

            # update polarization state
            self.update_polarization()

            # correctors value calculation
            self.update_corr_setpoints()

            # return if loop is not closed
            if not self.loop_state:
                self._do_sleep(_t0, tplanned)
                continue

            # setpoints implementation
            if self._corr_setpoints:
                self.implement_setpoints()

            # sleep unused time or signal overtime to stdout
            self._do_sleep(_t0, tplanned)
        self._thread_quit = False

    def implement_setpoints(self):
        """."""
        corrdevs = self.get_control_corrdevs()

        try:
            # use PS IOCs (IDFF) to implement setpoints
            setpoints, *_ = self._corr_setpoints
            self.idff.implement_setpoints(
                setpoints=setpoints, corrdevs=corrdevs)

        except ValueError as err:
            self.update_log('ERR:'+str(err))

    # ----- read and save methods -----

    def read_autosave_file(self):
        """Read autosave file."""
        # TODO: create a autosave/restore mechanism that is
        # standardized for all IOCS!
        filename = self.const.autosave_fname
        config_name = None
        if _os.path.isfile(filename):
            with open(filename, 'r') as fil:
                config_name = fil.read().strip('\n')
        if config_name is not None:
            self.write_config_name(config_name, save_autoconfig=False)
        else:
            _log.info(
                'No backup file was found, default value '
                'was used for si_idff configuration name.')
            self.config_name = self.const.configname + '_ref'
            self.update_autosave_file()
            self.update_log('First autosave file was created.')

    def update_autosave_file(self):
        """Update autosave file."""
        path = _os.path.split(self.const.autosave_fname)[0]
        _os.makedirs(path, exist_ok=True)
        with open(self.const.autosave_fname, 'w+') as fil:
            fil.write(self.config_name)

    def load_config(self, config_name):
        """."""
        try:
            self.idff.load_config(config_name)
            self.update_log(f'Updated configuration: {config_name}.')
        except (ValueError, _ConfigDBException) as err:
            self.update_log('ERR: could not load config ' + self.config_name)
            raise err
        return True

    def save_config_offsets(self):
        """."""
        try:
            offsets = self.idff.read_corr_offset_values()
        except:  # noqa: E722
            self.update_log('ERR: could not read correctors offsets')
            return False
        if not offsets:
            self.update_log('WARN: Offsets not defined for this IDFF')
            return False

        config = self.idff.idffconfig
        value = config.value
        value['offsets'] = offsets
        try:
            config.save()
        except:  # noqa: E722
            self.update_log('ERR: could not save configuration')
            return False
        self.update_log('Correctors offsets saved in ' + self.config_name)

    # ----- update methods -----

    def update_polarization(self):
        """."""
        new_pol, *_ = self.idff.get_polarization_state()
        if new_pol is not None and new_pol != self.polarization:
            self.polarization = new_pol
            self.run_callbacks('Polarization-Mon', new_pol)

    def update_corr_setpoints(self):
        """."""
        try:
            self._corr_setpoints = self.idff.calculate_setpoints()
            # setpoints, polarization, *parameters = self._corr_setpoints
            # pparameter_value, kparameter_value = parameters
            # print('pparameter: ', pparameter_value)
            # print('kparameter: ', kparameter_value)
            # print('polarization: ', polarization)
            # print('setpoints: ', setpoints)
            # print()
        except ValueError as err:
            self.update_log('ERR:'+str(err))

    def update_corr_status(self):
        """Update CorrStatus-Mon PV."""
        corrdevs = self.get_control_corrdevs()

        status = 0
        if all(d.connected for d in corrdevs):
            if any(d.pwrstate != d.PWRSTATE.On for d in corrdevs):
                status = _updt_bit(status, 1, 1)
            if any(d.opmode != d.OPMODE_STS.SlowRef for d in corrdevs):
                status = _updt_bit(status, 2, 1)
        else:
            status = _Const.DEFAULT_CORR_STATUS

        self.run_callbacks('CorrStatus-Mon', status)

    def update_corr_pvs(self):
        """Update corrector setpoint PVs."""
        if self._corr_setpoints is None:
            return
        setpoints, *_ = self._corr_setpoints
        idff = self.idff
        corrnames = idff.chnames + idff.cvnames + \
            idff.qsnames + idff.lcnames + idff.qnnames + \
            idff.ccnames
        corrlabels = (
            'CH_1', 'CH_2', 'CV_1', 'CV_2',
            'QS_1', 'QS_2', 'LCH', 'LCV',
            'QD1_1', 'QF_1', 'QD2_1', 'QD2_2', 'QF_2', 'QD1_2',
            'CC1_1', 'CC2_1', 'CC2_2', 'CC1_2',
            )
        for corrlabel, corrname in zip(corrlabels, corrnames):
            for corr_pvname in setpoints:
                if corrname in corr_pvname:
                    pvname = 'Corr' + corrlabel + 'Current-Mon'
                    value = setpoints[corr_pvname]
                    if pvname in self.pvs_database:
                        self.run_callbacks(pvname, value)

    def update_log(self, msg):
        """."""
        if 'ERR' in msg:
            _log.error(msg[4:])
        elif 'FATAL' in msg:
            _log.error(msg[6:])
        elif 'WARN' in msg:
            _log.warning(msg[5:])
        else:
            _log.info(msg)
        self.run_callbacks('Log-Mon', msg)

    #  ----- auxiliary methods -----

    def get_control_corrdevs(self):
        """Return devices of currently enabled correctors."""
        corrdevs = list()
        if self.control_ch == self.const.DsblEnbl.Enbl:
            corrdevs.extend(self.idff.chdevs)
        if self.control_cv == self.const.DsblEnbl.Enbl:
            corrdevs.extend(self.idff.cvdevs)
        if self.control_qs == self.const.DsblEnbl.Enbl:
            corrdevs.extend(self.idff.qsdevs)
        if self.control_lc == self.const.DsblEnbl.Enbl:
            corrdevs.extend(self.idff.lcdevs)
        if self.control_qn == self.const.DsblEnbl.Enbl:
            corrdevs.extend(self.idff.qndevs)
        if self.control_cc == self.const.DsblEnbl.Enbl:
            corrdevs.extend(self.idff.ccdevs)
        return corrdevs

    # ----- update pvs methods -----

    def _do_sleep(self, time0, tplanned):
        ttook = _time.time() - time0
        tsleep = tplanned - ttook
        if tsleep > 0:
            _time.sleep(tsleep)
        else:
            strf = (
                f'Feedforward step took more than planned... '
                f'{ttook:.3f}/{tplanned:.3f} s')
            _log.warning(strf)
