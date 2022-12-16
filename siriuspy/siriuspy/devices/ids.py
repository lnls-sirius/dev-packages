"""Define Insertion Devices."""

import time as _time
import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from ..namesys import SiriusPVName as _SiriusPVName
from ..search import IDSearch as _IDSearch
from ..magnet.idffwd import APUFFWDCalc as _APUFFWDCalc

from .device import Device as _Device
from .device import Devices as _Devices
from .device import DeviceApp as _DeviceApp
from .psconv import StrengthConv as _StrengthConv


class APU(_Device):
    """Insertion Device APU."""

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


class EPU(_Device):
    """."""

    class DEVICES:
        """."""

        EPU50_10SB = 'SI-10SB:ID-EPU50'
        ALL = (EPU50_10SB, )

    _idparam_fields = (
        'PERIOD',  # [mm]
        'PHASE_REFERENCE',  # [mm]
        'GAP_REFERENCE',  # [mm]
        )

    _dev2params = {
        DEVICES.EPU50_10SB:
            _get_namedtuple('IDParameters',
                _idparam_fields, (50.0, 0, 300.0)),
        }

    _short_shut_eye = 0.1  # [s]
    _default_timeout = 5  # [s]

    _properties = (
        'BeamLineCtrlEnbl-Sel', 'BeamLineCtrlEnbl-Sts',
        'EnblPwrAll-Cmd', 'PwrPhase-Mon', 'PwrGap-Mon',
        'EnblAndReleasePhase-Sel', 'EnblAndReleasePhase-Sts',
        'AllowedToChangePhase-Mon',
        'EnblAndReleaseGap-Sel', 'EnblAndReleaseGap-Sts',
        'AllowedToChangeGap-Mon',
        'Phase-SP', 'Phase-RB', 'Phase-Mon',
        'PhaseSpeed-SP', 'PhaseSpeed-RB', 'PhaseSpeed-Mon',
        'MaxPhaseSpeed-SP', 'MaxPhaseSpeed-RB',
        'ChangePhase-Cmd',
        'Gap-SP', 'Gap-RB', 'Gap-Mon',
        'GapSpeed-SP', 'GapSpeed-RB', 'GapSpeed-Mon',
        'MaxGapSpeed-SP', 'MaxGapSpeed-RB',
        'ChangeGap-Cmd',
        'Stop-Cmd', 'Moving-Mon', 'IsBusy-Mon',
        )

    def __init__(self, devname):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in EPU.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=EPU._properties, auto_mon=True)

    @property
    def parameters(self):
        """Return EPU parameters."""
        return EPU._dev2params[self.devname]

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
    def phase(self):
        """Return EPU phase readback [mm]."""
        return self['Phase-RB']

    @property
    def phase_min(self):
        """Return EPU phase lower control limit [mm]."""
        ctrlvars = self.pv_ctrlvars('Phase-SP')
        return ctrlvars['lower_ctrl_limit']

    @property
    def phase_max(self):
        """Return EPU phase upper control limit [mm]."""
        ctrlvars = self.pv_ctrlvars('Phase-SP')
        return ctrlvars['upper_ctrl_limit']

    @property
    def phase_mon(self):
        """Return EPU phase monitor [mm]."""
        return self['Phase-Mon']

    @property
    def gap(self):
        """Return EPU gap readback [mm]."""
        return self['Gap-RB']

    @property
    def gap_min(self):
        """Return EPU gap lower control limit [mm]."""
        ctrlvars = self.pv_ctrlvars('Gap-SP')
        return ctrlvars['lower_ctrl_limit']

    @property
    def gap_max(self):
        """Return EPU gap upper control limit [mm]."""
        ctrlvars = self.pv_ctrlvars('Gap-SP')
        return ctrlvars['upper_ctrl_limit']

    @property
    def gap_mon(self):
        """Return EPU gap monitor [mm]."""
        return self['Gap-Mon']

    @property
    def is_phase_drive_powered(self):
        """Return phase driver power state on (True|False)."""
        return self['PwrPhase-Mon'] != 0

    @property
    def is_gap_drive_powered(self):
        """Return gap driver power state on (True|False)."""
        return self['PwrGap-Mon'] != 0

    @property
    def is_drives_powered(self):
        """Return phase & gap drives powered state on (True|False)."""
        return self.is_phase_drive_powered and self.is_gap_drive_powered

    @property
    def is_move_phase_enabled(self):
        """Return phase movement enabled state (True|False)."""
        return self['AllowedToChangePhase-Mon'] != 0

    @property
    def is_move_gap_enabled(self):
        """Return gap movement enabled state (True|False)."""
        return self['AllowedToChangeGap-Mon'] != 0

    @property
    def is_move_enabled(self):
        """Return phase and gap movements enabled state (True|False)."""
        return self.is_move_phase_enabled and self.is_move_gap_enabled

    @property
    def is_moving(self):
        """Return is moving state (True|False)."""
        return self['Moving-Mon'] != 0

    @property
    def is_busy(self):
        """Return is busy state (True|False)."""
        return self['IsBusy-Mon'] != 0

    @property
    def is_beamline_ctrl_enabled(self):
        """Return beamline control enabled state (True|False)."""
        return self['BeamLineCtrlEnbl-Sts'] != 0

    # --- cmd_wait

    def cmd_wait_while_busy(self, timeout=None):
        """Command wait within timeout while EPU control is busy."""
        timeout = timeout or self._default_timeout
        time_init = _time.time()
        while self.is_busy:
            _time.sleep(min(EPU._short_shut_eye, timeout))
            if _time.time() - time_init > timeout:
                return False
        return True

    # --- cmd_beamline and cmd_drive

    def cmd_drive_turn_on(self, timeout=None):
        """Command turn phase and gap drives on."""
        if self.is_phase_drive_powered and self.is_gap_drive_powered:
            return True
        self['EnblPwrAll-Cmd'] = 1
        props_values = {
            'PwrPhase-Mon': 0,  # value compared to in 'not equal' operation
            'PwrGap-Mon': 0,  # value compared to in 'not equal' operation
            }
        return self._wait(props_values, timeout=timeout, comp='ne')

    def cmd_beamline_ctrl_enable(self, timeout=None):
        """Command enable bealine EPU control."""
        return self._set_sp('BeamLineCtrlEnbl-Sel', 1, timeout)

    def cmd_beamline_ctrl_disable(self, timeout=None):
        """Command disable bealine EPU control."""
        return self._set_sp('BeamLineCtrlEnbl-Sel', 0, timeout)

    # --- cmd_set ---

    def cmd_set_phase(self, phase, timeout=None):
        """Command to set EPU target phase for movement [mm]."""
        return self._set_sp('Phase-SP', phase, timeout)

    def cmd_set_gap(self, gap, timeout=None):
        """Command to set EPU target gap for movement [mm]."""
        return self._set_sp('Gap-SP', gap, timeout)

    def cmd_set_phase_speed(self, phase_speed, timeout=None):
        """Command to set EPU cruise phase speed for movement [mm/s]."""
        return self._set_sp('PhaseSpeed-SP', phase_speed, timeout)

    def cmd_set_gap_speed(self, gap_speed, timeout=None):
        """Command to set EPU cruise gap speed for movement [mm/s]."""
        return self._set_sp('GapSpeed-SP', gap_speed, timeout)

    def cmd_set_phase_speed_max(self, phase_speed_max, timeout=None):
        """Command to set EPU max cruise phase speed for movement [mm/s]."""
        return self._set_sp('MaxPhaseSpeed-SP', phase_speed_max, timeout)

    def cmd_set_gap_speed_max(self, gap_speed_max, timeout=None):
        """Command to set EPU max cruise gap speed for movement [mm/s]."""
        return self._set_sp('MaxGapSpeed-SP', gap_speed_max, timeout)

    # --- cmd_move disable/enable ---

    # TODO: not working. IOC with Sel/Sts PVs that are not consistent!

    def cmd_move_phase_enable(self, timeout=None):
        """Command to release and enable EPU phase movement."""
        # return self._set_sp('EnblAndReleasePhase-Sel', 1, timeout)
        self['EnblAndReleasePhase-Sel'] = 1
        return True

    def cmd_move_phase_disable(self, timeout=None):
        """Command to disable and break EPU phase movement."""
        # return self._set_sp('EnblAndReleasePhase-Sel', 0, timeout)
        self['EnblAndReleasePhase-Sel'] = 0
        return True

    def cmd_move_gap_enable(self, timeout=None):
        """Command to release and enable EPU gap movement."""
        # return self._set_sp('EnblAndReleaseGap-Sel', 1, timeout)
        self['EnblAndReleaseGap-Sel'] = 1
        return True

    def cmd_move_gap_disable(self, timeout=None):
        """Command to disable and break EPU gap movement."""
        # return self._set_sp('EnblAndReleaseGap-Sel', 0, timeout)
        self['EnblAndReleaseGap-Sel'] = 1
        return True

    def cmd_move_enable(self, timeout=None):
        """Command to release and enable EPU phase and gap movements."""
        success = True
        success &= self.cmd_move_phase_enable(timeout=timeout)
        success &= self.cmd_move_gap_enable(timeout=timeout)
        return success

    def cmd_move_disable(self, timeout=None):
        """Command to disable and break EPU phase and gap movements."""
        success = True
        success &= self.cmd_move_phase_disable(timeout=timeout)
        success &= self.cmd_move_gap_disable(timeout=timeout)
        return success

    # -- cmd_move

    def cmd_move_stop(self, timeout=None):
        """Command to interrupt and then enable phase and gap movements."""
        timeout = timeout or self._default_timeout

        # wait for not busy state
        if self.cmd_wait_while_busy(timeout=timeout):
            return False

        # send stop command
        self['Stop-Cmd'] = 1

        # check for successful stop
        if self.cmd_wait_while_busy(timeout=timeout):
            return False
        success = True
        success &= super()._wait('Moving-Mon', 0, tiemout=timeout)
        success &= super()._wait('IsBusy-Mon', 0, tiemout=timeout)
        if not success:
            return False

        # enable movement again
        return self.cmd_move_enable(timeout=timeout)

    def cmd_move_phase_start(self, timeout=None):
        """Command to start phase movement."""
        return self._move_start('ChangePhase-Cmd', timeout=timeout)

    def cmd_move_gap_start(self, timeout=None):
        """Command to start gap movement."""
        return self._move_start('ChangeGap-Cmd', timeout=timeout)

    def cmd_move(self, phase, gap, timeout=None):
        """Command to set and start phase and gap movements."""
        # calc ETA
        dtime_phase = abs(phase - self.phase) / self.phase_speed
        dtime_gap = abs(gap - self.gap) / self.gap_speed
        dtime_max = max(dtime_phase, dtime_gap)

        # additional percentual in ETA
        dtime_tol = 40  # [%]
        tol_factor = (1 + dtime_tol/100)

        # set target phase and gap
        self.cmd_set_phase(phase=phase, timeout=timeout)
        self.cmd_set_gap(gap=gap, timeout=timeout)

        # command move start
        if not self.cmd_move_phase_start(timeout=timeout):
            return False
        if not self.cmd_move_gap_start(timeout=timeout):
            return False

        # wait for movement within reasonable time
        time_init = _time.time()
        while self.is_moving:
            if _time.time() - time_init > tol_factor * dtime_max:
                return False
            _time.sleep(EPU._short_shut_eye)

        # successfull movement at this point
        return True

    def cmd_move_park(self, timeout=None):
        """Command to set and start EPU movement reference config."""
        params = self.parameters
        return self.cmd_move(
            params.PHASE_REFERENCE, params.GAP_REFERENCE, timeout=timeout)

    # --- cmd_reset

    def cmd_reset(self, timeout=None):
        """Command to reset EPU to a standard movement state."""
        success = True
        success &= self.cmd_beamline_ctrl_disable(timeout=timeout)
        success &= self.cmd_drive_turn_on(timeout=timeout)
        success &= self.cmd_move_enable(timeout=timeout)
        return success

    # --- private methods ---

    def _move_start(self, cmd_propty, timeout=None):
        """."""
        timeout = timeout or self._default_timeout

        # wait for not busy state
        if self.cmd_wait_while_busy(timeout=timeout):
            return False

        # send move command
        self[cmd_propty] = 1

        return True

    def _set_sp(self, propties_sp, values, timeout=None):
        timeout = timeout or self._default_timeout
        if isinstance(propties_sp, str):
            propties_sp = (propties_sp, )
            values = (values, )
        success = True
        for propty_sp, value in zip(propties_sp, values):
            if value == self[propty_sp]:
                continue
            if not self.cmd_wait_while_busy(timeout=timeout):
                return False
            self[propty_sp] = value
            propty_rb = propty_sp.replace('-SP', '-RB').replace('-Sel', '-Sts')
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


