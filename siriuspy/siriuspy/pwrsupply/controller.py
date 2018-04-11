"""Power supply controller classes."""
import time as _t
import random as _random
from threading import Thread as _Thread

from siriuspy import util as _util
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.bsmp import Response, BSMP
from siriuspy.pwrsupply.bsmp import FBPEntities
from siriuspy.pwrsupply.status import PSCStatus as _PSCStatus
from siriuspy.pwrsupply.bsmp import Const as _c
from .siggen import Trapezoidal

__version__ = _util.get_last_commit_hash()


class PSCommInterface:
    """Communication interface class for power supplies."""

    # TODO: should this class have its own python module?

    # --- public interface ---

    def __init__(self):
        """Init method."""
        self._callbacks = {}

    @property
    def connected(self):
        """Return connection status."""
        return self._connected()

    def read(self, field):
        """Return field value."""
        raise NotImplementedError

    def write(self, field, value):
        """Write value to a field.

        Return write value if command suceeds or None if it fails.
        """
        raise NotImplementedError

    def add_callback(self, func, index=None):
        """Add callback function."""
        if not callable(func):
            raise ValueError("Tried to set non callable as a callback")
        if index is None:
            index = 0 if len(self._callbacks) == 0 \
                else max(self._callbacks.keys()) + 1
        self._callbacks[index] = func

    # --- virtual private methods ---

    def _connected(self):
        raise NotImplementedError


class FBPController(BSMP):
    """FBP power supply."""

    def __init__(self, serial, slave_address):
        """Use FBPEntities."""
        super().__init__(serial, slave_address, FBPEntities())


class _ControllerSim:
    """Virtual controller."""

    def __init__(self, entities):
        """Entities."""
        self._variables = []
        self._entities = entities

    @property
    def entities(self):
        """PS entities."""
        return self._entities

    def read_variable(self, var_id):
        """Read a variable."""
        return Response.ok, self._variables[var_id]

    def remove_all_groups(self):
        """Remove all groups."""
        self.entities.remove_all_groups()
        return Response.ok, None

    def read_group_variables(self, group_id):
        """Read group of variables."""
        ids = [var.eid for var in self.entities.groups[group_id].variables]
        return Response.ok, [self.read_variable(id)[1] for id in ids]

    def create_group(self, var_ids):
        """Create new group."""
        self.entities.add_group(var_ids)
        return Response.ok, None

    def execute_function(self, func_id, input_val=None):
        """Execute a function."""
        raise NotImplementedError()


