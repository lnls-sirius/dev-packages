"""Define Insertion Devices."""

import time as _time

from ..namesys import SiriusPVName as _SiriusPVName
from ..search import IDSearch as _IDSearch

from .device import Device as _Device


class _ID(_Device):
    """Generic Insertion Device."""

    _SHORT_SHUT_EYE = 0.1  # [s]
    _MOVECHECK_SLEEP = 0.1  # [s]
    _DEF_TIMEOUT = 8  # [s]

    PROPERTIES_DEFAULT = (
        'Moving-Mon',
        'BeamLineCtrlEnbl-Sel', 'BeamLineCtrlEnbl-Sts',
    )

    def __init__(self, devname, props2init='all', auto_monitor_mon=True):
        """."""
        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)

    @property
    def parameters(self):
        """Return ID parameters."""
        return _IDSearch.conv_idname_2_parameters(self.devname)

    @property
    def period_length(self):
        """Return ID period length [mm]."""
        return self.parameters.PERIOD_LENGTH

    @property
    def pparameter_parked(self):
        """Return ID parked pparameter value [mm]."""
        return self.parameters.PPARAM_PARKED

    @property
    def kparameter_parked(self):
        """Return ID parked kparameter value [mm]."""
        return self.parameters.KPARAM_PARKED

    # --- movement checks ---

    @property
    def is_moving(self):
        """Return True if phase is changing."""
        return round(self['Moving-Mon']) == 1

    # --- cmd_beamline and cmd_drive

    def cmd_beamline_ctrl_enable(self, timeout=None):
        """Command enable bealine ID control."""
        return self._write_sp('BeamLineCtrlEnbl-Sel', 1, timeout)

    def cmd_beamline_ctrl_disable(self, timeout=None):
        """Command disable bealine ID control."""
        return self._write_sp('BeamLineCtrlEnbl-Sel', 0, timeout)

    # --- cmd_wait

    def wait_while_busy(self, timeout=None):
        """Command wait within timeout while ID control is busy."""
        return True

    # --- cmd_wait

    def cmd_wait_move(self, timeout=None):
        """Wait for phase movement to complete."""
        _time.sleep(APU._MOVECHECK_SLEEP)
        t0_ = _time.time()
        while self.is_moving:
            _time.sleep(APU._MOVECHECK_SLEEP)
            if timeout and _time.time() - t0_ > timeout:
                return False
        return True

    # --- private methods ---

    def _move_start(self, cmd_propty, timeout=None):
        timeout = timeout or self._DEF_TIMEOUT

        # wait for not busy state
        if not self.wait_while_busy(timeout=timeout):
            return False

        # send move command
        self[cmd_propty] = 1

        return True

    def _write_sp(self, propties_sp, values, timeout=None, pvs_sp_rb=None):
        timeout = timeout or self._DEF_TIMEOUT
        if isinstance(propties_sp, str):
            propties_sp = (propties_sp, )
            values = (values, )
        success = True
        for propty_sp, value in zip(propties_sp, values):
            if pvs_sp_rb is not None and propty_sp in pvs_sp_rb:
                # pv is unique for SP and RB variables.
                propty_rb = propty_sp
            else:
                propty_rb = \
                    propty_sp.replace('-SP', '-RB').replace('-Sel', '-Sts')
            self[propty_sp] = value
            success &= super()._wait(
                propty_rb, value, timeout=timeout, comp='eq')
        return success

    def _wait_propty(self, propty, value, timeout=None):
        """."""
        t0_ = _time.time()
        timeout = timeout if timeout is not None else self._DEF_TIMEOUT
        while self[propty] != value:
            _time.sleep(self._SHORT_SHUT_EYE)
            if _time.time() - t0_ > timeout:
                return False
        return True


