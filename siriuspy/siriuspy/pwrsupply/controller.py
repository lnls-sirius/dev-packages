"""Power supply controller classes."""
import time as _t
import random as _random
from threading import Thread as _Thread

from siriuspy import util as _util
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.bsmp import Response as _Response
from siriuspy.bsmp import BSMP as _BSMP
from siriuspy.bsmp import BSMPSim as _BSMPSim
from siriuspy.pwrsupply.bsmp import FBPEntities as _FBPEntities
from siriuspy.pwrsupply.status import PSCStatus as _PSCStatus
from siriuspy.pwrsupply.bsmp import Const as _c
from .siggen import SignalFactory as _SignalFactory

__version__ = _util.get_last_commit_hash()


class IOController:
    """Power supply controller component.

    This component manages BSMP serial-port communications with power supply
    controllers and access to beaglebone's PRU functionalities.
    """

    BSMP_CONST = _c

    def __init__(self, pru, psmodel):
        """Use FBPEntities."""
        self._psmodel = psmodel

        if psmodel == 'FBP':
            self._bsmp_entities = _FBPEntities()
        else:
            raise ValueError("Unknown psmodel!")

        self._pru = pru
        self._bsmp_conn = dict()

    def __getitem__(self, slave_id):
        """Return corresponding BSMP slave device communication object."""
        return self.bsmp_conn[slave_id]

    @property
    def pru(self):
        """Return the PRU object."""
        return self._pru

    @property
    def bsmp_conn(self):
        """Return BSMP slave device communication objects."""
        return self._bsmp_conn

    def add_slave(self, slave_id):
        """Add a BSMP slave device communication object."""
        self.bsmp_conn[slave_id] = \
            _BSMP(self._pru, slave_id, self._bsmp_entities)


class IOControllerSim(IOController):
    """Simulated Power supply controller component."""

    def add_slave(self, slave_id):
        """Add a BSMP slave to make serial communication."""
        if self._psmodel == 'FBP':
            self.bsmp_conn[slave_id] = FBP_BSMPSim()
        else:
            raise ValueError("Unknown psmodel!")