class FBPControllerSim(_ControllerSim):
    """Simulate a PS controller."""

    I_LOAD_FLUCTUATION_RMS = 0.01

    SlowRefState = 0
    SlowRefSyncState = 1
    CycleState = 2

    def __init__(self):
        """Use FBPEntities."""
        super().__init__(FBPEntities())
        # Set variables initial value
        firmware = [b'S', b'i', b'm', b'u', b'l', b'a', b't', b'i', b'o', b'n']
        while len(firmware) < 128:
            firmware.append('\x00'.encode())
        self._variables = [
            0, 0.0, 0.0, firmware, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0,
            [0.0, 0.0, 0.0, 0.0], 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0,
            0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0]
        # Operation mode states
        self._states = [
            FBPSlowRefState(), FBPSlowRefState(), FBPCycleState(),
            FBPSlowRefState(), FBPSlowRefState(), FBPSlowRefState()]
        # Current state
        self._state = self._states[self.SlowRefState]

    def read_variable(self, var_id):
        """Read variable."""
        return Response.ok, self._state.read_variable(self._variables, var_id)

    def execute_function(self, func_id, input_val=None):
        """Execute a function."""
        # Switch FBP func ids
        if func_id == _c.TURN_ON:
            self._state.turn_on(self._variables)
        elif func_id == _c.TURN_OFF:
            self._state.turn_off(self._variables)
        elif func_id == _c.SELECT_OP_MODE:  # Change state
            # Verify if ps is on
            if self._is_on():
                opmode = input_val - 3
                self._state = self._states[opmode]
                self._state.select_op_mode(self._variables)
        elif func_id == _c.RESET_INTERLOCKS:  # Change state
            self._state.reset_interlocks(self._variables)
            self._state = self._states[self.SlowRefState]
        elif func_id == _c.SET_SLOWREF:
            if self._is_on():
                self._state.set_slowref(self._variables, input_val)
        elif func_id == _c.CFG_SIGGEN:
            self._state.cfg_siggen(self._variables, input_val)
        elif func_id == _c.SET_SIGGEN:
            self._state.set_siggen(self._variables, input_val)
        elif func_id == _c.ENABLE_SIGGEN:
            self._state.enable_siggen(self._variables)
        elif func_id == _c.DISABLE_SIGGEN:
            self._state.disable_siggen(self._variables)

        return Response.ok, None

    def _is_on(self):
        ps_status = self._variables[_c.PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        return psc_status.ioc_pwrstate


class _FBPState:
    """Represent FBP operation modes."""

    def read_variable(self, variables, var_id):
        """Read variable."""
        if var_id == _c.I_LOAD:
            return variables[var_id] + \
                _random.gauss(0.0, FBPControllerSim.I_LOAD_FLUCTUATION_RMS)
        value = variables[var_id]
        return value

    def turn_on(self, variables):
        """Turn ps on."""
        ps_status = variables[_c.PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        if psc_status.ioc_pwrstate == _PSConst.PwrState.Off:
            # Set PSController status
            psc_status.ioc_pwrstate = _PSConst.PwrState.On
            psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
            variables[_c.PS_STATUS] = psc_status.ps_status
            # Set currents to 0
            variables[_c.PS_SETPOINT] = 0.0
            variables[_c.PS_REFERENCE] = 0.0
            variables[_c.I_LOAD] = 0.0

    def turn_off(self, variables):
        """Turn ps off."""
        ps_status = variables[_c.PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        if psc_status.ioc_pwrstate == _PSConst.PwrState.On:
            # Set PSController status
            psc_status.ioc_pwrstate = _PSConst.PwrState.Off
            variables[_c.PS_STATUS] = psc_status.ps_status
            # Set currents to 0
            variables[_c.PS_SETPOINT] = 0.0
            variables[_c.PS_REFERENCE] = 0.0
            variables[_c.I_LOAD] = 0.0

    def select_op_mode(self, variables):
        """Set operation mode."""
        raise NotImplementedError()

    def reset_interlocks(self, variables):
        """Reset ps."""
        ps_status = variables[_c.PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        # Set PSController status
        psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
        variables[_c.PS_STATUS] = psc_status.ps_status
        # Set Current to 0
        variables[_c.PS_SETPOINT] = 0.0
        variables[_c.PS_REFERENCE] = 0.0
        variables[_c.I_LOAD] = 0.0
        # Reset interlocks
        variables[_c.PS_SOFT_INTERLOCKS] = 0
        variables[_c.PS_HARD_INTERLOCKS] = 0

    def set_slowref(self, variables, input_val):
        """Set current."""
        raise NotImplementedError()

    def cfg_siggen(self, variables, input_val):
        """Config siggen."""
        raise NotImplementedError()

    def set_siggen(self, variables, input_val):
        """Set siggen parameters in continuos mode."""
        raise NotImplementedError()

    def enable_siggen(self, variables):
        """Enable siggen."""
        variables[_c.SIGGEN_ENABLE] = 1

    def disable_siggen(self, variables):
        """Disable siggen."""
        variables[_c.SIGGEN_ENABLE] = 0


class FBPSlowRefState(_FBPState):
    """FBP SlowRef state."""

    def select_op_mode(self, variables):
        """Set operation mode."""
        ps_status = variables[_c.PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
        variables[_c.PS_STATUS] = psc_status.ps_status
        self.set_slowref(variables, variables[_c.PS_SETPOINT])

    def set_slowref(self, variables, input_val):
        """Set current."""
        variables[_c.PS_SETPOINT] = input_val
        variables[_c.PS_REFERENCE] = input_val
        variables[_c.I_LOAD] = input_val

    def cfg_siggen(self, variables, input_val):
        """Set siggen configuration parameters."""
        variables[_c.SIGGEN_TYPE] = input_val[0]
        variables[_c.SIGGEN_NUM_CYCLES] = input_val[1]
        variables[_c.SIGGEN_FREQ] = input_val[2]
        variables[_c.SIGGEN_AMPLITUDE] = input_val[3]
        variables[_c.SIGGEN_OFFSET] = input_val[4]
        variables[_c.SIGGEN_AUX_PARAM] = input_val[5:]

    def set_siggen(self, variables, input_val):
        """Set siggen configuration parameters while in continuos mode."""
        variables[_c.SIGGEN_FREQ] = input_val[0]
        variables[_c.SIGGEN_AMPLITUDE] = input_val[1]
        variables[_c.SIGGEN_OFFSET] = input_val[2]


class FBPCycleState(_FBPState):
    """FBP Cycle state."""

    def __init__(self):
        """Set cycle parameters."""
        self._siggen_canceled = False

    def read_variable(self, variables, var_id):
        """Return variable."""
        enbl = variables[_c.SIGGEN_ENABLE]
        if enbl and var_id in (_c.PS_REFERENCE, _c.I_LOAD):
            value = self._signal.get_value()
            variables[_c.PS_REFERENCE] = value
            variables[_c.I_LOAD] = value
        return super().read_variable(variables, var_id)

    def select_op_mode(self, variables):
        """Set operation mode."""
        ps_status = variables[_c.PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        psc_status.ioc_opmode = _PSConst.OpMode.Cycle
        variables[_c.PS_STATUS] = psc_status.ps_status
        variables[_c.SIGGEN_ENABLE] = 0
        variables[_c.PS_REFERENCE] = 0.0
        variables[_c.I_LOAD] = 0.0
        self._set_signal(variables)

    def reset_interlocks(self, variables):
        """Reset interlocks."""
        super().reset_interlocks(variables)
        self.disable_siggen(variables)

    def set_slowref(self, variables, input_val):
        """Set current."""
        variables[_c.PS_SETPOINT] = input_val

    def cfg_siggen(self, variables, input_val):
        """Set siggen configuration parameters."""
        if not variables[_c.SIGGEN_ENABLE]:
            variables[_c.SIGGEN_TYPE] = input_val[0]
            variables[_c.SIGGEN_NUM_CYCLES] = input_val[1]
            variables[_c.SIGGEN_FREQ] = input_val[2]
            variables[_c.SIGGEN_AMPLITUDE] = input_val[3]
            variables[_c.SIGGEN_OFFSET] = input_val[4]
            variables[_c.SIGGEN_AUX_PARAM] = input_val[5:]

    def set_siggen(self, variables, input_val):
        """Set siggen configuration parameters while in continuos mode."""
        if not variables[_c.SIGGEN_ENABLE] or \
                (variables[_c.SIGGEN_ENABLE] and
                 variables[_c.SIGGEN_NUM_CYCLES] == 0):
            variables[_c.SIGGEN_FREQ] = input_val[0]
            variables[_c.SIGGEN_AMPLITUDE] = input_val[1]
            variables[_c.SIGGEN_OFFSET] = input_val[2]

    def enable_siggen(self, variables):
        """Enable siggen."""
        variables[_c.SIGGEN_ENABLE] = 1
        self._set_signal(variables)
        if self._signal.duration() > 0:
            self._siggen_canceled = False
            thread = _Thread(
                target=self._finish_siggen,
                args=(variables, self._signal.duration()),
                daemon=True)
            thread.start()

    def disable_siggen(self, variables):
        """Disable siggen."""
        if variables[_c.SIGGEN_ENABLE] == 1:
            variables[_c.SIGGEN_ENABLE] = 0
            self._siggen_canceled = True
            self._signal.enable = False

    def _set_signal(self, variables):
        n = variables[_c.SIGGEN_NUM_CYCLES]
        # f = variables[_c.SIGGEN_FREQ]
        a = variables[_c.SIGGEN_AMPLITUDE]
        o = variables[_c.SIGGEN_OFFSET]
        aux = variables[_c.SIGGEN_AUX_PARAM]
        # Switch Type
        # t = variables[_c.SIGGEN_TYPE]:
        # if t == 0:
        # elif t == 1:
        # elif t == 2:
        #     self._signal = Trapezoidal(n, a, o, aux)
        # else:
        #     raise ValueError()
        self._signal = Trapezoidal(n, a, o, aux)

    def _finish_siggen(self, variables, time):
        time_up = False
        elapsed = 0
        while not time_up:
            _t.sleep(0.5)
            elapsed += 0.5
            if elapsed >= time:
                time_up = True
            if self._siggen_canceled:
                return
        val = self._signal.get_value()
        variables[_c.PS_REFERENCE] = val
        variables[_c.I_LOAD] = val
        variables[_c.SIGGEN_ENABLE] = 0
