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
        'PHASE_MIN',  # [mm]
        'PHASE_MAX',  # [mm]
        'PHASE_PARK',  # [mm]
        'GAP_MIN',   # [mm]
        'GAP_MAX',  # [mm]
        'GAP_PARK',  # [mm]
        )

    _dev2params = {
        DEVICES.EPU50_10SB :
            _get_namedtuple('IDParameters',
                _idparam_fields, (50.0, -50.0/4, 50/4, 0, 22.0, 300.0, 300.0)),
        }
                
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
        'Gap-SP', 'Gap-RB', 'Gap-Mon',
        'GapSpeed-SP', 'GapSpeed-RB', 'GapSpeed-Mon',
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
        """."""
        return EPU._dev2params[self.devname]

    @property
    def speed_phase(self):
        """Phase speed [mm/s]."""
        return self['PhaseSpeed-Mon']

    @speed_phase.setter
    def speed_phase(self, value):
        """[mm/s]."""
        self['PhaseSpeed-SP'] = value

    @property
    def speed_gap(self):
        """[mm/s]."""
        return self['GapSpeed-Mon']

    @speed_gap.setter
    def speed_gap(self, value):
        """[mm/s]."""
        self['GapSpeed-SP'] = value

    @property
    def phase(self):
        """[mm]."""
        return self['Phase-Mon']

    @phase.setter
    def phase(self, value):
        """[mm]."""
        self['Phase-Mon'] = value

    @property
    def gap(self):
        """[mm]."""
        return self['Gap-Mon']

    @gap.setter
    def gap(self, value):
        """[mm]."""
        self['Gap-Mon'] = value

    @property
    def is_drives_powered(self):
        """."""
        status = True
        status &= self['PwrPhase-Mon'] != 0
        status &= self['PwrGap-Mon'] != 0
        return status

    @property
    def is_move_enabled(self):
        """."""
        status = True
        status &= self['AllowedToChangePhase-Mon'] != 0
        status &= self['AllowedToChangeGap-Mon'] != 0
        return status

    @property
    def is_moving(self):
        """."""
        return self['Moving-Mon'] != 0

    @property
    def is_busy(self):
        """."""
        return self['IsBusy-Mon'] != 0

    @property
    def beamline_ctrl_enabled(self):
        """."""
        return self['BeamLineCtrlEnbl-Sts'] != 0

    def cmd_beamline_ctrl_disable(self, timeout):
        """."""
        props_values = {'BeamLineCtrlEnbl-Sel': 0}
        return self._set_and_wait(props_values, timeout=timeout, comp='eq')

    def cmd_beamline_ctrl_enable(self, timeout):
        """."""
        # value compared to in 'not equal' operation
        props_values = {'BeamLineCtrlEnbl-Sel': 0}
        return self._set_and_wait(props_values, timeout=timeout, comp='ne')

    def cmd_drive_turn_on(self, timeout=None):
        """."""
        self['EnblPwrAll-Cmd'] = 1
        props_values = {
            'PwrPhase-Mon': 0,  # value compared to in 'not equal' operation
            'PwrGap-Mon': 0,  # value compared to in 'not equal' operation
            }
        return self._set_and_wait(props_values, timeout=timeout, comp='ne')

    def cmd_move_enable(self, timeout=None):
        """."""
        return self._move_enable_or_disable(state=1, timeout=timeout)

    def cmd_move_disable(self, timeout=None):
        """."""
        return self._move_enable_or_disable(state=0, timeout=timeout)
        
    def cmd_reset(self, timeout=None):
        """."""
        success = True
        success &= self.cmd_beamline_ctrl_disable(timeout=timeout)
        success &= self.cmd_drive_turn_on(timeout=timeout)
        success &= self.cmd_move_enable(timeout=timeout)
        return success
        
    def cmd_move_stop(self, timeout=None):
        """."""
        self['Stop-Cmd'] = 1
        success = True
        props_values = {'Moving-Mon': 0}
        success = self._set_and_wait(props_values, timeout=timeout)
        # value compared to in 'not equal' operation
        props_values = {'isBusy-Mon': 0}
        success = self._set_and_wait(props_values, timeout=timeout, cmp='ne')
        return success

    def cmd_move_start(self, timeout=None):
        """."""
        if self.is_busy:
            return False
        self.cmd_drive_turn_on()
        self.cmd_move_enable()
        self['ChangeGap-Cmd'] = 1
        self['ChangePhase-Cmd'] = 1
        # value compared to in 'not equal' operation
        props_values = {'Moving-Mon': 0}
        success = self._set_and_wait(props_values, timeout=timeout, cmp='ne')
        return success

    def cmd_move(self, phase, gap, timeout=None):
        """."""
        if self.is_busy:
            return False
        
        dtime_tol = 1.2  # additional percentual ETA
        dtime_phase = abs(phase - self.phase) / self.speed_phase
        dtime_gap = abs(gap - self.gap) / self.speed_gap
        dtime_max = max(dtime_phase, dtime_gap)
        
        # command move start
        self.phase, self.gap = phase, gap,
        success = self.cmd_move_start(timeout=timeout)
        if not success:
            return

        # wait for moviment within reasonable time
        time_init = _time.time()
        while self.is_moving or self.is_busy:
            if _time.time() - time_init > dtime_tol * dtime_max:
                return False
            _time.sleep(0.1)

        # successfull movement at this point
        return True
        
    def cmd_move_park(self, timeout=None):
        """."""
        if self.is_busy:
            return False
        params = self.parameters
        return self.cmd_move(
            params.PHASE_PARK, params.GAP_PARK, timeout=timeout)

    # --- private methods ---

    def _move_enable_or_disable(self, state, timeout=None):
        """."""
        props_values = {
            'EnblAndReleasePhase-Sel': state,
            'EnblAndReleaseGap-Sel': state,
            }
        return self._set_and_wait(props_values, timeout=timeout)

    def _set_and_wait(self, props_values, timeout=None, comp='eq'):
        timeout = timeout or self._default_timeout
        for propty, value in props_values.items():
            self[propty] = value
        success = True
        for propty, value in props_values.items():
            propty_sts = propty.replace('-Sel', '-Sts')
            success &= self._wait(
                propty_sts, value, timeout=timeout, comp=comp)
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
