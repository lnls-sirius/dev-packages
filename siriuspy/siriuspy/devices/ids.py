"""Define Insertion Devices."""

import time as _time
import inspect as _inspect

from ..search import IDSearch as _IDSearch

from .device import Device as _Device


class _PARAM_PVS:
    """."""

    # --- GENERAL ---
    PERIOD_LEN_CTE = None
    START_PARKING_CMD = None
    IS_MOVING = 'Moving-Mon'
    BLCTRL_ENBL_SEL = 'BeamLineCtrlEnbl-Sel'
    BLCTRL_ENBL_STS = 'BeamLineCtrlEnbl-Sts'
    MOVE_ABORT = None

    # --- PPARAM ---
    PPARAM_SP = None
    PPARAM_RB = None
    PPARAM_MON = None
    PPARAM_PARKED_CTE = None
    PPARAM_MAXVELO_SP = None
    PPARAM_MAXVELO_RB = None
    PPARAM_VELO_SP = None
    PPARAM_VELO_RB = None
    PPARAM_VELO_MON = None
    PPARAM_TOL_SP = None
    PPARAM_TOL_RB = None
    PPARAM_CHANGE_CMD = None

    # --- KPARAM ---
    KPARAM_SP = None
    KPARAM_RB = None
    KPARAM_MON = None
    KPARAM_PARKED_CTE = None
    KPARAM_MAXVELO_SP = None
    KPARAM_MAXVELO_RB = None
    KPARAM_VELO_SP = None
    KPARAM_VELO_RB = None
    KPARAM_VELO_MON = None
    KPARAM_TOL_SP = None
    KPARAM_TOL_RB = None
    KPARAM_CHANGE_CMD = None

    # --- POL ---
    POL_SEL = None
    POL_STS = None
    POL_MON = None
    POL_CHANGE_CMD = None

    def __str__(self):
        """Print parameters."""
        str_ = ''
        strf = '{}: {}'
        for key, value in _inspect.getmembers(self):
            if not key.startswith('_') and value is not None:
                lstr = strf.format(key, value)
                str_ += lstr if str_ == '' else '\n' + lstr
        return str_


