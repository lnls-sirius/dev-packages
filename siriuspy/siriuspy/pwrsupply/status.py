"""Translate `ps_state` bits to values exposed in EPICS."""
from siriuspy.csdevice.pwrsupply import ps_models as _ps_models
from siriuspy.csdevice.pwrsupply import ps_interface as _ps_interface
from siriuspy.csdevice.pwrsupply import ps_openloop as _ps_openloop
from siriuspy.csdevice.pwrsupply import ps_states as _ps_states
from siriuspy.csdevice.pwrsupply import ps_pwrstate_sel as _ps_pwrstate_sel
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.pwrsupply import ps_opmode as _ps_opmode


class Status:
    """Power supply status class."""

    _mask_state = 0b0000000000001111
    _mask_oloop = 0b0000000000010000
    _mask_intfc = 0b0000000001100000
    _mask_activ = 0b0000000010000000
    _mask_model = 0b0001111100000000
    _mask_unlck = 0b0010000000000000
    _mask_rsrvd = 0b1100000000000000

    _dsp2ps_state = {
        _PSConst.States.Off: _PSConst.OpMode.SlowRef,
        _PSConst.States.Interlock: _PSConst.OpMode.SlowRef,
        _PSConst.States.Initializing: _PSConst.OpMode.SlowRef,
        _PSConst.States.SlowRef: _PSConst.OpMode.SlowRef,
        _PSConst.States.SlowRefSync: _PSConst.OpMode.SlowRefSync,
        _PSConst.States.Cycle: _PSConst.OpMode.Cycle,
        _PSConst.States.RmpWfm: _PSConst.OpMode.RmpWfm,
        _PSConst.States.MigWfm: _PSConst.OpMode.MigWfm,
        _PSConst.States.FastRef: _PSConst.OpMode.FastRef,
    }

    _ps2dsp_state = {
        # current PS version implements only SlowRef!
        _PSConst.OpMode.SlowRef: _PSConst.States.SlowRef,
        _PSConst.OpMode.SlowRefSync: _PSConst.States.SlowRefSync,
        _PSConst.OpMode.FastRef: _PSConst.States.SlowRef,
        _PSConst.OpMode.RmpWfm: _PSConst.States.SlowRef,
        _PSConst.OpMode.MigWfm: _PSConst.States.SlowRef,
        _PSConst.OpMode.Cycle: _PSConst.States.Cycle,
    }

    @staticmethod
    def state(status, label=False):
        """Return DSP state of power supply."""
        index = (status & (0b1111 << 0)) >> 0
        return _ps_states[index] if label else index

    @staticmethod
    def set_state(status, value):
        """Set state in power supply status."""
        if not (0 <= value < len(_ps_states)):
            raise ValueError('Invalid state value!')
        status = status & ~Status._mask_state
        status += value << 0
        return status

    @staticmethod
    def pwrstate(status, label=False):
        """Return PS powerstate."""
        state = Status.state(status, label=False)
        index = _PSConst.PwrState.Off if state == _PSConst.States.Off else \
            _PSConst.PwrState.On
        return _ps_pwrstate_sel[index] if label else index

    @staticmethod
    def set_pwrstate(status, value):
        """Set pwrstate in power supply status."""
        if not (0 <= value < len(_ps_pwrstate_sel)):
            raise ValueError('Invalid pwrstate value!')
        status = status & ~Status._mask_state
        value = _PSConst.States.Off if value == _PSConst.PwrState.Off else \
            _PSConst.States.SlowRef
        status += value << 0
        return status

    @staticmethod
    def opmode(status, label=False):
        """Return PS opmode."""
        state = Status.state(status, label=False)
        index = Status._dsp2ps_state[state]
        return _ps_opmode[index] if label else index

    @staticmethod
    def set_opmode(status, value):
        """Set power supply opmode."""
        if not (0 <= value < len(_ps_opmode)):
            raise ValueError('Invalid opmode value!')
        value = Status._ps2dsp_state[value]
        status = Status.set_state(status, value)
        return status

    @staticmethod
    def openloop(status, label=False):
        """Return open-loop state index of power supply."""
        index = (status & (0b1 << 4)) >> 4
        return _ps_openloop[index] if label else index

    @staticmethod
    def set_openloop(status, value):
        """Set openloop in power supply status."""
        if not (0 <= value < len(_ps_openloop)):
            raise ValueError('Invalid openloop value!')
        status = status & ~Status._mask_oloop
        status += value << 4
        return status

    @staticmethod
    def interface(status, label=False):
        """Return interface index of power supply."""
        index = (status & (0b11 << 5)) >> 5
        return _ps_interface[index] if label else index

    @staticmethod
    def set_interface(status, value):
        """Set interface index in power supply status."""
        if not (0 <= value < len(_ps_interface)):
            raise ValueError('Invalid interface number!')
        status = status & ~Status._mask_intfc
        status += value << 5
        return status

    @staticmethod
    def active(status, label=False):
        """Return active index of power supply."""
        return (status & (0b1 << 7)) >> 7

    @staticmethod
    def set_active(status, value):
        """Set active index in power supply status."""
        if not (0 <= value <= 1):
            raise ValueError('Invalid active number!')
        status = status & ~Status._mask_activ
        status += value << 7
        return status

    @staticmethod
    def model(status, label=False):
        """Return model index for power supply."""
        index = (status & Status._mask_model) >> 8
        return _ps_models[index] if label else index

    @staticmethod
    def set_model(status, value):
        """Set model in power supply status."""
        if not (0 <= value < len(_ps_models)):
            raise ValueError('Invalid model number!')
        status = status & ~Status._mask_model
        status += value << 8
        return status

    @staticmethod
    def unlocked(status, label=False):
        """Return unlocked index for power supply."""
        return (status & (0b1 << 13)) >> 13

    @staticmethod
    def set_unlocked(status, value):
        """Set unlocked in power supply status."""
        if not (0 <= value <= 1):
            raise ValueError('Invalid unlocked number!')
        status = status & ~Status._mask_unlck
        status += value << 13
        return status