class APU(_ID):
    """APU Insertion Device."""

    class DEVICES:
        """Device names."""

        APU22_06SB = 'SI-06SB:ID-APU22'
        APU22_07SP = 'SI-07SP:ID-APU22'
        APU22_08SB = 'SI-08SB:ID-APU22'
        APU22_09SA = 'SI-09SA:ID-APU22'
        APU58_11SP = 'SI-11SP:ID-APU58'
        ALL = (
            APU22_06SB, APU22_07SP, APU22_08SB, APU22_09SA, APU58_11SP, )

    TOLERANCE_PHASE = 0.01  # [mm]

    _CMD_MOVE_STOP, _CMD_MOVE_START = 1, 3
    _CMD_MOVE = 3

    PROPERTIES_DEFAULT = _ID.PROPERTIES_DEFAULT + (
        'DevCtrl-Cmd',
        'MaxPhaseSpeed-SP', 'MaxPhaseSpeed-RB',
        'PhaseSpeed-SP', 'PhaseSpeed-Mon',
        'Phase-SP', 'Phase-Mon',
        'Kx-SP', 'Kx-Mon',
        )

    def __init__(self, devname, props2init='all', auto_monitor_mon=True):
        """."""
        # check if device exists
        if devname not in APU.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)

    # --- phase speeds ----

    @property
    def phase_speed(self):
        """Return phase speed [mm/s]."""
        return self['PhaseSpeed-RB']

    @property
    def phase_speed_mon(self):
        """Return phase speed monitor [mm/s]."""
        return self['PhaseSpeed-Mon']

    @property
    def phase_speed_max(self):
        """Return max phase speed readback [mm/s]."""
        return self['MaxPhaseSpeed-RB']

    @property
    def phase_speed_max_lims(self):
        """Return max phase speed limits."""
        ctrl = self.pv_ctrlvars('MaxPhaseSpeed-SP')
        lims = [ctrl['lower_ctrl_limit'], ctrl['upper_ctrl_limit']]
        return lims

    # --- phase ---

    @property
    def phase_parked(self):
        """Return ID parked phase value [mm]."""
        return self.period_length / 2

    @property
    def phase(self):
        """Return APU phase [mm]."""
        return self['Phase-SP']

    @property
    def phase_min(self):
        """Return ID phase lower control limit [mm]."""
        ctrlvars = self.pv_ctrlvars('Phase-SP')
        return ctrlvars['lower_ctrl_limit']

    @property
    def phase_max(self):
        """Return ID phase upper control limit [mm]."""
        ctrlvars = self.pv_ctrlvars('Phase-SP')
        return ctrlvars['upper_ctrl_limit']

    @property
    def phase_mon(self):
        """Return APU phase [mm]."""
        return self['Phase-Mon']

    # --- Kparam methods ---

    @property
    def idkx(self):
        """Return APU Kx."""
        return self['Kx-SP']

    @idkx.setter
    def idkx(self, value):
        """Set APU Kx."""
        self['Kx-SP'] = value

    # --- set methods ---

    def set_phase(self, phase, timeout=None):
        """Command to set ID target phase for movement [mm]."""
        return self._write_sp('Phase-SP', phase, timeout)

    def set_phase_speed(self, phase_speed, timeout=None):
        """Command to set ID cruise phase speed for movement [mm/s]."""
        return self._write_sp('PhaseSpeed-SP', phase_speed, timeout)

    def set_phase_speed_max(self, phase_speed_max, timeout=None):
        """Command to set ID max cruise phase speed for movement [mm/s]."""
        return self._write_sp('MaxPhaseSpeed-SP', phase_speed_max, timeout)

    # -- cmd_move

    def cmd_move_stop(self, timeout=None):
        """Send command to stop ID movement."""
        self['DevCtrl-Cmd'] = APU._CMD_MOVE_STOP
        return True

    def cmd_move_start(self, timeout=None):
        """Send command to start ID movement."""
        self['DevCtrl-Cmd'] = APU._CMD_MOVE_START
        return True

    def cmd_move_park(self, timeout=None):
        """Command to set and start ID movement to parked config."""
        return self.move(self.phase_parked, timeout=timeout)

    def move(self, phase, timeout=None):
        """Command to set and start phase movements."""
        # calc ETA
        dtime_max = abs(phase - self.phase_mon) / self.phase_speed

        # additional percentual in ETA
        tol_dtime = 300  # [%]
        tol_factor = (1 + tol_dtime/100)
        tol_total = tol_factor * dtime_max + 5

        # set target phase and gap
        if not self.set_phase(phase=phase, timeout=timeout):
            return False

        # command move start
        if not self.cmd_move_start(timeout=timeout):
            return False

        # wait for movement within reasonable time
        time_init = _time.time()
        while \
                abs(self.phase_mon - phase) > self.TOLERANCE_PHASE or \
                self.is_moving:
            if _time.time() - time_init > tol_total:
                print(f'tol_total: {tol_total:.3f} s')
                print(f'wait_time: {_time.time() - time_init:.3f} s')
                print()
                return False
            _time.sleep(self._SHORT_SHUT_EYE)

        # successfull movement at this point
        return True

    # --- private methods ---

    def _write_sp(self, propties_sp, values, timeout=None):
        pvs_sp_rb = ('Phase-SP', 'PhaseSpeed-SP')
        return super()._write_sp(
            propties_sp, values, timeout=timeout, pvs_sp_rb=pvs_sp_rb)