class _ID(_Device):
    """Generic Insertion Device."""

    _SHORT_SHUT_EYE = 0.1  # [s]
    _DEF_TIMEOUT = 8  # [s]

    PARAM_PVS = _PARAM_PVS()

    PROPERTIES_DEFAULT = \
        tuple(set(value for key, value in _inspect.getmembers(PARAM_PVS) \
            if not key.startswith('_') and value is not None))

    def __init__(self, devname, props2init='all', auto_monitor_mon=True):
        """."""
        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)
        self._pols_sel_str = \
            _IDSearch.conv_idname_2_polarizations(self.devname)
        self._pols_sts_str = \
            _IDSearch.conv_idname_2_polarizations_sts(self.devname)

    # --- general ---

    @property
    def parameters(self):
        """Return ID parameters."""
        return _IDSearch.conv_idname_2_parameters(self.devname)

    @property
    def period_length(self):
        """Return ID period length [mm]."""
        if self.PARAM_PVS.PERIOD_LEN_CTE in self.properties_all:
            return self[self.PARAM_PVS.PERIOD_LEN_CTE]
        else:
            return self.parameters.PERIOD_LENGTH

    # --- polarization ---

    @property
    def polarization(self):
        """Return ID polarization."""
        if self.PARAM_PVS.POL_STS in self.properties_all:
            return self[self.PARAM_PVS.POL_STS]
        else:
            if _IDSearch.POL_UNDEF_STR in self._pols_sts_str:
                return self._pols_sts_str.index(_IDSearch.POL_UNDEF_STR)
            else:
                return None

    @property
    def polarization_str(self):
        """Return ID polarization string."""
        pol_idx = self.polarization
        if pol_idx is None:
            return None
        else:
            return self._pols_sts_str[pol_idx]

    @polarization.setter
    def polarization(self, value):
        """Set ID polarization."""
        if self.PARAM_PVS.POL_SEL in self.properties_all:
            if isinstance(value, str):
                value = self._pols_sel_str.index(value)
            self[self.PARAM_PVS.POL_SEL] = value

    @property
    def polarization_mon(self):
        """Return ID polarization monitor."""
        if self.PARAM_PVS.POL_MON in self.properties_all:
            return self[self.PARAM_PVS.POL_MON]
        else:
            return None

    @property
    def polarization_mon_str(self):
        """Return ID polarization string."""
        pol_idx = self.polarization_mon
        if pol_idx is None:
            return None
        else:
            return self._pols_sts_str[pol_idx]

    # --- pparameter ---

    @property
    def pparameter_tol(self):
        """PParameter position tolerance [mm]."""
        if self.PARAM_PVS.PPARAM_TOL_RB is None:
            return self.parameters.PPARAM_TOL
        else:
            return self[self.PARAM_PVS.PPARAM_TOL_RB]

    @property
    def pparameter_parked(self):
        """Return ID parked pparameter value [mm]."""
        if self.PARAM_PVS.PPARAM_PARKED_CTE in self.properties_all:
            return self[self.PARAM_PVS.PPARAM_PARKED_CTE]
        else:
            return self.parameters.PPARAM_PARKED

    @property
    def pparameter_speed_max(self):
        """Return max pparameter speed readback [mm/s]."""
        if self.PARAM_PVS.PPARAM_MAXVELO_RB is None:
            return None
        else:
            return self[self.PARAM_PVS.PPARAM_MAXVELO_RB]

    @property
    def pparameter_speed_max_lims(self):
        """Return max pparameter speed limits."""
        if self.PARAM_PVS.PPARAM_MAXVELO_RB is None:
            return None
        else:
            ctrl = self.pv_ctrlvars(self.PARAM_PVS.PPARAM_MAXVELO_SP)
            lims = [ctrl['lower_ctrl_limit'], ctrl['upper_ctrl_limit']]
            return lims

    @property
    def pparameter_speed(self):
        """Return pparameter speed readback [mm/s]."""
        if self.PARAM_PVS.PPARAM_VELO_RB is None:
            return None
        else:
            return self[self.PARAM_PVS.PPARAM_VELO_SP]

    @property
    def pparameter_lims(self):
        """Return ID pparameter lower control limit [mm]."""
        if self.PARAM_PVS.PPARAM_VELO_SP is None:
            return None
        else:
            ctrl = self.pv_ctrlvars(self.PARAM_PVS.PPARAM_SP)
            return [ctrl['lower_ctrl_limit'], ctrl['upper_ctrl_limit']]

    @property
    def pparameter(self):
        """Return ID pparameter readback [mm]."""
        if self.PARAM_PVS.PPARAM_RB is None:
            return None
        else:
            return self[self.PARAM_PVS.PPARAM_RB]

    @property
    def pparameter_mon(self):
        """Return ID pparameter monitor [mm]."""
        if self.PARAM_PVS.PPARAM_MON is None:
            return None
        else:
            return self[self.PARAM_PVS.PPARAM_MON]

    def pparameter_set(self, pparam, timeout=None):
        """Set ID target pparameter for movement [mm]."""
        if self.PARAM_PVS.PPARAM_SP is None:
            return True
        else:
            return self._write_sp(self.PARAM_PVS.PPARAM_SP, pparam, timeout)

    def pparameter_speed_set(self, pparam_speed, timeout=None):
        """Command to set ID cruise pparameterspeed for movement [mm/s]."""
        if self.PARAM_PVS.PPARAM_VELO_SP is None:
            return True
        else:
            return self._write_sp(
                self.PARAM_PVS.PPARAM_VELO_SP, pparam_speed, timeout)

    def pparameter_speed_max_set(self, pparam_speed_max, timeout=None):
        """Command to set ID max cruise pparam speed for movement [mm/s]."""
        if self.PARAM_PVS.PPARAM_MAXVELO_SP is None:
            return True
        else:
            return self._write_sp(
                self.PARAM_PVS.PPARAM_MAXVELO_SP, pparam_speed_max, timeout)

    # --- kparameter ---

    @property
    def kparameter_tol(self):
        """KParameter position tolerance [mm]."""
        if self.PARAM_PVS.KPARAM_TOL_RB is None:
            return self.parameters.KPARAM_TOL
        else:
            return self[self.PARAM_PVS.KPARAM_TOL_RB]

    @property
    def kparameter_parked(self):
        """Return ID parked kparameter value [mm]."""
        if self.PARAM_PVS.KPARAM_PARKED_CTE in self.properties_all:
            return self[self.PARAM_PVS.KPARAM_PARKED_CTE]
        else:
            return self.parameters.KPARAM_PARKED

    @property
    def kparameter_speed_max(self):
        """Return max kparameter speed readback [mm/s]."""
        return self[self.PARAM_PVS.KPARAM_MAXVELO_RB]

    @property
    def kparameter_speed_max_lims(self):
        """Return max kparameter speed limits."""
        ctrl = self.pv_ctrlvars(self.PARAM_PVS.KPARAM_MAXVELO_SP)
        lims = [ctrl['lower_ctrl_limit'], ctrl['upper_ctrl_limit']]
        return lims

    @property
    def kparameter_speed(self):
        """Return kparameter speed readback [mm/s]."""
        return self[self.PARAM_PVS.KPARAM_VELO_SP]

    @property
    def kparameter_speed_mon(self):
        """Return kparameter speed monitor [mm/s]."""
        if self.PARAM_PVS.KPARAM_VELO_MON in self.properties_all:
            return self[self.PARAM_PVS.KPARAM_VELO_MON]
        else:
            raise TypeError('ID does not have speed_mon PV!')

    @property
    def kparameter_lims(self):
        """Return ID kparameter control limits [mm]."""
        ctrl = self.pv_ctrlvars(self.PARAM_PVS.KPARAM_SP)
        return [ctrl['lower_ctrl_limit'], ctrl['upper_ctrl_limit']]

    @property
    def kparameter(self):
        """Return ID kparameter readback [mm]."""
        return self[self.PARAM_PVS.KPARAM_RB]

    @property
    def kparameter_mon(self):
        """Return ID kparameter monitor [mm]."""
        return self[self.PARAM_PVS.KPARAM_MON]

    def kparameter_set(self, kparam, timeout=None):
        """Set ID target kparameter for movement [mm]."""
        return self._write_sp(self.PARAM_PVS.KPARAM_SP, kparam, timeout)

    def kparameter_speed_set(self, kparam_speed, timeout=None):
        """Command to set ID cruise kparam speed for movement [mm/s]."""
        return self._write_sp(
            self.PARAM_PVS.KPARAM_VELO_SP, kparam_speed, timeout)

    def kparameter_speed_max_set(self, kparam_speed_max, timeout=None):
        """Command to set ID max cruise kparam speed for movement [mm/s]."""
        return self._write_sp(
            self.PARAM_PVS.KPARAM_MAXVELO_SP, kparam_speed_max, timeout)

    # --- checks ---

    @property
    def is_moving(self):
        """Return True if phase is changing."""
        return round(self['Moving-Mon']) == 1

    @property
    def is_beamline_ctrl_enabled(self):
        """Return beamline control enabled state (True|False)."""
        return self['BeamLineCtrlEnbl-Sts'] != 0

    # --- cmd_beamline and cmd_drive

    def cmd_beamline_ctrl_enable(self, timeout=None):
        """Command enable bealine ID control."""
        return self._write_sp('BeamLineCtrlEnbl-Sel', 1, timeout)

    def cmd_beamline_ctrl_disable(self, timeout=None):
        """Command disable bealine ID control."""
        return self._write_sp('BeamLineCtrlEnbl-Sel', 0, timeout)

    # --- wait

    def wait_while_busy(self, timeout=None):
        """Command wait within timeout while ID control is busy."""
        return True

    def wait_move_start(self, timeout=None):
        """Wait for movement to start."""
        return self._wait('Moving-Mon', 1, timeout)

    def wait_move_finish(self, timeout=None):
        """Wait for movement to finish."""
        return self._wait('Moving-Mon', 0, timeout)

    def wait_move_config(self, pparam, kparam, timeout):
        """."""
        tol_kparam, tol_pparam = self.kparameter_tol, self.pparameter_tol
        # wait for movement within reasonable time
        time_init = _time.time()
        while True:
            k_pos_ok = True if kparam is None else \
                abs(abs(self.kparameter_mon) - abs(kparam)) <= tol_kparam
            p_pos_ok = True if pparam is None else \
                abs(self.pparameter_mon - pparam) <= tol_pparam
            if p_pos_ok and k_pos_ok and not self.is_moving:
                return True
            if _time.time() - time_init > timeout:
                print(f'tol_total: {timeout:.3f} s')
                print(f'wait_time: {_time.time() - time_init:.3f} s')
                print()
                return False
            _time.sleep(self._SHORT_SHUT_EYE)

    # --- cmd_move ---

    def cmd_move_disable(self):
        """Command to disable and break ID movements."""
        return True

    def cmd_move_enable(self):
        """Command to enable ID movements."""
        return True

    def cmd_move_abort(self):
        """."""
        if self.PARAM_PVS.MOVE_ABORT is not None:
            self[self.PARAM_PVS.MOVE_ABORT] = 1

    def cmd_move_stop(self, timeout=None):
        """Command to interrupt and then enable phase movements."""
        timeout = timeout or self._DEF_TIMEOUT

        # wait for not busy state
        if not self.wait_while_busy(timeout=timeout):
            return False

        # send abort command
        self.cmd_move_abort()

        # send disable command
        self.cmd_move_disable()

        # check for successful stop
        if not self.wait_while_busy(timeout=timeout):
            return False
        if not self.wait_move_finish(timeout=timeout):
            return False

        # enable movement again
        if not self.cmd_move_enable():
            return False

        return True

    def cmd_move_start(self, timeout=None):
        """Command to start movement."""
        success = True
        success &= self.cmd_move_pparameter_start(timeout=timeout)
        success &= self.cmd_move_kparameter_start(timeout=timeout)
        return success

    def cmd_move_pparameter_start(self, timeout=None):
        """Command to start Pparameter movement."""
        return self._move_start(
            self.PARAM_PVS.PPARAM_CHANGE_CMD, timeout=timeout)

    def cmd_move_kparameter_start(self, timeout=None):
        """Command to start Kparameter movement."""
        return self._move_start(
            self.PARAM_PVS.KPARAM_CHANGE_CMD, timeout=timeout)

    def cmd_change_polarization_start(self, timeout=None):
        """Change polarization."""
        return self._move_start(
            self.PARAM_PVS.POL_CHANGE_CMD, timeout=timeout)

    def cmd_move_park(self, timeout=None):
        """Move ID to parked config."""
        pparam, kparam = self.pparameter_parked, self.kparameter_parked
        timeout = self._calc_eta(pparam, kparam) if timeout is None \
            else timeout
        if self.PARAM_PVS.START_PARKING_CMD is not None:
            self[self.PARAM_PVS.START_PARKING_CMD] = 1
            return self.wait_move_config(pparam, kparam, timeout)
        else:
            return self.cmd_move(pparam, kparam, timeout)

    def cmd_move_pparameter(self, pparam=None, timeout=None):
        """Command to set and start pparam movement."""
        pparam = self.pparameter if pparam is None else pparam
        return self.cmd_move(pparam, None, timeout)

    def cmd_move_kparameter(self, kparam=None, timeout=None):
        """Command to set and start kparam movement."""
        kparam = self.kparameter if kparam is None else kparam
        return self.cmd_move(None, kparam, timeout)

    def cmd_move(self, pparam=None, kparam=None, timeout=None):
        """Command to set and start pparam and kparam movements."""
        if self.PARAM_PVS.PPARAM_SP is None:
            pparam = None

        # set target pparam and kparam
        t0_ = _time.time()
        if pparam is not None and \
                not self.pparameter_set(pparam, timeout=timeout):
            return False
        if kparam is not None and \
                not self.kparameter_set(kparam, timeout=timeout):
            return False
        t1_ = _time.time()
        if timeout is not None:
            timeout = max(timeout - (t1_ - t0_), 0)

        # command move start
        t0_ = _time.time()
        if pparam is not None and \
                not self.cmd_move_pparameter_start(timeout=timeout):
            return False
        if kparam is not None and \
                not self.cmd_move_kparameter_start(timeout=timeout):
            return False
        t1_ = _time.time()
        if timeout is not None:
            timeout = max(timeout - (t1_ - t0_), 0)

        # calc ETA
        eta = self._calc_eta(pparam, kparam)
        timeout = eta if timeout is None else timeout

        # wait for movement within reasonable time
        return self.wait_move_config(pparam, kparam, timeout)

    def cmd_change_polarization(self, polarization, timeout=None):
        """."""
        if self.PARAM_PVS.POL_SEL not in self.properties_all:
            return True
        if self.PARAM_PVS.POL_MON not in self.properties_all:
            return True

        t0_ = _time.time()

        # set desired polarization
        if not self._write_sp(
                self.PARAM_PVS.POL_SEL, polarization, timeout=timeout):
            return False
        t1_ = _time.time()
        timeout = max(0, timeout - (t1_ - t0_))

        # send change polarization command
        if not self.cmd_change_polarization_start(timeout=timeout):
            return False
        t2_ = _time.time()
        timeout = max(0, timeout - (t2_ - t0_))

        # wait for polarization value within timeout
        return self._wait(
            self.PARAM_PVS.POL_MON, polarization, timeout=timeout, comp='eq')

    # --- private methods ---

    def _move_start(self, cmd_propty, timeout=None, cmd_value=1):
        timeout = timeout or self._DEF_TIMEOUT

        # wait for not busy state
        if not self.wait_while_busy(timeout=timeout):
            return False

        if cmd_propty in self.properties_all:
            # send move command
            self[cmd_propty] = cmd_value

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
            if isinstance(value, float):
                success &= super()._wait_float(
                    propty_rb, value, timeout=timeout)
            else:
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

    def _calc_eta(self, pparam, kparam):
        """."""
        # calc ETA
        dtime_kparam = 0 if kparam is None else \
            abs(kparam - self.kparameter_mon) / self.kparameter_speed
        dtime_pparam = 0 if pparam is None else \
            abs(pparam - self.pparameter_mon) / self.pparameter_speed
        dtime_max = self._calc_eta_select_time(dtime_kparam, dtime_pparam)
        # additional percentual in ETA
        eta = 1.5 * dtime_max + 5
        return eta

    @staticmethod
    def _calc_eta_select_time(dtime_kparam, dtime_pparam):
        return dtime_kparam + dtime_pparam


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

    _CMD_MOVE_STOP, _CMD_MOVE_START = 1, 3
    _CMD_MOVE = 3

    # --- PARAM_PVS ---
    PARAM_PVS = _PARAM_PVS()
    PARAM_PVS.KPARAM_SP = 'Phase-SP'
    PARAM_PVS.KPARAM_RB = 'Phase-SP'  # There is no Phase-RB!
    PARAM_PVS.KPARAM_MON = 'Phase-Mon'
    PARAM_PVS.KPARAM_MAXVELO_SP = 'MaxPhaseSpeed-SP'
    PARAM_PVS.KPARAM_MAXVELO_RB = 'MaxPhaseSpeed-RB'
    PARAM_PVS.KPARAM_VELO_SP = 'PhaseSpeed-SP'
    PARAM_PVS.KPARAM_VELO_RB = 'PhaseSpeed-SP'
    PARAM_PVS.KPARAM_VELO_MON = 'PhaseSpeed-Mon'
    PARAM_PVS.KPARAM_CHANGE_CMD = 'DevCtrl-Cmd'

    PROPERTIES_DEFAULT = \
        tuple(set(value for key, value in _inspect.getmembers(PARAM_PVS) \
            if not key.startswith('_') and value is not None))

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
    def phase_speed_max(self):
        """Return max phase speed readback [mm/s]."""
        return self.kparameter_speed_max

    @property
    def phase_speed_max_lims(self):
        """Return max phase speed limits."""
        return self.kparameter_speed_max_lims

    @property
    def phase_speed(self):
        """Return phase speed [mm/s]."""
        return self.kparameter_speed

    @property
    def phase_speed_mon(self):
        """Return phase speed monitor [mm/s]."""
        return self.kparameter_speed_mon

    # --- phase ---

    @property
    def phase_parked(self):
        """Return ID parked phase value [mm]."""
        return self.kparameter_parked

    @property
    def phase_lims(self):
        """Return ID phase lower control limit [mm]."""
        return self.kparameter_lims

    @property
    def phase(self):
        """Return APU phase [mm]."""
        return self.kparameter

    @property
    def phase_mon(self):
        """Return APU phase [mm]."""
        return self.kparameter_mon

    # --- set methods ---

    def phase_set(self, phase, timeout=None):
        """Command to set ID target phase for movement [mm]."""
        return self.kparameter_set(phase, timeout)

    def phase_speed_set(self, phase_speed, timeout=None):
        """Command to set ID cruise phase speed for movement [mm/s]."""
        return self.kparameter_speed_set(phase_speed, timeout)

    def phase_speed_max_set(self, phase_speed_max, timeout=None):
        """Command to set ID max cruise phase speed for movement [mm/s]."""
        return self._write_sp('MaxPhaseSpeed-SP', phase_speed_max, timeout)

    # -- cmd_move

    def cmd_move_stop(self, timeout=None):
        """Send command to stop ID movement."""
        self['DevCtrl-Cmd'] = self._CMD_MOVE_STOP
        return True

    # --- private methods ---

    def _write_sp(self, propties_sp, values, timeout=None):
        pvs_sp_rb = ('Phase-SP', 'PhaseSpeed-SP')
        return super()._write_sp(
            propties_sp, values, timeout=timeout, pvs_sp_rb=pvs_sp_rb)

    def _move_start(
            self, cmd_propty, timeout=None, cmd_value=_CMD_MOVE_START):
        return super()._move_start(cmd_propty, timeout, cmd_value)