class FBP_BSMPSim(_BSMPSim):
    """Simulate a PS controller."""

    I_LOAD_FLUCTUATION_RMS = 0.01

    SlowRefState = 0
    SlowRefSyncState = 1
    CycleState = 2

    def __init__(self):
        """Use FBPEntities."""
        super().__init__(_FBPEntities())

        # Set variables initial value
        self._variables = self._get_init_variables()

        # Operation mode states
        self._states = [
            FBPSlowRefState(), FBPSlowRefState(), FBPCycleState(),
            FBPSlowRefState(), FBPSlowRefState(), FBPSlowRefState()]

        # Current state
        self._state = self._states[self.SlowRefState]

    def read_variable(self, var_id):
        """Read variable."""
        return _Response.ok, self._state.read_variable(self._variables, var_id)

    def execute_function(self, func_id, input_val=None):
        """Execute a function."""
        # Switch FBP func ids
        if func_id == _c.F_TURN_ON:
            self._state.turn_on(self._variables)
        elif func_id == _c.F_TURN_OFF:
            self._state.turn_off(self._variables)
        elif func_id == _c.F_SELECT_OP_MODE:  # Change state
            # Verify if ps is on
            if self._is_on():
                psc_status = _PSCStatus(input_val)
                input_val = psc_status.ioc_opmode
                self._state = self._states[input_val]
                self._state.select_op_mode(self._variables)
        elif func_id == _c.F_RESET_INTERLOCKS:  # Change state
            self._state.reset_interlocks(self._variables)
            self._state = self._states[self.SlowRefState]
        elif func_id == _c.F_SET_SLOWREF:
            if self._is_on():
                self._state.set_slowref(self._variables, input_val)
        elif func_id == _c.F_CFG_SIGGEN:
            self._state.cfg_siggen(self._variables, input_val)
        elif func_id == _c.F_SET_SIGGEN:
            self._state.set_siggen(self._variables, input_val)
        elif func_id == _c.F_ENABLE_SIGGEN:
            self._state.enable_siggen(self._variables)
        elif func_id == _c.F_DISABLE_SIGGEN:
            self._state.disable_siggen(self._variables)

        return _Response.ok, None

    def _get_init_variables(self):
        firmware = [b'S', b'i', b'm', b'u', b'l', b'a', b't', b'i', b'o', b'n']
        while len(firmware) < 128:
            firmware.append('\x00'.encode())
        variables = [
            0, 0.0, 0.0, firmware, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0,
            [0.0, 0.0, 0.0, 0.0], 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0,
            0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0]
        default_siggen_parms = \
            _SignalFactory.DEFAULT_CONFIGS['Sine']
        variables[_c.V_SIGGEN_TYPE] = default_siggen_parms[0]
        variables[_c.V_SIGGEN_NUM_CYCLES] = default_siggen_parms[1]
        variables[_c.V_SIGGEN_FREQ] = default_siggen_parms[2]
        variables[_c.V_SIGGEN_AMPLITUDE] = default_siggen_parms[3]
        variables[_c.V_SIGGEN_OFFSET] = default_siggen_parms[4]
        variables[_c.V_SIGGEN_AUX_PARAM] = default_siggen_parms[5:9]
        return variables

    def _is_on(self):
        ps_status = self._variables[_c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        return psc_status.ioc_pwrstate


class _FBPState:
    """Represent FBP operation modes."""

    def read_variable(self, variables, var_id):
        """Read variable."""
        if var_id == _c.V_I_LOAD:
            return variables[var_id] + \
                _random.gauss(0.0, FBP_BSMPSim.I_LOAD_FLUCTUATION_RMS)
        value = variables[var_id]
        return value

    def turn_on(self, variables):
        """Turn ps on."""
        ps_status = variables[_c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        if psc_status.ioc_pwrstate == _PSConst.PwrState.Off:
            # Set PSController status
            psc_status.ioc_pwrstate = _PSConst.PwrState.On
            psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
            variables[_c.V_PS_STATUS] = psc_status.ps_status
            # Set currents to 0
            variables[_c.V_PS_SETPOINT] = 0.0
            variables[_c.V_PS_REFERENCE] = 0.0
            variables[_c.V_I_LOAD] = 0.0

    def turn_off(self, variables):
        """Turn ps off."""
        ps_status = variables[_c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        if psc_status.ioc_pwrstate == _PSConst.PwrState.On:
            # Set PSController status
            psc_status.ioc_pwrstate = _PSConst.PwrState.Off
            variables[_c.V_PS_STATUS] = psc_status.ps_status
            # Set currents to 0
            variables[_c.V_PS_SETPOINT] = 0.0
            variables[_c.V_PS_REFERENCE] = 0.0
            variables[_c.V_I_LOAD] = 0.0

    def select_op_mode(self, variables):
        """Set operation mode."""
        raise NotImplementedError()

    def reset_interlocks(self, variables):
        """Reset ps."""
        ps_status = variables[_c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        # Set PSController status
        psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
        variables[_c.V_PS_STATUS] = psc_status.ps_status
        # Set Current to 0
        variables[_c.V_PS_SETPOINT] = 0.0
        variables[_c.V_PS_REFERENCE] = 0.0
        variables[_c.V_I_LOAD] = 0.0
        # Reset interlocks
        variables[_c.V_PS_SOFT_INTERLOCKS] = 0
        variables[_c.V_PS_HARD_INTERLOCKS] = 0

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
        variables[_c.V_SIGGEN_ENABLE] = 1

    def disable_siggen(self, variables):
        """Disable siggen."""
        variables[_c.V_SIGGEN_ENABLE] = 0


class FBPSlowRefState(_FBPState):
    """FBP SlowRef state."""

    def select_op_mode(self, variables):
        """Set operation mode."""
        ps_status = variables[_c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
        variables[_c.V_PS_STATUS] = psc_status.ps_status
        self.set_slowref(variables, variables[_c.V_PS_SETPOINT])

    def set_slowref(self, variables, input_val):
        """Set current."""
        variables[_c.V_PS_SETPOINT] = input_val
        variables[_c.V_PS_REFERENCE] = input_val
        variables[_c.V_I_LOAD] = input_val

    def cfg_siggen(self, variables, input_val):
        """Set siggen configuration parameters."""
        variables[_c.V_SIGGEN_TYPE] = input_val[0]
        variables[_c.V_SIGGEN_NUM_CYCLES] = input_val[1]
        variables[_c.V_SIGGEN_FREQ] = input_val[2]
        variables[_c.V_SIGGEN_AMPLITUDE] = input_val[3]
        variables[_c.V_SIGGEN_OFFSET] = input_val[4]
        variables[_c.V_SIGGEN_AUX_PARAM] = input_val[5:]

    def set_siggen(self, variables, input_val):
        """Set siggen configuration parameters while in continuos mode."""
        variables[_c.V_SIGGEN_FREQ] = input_val[0]
        variables[_c.V_SIGGEN_AMPLITUDE] = input_val[1]
        variables[_c.V_SIGGEN_OFFSET] = input_val[2]


class FBPCycleState(_FBPState):
    """FBP Cycle state."""

    def __init__(self):
        """Set cycle parameters."""
        self._siggen_canceled = False

    def read_variable(self, variables, var_id):
        """Return variable."""
        enbl = variables[_c.V_SIGGEN_ENABLE]
        if enbl and var_id in (_c.V_PS_REFERENCE, _c.V_I_LOAD):
            value = self._signal.value
            variables[_c.V_PS_REFERENCE] = value
            variables[_c.V_I_LOAD] = value
        return super().read_variable(variables, var_id)

    def select_op_mode(self, variables):
        """Set operation mode."""
        ps_status = variables[_c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        psc_status.ioc_opmode = _PSConst.OpMode.Cycle
        variables[_c.V_PS_STATUS] = psc_status.ps_status
        variables[_c.V_SIGGEN_ENABLE] = 0
        variables[_c.V_PS_REFERENCE] = 0.0
        variables[_c.V_I_LOAD] = 0.0
        # self._set_signal(variables)
        self.enable_siggen(variables)

    def reset_interlocks(self, variables):
        """Reset interlocks."""
        super().reset_interlocks(variables)
        self.disable_siggen(variables)

    def set_slowref(self, variables, input_val):
        """Set current."""
        variables[_c.V_PS_SETPOINT] = input_val

    def cfg_siggen(self, variables, input_val):
        """Set siggen configuration parameters."""
        if not variables[_c.V_SIGGEN_ENABLE]:
            variables[_c.V_SIGGEN_TYPE] = input_val[0]
            variables[_c.V_SIGGEN_NUM_CYCLES] = input_val[1]
            variables[_c.V_SIGGEN_FREQ] = input_val[2]
            variables[_c.V_SIGGEN_AMPLITUDE] = input_val[3]
            variables[_c.V_SIGGEN_OFFSET] = input_val[4]
            variables[_c.V_SIGGEN_AUX_PARAM] = input_val[5:]

    def set_siggen(self, variables, input_val):
        """Set siggen configuration parameters while in continuos mode."""
        if not variables[_c.V_SIGGEN_ENABLE] or \
                (variables[_c.V_SIGGEN_ENABLE] and
                 variables[_c.V_SIGGEN_NUM_CYCLES] == 0):
            variables[_c.V_SIGGEN_FREQ] = input_val[0]
            variables[_c.V_SIGGEN_AMPLITUDE] = input_val[1]
            variables[_c.V_SIGGEN_OFFSET] = input_val[2]

    def enable_siggen(self, variables):
        """Enable siggen."""
        variables[_c.V_SIGGEN_ENABLE] = 1
        self._set_signal(variables)
        if self._signal.duration > 0:
            self._siggen_canceled = False
            thread = _Thread(
                target=self._finish_siggen,
                args=(variables, self._signal.duration),
                daemon=True)
            thread.start()

    def disable_siggen(self, variables):
        """Disable siggen."""
        if variables[_c.V_SIGGEN_ENABLE] == 1:
            variables[_c.V_SIGGEN_ENABLE] = 0
            self._siggen_canceled = True
            self._signal.enable = False

    def _set_signal(self, variables):
        t = variables[_c.V_SIGGEN_TYPE]
        n = variables[_c.V_SIGGEN_NUM_CYCLES]
        f = variables[_c.V_SIGGEN_FREQ]
        a = variables[_c.V_SIGGEN_AMPLITUDE]
        o = variables[_c.V_SIGGEN_OFFSET]
        p = variables[_c.V_SIGGEN_AUX_PARAM]
        self._signal = _SignalFactory.factory(type=t,
                                              num_cycles=n,
                                              freq=f,
                                              amplitude=a,
                                              offset=o,
                                              aux_param=p)

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
        val = self._signal.value
        variables[_c.V_PS_REFERENCE] = val
        variables[_c.V_I_LOAD] = val
        variables[_c.V_SIGGEN_ENABLE] = 0
