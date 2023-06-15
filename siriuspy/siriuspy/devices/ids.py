"""Define Insertion Devices."""

import time as _time
import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from ..namesys import SiriusPVName as _SiriusPVName

from .device import Device as _Device


class APU(_Device):
    """APU Insertion Device."""

    class DEVICES:
        """."""

        APU22_06SB = 'SI-06SB:ID-APU22'
        APU22_07SP = 'SI-07SP:ID-APU22'
        APU22_08SB = 'SI-08SB:ID-APU22'
        APU22_09SA = 'SI-09SA:ID-APU22'
        APU58_11SP = 'SI-11SP:ID-APU58'
        ALL = (APU22_06SB, APU22_07SP, APU22_08SB, APU22_09SA,
               APU58_11SP, )

    _properties = (
        'DevCtrl-Cmd', 'Moving-Mon',
        'PhaseSpeed-SP', 'PhaseSpeed-Mon',
        'Phase-SP', 'Phase-Mon',
        'Kx-SP', 'Kx-Mon',
    )

    _DEF_TIMEOUT = 10  # [s]
    _CMD_MOVE = 3
    _MOVECHECK_SLEEP = 0.1  # [s]

    def __init__(self, devname):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in APU.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=APU._properties, auto_mon=True)

    @property
    def phase(self):
        """Return APU phase [mm]."""
        return self['Phase-Mon']

    @phase.setter
    def phase(self, value):
        """Set APU phase [mm]."""
        self['Phase-SP'] = value

    @property
    def phase_sp(self):
        """Return APU phase SP [mm]."""
        return self['Phase-SP']

    @property
    def phase_speed(self):
        """Return APU phase speed [mm/s]."""
        return self['PhaseSpeed-Mon']

    @phase_speed.setter
    def phase_speed(self, value):
        """Set APU phase_speed [mm/s]."""
        self['PhaseSpeed-SP'] = value

    @property
    def phase_speed_sp(self):
        """Return APU phase speed SP [mm/s]."""
        return self['PhaseSpeed-SP']

    @property
    def idkx(self):
        """Return APU Kx."""
        return self['Kx-SP']

    @idkx.setter
    def idkx(self, value):
        """Set APU Kx."""
        self['Kx-SP'] = value

    @property
    def is_moving(self):
        """Return True if phase is changing."""
        return round(self['Moving-Mon']) == 1

    def cmd_move(self, timeout=_DEF_TIMEOUT):
        """."""
        self['DevCtrl-Cmd'] = APU._CMD_MOVE
        return True

    def wait_move(self):
        """Wait for phase movement to complete."""
        _time.sleep(APU._MOVECHECK_SLEEP)
        while self.is_moving:
            _time.sleep(APU._MOVECHECK_SLEEP)