class IDCorrectors(_DeviceApp):
    """."""

    DEVICES = APU.DEVICES

    def __init__(self, devname):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in IDCorrectors.DEVICES.ALL:
            raise NotImplementedError(devname)

        # get correctors names
        self._psnames_orb = _IDSearch.conv_idname_2_orbitcorr(devname)

        # get deviceapp properties
        properties, \
            self._orb_sp, self._orb_rb, self._orb_refmon, self._orb_mon = \
            self._get_properties()

        # call base class constructor
        super().__init__(properties=properties, devname=devname)

    @property
    def orbitcorr_psnames(self):
        """Return orbit corrector names."""
        return self._psnames_orb

    @property
    def orbitcorr_current(self):
        """Return orbit SOFBCurrent Mon."""
        return self[self._orb_mon]

    @orbitcorr_current.setter
    def orbitcorr_current(self, value):
        """Set orbit SOFBCurrent SP."""
        self[self._orb_sp] = value

    @property
    def orbitcorr_current_sp(self):
        """Return orbit SOFBCurrent setpoint."""
        return self[self._orb_sp]

    @property
    def orbitcorr_current_rb(self):
        """Return orbit SOFBCurrent readback."""
        return self[self._orb_rb]

    @property
    def orbitcorr_current_mon(self):
        """Return orbit SOFBCurrent monitor."""
        return self[self._orb_mon]

    def _get_properties(self):
        corrname = self._psnames_orb[0]
        orb_sp = corrname + ':SOFBCurrent-SP'
        orb_rb = corrname + ':SOFBCurrent-RB'
        orb_refmon = corrname + ':SOFBCurrentRef-Mon'
        orb_mon = corrname + ':SOFBCurrent-Mon'
        properties = (
            orb_sp, orb_rb, orb_refmon, orb_mon
        )
        return properties, orb_sp, orb_rb, orb_refmon, orb_mon