class PAPU(_ID):
    """PAPU Insertion Device."""

    class DEVICES:
        """Device names."""

        PAPU50_17SA = 'SI-17SA:ID-PAPU50'
        ALL = (PAPU50_17SA, )

    TOLERANCE_PHASE = 0.01  # [mm]

    _SHORT_SHUT_EYE = 0.1  # [s]

    _properties = (
        'PeriodLength-Cte',
        'PwrPhase-Mon',
        'EnblAndReleasePhase-Sel', 'EnblAndReleasePhase-Sts',
        'AllowedToChangePhase-Mon',
        'ParkedPhase-Cte',
        'Phase-SP', 'Phase-RB', 'Phase-Mon',
        'PhaseSpeed-SP', 'PhaseSpeed-RB', 'PhaseSpeed-Mon',
        'MaxPhaseSpeed-SP', 'MaxPhaseSpeed-RB',
        'StopPhase-Cmd', 'ChangePhase-Cmd',
        'Log-Mon',
        )
    _properties_papu = (
        'Home-Cmd', 'EnblPwrPhase-Cmd', 'ClearErr-Cmd',
        'BeamLineCtrl-Mon',
        )

    PROPERTIES_DEFAULT = \
        _ID.PROPERTIES_DEFAULT + _properties + _properties_papu

    def __init__(self, devname=None, props2init='all', auto_monitor_mon=True):
        """."""
        # check if device exists
        if devname is None:
            devname = self.DEVICES.PAPU50_17SA
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)

    @property
    def period_length(self):
        """Return ID period length [mm]."""
        return self['PeriodLength-Cte']

    @property
    def log_mon(self):
        """Return ID Log."""
        return self['Log-Mon']

    # --- phase speeds ----

    @property
    def phase_speed(self):
        """Return phase speed readback [mm/s]."""
        return self['PhaseSpeed-RB']

    @property
    def phase_speed_mon(self):
        """Return phase speed monitor [mm/s]."""
        return self['PhaseSpeed-Mon']

    @property
    def phase_speed_max(self):
        """Return max phase speed readback [mm/s]."""
        return self['MaxPhaseSpeed-RB']

    @property
    def phase_speed_max_lims(self):
        """Return max phase speed limits."""
        ctrl = self.pv_ctrlvars('MaxPhaseSpeed-SP')
        lims = [ctrl['lower_ctrl_limit'], ctrl['upper_ctrl_limit']]
        return lims

    # --- phase ---

    @property
    def phase_parked(self):
        """Return ID parked phase value [mm]."""
        return self['ParkedPhase-Cte']

    @property
    def phase(self):
        """Return ID phase readback [mm]."""
        return self['Phase-RB']

    @property
    def phase_min(self):
        """Return ID phase lower control limit [mm]."""
        ctrlvars = self.pv_ctrlvars('Phase-SP')
        return ctrlvars['lower_ctrl_limit']

    @property
    def phase_max(self):
        """Return ID phase upper control limit [mm]."""
        ctrlvars = self.pv_ctrlvars('Phase-SP')
        return ctrlvars['upper_ctrl_limit']

    @property
    def phase_mon(self):
        """Return ID phase monitor [mm]."""
        return self['Phase-Mon']

    # --- drive checks ---

    @property
    def is_phase_drive_powered(self):
        """Return phase driver power state on (True|False)."""
        return self['PwrPhase-Mon'] != 0

    # --- movement checks ---

    @property
    def is_move_phase_enabled(self):
        """Return phase movement enabled state (True|False)."""
        return self['AllowedToChangePhase-Mon'] != 0

    @property
    def is_moving(self):
        """Return is moving state (True|False)."""
        return self['Moving-Mon'] != 0

    @property
    def is_homing(self):
        """Return whether ID is in homing procedure (True|False)."""
        return self['Home-Mon'] != 0

    @property
    def is_beamline_ctrl_enabled(self):
        """Return beamline control enabled state (True|False)."""
        return self['BeamLineCtrlEnbl-Sts'] != 0

    # --- cmd_drive

    def cmd_drive_turn_power_on(self, timeout=None):
        """Command turn phase drive on."""
        if self.is_phase_drive_powered:
            return True
        self['EnblPwrPhase-Cmd'] = 1
        props_values = {'PwrPhase-Mon': 1}
        return self._wait_propty_values(props_values, timeout=timeout)

    # --- set methods ---

    def set_phase(self, phase, timeout=None):
        """Command to set ID target phase for movement [mm]."""
        return self._write_sp('Phase-SP', phase, timeout)

    def set_phase_speed(self, phase_speed, timeout=None):
        """Command to set ID cruise phase speed for movement [mm/s]."""
        return self._write_sp('PhaseSpeed-SP', phase_speed, timeout)

    def set_phase_speed_max(self, phase_speed_max, timeout=None):
        """Command to set ID max cruise phase speed for movement [mm/s]."""
        return self._write_sp('MaxPhaseSpeed-SP', phase_speed_max, timeout)

    # --- cmd_move disable/enable ---

    def cmd_move_phase_enable(self, timeout=None):
        """Command to release and enable ID phase movement."""
        self['EnblAndReleasePhase-Sel'] = 1
        return super()._wait(
            'AllowedToChangePhase-Mon',
            1, timeout=timeout, comp='eq')

    def cmd_move_phase_disable(self, timeout=None):
        """Command to disable and break ID phase movement."""
        self['EnblAndReleasePhase-Sel'] = 0
        return super()._wait(
            'AllowedToChangePhase-Mon',
            0, timeout=timeout, comp='eq')

    def cmd_move_enable(self, timeout=None):
        """Command to release and enable ID phase and gap movements."""
        return self.cmd_move_phase_enable(timeout=timeout)

    def cmd_move_disable(self, timeout=None):
        """Command to disable and break ID phase and gap movements."""
        return self.cmd_move_phase_disable(timeout=timeout)

    def wait_move_start(self, timeout=None):
        """Command wait until movement starts or timeout."""
        time_init = _time.time()
        while not self.is_moving:
            if timeout is not None and _time.time() - time_init > timeout:
                return False
        return True

    # -- cmd_move

    def cmd_move_stop(self, timeout=None):
        """Command to interrupt and then enable phase movements."""
        timeout = timeout or self._DEF_TIMEOUT

        # wait for not busy state
        if not self.wait_while_busy(timeout=timeout):
            return False

        # send stop command
        self.cmd_move_disable()

        # check for successful stop
        if not self.wait_while_busy(timeout=timeout):
            return False

        success = True
        success &= super()._wait('Moving-Mon', 0, timeout=timeout)

        if not success:
            return False

        # enable movement again
        status = self.cmd_move_enable(timeout=timeout)

        return status

    def cmd_move_start(self, timeout=None):
        """Command to start movement."""
        success = True
        success &= self.cmd_move_phase_start(timeout=timeout)
        return success

    def cmd_move_phase_start(self, timeout=None):
        """Command to start phase movement."""
        return self._move_start('ChangePhase-Cmd', timeout=timeout)

    def cmd_move_park(self, timeout=None):
        """Command to set and start ID movement to parked config."""
        return self.move(self.phase_parked, timeout=timeout)

    def move(self, phase, timeout=None):
        """Command to set and start phase movements."""
        # calc ETA
        dtime_max = abs(phase - self.phase_mon) / self.phase_speed

        # additional percentual in ETA
        tol_dtime = 300  # [%]
        tol_factor = (1 + tol_dtime/100)
        tol_total = tol_factor * dtime_max + 5

        # set target phase and gap
        if not self.set_phase(phase=phase, timeout=timeout):
            return False

        # command move start
        if not self.cmd_move_phase_start(timeout=timeout):
            return False

        # wait for movement within reasonable time
        time_init = _time.time()
        while \
                abs(self.phase_mon - phase) > self.TOLERANCE_PHASE or \
                self.is_moving:
            if _time.time() - time_init > tol_total:
                print(f'tol_total: {tol_total:.3f} s')
                print(f'wait_time: {_time.time() - time_init:.3f} s')
                print()
                return False
            _time.sleep(self._SHORT_SHUT_EYE)

        # successfull movement at this point
        return True

    # --- cmd_reset

    def cmd_device_reset(self, timeout=None):
        """Command to reset ID to a standard movement state."""
        success = True
        success &= self.cmd_beamline_ctrl_disable(timeout=timeout)
        success &= self.cmd_drive_turn_power_on(timeout=timeout)
        success &= self.cmd_move_enable(timeout=timeout)
        return success

    # --- other cmds ---

    def cmd_clear_error(self):
        """Command to clear errors."""
        self['ClearErr-Cmd'] = 1

    # --- private methods ---

    def _write_sp(self, propties_sp, values, timeout=None):
        timeout = timeout or self._DEF_TIMEOUT
        if isinstance(propties_sp, str):
            propties_sp = (propties_sp, )
            values = (values, )
        success = True
        for propty_sp, value in zip(propties_sp, values):
            propty_rb = propty_sp.replace('-SP', '-RB').replace('-Sel', '-Sts')
            if not self.wait_while_busy(timeout=timeout):
                return False
            self[propty_sp] = value
            success &= super()._wait(
                propty_rb, value, timeout=timeout, comp='eq')
        return success

    def _wait_propty_values(self, props_values, timeout=None, comp='eq'):
        timeout = timeout if timeout is not None else self._DEF_TIMEOUT
        time0 = _time.time()
        for propty, value in props_values.items():
            timeout_left = max(0, timeout - (_time.time() - time0))
            if timeout_left == 0:
                return False
            if not super()._wait(
                    propty, value, timeout=timeout_left, comp=comp):
                return False
        return True