class PAPU(_ID):
    """PAPU Insertion Device."""

    class DEVICES:
        """Device names."""

        PAPU50_17SA = 'SI-17SA:ID-PAPU50'
        ALL = (PAPU50_17SA, )

    # --- PARAM_PVS ---
    PARAM_PVS = _PARAM_PVS()
    PARAM_PVS.PERIOD_LEN_CTE = 'PeriodLength-Cte'
    PARAM_PVS.KPARAM_SP = 'Phase-SP'
    PARAM_PVS.KPARAM_RB = 'Phase-RB'
    PARAM_PVS.KPARAM_MON = 'Phase-Mon'
    PARAM_PVS.KPARAM_PARKED_CTE = 'ParkedPhase-Cte'
    PARAM_PVS.KPARAM_MAXVELO_SP = 'MaxPhaseSpeed-SP'
    PARAM_PVS.KPARAM_MAXVELO_RB = 'MaxPhaseSpeed-RB'
    PARAM_PVS.KPARAM_VELO_SP = 'PhaseSpeed-SP'
    PARAM_PVS.KPARAM_VELO_RB = 'PhaseSpeed-RB'
    PARAM_PVS.KPARAM_VELO_MON = 'PhaseSpeed-Mon'
    PARAM_PVS.KPARAM_CHANGE_CMD = 'ChangePhase-Cmd'

    _properties = (
        'PwrPhase-Mon',
        'EnblAndReleasePhase-Sel', 'EnblAndReleasePhase-Sts',
        'AllowedToChangePhase-Mon',
        'StopPhase-Cmd', 'Log-Mon',
        )
    _properties_papu = (
        'Home-Cmd', 'EnblPwrPhase-Cmd', 'ClearErr-Cmd',
        'BeamLineCtrl-Mon',
        )

    PROPERTIES_DEFAULT = \
        tuple(set(value for key, value in _inspect.getmembers(PARAM_PVS) \
            if not key.startswith('_') and value is not None)) + \
        _properties + _properties_papu

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
    def log_mon(self):
        """Return ID Log."""
        return self['Log-Mon']

    # --- phase speeds ----

    @property
    def phase_speed_max(self):
        """Return max phase speed readback [mm/s]."""
        return self.kparameter_speed_max

    @property
    def phase_speed_max_lims(self):
        """Return max phase speed limits."""
        return self.kparameter_speed_max_lims

    @property
    def phase_speed(self):
        """Return phase speed readback [mm/s]."""
        return self.kparameter_speed

    @property
    def phase_speed_mon(self):
        """Return phase speed monitor [mm/s]."""
        return self.kparameter_speed_mon

    # --- phase ---

    @property
    def phase_parked(self):
        """Return ID parked phase value [mm]."""
        return self.kparameter_parked

    @property
    def phase_lims(self):
        """Return ID phase limits [mm]."""
        return self.kparameter_lims

    @property
    def phase(self):
        """Return ID phase readback [mm]."""
        return self.kparameter

    @property
    def phase_mon(self):
        """Return ID phase monitor [mm]."""
        return self.kparameter_mon

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
        return self[self.PARAM_PVS.IS_MOVING] != 0

    @property
    def is_homing(self):
        """Return whether ID is in homing procedure (True|False)."""
        return self['Home-Mon'] != 0

    # --- cmd_drive

    def cmd_drive_turn_power_on(self, timeout=None):
        """Command turn phase drive on."""
        if self.is_phase_drive_powered:
            return True
        self['EnblPwrPhase-Cmd'] = 1
        props_values = {'PwrPhase-Mon': 1}
        return self._wait_propty_values(props_values, timeout=timeout)

    # --- set methods ---

    def phase_set(self, phase, timeout=None):
        """Command to set ID target phase for movement [mm]."""
        return self.kparameter_set(phase, timeout)

    def phase_speed_set(self, phase_speed, timeout=None):
        """Command to set ID cruise phase speed for movement [mm/s]."""
        return self.kparameter_speed_set(phase_speed, timeout)

    def phase_speed_max_set(self, phase_speed_max, timeout=None):
        """Command to set ID max cruise phase speed for movement [mm/s]."""
        return self.kparameter_speed_max_set(phase_speed_max, timeout)

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

    # -- cmd_move

    def cmd_move_phase_start(self, timeout=None):
        """Command to start phase movement."""
        return self.cmd_move_kparameter_start(timeout=timeout)

    # def cmd_move_park(self, timeout=None):
    #     """Command to set and start ID movement to parked config."""
    #     return super().cmd_move_park(timeout)

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


