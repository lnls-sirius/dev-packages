"""Translate `ps_state` bits to values exposed in EPICS."""

from ..csdev import ETypes as _et
from ..csdev import Const as _c


class PSCStatus:
    """Power Supply Controller Status."""

    OPMODE = _c.OpMode
    PWRSTATE = _c.PwrStateSel
    STATES = _c.States
    CYCLETYPE = _c.CycleType

    _mask_state = 0b0000000000001111
    _mask_oloop = 0b0000000000010000
    _mask_intfc = 0b0000000001100000
    _mask_activ = 0b0000000010000000
    _mask_model = 0b0001111100000000
    _mask_unlck = 0b0010000000000000
    _mask_rsrvd = 0b1100000000000000
    _mask_stats = 0b1111111111111111

    _psc2ioc_state = {
        _c.States.Off: _c.OpMode.SlowRef,
        _c.States.Interlock: _c.OpMode.SlowRef,
        _c.States.Initializing: _c.OpMode.SlowRef,
        _c.States.SlowRef: _c.OpMode.SlowRef,
        _c.States.SlowRefSync: _c.OpMode.SlowRefSync,
        _c.States.Cycle: _c.OpMode.Cycle,
        _c.States.RmpWfm: _c.OpMode.RmpWfm,
        _c.States.MigWfm: _c.OpMode.MigWfm,
        _c.States.FastRef: _c.OpMode.FastRef,
    }

    _ioc2psc_state = {
        # TODO: controller firmware still defines only a subset of opmodes
        _c.OpMode.SlowRef: _c.States.SlowRef,
        _c.OpMode.SlowRefSync: _c.States.SlowRefSync,
        _c.OpMode.Cycle: _c.States.Cycle,
        _c.OpMode.RmpWfm: _c.States.SlowRef,
        _c.OpMode.MigWfm: _c.States.SlowRef,
        _c.OpMode.FastRef: _c.States.SlowRef,
    }

    def __init__(self, ps_status=0):
        """Constructor."""
        self._ps_status = ps_status

    # --- public interface ---

    @property
    def ps_status(self):
        """Return ps-controller ps_status."""
        return self._ps_status

    @ps_status.setter
    def ps_status(self, value):
        """Set ps-controller ps_status."""
        self._ps_status = value & PSCStatus._mask_stats

    @property
    def state(self):
        """Return ps-controller state."""
        return (self._ps_status & PSCStatus._mask_state) >> 0

    @state.setter
    def state(self, value):
        """Set ps-controller state."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_state
        self._ps_status += (value & 0b1111) << 0

    @property
    def open_loop(self):
        """Return ps-controller open_loop."""
        return (self._ps_status & PSCStatus._mask_oloop) >> 4

    @open_loop.setter
    def open_loop(self, value):
        """Set ps-controller open_loop."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_oloop
        self._ps_status += (value & 0b1) << 4

    @property
    def interface(self):
        """Return ps-controller interface."""
        return (self._ps_status & PSCStatus._mask_intfc) >> 5

    @interface.setter
    def interface(self, value):
        """Set ps-controller interface."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_intfc
        self._ps_status += (value & 0b11) << 5

    @property
    def active(self):
        """Return ps-controller active."""
        return (self._ps_status & PSCStatus._mask_activ) >> 7

    @active.setter
    def active(self, value):
        """Set ps-controller active."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_activ
        self._ps_status += (value & 0b1) << 7

    @property
    def model(self):
        """Return ps-controller model."""
        return (self._ps_status & PSCStatus._mask_model) >> 8

    @model.setter
    def model(self, value):
        """Set ps-controller interface."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_model
        self._ps_status += (value & 0b11111) << 8

    @property
    def unlocked(self):
        """Return ps-controller unlocked."""
        return (self._ps_status & PSCStatus._mask_unlck) >> 13

    @unlocked.setter
    def unlocked(self, value):
        """Set ps-controller unlocked."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_unlck
        self._ps_status += (value & 0b1) << 13

    @property
    def reserved(self):
        """Return ps-controller reserved."""
        return (self._ps_status & PSCStatus._mask_rsrvd) >> 14

    @reserved.setter
    def reserved(self, value):
        """Set ps-controller reserved."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_rsrvd
        self._ps_status += (value & 0b11) << 14

    @property
    def ioc_pwrstate(self):
        """Return ioc-controller power state."""
        state = self.state
        if state in (_c.States.Off,
                     _c.States.Interlock):
            pwrstate = _c.PwrStateSel.Off
        else:
            pwrstate = _c.PwrStateSel.On
        return pwrstate

    @ioc_pwrstate.setter
    def ioc_pwrstate(self, value):
        """Set ps_status with a given ioc-controller power state."""
        if not 0 <= value < len(_et.PWRSTATE_SEL):
            raise ValueError('Invalid pwrstate value!')
        # TurnOn sets Opmode to SlowRef by default.
        state = _c.States.Off if value == _c.PwrStateSel.Off else \
            _c.States.SlowRef
        self.state = state

    @property
    def ioc_opmode(self):
        """Return ioc-controller opmode."""
        state = self.state
        opmode = PSCStatus._psc2ioc_state[state]
        return opmode

    @ioc_opmode.setter
    def ioc_opmode(self, value):
        """Set ps_status with a given ioc-controller opmode."""
        if not 0 <= value < len(_et.OPMODES):
            raise ValueError('Invalid opmode value!')
        state = PSCStatus._ioc2psc_state[value]
        self.state = state