class EPU(PAPU):
    """EPU Insertion Device."""

    class DEVICES:
        """Device names."""

        EPU50_10SB = 'SI-10SB:ID-EPU50'
        ALL = (EPU50_10SB, )

    PROPERTIES_DEFAULT = PAPU._properties + (
        'EnblPwrAll-Cmd',
        'PwrGap-Mon',
        'Status-Mon',
        'EnblAndReleaseGap-Sel', 'EnblAndReleaseGap-Sts',
        'AllowedToChangeGap-Mon',
        'ParkedGap-Cte', 'IsBusy-Mon',
        'Gap-SP', 'Gap-RB', 'Gap-Mon',
        'GapSpeed-SP', 'GapSpeed-RB', 'GapSpeed-Mon',
        'MaxGapSpeed-SP', 'MaxGapSpeed-RB',
        'ChangeGap-Cmd', 'Stop-Cmd',
        )

    def __init__(self, devname=None, props2init='all', auto_monitor_mon=True):
        """."""
        # check if device exists
        if devname is None:
            devname = self.DEVICES.EPU50_10SB
        if devname not in EPU.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)

    @property
    def status(self):
        """ID status."""
        return self['Status-Mon']

    # --- gap speeds ----

    @property
    def gap_parked(self):
        """Return ID parked gap value [mm]."""
        return self['ParkedGap-Cte']

    @property
    def gap_speed(self):
        """Return gap speed readback [mm/s]."""
        return self['GapSpeed-RB']

    @property
    def gap_speed_mon(self):
        """Return gap speed monitor [mm/s]."""
        return self['GapSpeed-Mon']

    @property
    def gap_speed_max(self):
        """Return max gap speed readback [mm/s]."""
        return self['MaxGapSpeed-RB']

    @property
    def gap_speed_max_lims(self):
        """Return max gap speed limits."""
        ctrl = self.pv_ctrlvars('MaxGapSpeed-SP')
        lims = [ctrl['lower_ctrl_limit'], ctrl['upper_ctrl_limit']]
        return lims

    # --- gap ---

    @property
    def gap(self):
        """Return ID gap readback [mm]."""
        return self['Gap-RB']

    @property
    def gap_min(self):
        """Return ID gap lower control limit [mm]."""
        ctrlvars = self.pv_ctrlvars('Gap-SP')
        return ctrlvars['lower_ctrl_limit']

    @property
    def gap_max(self):
        """Return ID gap upper control limit [mm]."""
        ctrlvars = self.pv_ctrlvars('Gap-SP')
        return ctrlvars['upper_ctrl_limit']

    @property
    def gap_mon(self):
        """Return ID gap monitor [mm]."""
        return self['Gap-Mon']

    # --- drive checks ---

    @property
    def is_gap_drive_powered(self):
        """Return gap driver power state on (True|False)."""
        return self['PwrGap-Mon'] != 0

    @property
    def is_drives_powered(self):
        """Return phase & gap drives powered state on (True|False)."""
        return self.is_phase_drive_powered and self.is_gap_drive_powered

    # --- movement checks ---

    @property
    def is_move_gap_enabled(self):
        """Return gap movement enabled state (True|False)."""
        return self['AllowedToChangeGap-Mon'] != 0

    @property
    def is_move_enabled(self):
        """Return phase and gap movements enabled state (True|False)."""
        return self.is_move_phase_enabled and self.is_move_gap_enabled

    @property
    def is_homing(self):
        """Return whether ID is in homing procedure."""
        return False

    # --- other checks ---

    @property
    def is_busy(self):
        """Return is busy state (True|False)."""
        return self['IsBusy-Mon'] != 0

    # --- cmd_beamline and cmd_drive

    def cmd_drive_turn_power_on(self, timeout=None):
        """Command turn phase and gap drives on."""
        if self.is_phase_drive_powered and self.is_gap_drive_powered:
            return True
        self['EnblPwrAll-Cmd'] = 1
        props_values = {'PwrPhase-Mon': 1, 'PwrGap-Mon': 1}
        return self._wait_propty_values(props_values, timeout=timeout)

    # --- set methods ---

    def set_gap(self, gap, timeout=None):
        """Command to set ID target gap for movement [mm]."""
        return self._write_sp('Gap-SP', gap, timeout)

    def set_gap_speed(self, gap_speed, timeout=None):
        """Command to set ID cruise gap speed for movement [mm/s]."""
        return self._write_sp('GapSpeed-SP', gap_speed, timeout)

    def set_gap_speed_max(self, gap_speed_max, timeout=None):
        """Command to set ID max cruise gap speed for movement [mm/s]."""
        return self._write_sp('MaxGapSpeed-SP', gap_speed_max, timeout)

    # --- cmd_move disable/enable ---

    def cmd_move_gap_enable(self, timeout=None):
        """Command to release and enable ID gap movement."""
        self['EnblAndReleaseGap-Sel'] = 1
        return super()._wait(
            'AllowedToChangeGap-Mon',
            1, timeout=timeout, comp='eq')

    def cmd_move_gap_disable(self, timeout=None):
        """Command to disable and break ID gap movement."""
        self['EnblAndReleaseGap-Sel'] = 0
        return super()._wait(
            'AllowedToChangeGap-Mon',
            0, timeout=timeout, comp='eq')

    def cmd_move_enable(self, timeout=None):
        """Command to release and enable ID phase and gap movements."""
        success = True
        success &= self.cmd_move_phase_enable(timeout=timeout)
        success &= self.cmd_move_gap_enable(timeout=timeout)
        return success

    def cmd_move_disable(self, timeout=None):
        """Command to disable and break ID phase and gap movements."""
        success = True
        success &= self.cmd_move_phase_disable(timeout=timeout)
        success &= self.cmd_move_gap_disable(timeout=timeout)
        return success

    # --- cmd_wait

    def wait_while_busy(self, timeout=None):
        """Command wait within timeout while ID control is busy."""
        timeout = timeout or self._DEF_TIMEOUT
        time_init = _time.time()
        while self.is_busy:
            _time.sleep(min(self._SHORT_SHUT_EYE, timeout))
            if _time.time() - time_init > timeout:
                return False
        return True

    # -- cmd_move

    def cmd_move_start(self, timeout=None):
        """Command to start movement."""
        success = True
        success &= self.cmd_move_gap_start(timeout=timeout)
        success &= self.cmd_move_phase_start(timeout=timeout)
        return success

    def cmd_move_gap_start(self, timeout=None):
        """Command to start gap movement."""
        return self._move_start('ChangeGap-Cmd', timeout=timeout)

    def cmd_move_park(self, timeout=None):
        """Command to set and start ID movement to parked config."""
        return self.move(
            self.phase_parked, self.gap_parked, timeout=timeout)

    def move(self, phase, gap, timeout=None):
        """Command to set and start phase and gap movements."""
        # calc ETA
        dtime_phase = abs(phase - self.phase_mon) / self.phase_speed
        dtime_gap = abs(gap - self.gap_mon) / self.gap_speed
        dtime_max = max(dtime_phase, dtime_gap)

        # additional percentual in ETA
        tol_gap = 0.01  # [mm]
        tol_phase = 0.01  # [mm]
        tol_dtime = 300  # [%]
        tol_factor = (1 + tol_dtime/100)
        tol_total = tol_factor * dtime_max + 5

        # set target phase and gap
        if not self.set_phase(phase=phase, timeout=timeout):
            return False
        if not self.set_gap(gap=gap, timeout=timeout):
            return False

        # command move start
        if not self.cmd_move_phase_start(timeout=timeout):
            return False
        if not self.cmd_move_gap_start(timeout=timeout):
            return False

        # wait for movement within reasonable time
        time_init = _time.time()
        while \
                abs(self.gap_mon - gap) > tol_gap or \
                abs(self.phase_mon - phase) > tol_phase or \
                self.is_moving:
            if _time.time() - time_init > tol_total:
                print(f'tol_total: {tol_total:.3f} s')
                print(f'wait_time: {_time.time() - time_init:.3f} s')
                print()
                return False
            _time.sleep(self._SHORT_SHUT_EYE)

        # successfull movement at this point
        return True

    # --- other cmds ---

    def cmd_clear_error(self):
        """Command to clear errors."""
        pass