class APUFeedForward(_Devices):
    """Insertion Device APU FeedForward."""

    DEVICES = APU.DEVICES

    def __init__(self, devname):
        """."""
        # create APU device
        self._apu = APU(devname)

        # create IDCorrectors
        self._idcorrs = IDCorrectors(devname)

        # create FFWDCalc
        self._ffwdcalc = _APUFFWDCalc(devname)

        # create normalizers
        self._strenconv_chs, self._strenconv_cvs = self._create_strenconv()

        # call base class constructor
        devices = (
            self._apu, self._idcorrs,
            self._strenconv_chs, self._strenconv_cvs)
        super().__init__(devname, devices)

        # bumps
        self._posx, self._angx, self._posy, self._angy = \
            self._init_posang()

    @property
    def apu(self):
        """Return APU device."""
        return self._apu

    @property
    def correctors(self):
        """Return IDCorrectors device."""
        return self._idcorrs

    @property
    def ffwdcalc(self):
        """."""
        return self._ffwdcalc

    @property
    def posx(self):
        """Return posx bump value."""
        return self._posx

    @posx.setter
    def posx(self, value):
        """Return posx bump value."""
        self._posx = value

    @property
    def angx(self):
        """Return angx bump value."""
        return self._angx

    @angx.setter
    def angx(self, value):
        """Return angx bump value."""
        self._angx = value

    @property
    def posy(self):
        """Return posy bump value."""
        return self._posy

    @posy.setter
    def posy(self, value):
        """Return posy bump value."""
        self._posy = value

    @property
    def angy(self):
        """Return angy bump value."""
        return self._angy

    @angy.setter
    def angy(self, value):
        """Return angy bump value."""
        self._angy = value

    def conv_orbitcorr_kick2curr(self, kicks):
        """."""
        # 127 µs ± 1.01 µs per loop
        kickx = kicks[:self.ffwdcalc.nr_chs]
        kicky = kicks[self.ffwdcalc.nr_chs:]
        curr_chs = self._strenconv_chs.conv_strength_2_current(kickx)
        curr_cvs = self._strenconv_cvs.conv_strength_2_current(kicky)
        currs = _np.hstack((curr_chs, curr_cvs))
        return currs

    def bump_get_orbitcorr_current(self):
        """Return bump orbit correctors currents."""
        kicks = self.ffwdcalc.conv_posang2kick(
            self.posx, self.angx, self.posy, self.angy)
        currents = self.conv_orbitcorr_kick2curr(kicks)
        return currents

    def ffwd_get_orbitcorr_current(self, phase=None):
        """Return feedforward orbitcorr currents for a given ID phase."""
        # 157 µs ± 3.93 µs per loop [if phase is passed]
        if phase is None:
            phase = self.apu.phase
        currents = self.ffwdcalc.conv_phase_2_orbcorr_currents(phase)
        return currents

    def ffwd_update_orbitcorr(self, phase=None):
        """Update orbit feedforward."""
        currents_ffwd = self.ffwd_get_orbitcorr_current(phase)
        currents_bump = self.bump_get_orbitcorr_current()
        self.correctors.orbitcorr_current = currents_ffwd + currents_bump

    def ffwd_update(self, phase=None):
        """Update feedforward with bump."""
        # 305 µs ± 45.5 µs per loop
        self.ffwd_update_orbitcorr(phase)

    # --- private methods ---

    def _init_posang(self):
        _ = self  # throaway arguments (temporary)
        posx, angx = 0.0, 0.0
        posy, angy = 0.0, 0.0
        # NOTE: we could initialize posang with corrector values.
        return posx, angx, posy, angy

    def _create_strenconv(self):
        """."""
        psnames = self.correctors.orbitcorr_psnames

        maname = psnames[0].replace(':PS-', ':MA-')
        strenconv_chs = _StrengthConv(
            maname, proptype='Ref-Mon', auto_mon=True)
        maname = psnames[self.ffwdcalc.nr_chs].replace(':PS-', ':MA-')
        strenconv_cvs = _StrengthConv(
            maname, proptype='Ref-Mon', auto_mon=True)

        return strenconv_chs, strenconv_cvs