class PAPU(_Device):
    """PAPU Insertion Device."""

    class DEVICES:
        """."""

        PAPU50_17SA = 'SI-17SA:ID-PAPU50'
        ALL = (PAPU50_17SA, )

    _SHORT_SHUT_EYE = 0.1  # [s]
    _default_timeout = 8  # [s]

    _properties_papu = (
        'Home-Cmd', 'EnblPwrPhase-Cmd', 'ClearErr-Cmd',
        'BeamLineCtrl-Mon', 'Home-Mon',
        )
    _properties = (
        'PeriodLength-Cte',
        'BeamLineCtrlEnbl-Sel', 'BeamLineCtrlEnbl-Sts',
        'Moving-Mon',
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


    def __init__(self, devname, properties=None, auto_mon=True):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        properties = properties or self._properties + self._properties_papu
        super().__init__(devname, properties=properties, auto_mon=auto_mon)

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
        """."""
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
        """Return whether ID is in homing procedure."""
        return self['Home-Mon']

    @property
    def is_beamline_ctrl_enabled(self):
        """Return beamline control enabled state (True|False)."""
        return self['BeamLineCtrlEnbl-Sts'] != 0

    # --- cmd_beamline and cmd_drive

    def cmd_drive_turn_power_on(self, timeout=None):
        """Command turn phase drive on."""
        if self.is_phase_drive_powered:
            return True
        self['EnblPwrPhase-Cmd'] = 1
        props_values = {'PwrPhase-Mon': 1}
        return self._wait(props_values, timeout=timeout)

    def cmd_beamline_ctrl_enable(self, timeout=None):
        """Command enable bealine ID control."""
        return self._write_sp('BeamLineCtrlEnbl-Sel', 1, timeout)

    def cmd_beamline_ctrl_disable(self, timeout=None):
        """Command disable bealine ID control."""
        return self._write_sp('BeamLineCtrlEnbl-Sel', 0, timeout)

    # --- cmd_set ---

    def cmd_set_phase(self, phase, timeout=None):
        """Command to set ID target phase for movement [mm]."""
        return self._write_sp('Phase-SP', phase, timeout)

    def cmd_set_phase_speed(self, phase_speed, timeout=None):
        """Command to set ID cruise phase speed for movement [mm/s]."""
        return self._write_sp('PhaseSpeed-SP', phase_speed, timeout)

    def cmd_set_phase_speed_max(self, phase_speed_max, timeout=None):
        """Command to set ID max cruise phase speed for movement [mm/s]."""
        return self._write_sp('MaxPhaseSpeed-SP', phase_speed_max, timeout)

    # --- cmd_move disable/enable ---

    def cmd_move_phase_enable(self, timeout=None):
        """Command to release and enable ID phase movement."""
        return self._write_sp('EnblAndReleasePhase-Sel', 1, timeout)

    def cmd_move_phase_disable(self, timeout=None):
        """Command to disable and break ID phase movement."""
        return self._write_sp('EnblAndReleasePhase-Sel', 0, timeout)

    def cmd_move_enable(self, timeout=None):
        """Command to release and enable ID phase and gap movements."""
        return self.cmd_move_phase_enable(timeout=timeout)

    def cmd_move_disable(self, timeout=None):
        """Command to disable and break ID phase and gap movements."""
        return self.cmd_move_phase_disable(timeout=timeout)

    # -- cmd_move

    def cmd_move_stop(self, timeout=None):
        """Command to interrupt and then enable phase movements."""
        timeout = timeout or self._default_timeout

        # wait for not busy state
        if not self.cmd_wait_while_busy(timeout=timeout):
            return False

        # send stop command
        self.cmd_move_disable()

        # check for successful stop
        if not self.cmd_wait_while_busy(timeout=timeout):
            return False
        success = True
        success &= super()._wait('Moving-Mon', 0, timeout=timeout)
        if not success:
            return False

        # enable movement again
        return self.cmd_move_enable(timeout=timeout)

    def cmd_move_phase_start(self, timeout=None):
        """Command to start phase movement."""
        return self._move_start('ChangePhase-Cmd', timeout=timeout)

        """Command to start gap movement."""
        return self._move_start('ChangeGap-Cmd', timeout=timeout)

    def cmd_move(self, phase, timeout=None):
        """Command to set and start phase movements."""
        # calc ETA
        dtime_max = abs(phase - self.phase_mon) / self.phase_speed

        # additional percentual in ETA
        tol_phase = 0.01  # [mm]
        tol_dtime = 300  # [%]
        tol_factor = (1 + tol_dtime/100)
        tol_total = tol_factor * dtime_max + 5

        # set target phase and gap
        if not self.cmd_set_phase(phase=phase, timeout=timeout):
            return False

        # command move start
        if not self.cmd_move_phase_start(timeout=timeout):
            return False

        # wait for movement within reasonable time
        time_init = _time.time()
        while \
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

    def cmd_move_park(self, timeout=None):
        """Command to set and start ID movement to parked config."""
        return self.cmd_move(self.phase_parked, timeout=timeout)

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
        """."""
        self['ClearErr-Cmd'] = 1

    # --- private methods ---

    def _move_start(self, cmd_propty, timeout=None):
        """."""
        timeout = timeout or self._default_timeout

        # wait for not busy state
        if not self.cmd_wait_while_busy(timeout=timeout):
            return False

        # send move command
        self[cmd_propty] = 1

        return True

    def _write_sp(self, propties_sp, values, timeout=None):
        timeout = timeout or self._default_timeout
        if isinstance(propties_sp, str):
            propties_sp = (propties_sp, )
            values = (values, )
        success = True
        for propty_sp, value in zip(propties_sp, values):
            propty_rb = propty_sp.replace('-SP', '-RB').replace('-Sel', '-Sts')
            # if self[propty_rb] == value:
            #     continue
            if not self.cmd_wait_while_busy(timeout=timeout):
                return False
            self[propty_sp] = value
            success &= super()._wait(
                propty_rb, value, timeout=timeout, comp='eq')
        return success

    def _wait(self, props_values, timeout=None, comp='eq'):
        timeout = timeout or self._default_timeout
        success = True
        for propty, value in props_values.items():
            success &= super()._wait(
                propty, value, timeout=timeout, comp=comp)
        return success


class EPU(PAPU):
    """EPU Insertion Device."""

    class DEVICES:
        """."""

        EPU50_10SB = 'SI-10SB:ID-EPU50'
        ALL = (EPU50_10SB, )

    _properties = PAPU._properties + (
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

    def __init__(self, devname):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in EPU.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=self._properties, auto_mon=True)

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
        """."""
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
        return self._wait(props_values, timeout=timeout)

    # --- cmd_set ---

    def cmd_set_gap(self, gap, timeout=None):
        """Command to set ID target gap for movement [mm]."""
        return self._write_sp('Gap-SP', gap, timeout)

    def cmd_set_gap_speed(self, gap_speed, timeout=None):
        """Command to set ID cruise gap speed for movement [mm/s]."""
        return self._write_sp('GapSpeed-SP', gap_speed, timeout)

    def cmd_set_gap_speed_max(self, gap_speed_max, timeout=None):
        """Command to set ID max cruise gap speed for movement [mm/s]."""
        return self._write_sp('MaxGapSpeed-SP', gap_speed_max, timeout)

    # --- cmd_move disable/enable ---

    def cmd_move_gap_enable(self, timeout=None):
        """Command to release and enable ID gap movement."""
        return self._write_sp('EnblAndReleaseGap-Sel', 1, timeout)

    def cmd_move_gap_disable(self, timeout=None):
        """Command to disable and break ID gap movement."""
        return self._write_sp('EnblAndReleaseGap-Sel', 0, timeout)

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

    def cmd_wait_while_busy(self, timeout=None):
        """Command wait within timeout while ID control is busy."""
        timeout = timeout or self._default_timeout
        time_init = _time.time()
        while self.is_busy:
            _time.sleep(min(self._SHORT_SHUT_EYE, timeout))
            if _time.time() - time_init > timeout:
                return False
        return True

    # -- cmd_move

    def cmd_move_gap_start(self, timeout=None):
        """Command to start gap movement."""
        return self._move_start('ChangeGap-Cmd', timeout=timeout)

    def cmd_move(self, phase, gap, timeout=None):
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
        if not self.cmd_set_phase(phase=phase, timeout=timeout):
            return False
        if not self.cmd_set_gap(gap=gap, timeout=timeout):
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
            _time.sleep(EPU._SHORT_SHUT_EYE)

        # successfull movement at this point
        return True

    def cmd_move_park(self, timeout=None):
        """Command to set and start ID movement to parked config."""
        return self.cmd_move(
            self.phase_parked, self.gap_parked, timeout=timeout)

    # --- other cmds ---

    def cmd_clear_error(self):
        """."""
        pass


class WIG(_Device):
    """Wiggler Insertion Device."""

    class DEVICES:
        """."""
        WIG180_14SB = 'SI-14SB:ID-WIG180'
        ALL = (WIG180_14SB, )

    # NOTE: IOC yet to be written!
    _properties = (
        'Gap-SP', 'Gap-RB', 'Gap-Mon',
    )

    def __init__(self, devname):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in WIG.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=WIG._properties, auto_mon=True)