class DELTA(_ID):
    """DELTA Insertion Device."""

    class DEVICES:
        """Device names."""

        DELTA52_10SB = 'SI-10SB:ID-DELTA52'
        ALL = (DELTA52_10SB, )

    PROPERTIES_DEFAULT = _ID.PROPERTIES_DEFAULT + (
        'Pol-Sel', 'Pol-Sts', 'Pol-Mon',
        'ChangePol-Cmd',
        'MaxVelo-SP', 'MaxVelo-RB',
        'ParkedPparameter-Cte',
        'PParam-SP', 'PParam-RB', 'PParam-Mon',
        'PParamVelo-SP', 'PParamVelo-RB',
        'PParamAcc-SP', 'PParamAcc-RB',
        'ParkedKparameter-Cte',
        'KParam-SP', 'KParam-RB', 'KParam-Mon',
        'KParamVelo-SP', 'KParamVelo-RB',
        'KParamAcc-SP', 'KParamAcc-RB',
        )

    def __init__(self, devname=None, props2init='all', auto_monitor_mon=True):
        """."""
        # check if device exists
        if devname is None:
            devname = self.DEVICES.DELTA52_10SB
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)

    # --- polarization ---

    @property
    def polarization(self):
        """Return ID polarization."""
        return self['Pol-Sts']

    @polarization.setter
    def polarization(self, value):
        """Set ID polarization."""
        self['Pol-Sel'] = value

    @property
    def polarization_mon(self):
        """Return ID polarization monitor."""
        return self['Pol-Mon']

    # --- pparameter ---

    @property
    def pparameter_parked(self):
        """Return ID parked pparameter value [mm]."""
        return self['ParkedPparameter-Cte']

    @property
    def pparameter_speed_max(self):
        """Return max pparameter speed readback [mm/s]."""
        return self['MaxVelo-RB']

    @property
    def pparameter_speed_max_lims(self):
        """Return max pparameter speed limits."""
        ctrl = self.pv_ctrlvars('MaxVelo-SP')
        lims = [ctrl['lower_ctrl_limit'], ctrl['upper_ctrl_limit']]
        return lims

    @property
    def pparameter_speed(self):
        """Return pparameter speed readback [mm/s]."""
        return self['PParamVelo-RB']

    @property
    def pparameter_lims(self):
        """Return ID pparameter lower control limit [mm]."""
        ctrl = self.pv_ctrlvars('PParam-Mon')
        return [ctrl['lower_ctrl_limit'], ctrl['upper_ctrl_limit']]

    @property
    def pparameter(self):
        """Return ID pparameter readback [mm]."""
        return self['KParam-RB']

    @property
    def pparameter_mon(self):
        """Return ID pparameter monitor [mm]."""
        return self['PParam-Mon']

    def set_pparameter(self, kparam, timeout=None):
        """Set ID target pparameter for movement [mm]."""
        return self._write_sp('PParam-SP', kparam, timeout)

    def set_pparameter_speed(self, pparam_speed, timeout=None):
        """Command to set ID cruise pparam speed for movement [mm/s]."""
        return self._write_sp('PParamVelo-SP', pparam_speed, timeout)

    def set_pparameter_speed_max(self, pparam_speed_max, timeout=None):
        """Command to set ID max cruise pparam speed for movement [mm/s]."""
        return self._write_sp('MaxVelo-SP', pparam_speed_max, timeout)

    # --- kparameter ---

    @property
    def kparameter_parked(self):
        """Return ID parked kparameter value [mm]."""
        return self['ParkedKparameter-Cte']

    @property
    def kparameter_speed_max(self):
        """Return max kparameter speed readback [mm/s]."""
        return self['MaxVelo-RB']

    @property
    def kparameter_speed_max_lims(self):
        """Return max kparameter speed limits."""
        ctrl = self.pv_ctrlvars('MaxVelo-SP')
        lims = [ctrl['lower_ctrl_limit'], ctrl['upper_ctrl_limit']]
        return lims

    @property
    def kparameter_speed(self):
        """Return kparameter speed readback [mm/s]."""
        return self['KParamVelo-RB']

    @property
    def kparameter_lims(self):
        """Return ID kparameter lower control limit [mm]."""
        ctrl = self.pv_ctrlvars('KParam-Mon')
        return [ctrl['lower_ctrl_limit'], ctrl['upper_ctrl_limit']]

    @property
    def kparameter(self):
        """Return ID kparameter readback [mm]."""
        return self['KParam-RB']

    @property
    def kparameter_mon(self):
        """Return ID kparameter monitor [mm]."""
        return self['KParam-Mon']

     # --- set methods ---

    def set_kparameter(self, kparam, timeout=None):
        """Command to set ID target kparameter for movement [mm]."""
        return self._write_sp('KParam-SP', kparam, timeout)

    def set_kparameter_speed(self, kparam_speed, timeout=None):
        """Command to set ID cruise kparam speed for movement [mm/s]."""
        return self._write_sp('KParamVelo-SP', kparam_speed, timeout)

    def set_kparameter_speed_max(self, kparam_speed_max, timeout=None):
        """Command to set ID max cruise kparam speed for movement [mm/s]."""
        return self._write_sp('MaxVelo-SP', kparam_speed_max, timeout)

    # --- commands ---

    def cmd_move_start(self, timeout=None):
        """Command to start movement."""
        success = True
        success &= self.cmd_move_pparam_start(timeout=timeout)
        success &= self.cmd_move_kparam_start(timeout=timeout)
        return success

    def cmd_move_pparam_start(self, timeout=None):
        """Command to start Pparameter movement."""
        return self._move_start('ChangePparam-Cmd', timeout=timeout)

    def cmd_move_kparam_start(self, timeout=None):
        """Command to start Kparameter movement."""
        return self._move_start('ChangeKparam-Cmd', timeout=timeout)

    def cmd_change_polarization_start(self, timeout=None):
        """Change polarization."""
        _ = timeout
        self['ChangePol-Cmd'] = 1

    def cmd_move_park(self, timeout=None):
        """Move ID to parked config."""
        return self.move(
            self.pparameter_parked, self.kparameter_parked, timeout=timeout)

    def move(self, pparam, kparam, timeout=None):
        """Command to set and start pparam and kparam movements."""
        # calc ETA
        dtime_phase = abs(pparam - self.pparameter_mon) / self.pparameter_speed
        dtime_gap = abs(kparam - self.kparameter_mon) / self.kparameter_speed
        dtime_max = max(dtime_phase, dtime_gap)

        # additional percentual in ETA
        tol_gap = 0.01  # [mm]
        tol_phase = 0.01  # [mm]
        tol_dtime = 300  # [%]
        tol_factor = (1 + tol_dtime/100)
        tol_total = tol_factor * dtime_max + 5

        # set target phase and gap
        if not self.set_pparameter(phase=pparam, timeout=timeout):
            return False
        if not self.set_kparameter(gap=kparam, timeout=timeout):
            return False

        # command move start
        if not self.cmd_move_pparam_start(timeout=timeout):
            return False
        if not self.cmd_move_kparam_start(timeout=timeout):
            return False

        # wait for movement within reasonable time
        time_init = _time.time()
        while \
                abs(self.kparameter_mon - kparam) > tol_gap or \
                abs(self.pparameter_mon - pparam) > tol_phase or \
                self.is_moving:
            if _time.time() - time_init > tol_total:
                print(f'tol_total: {tol_total:.3f} s')
                print(f'wait_time: {_time.time() - time_init:.3f} s')
                print()
                return False
            _time.sleep(self._SHORT_SHUT_EYE)

        # successfull movement at this point
        return True

    def change_polarization(self, polarization, timeout=None):
        """."""
        t0_ = _time.time()
        # set desired polarization
        if not self._write_sp('Pol-Sel', polarization, timeout=timeout):
            return False
        # send change polarization command
        self['ChangePol-Cmd'] = 1
        timeout -= _time.time() - t0_
        # wait for polarization value within timeout
        return self._wait('Pol-Mon', polarization, timeout=timeout, comp='eq')


class WIG(_Device):
    """Wiggler Insertion Device."""

    class DEVICES:
        """Device names."""

        WIG180_14SB = 'SI-14SB:ID-WIG180'
        ALL = (WIG180_14SB, )

    # NOTE: IOC yet to be written!
    PROPERTIES_DEFAULT = ('Gap-SP', 'Gap-RB', 'Gap-Mon')

    def __init__(self, devname=None, props2init='all', auto_monitor_mon=True):
        """."""
        # check if device exists
        if devname is None:
            devname = self.DEVICES.WIG180_14SB
        if devname not in WIG.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)