class EPU(PAPU):
    """EPU Insertion Device."""

    class DEVICES:
        """Device names."""

        EPU50_10SB = 'SI-10SB:ID-EPU50'
        ALL = (EPU50_10SB, )

    # --- PARAM_PVS ---
    PARAM_PVS = _PARAM_PVS()
    PARAM_PVS.PERIOD_LEN_CTE = 'PeriodLength-Cte'
    PARAM_PVS.IS_MOVING = 'IsMoving-Mon'
    PARAM_PVS.PPARAM_SP = 'Phase-SP'
    PARAM_PVS.PPARAM_RB = 'Phase-RB'
    PARAM_PVS.PPARAM_MON = 'Phase-Mon'
    PARAM_PVS.PPARAM_PARKED_CTE = 'ParkedPhase-Cte'
    PARAM_PVS.PPARAM_MAXVELO_SP = 'MaxPhaseSpeed-SP'
    PARAM_PVS.PPARAM_MAXVELO_RB = 'MaxPhaseSpeed-RB'
    PARAM_PVS.PPARAM_VELO_SP = 'PhaseSpeed-SP'
    PARAM_PVS.PPARAM_VELO_RB = 'PhaseSpeed-RB'
    PARAM_PVS.PPARAM_VELO_MON = 'PhaseSpeed-Mon'
    PARAM_PVS.PPARAM_CHANGE_CMD = 'ChangePhase-Cmd'
    PARAM_PVS.KPARAM_SP = 'Gap-SP'
    PARAM_PVS.KPARAM_RB = 'Gap-RB'
    PARAM_PVS.KPARAM_MON = 'Gap-Mon'
    PARAM_PVS.KPARAM_PARKED_CTE = 'ParkedGap-Cte'
    PARAM_PVS.KPARAM_MAXVELO_SP = 'MaxGapSpeed-SP'
    PARAM_PVS.KPARAM_MAXVELO_RB = 'MaxGapSpeed-RB'
    PARAM_PVS.KPARAM_VELO_SP = 'GapSpeed-SP'
    PARAM_PVS.KPARAM_VELO_RB = 'GapSpeed-RB'
    PARAM_PVS.KPARAM_VELO_MON = 'GapSpeed-Mon'
    PARAM_PVS.KPARAM_CHANGE_CMD = 'ChangeGap-Cmd'
    PARAM_PVS.POL_SEL = 'Polarization-Sel'
    PARAM_PVS.POL_STS = 'Polarization-Sts'
    PARAM_PVS.POL_MON = 'Polarization-Mon'
    PARAM_PVS.POL_CHANGE_CMD = 'ChangePolarization-Cmd'

    PROPERTIES_DEFAULT = PAPU._properties + \
        tuple(set(value for key, value in _inspect.getmembers(PARAM_PVS) \
            if not key.startswith('_') and value is not None)) + (
        'EnblPwrAll-Cmd', 'PwrGap-Mon', 'Status-Mon',
        'EnblAndReleaseGap-Sel', 'EnblAndReleaseGap-Sts',
        'AllowedToChangeGap-Mon',
        'IsBusy-Mon', 'Stop-Cmd',
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
    def gap_speed(self):
        """Return gap speed readback [mm/s]."""
        return self.kparameter_speed

    @property
    def gap_speed_mon(self):
        """Return gap speed monitor [mm/s]."""
        return self.kparameter_speed_mon

    @property
    def gap_speed_max(self):
        """Return max gap speed readback [mm/s]."""
        return self.kparameter_speed_max

    @property
    def gap_speed_max_lims(self):
        """Return max gap speed limits."""
        return self.kparameter_speed_max_lims

    # --- gap ---

    @property
    def gap_parked(self):
        """Return ID parked gap value [mm]."""
        return self.kparameter_parked

    @property
    def gap(self):
        """Return ID gap readback [mm]."""
        return self.kparameter

    @property
    def gap_lims(self):
        """Return ID gap control limits [mm]."""
        return self.kparameter_lims

    @property
    def gap_mon(self):
        """Return ID gap monitor [mm]."""
        return self.kparameter_mon

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
        return self._wait_set(props_values, timeout=timeout)

    # --- set methods ---

    def gap_set(self, gap, timeout=None):
        """Set ID target gap for movement [mm]."""
        return self.kparameter_set(gap, timeout)

    def gap_speed_set(self, gap_speed, timeout=None):
        """Set ID cruise gap speed for movement [mm/s]."""
        return self.kparameter_speed_set(gap_speed, timeout)

    def gap_speed_max_set(self, gap_speed_max, timeout=None):
        """Set ID max cruise gap speed for movement [mm/s]."""
        return self.kparameter_speed_max_set(gap_speed_max, timeout)

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

    def cmd_move_gap_start(self, timeout=None):
        """Command to start gap movement."""
        return self.cmd_move_kparameter_start(timeout)

    # --- other cmds ---

    def cmd_clear_error(self):
        """Command to clear errors."""
        pass

    # --- private methods ---

    @staticmethod
    def _calc_eta_select_time(dtime_kparam, dtime_pparam):
        return max(dtime_kparam, dtime_pparam)


class DELTA(_ID):
    """DELTA Insertion Device."""

    class DEVICES:
        """Device names."""

        DELTA52_10SB = 'SI-10SB:ID-DELTA52'
        ALL = (DELTA52_10SB, )

    # --- PARAM_PVS ---
    PARAM_PVS = _PARAM_PVS()
    PARAM_PVS.PERIOD_LEN_CTE = 'PeriodLength-Cte'
    PARAM_PVS.IS_MOVING = 'Moving-Mon'
    PARAM_PVS.START_PARKING_CMD = 'StartParking-Cmd'
    PARAM_PVS.MOVE_ABORT = 'Abort-Cmd'
    PARAM_PVS.PPARAM_SP = 'PParam-SP'
    PARAM_PVS.PPARAM_RB = 'PParam-RB'
    PARAM_PVS.PPARAM_MON = 'PParam-Mon'
    PARAM_PVS.PPARAM_PARKED_CTE = 'PParamParked-Cte'
    PARAM_PVS.PPARAM_MAXVELO_SP = 'MaxVelo-SP'
    PARAM_PVS.PPARAM_MAXVELO_RB = 'MaxVelo-RB'
    PARAM_PVS.PPARAM_VELO_SP = 'PParamVelo-SP'
    PARAM_PVS.PPARAM_VELO_RB = 'PParamVelo-RB'
    PARAM_PVS.PPARAM_TOL_SP = 'PolTol-SP'
    PARAM_PVS.PPARAM_TOL_RB = 'PolTol-RB'
    PARAM_PVS.PPARAM_CHANGE_CMD = 'PParamChange-Cmd'
    PARAM_PVS.KPARAM_SP = 'KParam-SP'
    PARAM_PVS.KPARAM_RB = 'KParam-RB'
    PARAM_PVS.KPARAM_MON = 'KParam-Mon'
    PARAM_PVS.KPARAM_PARKED_CTE = 'KParamParked-Cte'
    PARAM_PVS.KPARAM_MAXVELO_SP = 'MaxVelo-SP'
    PARAM_PVS.KPARAM_MAXVELO_RB = 'MaxVelo-RB'
    PARAM_PVS.KPARAM_VELO_SP = 'KParamVelo-SP'
    PARAM_PVS.KPARAM_VELO_RB = 'KParamVelo-RB'
    PARAM_PVS.KPARAM_TOL_SP = 'PosTol-SP'
    PARAM_PVS.KPARAM_TOL_RB = 'PosTol-RB'
    PARAM_PVS.KPARAM_CHANGE_CMD = 'KParamChange-Cmd'
    PARAM_PVS.POL_SEL = 'Pol-Sel'
    PARAM_PVS.POL_STS = 'Pol-Sts'
    PARAM_PVS.POL_MON = 'Pol-Mon'
    PARAM_PVS.POL_CHANGE_CMD = 'PolChange-Cmd'

    PROPERTIES_DEFAULT = tuple(set(
        value for key, value in _inspect.getmembers(PARAM_PVS)
        if not key.startswith('_') and value is not None))
    PROPERTIES_DEFAULT = PROPERTIES_DEFAULT + (
        'CSDVirtPos-Mon', 'CSEVirtPos-Mon',
        'CIEVirtPos-Mon', 'CIDVirtPos-Mon',
        'IsOperational-Mon', 'MotorsEnbld-Mon',
        'Alarm-Mon', 'Intlk-Mon', 'IntlkBits-Mon', 'IntlkLabels-Cte',
        'ConsistentSetPoints-Mon', 'PLCState-Mon',
        'Energy-SP', 'Energy-RB', 'Energy-Mon',
        'KValue-SP', 'KValue-RB', 'KValue-Mon',
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

    @property
    def is_operational(self):
        """Return True if ID is operational."""
        return self['IsOperational-Mon'] == 0  # 0 : 'OK'

    # --- cassette positions ---

    @property
    def pos_csd_mon(self):
        """Return longitudinal position of CSD [mm].

        cassette positions x (PParam, KParam):
            pos_cid = PParam
            pos_cse = PParam + KParam
            pos_csd = KParam
            pos_cie = 0
        """
        return self['CSDVirtPos-Mon']

    @property
    def pos_cse_mon(self):
        """Return longitudinal position of CSE [mm].

        cassette positions x (PParam, KParam):
            pos_cid = PParam
            pos_cse = PParam + KParam
            pos_csd = KParam
            pos_cie = 0
        """
        return self['CSEVirtPos-Mon']

    @property
    def pos_cie_mon(self):
        """Return longitudinal position of CIE [mm].

        cassette positions x (PParam, KParam):
            pos_cid = PParam
            pos_cse = PParam + KParam
            pos_csd = KParam
            pos_cie = 0
        """
        return self['CIEVirtPos-Mon']

    @property
    def pos_cid_mon(self):
        """Return longitudinal position of CID [mm].

        cassette positions x (PParam, KParam):
            pos_cid = PParam
            pos_cse = PParam + KParam
            pos_csd = KParam
            pos_cie = 0
        """
        return self['CIDVirtPos-Mon']

    def _calc_eta(self, pparam, kparam):
        """."""
        if kparam is not None and self.polarization_mon_str == 'circularp':
            kparam = -kparam
        return super()._calc_eta(pparam, kparam)


class WIG(_ID):
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
