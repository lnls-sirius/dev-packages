"""Power supply controller classes."""
import time as _t
import random as _random
from threading import Thread as _Thread

from siriuspy import util as _util
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.bsmp import Response as _Response
# from siriuspy.bsmp import BSMP as _BSMP
from siriuspy.bsmp import BSMPSim as _BSMPSim
from siriuspy.pwrsupply.bsmp import FBPEntities as _FBPEntities
from siriuspy.pwrsupply.bsmp import FBP_DCLINKEntities as _FBP_DCLINKEntities
from siriuspy.pwrsupply.bsmp import FACEntities as _FACEntities
from siriuspy.pwrsupply.bsmp import FAC_ACDCEntities as _FAC_ACDCEntities
from siriuspy.pwrsupply.status import PSCStatus as _PSCStatus
from siriuspy.pwrsupply.bsmp import ConstFBP as _cFBP
from siriuspy.pwrsupply.bsmp import ConstFBP_DCLINK as _cFBP_DCLINK
from siriuspy.pwrsupply.bsmp import ConstFAC as _cFAC
from siriuspy.pwrsupply.bsmp import ConstFAC_ACDC as _cFAC_ACDC
from .siggen import SignalFactory as _SignalFactory

__version__ = _util.get_last_commit_hash()


_I_LOAD_FLUCTUATION_RMS = 0.01  # [A]


# --- classes to specialize the type of PS ---


class _FAC:
    """SlowRef FAC state."""

    def _get_i_load_fluctuation_rms(self):
        return _I_LOAD_FLUCTUATION_RMS

    def _get_constants(self):
        return _cFAC

    def _get_iloads_ids(self):
        return (_cFAC.V_I_LOAD1, _cFAC.V_I_LOAD2)


class _FBP:
    """SlowRef FBP state."""

    def _get_i_load_fluctuation_rms(self):
        return _I_LOAD_FLUCTUATION_RMS

    def _get_constants(self):
        return _cFBP

    def _get_iloads_ids(self):
        return (_cFBP.V_I_LOAD, )


class _FAC_ACDC:
    """SlowRef FAC_ACDC state."""

    def _get_i_load_fluctuation_rms(self):
        return _I_LOAD_FLUCTUATION_RMS

    def _get_constants(self):
        return _cFAC_ACDC

    def _get_iloads_ids(self):
        return ()


class _FBP_DCLINK:
    """SlowRef FAC_ACDC state."""

    def _get_i_load_fluctuation_rms(self):
        return _I_LOAD_FLUCTUATION_RMS

    def _get_constants(self):
        return _cFBP_DCLINK

    def _get_iloads_ids(self):
        return ()

# --- State classes ---


class _State:
    """Represent operation modes."""

    def __init__(self):
        self._c = self._get_constants()
        self._iloads = self._get_iloads_ids()

    def read_variable(self, variables, var_id):
        """Read variable."""
        for iload_id in self._iloads:
            if var_id == iload_id:
                return variables[var_id] + \
                    _random.gauss(0.0, self._get_i_load_fluctuation_rms())
        value = variables[var_id]
        return value

    def turn_on(self, variables):
        """Turn ps on."""
        ps_status = variables[self._c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        if psc_status.ioc_pwrstate == _PSConst.PwrState.Off:
            # Set PSController status
            psc_status.ioc_pwrstate = _PSConst.PwrState.On
            psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
            variables[self._c.V_PS_STATUS] = psc_status.ps_status
            # Set currents to 0
            variables[self._c.V_PS_SETPOINT] = 0.0
            variables[self._c.V_PS_REFERENCE] = 0.0
            for iload_id in self._iloads:
                variables[iload_id] = 0.0

    def turn_off(self, variables):
        """Turn ps off."""
        ps_status = variables[self._c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        if psc_status.ioc_pwrstate == _PSConst.PwrState.On:
            # Set PSController status
            psc_status.ioc_pwrstate = _PSConst.PwrState.Off
            variables[self._c.V_PS_STATUS] = psc_status.ps_status
            # Set currents to 0
            variables[self._c.V_PS_SETPOINT] = 0.0
            variables[self._c.V_PS_REFERENCE] = 0.0
            for iload_id in self._iloads:
                variables[iload_id] = 0.0

    def open_loop(self, variables):
        """Open control loop."""
        ps_status = variables[self._c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        psc_status.open_loop = 1
        variables[self._c.V_PS_STATUS] = psc_status.ps_status

    def close_loop(self, variables):
        """Close control loop."""
        ps_status = variables[self._c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        psc_status.open_loop = 0
        variables[self._c.V_PS_STATUS] = psc_status.ps_status
        for iload_id in self._iloads:
            variables[iload_id] = variables[self._c.V_PS_REFERENCE]

    def select_op_mode(self, variables):
        """Set operation mode."""
        raise NotImplementedError()

    def reset_interlocks(self, variables):
        """Reset ps."""
        ps_status = variables[self._c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        # Set PSController status
        psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
        variables[self._c.V_PS_STATUS] = psc_status.ps_status
        # Set Current to 0
        variables[self._c.V_PS_SETPOINT] = 0.0
        variables[self._c.V_PS_REFERENCE] = 0.0
        for iload_id in self._iloads:
            variables[iload_id] = 0.0
        # Reset interlocks
        variables[self._c.V_PS_SOFT_INTERLOCKS] = 0
        variables[self._c.V_PS_HARD_INTERLOCKS] = 0

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
        variables[self._c.V_SIGGEN_ENABLE] = 1

    def disable_siggen(self, variables):
        """Disable siggen."""
        variables[self._c.V_SIGGEN_ENABLE] = 0

    def _is_on(self, variables):
        ps_status = variables[self._c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        return psc_status.ioc_pwrstate

    def _is_open_loop(self, variables):
        ps_status = variables[self._c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        return psc_status.open_loop


class _SlowRefState(_State):
    """SlowRef state."""

    def select_op_mode(self, variables):
        """Set operation mode."""
        ps_status = variables[self._c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
        variables[self._c.V_PS_STATUS] = psc_status.ps_status
        self.set_slowref(variables, variables[self._c.V_PS_SETPOINT])

    def set_slowref(self, variables, input_val):
        """Set current."""
        variables[self._c.V_PS_SETPOINT] = input_val
        if self._is_on(variables):
            variables[self._c.V_PS_REFERENCE] = input_val
            if self._is_open_loop(variables) == 0:
                # control loop closed
                for iload_id in self._iloads:
                    variables[iload_id] = input_val

    def cfg_siggen(self, variables, input_val):
        """Set siggen configuration parameters."""
        variables[self._c.V_SIGGEN_TYPE] = input_val[0]
        variables[self._c.V_SIGGEN_NUM_CYCLES] = input_val[1]
        variables[self._c.V_SIGGEN_FREQ] = input_val[2]
        variables[self._c.V_SIGGEN_AMPLITUDE] = input_val[3]
        variables[self._c.V_SIGGEN_OFFSET] = input_val[4]
        variables[self._c.V_SIGGEN_AUX_PARAM] = input_val[5:]

    def set_siggen(self, variables, input_val):
        """Set siggen configuration parameters while in continuos mode."""
        variables[self._c.V_SIGGEN_FREQ] = input_val[0]
        variables[self._c.V_SIGGEN_AMPLITUDE] = input_val[1]
        variables[self._c.V_SIGGEN_OFFSET] = input_val[2]

    def trigger(self, variables, value):
        """Slow Ref does nothing when trigger is received."""
        if self._is_on(variables):
            variables[self._c.V_PS_REFERENCE] = value
            if self._is_open_loop(variables) == 0:
                # control loop closed
                for iload_id in self._iloads:
                    variables[iload_id] = value


class _SlowRefSyncState(_State):

    def __init__(self):
        """Init."""
        _State.__init__(self)
        self._last_setpoint = None

    def select_op_mode(self, variables):
        """Set operation mode."""
        ps_status = variables[self._c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        psc_status.ioc_opmode = _PSConst.OpMode.SlowRefSync
        variables[self._c.V_PS_STATUS] = psc_status.ps_status

    def set_slowref(self, variables, input_val):
        """Set current."""
        self._last_setpoint = input_val

    def trigger(self, variables):
        """Apply last setpoint received."""
        if self._last_setpoint is None:
            self._last_setpoint = variables[self._c.V_PS_SETPOINT]
        variables[self._c.V_PS_SETPOINT] = self._last_setpoint
        if self._is_on(variables):
            variables[self._c.V_PS_REFERENCE] = self._last_setpoint
            if self._is_open_loop(variables) == 0:
                # control loop closed
                for iload_id in self._iloads:
                    variables[iload_id] = self._last_setpoint


class _CycleState(_State):
    """FBP Cycle state."""

    def __init__(self, pru):
        """Set cycle parameters."""
        _State.__init__(self)
        self._siggen_canceled = False
        self._pru = pru

    def read_variable(self, variables, var_id):
        """Return variable."""
        enbl = variables[self._c.V_SIGGEN_ENABLE]
        if enbl and \
           (var_id in self._iloads or var_id == self._c.V_PS_REFERENCE):
            value = self._signal.value
            variables[self._c.V_PS_REFERENCE] = value
            for iload_id in self._iloads:
                variables[iload_id] = value
            variables[self._c.V_SIGGEN_N] += 1
        return super().read_variable(variables, var_id)

    def select_op_mode(self, variables):
        """Set operation mode."""
        ps_status = variables[self._c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        psc_status.ioc_opmode = _PSConst.OpMode.Cycle
        variables[self._c.V_PS_STATUS] = psc_status.ps_status
        variables[self._c.V_SIGGEN_ENABLE] = 0
        variables[self._c.V_PS_REFERENCE] = 0.0
        for iload_id in self._iloads:
            variables[iload_id] = 0.0
        # self._set_signal(variables)
        # self.enable_siggen(variables)

    def reset_interlocks(self, variables):
        """Reset interlocks."""
        super().reset_interlocks(variables)
        self.disable_siggen(variables)

    def set_slowref(self, variables, input_val):
        """Set current."""
        variables[self._c.V_PS_SETPOINT] = input_val

    def cfg_siggen(self, variables, input_val):
        """Set siggen configuration parameters."""
        if not variables[self._c.V_SIGGEN_ENABLE]:
            variables[self._c.V_SIGGEN_TYPE] = input_val[0]
            variables[self._c.V_SIGGEN_NUM_CYCLES] = input_val[1]
            variables[self._c.V_SIGGEN_FREQ] = input_val[2]
            variables[self._c.V_SIGGEN_AMPLITUDE] = input_val[3]
            variables[self._c.V_SIGGEN_OFFSET] = input_val[4]
            variables[self._c.V_SIGGEN_AUX_PARAM] = input_val[5:]

    def set_siggen(self, variables, input_val):
        """Set siggen configuration parameters while in continuos mode."""
        if not variables[self._c.V_SIGGEN_ENABLE] or \
                (variables[self._c.V_SIGGEN_ENABLE] and
                 variables[self._c.V_SIGGEN_NUM_CYCLES] == 0):
            variables[self._c.V_SIGGEN_FREQ] = input_val[0]
            variables[self._c.V_SIGGEN_AMPLITUDE] = input_val[1]
            variables[self._c.V_SIGGEN_OFFSET] = input_val[2]

    def enable_siggen(self, variables):
        """Enable siggen."""
        # variables[self._c.V_SIGGEN_ENABLE] = 1
        self._siggen_canceled = False
        thread = _Thread(
            target=self._finish_siggen,
            args=(variables, ),
            daemon=True)
        thread.start()

    def disable_siggen(self, variables):
        """Disable siggen."""
        if variables[self._c.V_SIGGEN_ENABLE] == 1:
            variables[self._c.V_SIGGEN_ENABLE] = 0
            self._siggen_canceled = True
            self._signal.enable = False

    def _set_signal(self, variables):
        t = variables[self._c.V_SIGGEN_TYPE]
        n = variables[self._c.V_SIGGEN_NUM_CYCLES]
        f = variables[self._c.V_SIGGEN_FREQ]
        a = variables[self._c.V_SIGGEN_AMPLITUDE]
        o = variables[self._c.V_SIGGEN_OFFSET]
        p = variables[self._c.V_SIGGEN_AUX_PARAM]
        self._signal = _SignalFactory.factory(type=t,
                                              num_cycles=n,
                                              freq=f,
                                              amplitude=a,
                                              offset=o,
                                              aux_param=p)

    def _finish_siggen(self, variables):
        self._set_signal(variables)
        if self._signal.duration <= 0:
            return
        time = self._signal.duration
        variables[self._c.V_SIGGEN_ENABLE] = 1
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
        variables[self._c.V_PS_REFERENCE] = val
        for iload_id in self._iloads:
            variables[iload_id] = val
        variables[self._c.V_SIGGEN_ENABLE] = 0
        variables[self._c.V_SIGGEN_N] = 0

    def trigger(self, variables):
        """Trigger received."""
        self.enable_siggen(variables)


# --- Specialized PS states ---

class SlowRefStateFAC(_SlowRefState, _FAC):
    """SlowRef FAC state."""

    pass


class SlowRefSyncStateFAC(_SlowRefSyncState, _FAC):
    """SlowRefSync FAC state."""

    pass


class CycleStateFAC(_CycleState, _FAC):
    """Cycle FAC state."""

    pass


class SlowRefStateFBP(_SlowRefState, _FBP):
    """SlowRef FBP state."""

    pass


class SlowRefSyncStateFBP(_SlowRefSyncState, _FBP):
    """SlowRefSync FBP state."""

    pass


class CycleStateFBP(_CycleState, _FBP):
    """Cycle FBP state."""

    pass


class SlowRefStateFBP_DCLINK(_SlowRefState, _FAC_ACDC):
    """SlowRef FAC_ACDC state."""

    pass


class SlowRefStateFAC_ACDC(_SlowRefState, _FAC_ACDC):
    """SlowRef FAC_ACDC state."""

    pass


# --- BSMPSim classes ---

class _GBSMPSim(_BSMPSim):
    """Simulate a PS controller."""

    SlowRefState = 0
    SlowRefSyncState = 1
    CycleState = 2

    def __init__(self, pru):
        """Init."""
        entities = self._get_entities()
        super().__init__(entities)
        self._pru = pru
        self._pru.add_callback(self._trigger)

        # set constants
        self._c = self._get_constants()

        # Set variables initial value
        self._variables = self._get_init_variables()

        # Operation mode states
        self._states = self._get_states()

        # Current state
        self._state = self._states[self.SlowRefState]

    def read_variable(self, var_id):
        """Read variable."""
        while self._pru.sync_block:
            _t.sleep(1e-1)
        return _Response.ok, self._state.read_variable(self._variables, var_id)

    def execute_function(self, func_id, input_val=None):
        """Execute a function."""
        # Switch FBP func ids
        if func_id == self._c.F_TURN_ON:
            self._state.turn_on(self._variables)
        elif func_id == self._c.F_TURN_OFF:
            self._state.turn_off(self._variables)
        elif func_id == self._c.F_OPEN_LOOP:
            self._state.open_loop(self._variables)
        elif func_id == self._c.F_CLOSE_LOOP:
            self._state.close_loop(self._variables)
        elif func_id == self._c.F_SELECT_OP_MODE:  # Change state
            # Verify if ps is on
            if self._is_on():
                psc_status = _PSCStatus(input_val)
                input_val = psc_status.ioc_opmode
                self._state = self._states[input_val]
                self._state.select_op_mode(self._variables)
        elif func_id == self._c.F_RESET_INTERLOCKS:  # Change state
            self._state.reset_interlocks(self._variables)
            self._state = self._states[self.SlowRefState]
        elif func_id == self._c.F_SET_SLOWREF:
            if self._is_on():
                self._state.set_slowref(self._variables, input_val)
        elif func_id == self._c.F_CFG_SIGGEN:
            self._state.cfg_siggen(self._variables, input_val)
        elif func_id == self._c.F_SET_SIGGEN:
            self._state.set_siggen(self._variables, input_val)
        elif func_id == self._c.F_ENABLE_SIGGEN:
            self._state.enable_siggen(self._variables)
        elif func_id == self._c.F_DISABLE_SIGGEN:
            self._state.disable_siggen(self._variables)

        return _Response.ok, None

    def _is_on(self):
        ps_status = self._variables[self._c.V_PS_STATUS]
        psc_status = _PSCStatus(ps_status=ps_status)
        return psc_status.ioc_pwrstate

    def _trigger(self, value=None):
        if self._is_on():
            if value is not None:
                self._state.trigger(self._variables, value)
            else:
                self._state.trigger(self._variables)


class BSMPSimFBP(_GBSMPSim, _FBP):

    def _get_entities(self):
        return _FBPEntities()

    def _get_states(self):
        return [SlowRefStateFBP(), SlowRefSyncStateFBP(),
                CycleStateFBP(self._pru)]

    def _get_init_variables(self):

        firmware = [b'S', b'i', b'm', b'u', b'l', b'a', b't', b'i', b'o', b'n']
        while len(firmware) < 128:
            firmware.append('\x00'.encode())
        variables = [
            0b10000,  # V_PS_STATUS
            0.0, 0.0, firmware, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0,
            [0.0, 0.0, 0.0, 0.0], 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0,
            0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0]
        default_siggen_parms = \
            _SignalFactory.DEFAULT_CONFIGS['Sine']
        variables[_cFBP.V_SIGGEN_TYPE] = default_siggen_parms[0]
        variables[_cFBP.V_SIGGEN_NUM_CYCLES] = default_siggen_parms[1]
        variables[_cFBP.V_SIGGEN_FREQ] = default_siggen_parms[2]
        variables[_cFBP.V_SIGGEN_AMPLITUDE] = default_siggen_parms[3]
        variables[_cFBP.V_SIGGEN_OFFSET] = default_siggen_parms[4]
        variables[_cFBP.V_SIGGEN_AUX_PARAM] = default_siggen_parms[5:9]
        return variables


class BSMPSimFBP_DCLINK(_GBSMPSim, _FBP_DCLINK):

    def _get_entities(self):
        return _FBP_DCLINKEntities()

    def _get_states(self):
        return [SlowRefStateFBP_DCLINK]

    def _get_init_variables(self):
        variables = []
        firmware = [b'S', b'i', b'm', b'u', b'l', b'a', b't', b'i', b'o', b'n']
        while len(firmware) < 128:
            firmware.append('\x00'.encode())
        for idx, variable in enumerate(_FBP_DCLINKEntities.Variables):
            if idx == 3:
                variables[idx] = firmware
            if 'uint' in variable.type:
                variables[idx] = 0
            elif variable.type == 'float':
                variables[idx] = 0
        return variables


class BSMPSimFAC(_GBSMPSim, _FAC):

    def _get_entities(self):
        return _FACEntities()

    def _get_states(self):
        return [SlowRefStateFAC(), SlowRefSyncStateFAC(),
                CycleStateFAC(self._pru)]

    def _get_init_variables(self):
        firmware = [b'S', b'i', b'm', b'u', b'l', b'a', b't', b'i', b'o', b'n']
        while len(firmware) < 128:
            firmware.append('\x00'.encode())
        variables = [
            0b10000,  # V_PS_STATUS
            0.0, 0.0,  # ps_setpoint, ps_reference
            firmware,
            0, 0,  # counters
            0, 0, 0, 0.0, 0.0, 0.0, 0.0, [0.0, 0.0, 0.0, 0.0],  # siggen [6-13]
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # undef [14-24]
            0, 0,  # interlocks [25-26]
            0.0, 0.0,  # iload1, iload2 [27-28]
            0.0, 0.0, 0.0, 0.0, 0.0]  # [29-33]
        default_siggen_parms = \
            _SignalFactory.DEFAULT_CONFIGS['Sine']
        variables[_cFAC.V_SIGGEN_TYPE] = default_siggen_parms[0]
        variables[_cFAC.V_SIGGEN_NUM_CYCLES] = default_siggen_parms[1]
        variables[_cFAC.V_SIGGEN_FREQ] = default_siggen_parms[2]
        variables[_cFAC.V_SIGGEN_AMPLITUDE] = default_siggen_parms[3]
        variables[_cFAC.V_SIGGEN_OFFSET] = default_siggen_parms[4]
        variables[_cFAC.V_SIGGEN_AUX_PARAM] = default_siggen_parms[5:9]
        return variables


class BSMPSimFAC_ACDC(_GBSMPSim, _FAC_ACDC):

    def _get_entities(self):
        return _FAC_ACDCEntities()

    def _get_states(self):
        return [SlowRefStateFAC(), SlowRefSyncStateFAC(),
                CycleStateFAC(self._pru)]

    def _get_init_variables(self):
        firmware = [b'S', b'i', b'm', b'u', b'l', b'a', b't', b'i', b'o', b'n']
        while len(firmware) < 128:
            firmware.append('\x00'.encode())
        variables = [
            0b10000,  # V_PS_STATUS
            0.0, 0.0,  # ps_setpoint, ps_reference
            firmware,
            0, 0,  # counters
            0, 0, 0, 0.0, 0.0, 0.0, 0.0, [0.0, 0.0, 0.0, 0.0],  # siggen [6-13]
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # undef [14-24]
            0, 0,  # interlocks [25-26]
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # [27-32]
        default_siggen_parms = \
            _SignalFactory.DEFAULT_CONFIGS['Sine']
        variables[_cFAC.V_SIGGEN_TYPE] = default_siggen_parms[0]
        variables[_cFAC.V_SIGGEN_NUM_CYCLES] = default_siggen_parms[1]
        variables[_cFAC.V_SIGGEN_FREQ] = default_siggen_parms[2]
        variables[_cFAC.V_SIGGEN_AMPLITUDE] = default_siggen_parms[3]
        variables[_cFAC.V_SIGGEN_OFFSET] = default_siggen_parms[4]
        variables[_cFAC.V_SIGGEN_AUX_PARAM] = default_siggen_parms[5:9]
        return variables


# # --- FBP BSMP controller simulation ---
#
# class FBP_BSMPSim(_BSMPSim):
#     """Simulate a FBP PS controller."""
#
#     I_LOAD_FLUCTUATION_RMS = 0.01
#
#     SlowRefState = 0
#     SlowRefSyncState = 1
#     CycleState = 2
#
#     def __init__(self, pru):
#         """Use FBPEntities."""
#         super().__init__(_FBPEntities())
#         self._pru = pru
#         self._pru.add_callback(self._trigger)
#
#         # Set variables initial value
#         self._variables = self._get_init_variables()
#
#         # Operation mode states
#         self._states = [
#             FBPSlowRefState(), FBPSlowRefSyncState(), FBPCycleState(pru)]
#
#         # Current state
#         self._state = self._states[self.SlowRefState]
#
#     def read_variable(self, var_id):
#         """Read variable."""
#         while self._pru.sync_block:
#             _t.sleep(1e-1)
#         return _Response.ok, self._state.read_variable(self._variables, var_id)
#
#     def execute_function(self, func_id, input_val=None):
#         """Execute a function."""
#         # Switch FBP func ids
#         if func_id == _cFBP.F_TURN_ON:
#             self._state.turn_on(self._variables)
#         elif func_id == _cFBP.F_TURN_OFF:
#             self._state.turn_off(self._variables)
#         elif func_id == _cFBP.F_OPEN_LOOP:
#             self._state.open_loop(self._variables)
#         elif func_id == _cFBP.F_CLOSE_LOOP:
#             self._state.close_loop(self._variables)
#         elif func_id == _cFBP.F_SELECT_OP_MODE:  # Change state
#             # Verify if ps is on
#             if self._is_on():
#                 psc_status = _PSCStatus(input_val)
#                 input_val = psc_status.ioc_opmode
#                 self._state = self._states[input_val]
#                 self._state.select_op_mode(self._variables)
#         elif func_id == _cFBP.F_RESET_INTERLOCKS:  # Change state
#             self._state.reset_interlocks(self._variables)
#             self._state = self._states[self.SlowRefState]
#         elif func_id == _cFBP.F_SET_SLOWREF:
#             if self._is_on():
#                 self._state.set_slowref(self._variables, input_val)
#         elif func_id == _cFBP.F_CFG_SIGGEN:
#             self._state.cfg_siggen(self._variables, input_val)
#         elif func_id == _cFBP.F_SET_SIGGEN:
#             self._state.set_siggen(self._variables, input_val)
#         elif func_id == _cFBP.F_ENABLE_SIGGEN:
#             self._state.enable_siggen(self._variables)
#         elif func_id == _cFBP.F_DISABLE_SIGGEN:
#             self._state.disable_siggen(self._variables)
#
#         return _Response.ok, None
#
#     def _get_init_variables(self):
#         firmware = [b'S', b'i', b'm', b'u', b'l', b'a', b't', b'i', b'o', b'n']
#         while len(firmware) < 128:
#             firmware.append('\x00'.encode())
#         variables = [
#             0b10000,  # V_PS_STATUS
#             0.0, 0.0, firmware, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0,
#             [0.0, 0.0, 0.0, 0.0], 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0,
#             0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0]
#         default_siggen_parms = \
#             _SignalFactory.DEFAULT_CONFIGS['Sine']
#         variables[_cFBP.V_SIGGEN_TYPE] = default_siggen_parms[0]
#         variables[_cFBP.V_SIGGEN_NUM_CYCLES] = default_siggen_parms[1]
#         variables[_cFBP.V_SIGGEN_FREQ] = default_siggen_parms[2]
#         variables[_cFBP.V_SIGGEN_AMPLITUDE] = default_siggen_parms[3]
#         variables[_cFBP.V_SIGGEN_OFFSET] = default_siggen_parms[4]
#         variables[_cFBP.V_SIGGEN_AUX_PARAM] = default_siggen_parms[5:9]
#         return variables
#
#     def _is_on(self):
#         ps_status = self._variables[_cFBP.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         return psc_status.ioc_pwrstate
#
#     def _trigger(self, value=None):
#         if self._is_on():
#             if value is not None:
#                 self._state.trigger(self._variables, value)
#             else:
#                 self._state.trigger(self._variables)
#
#
# class _FBPState:
#     """Represent FBP operation modes."""
#
#     def read_variable(self, variables, var_id):
#         """Read variable."""
#         if var_id == _cFBP.V_I_LOAD:
#             return variables[var_id] + \
#                 _random.gauss(0.0, FBP_BSMPSim.I_LOAD_FLUCTUATION_RMS)
#         value = variables[var_id]
#         return value
#
#     def turn_on(self, variables):
#         """Turn ps on."""
#         ps_status = variables[_cFBP.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         if psc_status.ioc_pwrstate == _PSConst.PwrState.Off:
#             # Set PSController status
#             psc_status.ioc_pwrstate = _PSConst.PwrState.On
#             psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
#             variables[_cFBP.V_PS_STATUS] = psc_status.ps_status
#             # Set currents to 0
#             variables[_cFBP.V_PS_SETPOINT] = 0.0
#             variables[_cFBP.V_PS_REFERENCE] = 0.0
#             variables[_cFBP.V_I_LOAD] = 0.0
#
#     def turn_off(self, variables):
#         """Turn ps off."""
#         ps_status = variables[_cFBP.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         if psc_status.ioc_pwrstate == _PSConst.PwrState.On:
#             # Set PSController status
#             psc_status.ioc_pwrstate = _PSConst.PwrState.Off
#             variables[_cFBP.V_PS_STATUS] = psc_status.ps_status
#             # Set currents to 0
#             variables[_cFBP.V_PS_SETPOINT] = 0.0
#             variables[_cFBP.V_PS_REFERENCE] = 0.0
#             variables[_cFBP.V_I_LOAD] = 0.0
#
#     def open_loop(self, variables):
#         """Open control loop."""
#         ps_status = variables[_cFBP.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         psc_status.open_loop = 1
#         variables[_cFBP.V_PS_STATUS] = psc_status.ps_status
#
#     def close_loop(self, variables):
#         """Close control loop."""
#         ps_status = variables[_cFBP.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         psc_status.open_loop = 0
#         variables[_cFBP.V_PS_STATUS] = psc_status.ps_status
#         variables[_cFBP.V_I_LOAD] = variables[_cFBP.V_PS_REFERENCE]
#
#     def select_op_mode(self, variables):
#         """Set operation mode."""
#         raise NotImplementedError()
#
#     def reset_interlocks(self, variables):
#         """Reset ps."""
#         ps_status = variables[_cFBP.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         # Set PSController status
#         psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
#         variables[_cFBP.V_PS_STATUS] = psc_status.ps_status
#         # Set Current to 0
#         variables[_cFBP.V_PS_SETPOINT] = 0.0
#         variables[_cFBP.V_PS_REFERENCE] = 0.0
#         variables[_cFBP.V_I_LOAD] = 0.0
#         # Reset interlocks
#         variables[_cFBP.V_PS_SOFT_INTERLOCKS] = 0
#         variables[_cFBP.V_PS_HARD_INTERLOCKS] = 0
#
#     def set_slowref(self, variables, input_val):
#         """Set current."""
#         raise NotImplementedError()
#
#     def cfg_siggen(self, variables, input_val):
#         """Config siggen."""
#         raise NotImplementedError()
#
#     def set_siggen(self, variables, input_val):
#         """Set siggen parameters in continuos mode."""
#         raise NotImplementedError()
#
#     def enable_siggen(self, variables):
#         """Enable siggen."""
#         variables[_cFBP.V_SIGGEN_ENABLE] = 1
#
#     def disable_siggen(self, variables):
#         """Disable siggen."""
#         variables[_cFBP.V_SIGGEN_ENABLE] = 0
#
#     def _is_on(self, variables):
#         ps_status = variables[_cFBP.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         return psc_status.ioc_pwrstate
#
#     def _is_open_loop(self, variables):
#         ps_status = variables[_cFBP.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         return psc_status.open_loop
#
#
# class FBPSlowRefState(_FBPState):
#     """FBP SlowRef state."""
#
#     def select_op_mode(self, variables):
#         """Set operation mode."""
#         ps_status = variables[_cFBP.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
#         variables[_cFBP.V_PS_STATUS] = psc_status.ps_status
#         self.set_slowref(variables, variables[_cFBP.V_PS_SETPOINT])
#
#     def set_slowref(self, variables, input_val):
#         """Set current."""
#         variables[_cFBP.V_PS_SETPOINT] = input_val
#         if self._is_on(variables):
#             variables[_cFBP.V_PS_REFERENCE] = input_val
#             if self._is_open_loop(variables) == 0:
#                 # control loop closed
#                 variables[_cFBP.V_I_LOAD] = input_val
#
#     def cfg_siggen(self, variables, input_val):
#         """Set siggen configuration parameters."""
#         variables[_cFBP.V_SIGGEN_TYPE] = input_val[0]
#         variables[_cFBP.V_SIGGEN_NUM_CYCLES] = input_val[1]
#         variables[_cFBP.V_SIGGEN_FREQ] = input_val[2]
#         variables[_cFBP.V_SIGGEN_AMPLITUDE] = input_val[3]
#         variables[_cFBP.V_SIGGEN_OFFSET] = input_val[4]
#         variables[_cFBP.V_SIGGEN_AUX_PARAM] = input_val[5:]
#
#     def set_siggen(self, variables, input_val):
#         """Set siggen configuration parameters while in continuos mode."""
#         variables[_cFBP.V_SIGGEN_FREQ] = input_val[0]
#         variables[_cFBP.V_SIGGEN_AMPLITUDE] = input_val[1]
#         variables[_cFBP.V_SIGGEN_OFFSET] = input_val[2]
#
#     def trigger(self, variables, value):
#         """Slow Ref does nothing when trigger is received."""
#         if self._is_on(variables):
#             variables[_cFBP.V_PS_REFERENCE] = value
#             if self._is_open_loop(variables) == 0:
#                 # control loop closed
#                 variables[_cFBP.V_I_LOAD] = value
#
#
# class FBPSlowRefSyncState(_FBPState):
#
#     def __init__(self):
#         """Init."""
#         self._last_setpoint = None
#
#     def select_op_mode(self, variables):
#         """Set operation mode."""
#         ps_status = variables[_cFBP.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         psc_status.ioc_opmode = _PSConst.OpMode.SlowRefSync
#         variables[_cFBP.V_PS_STATUS] = psc_status.ps_status
#
#     def set_slowref(self, variables, input_val):
#         """Set current."""
#         self._last_setpoint = input_val
#
#     def trigger(self, variables):
#         """Apply last setpoint received."""
#         if self._last_setpoint is None:
#             self._last_setpoint = variables[_cFBP.V_PS_SETPOINT]
#         variables[_cFBP.V_PS_SETPOINT] = self._last_setpoint
#         if self._is_on(variables):
#             variables[_cFBP.V_PS_REFERENCE] = self._last_setpoint
#             if self._is_open_loop(variables) == 0:
#                 # control loop closed
#                 variables[_cFBP.V_I_LOAD] = self._last_setpoint
#
#
# class FBPCycleState(_FBPState):
#     """FBP Cycle state."""
#
#     def __init__(self, pru):
#         """Set cycle parameters."""
#         self._siggen_canceled = False
#         self._pru = pru
#
#     def read_variable(self, variables, var_id):
#         """Return variable."""
#         enbl = variables[_cFBP.V_SIGGEN_ENABLE]
#         if enbl and var_id in (_cFBP.V_PS_REFERENCE, _cFBP.V_I_LOAD):
#             value = self._signal.value
#             variables[_cFBP.V_PS_REFERENCE] = value
#             variables[_cFBP.V_I_LOAD] = value
#             variables[_cFBP.V_SIGGEN_N] += 1
#         return super().read_variable(variables, var_id)
#
#     def select_op_mode(self, variables):
#         """Set operation mode."""
#         ps_status = variables[_cFBP.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         psc_status.ioc_opmode = _PSConst.OpMode.Cycle
#         variables[_cFBP.V_PS_STATUS] = psc_status.ps_status
#         variables[_cFBP.V_SIGGEN_ENABLE] = 0
#         variables[_cFBP.V_PS_REFERENCE] = 0.0
#         variables[_cFBP.V_I_LOAD] = 0.0
#         # self._set_signal(variables)
#         # self.enable_siggen(variables)
#
#     def reset_interlocks(self, variables):
#         """Reset interlocks."""
#         super().reset_interlocks(variables)
#         self.disable_siggen(variables)
#
#     def set_slowref(self, variables, input_val):
#         """Set current."""
#         variables[_cFBP.V_PS_SETPOINT] = input_val
#
#     def cfg_siggen(self, variables, input_val):
#         """Set siggen configuration parameters."""
#         if not variables[_cFBP.V_SIGGEN_ENABLE]:
#             variables[_cFBP.V_SIGGEN_TYPE] = input_val[0]
#             variables[_cFBP.V_SIGGEN_NUM_CYCLES] = input_val[1]
#             variables[_cFBP.V_SIGGEN_FREQ] = input_val[2]
#             variables[_cFBP.V_SIGGEN_AMPLITUDE] = input_val[3]
#             variables[_cFBP.V_SIGGEN_OFFSET] = input_val[4]
#             variables[_cFBP.V_SIGGEN_AUX_PARAM] = input_val[5:]
#
#     def set_siggen(self, variables, input_val):
#         """Set siggen configuration parameters while in continuos mode."""
#         if not variables[_cFBP.V_SIGGEN_ENABLE] or \
#                 (variables[_cFBP.V_SIGGEN_ENABLE] and
#                  variables[_cFBP.V_SIGGEN_NUM_CYCLES] == 0):
#             variables[_cFBP.V_SIGGEN_FREQ] = input_val[0]
#             variables[_cFBP.V_SIGGEN_AMPLITUDE] = input_val[1]
#             variables[_cFBP.V_SIGGEN_OFFSET] = input_val[2]
#
#     def enable_siggen(self, variables):
#         """Enable siggen."""
#         # variables[_cFBP.V_SIGGEN_ENABLE] = 1
#         self._siggen_canceled = False
#         thread = _Thread(
#             target=self._finish_siggen,
#             args=(variables, ),
#             daemon=True)
#         thread.start()
#
#     def disable_siggen(self, variables):
#         """Disable siggen."""
#         if variables[_cFBP.V_SIGGEN_ENABLE] == 1:
#             variables[_cFBP.V_SIGGEN_ENABLE] = 0
#             self._siggen_canceled = True
#             self._signal.enable = False
#
#     def _set_signal(self, variables):
#         t = variables[_cFBP.V_SIGGEN_TYPE]
#         n = variables[_cFBP.V_SIGGEN_NUM_CYCLES]
#         f = variables[_cFBP.V_SIGGEN_FREQ]
#         a = variables[_cFBP.V_SIGGEN_AMPLITUDE]
#         o = variables[_cFBP.V_SIGGEN_OFFSET]
#         p = variables[_cFBP.V_SIGGEN_AUX_PARAM]
#         self._signal = _SignalFactory.factory(type=t,
#                                               num_cycles=n,
#                                               freq=f,
#                                               amplitude=a,
#                                               offset=o,
#                                               aux_param=p)
#
#     def _finish_siggen(self, variables):
#         self._set_signal(variables)
#         if self._signal.duration <= 0:
#             return
#         time = self._signal.duration
#         variables[_cFBP.V_SIGGEN_ENABLE] = 1
#         time_up = False
#         elapsed = 0
#         while not time_up:
#             _t.sleep(0.5)
#             elapsed += 0.5
#             if elapsed >= time:
#                 time_up = True
#             if self._siggen_canceled:
#                 return
#         val = self._signal.value
#         variables[_cFBP.V_PS_REFERENCE] = val
#         variables[_cFBP.V_I_LOAD] = val
#         variables[_cFBP.V_SIGGEN_ENABLE] = 0
#         variables[_cFBP.V_SIGGEN_N] = 0
#
#     def trigger(self, variables):
#         """Trigger received."""
#         self.enable_siggen(variables)
#
#
# # --- FBP BSMP controller simulation ---
#
#
# class FAC_BSMPSim(_BSMPSim):
#     """Simulate a FAC PS controller."""
#
#     I_LOAD_FLUCTUATION_RMS = 0.01
#
#     SlowRefState = 0
#     SlowRefSyncState = 1
#     CycleState = 2
#
#     def __init__(self, pru):
#         """Use FACEntities."""
#         super().__init__(_FACEntities())
#         self._pru = pru
#         self._pru.add_callback(self._trigger)
#
#         # Set variables initial value
#         self._variables = self._get_init_variables()
#
#         # Operation mode states
#         self._states = [
#             FACSlowRefState(), FACSlowRefSyncState(), FACCycleState(pru)]
#
#         # Current state
#         self._state = self._states[self.SlowRefState]
#
#     def read_variable(self, var_id):
#         """Read variable."""
#         while self._pru.sync_block:
#             _t.sleep(1e-1)
#         return _Response.ok, self._state.read_variable(self._variables, var_id)
#
#     def execute_function(self, func_id, input_val=None):
#         """Execute a function."""
#         # Switch FBP func ids
#         if func_id == _cFAC.F_TURN_ON:
#             self._state.turn_on(self._variables)
#         elif func_id == _cFAC.F_TURN_OFF:
#             self._state.turn_off(self._variables)
#         elif func_id == _cFAC.F_OPEN_LOOP:
#             self._state.open_loop(self._variables)
#         elif func_id == _cFAC.F_CLOSE_LOOP:
#             self._state.close_loop(self._variables)
#         elif func_id == _cFAC.F_SELECT_OP_MODE:  # Change state
#             # Verify if ps is on
#             if self._is_on():
#                 psc_status = _PSCStatus(input_val)
#                 input_val = psc_status.ioc_opmode
#                 self._state = self._states[input_val]
#                 self._state.select_op_mode(self._variables)
#         elif func_id == _cFAC.F_RESET_INTERLOCKS:  # Change state
#             self._state.reset_interlocks(self._variables)
#             self._state = self._states[self.SlowRefState]
#         elif func_id == _cFAC.F_SET_SLOWREF:
#             if self._is_on():
#                 self._state.set_slowref(self._variables, input_val)
#         elif func_id == _cFAC.F_CFG_SIGGEN:
#             self._state.cfg_siggen(self._variables, input_val)
#         elif func_id == _cFAC.F_SET_SIGGEN:
#             self._state.set_siggen(self._variables, input_val)
#         elif func_id == _cFAC.F_ENABLE_SIGGEN:
#             self._state.enable_siggen(self._variables)
#         elif func_id == _cFAC.F_DISABLE_SIGGEN:
#             self._state.disable_siggen(self._variables)
#
#         return _Response.ok, None
#
#     def _get_init_variables(self):
#         firmware = [b'S', b'i', b'm', b'u', b'l', b'a', b't', b'i', b'o', b'n']
#         while len(firmware) < 128:
#             firmware.append('\x00'.encode())
#         variables = [
#             0b10000,  # V_PS_STATUS
#             0.0, 0.0,  # ps_setpoint, ps_reference
#             firmware,
#             0, 0,  # counters
#             0, 0, 0, 0.0, 0.0, 0.0, 0.0, [0.0, 0.0, 0.0, 0.0],  # siggen [6-13]
#             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # undef [14-24]
#             0, 0,  # interlocks [25-26]
#             0.0, 0.0,  # iload1, iload2 [27-28]
#             0.0, 0.0, 0.0, 0.0, 0.0]  # [29-33]
#         default_siggen_parms = \
#             _SignalFactory.DEFAULT_CONFIGS['Sine']
#         variables[_cFAC.V_SIGGEN_TYPE] = default_siggen_parms[0]
#         variables[_cFAC.V_SIGGEN_NUM_CYCLES] = default_siggen_parms[1]
#         variables[_cFAC.V_SIGGEN_FREQ] = default_siggen_parms[2]
#         variables[_cFAC.V_SIGGEN_AMPLITUDE] = default_siggen_parms[3]
#         variables[_cFAC.V_SIGGEN_OFFSET] = default_siggen_parms[4]
#         variables[_cFAC.V_SIGGEN_AUX_PARAM] = default_siggen_parms[5:9]
#         return variables
#
#     def _is_on(self):
#         ps_status = self._variables[_cFAC.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         return psc_status.ioc_pwrstate
#
#     def _trigger(self, value=None):
#         if self._is_on():
#             if value is not None:
#                 self._state.trigger(self._variables, value)
#             else:
#                 self._state.trigger(self._variables)
#
#
# class _FACState:
#     """Represent FAC operation modes."""
#
#     def read_variable(self, variables, var_id):
#         """Read variable."""
#         if var_id == _cFAC.V_I_LOAD1:
#             return variables[var_id] + \
#                 _random.gauss(0.0, FAC_BSMPSim.I_LOAD_FLUCTUATION_RMS)
#         if var_id == _cFAC.V_I_LOAD2:
#             return variables[var_id] + \
#                 _random.gauss(0.0, FAC_BSMPSim.I_LOAD_FLUCTUATION_RMS)
#         value = variables[var_id]
#         return value
#
#     def turn_on(self, variables):
#         """Turn ps on."""
#         ps_status = variables[_cFAC.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         if psc_status.ioc_pwrstate == _PSConst.PwrState.Off:
#             # Set PSController status
#             psc_status.ioc_pwrstate = _PSConst.PwrState.On
#             psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
#             variables[_cFAC.V_PS_STATUS] = psc_status.ps_status
#             # Set currents to 0
#             variables[_cFAC.V_PS_SETPOINT] = 0.0
#             variables[_cFAC.V_PS_REFERENCE] = 0.0
#             variables[_cFAC.V_I_LOAD1] = 0.0
#             variables[_cFAC.V_I_LOAD2] = 0.0
#
#     def turn_off(self, variables):
#         """Turn ps off."""
#         ps_status = variables[_cFAC.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         if psc_status.ioc_pwrstate == _PSConst.PwrState.On:
#             # Set PSController status
#             psc_status.ioc_pwrstate = _PSConst.PwrState.Off
#             variables[_cFAC.V_PS_STATUS] = psc_status.ps_status
#             # Set currents to 0
#             variables[_cFAC.V_PS_SETPOINT] = 0.0
#             variables[_cFAC.V_PS_REFERENCE] = 0.0
#             variables[_cFAC.V_I_LOAD1] = 0.0
#             variables[_cFAC.V_I_LOAD2] = 0.0
#
#     def open_loop(self, variables):
#         """Open control loop."""
#         ps_status = variables[_cFAC.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         psc_status.open_loop = 1
#         variables[_cFAC.V_PS_STATUS] = psc_status.ps_status
#
#     def close_loop(self, variables):
#         """Close control loop."""
#         ps_status = variables[_cFAC.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         psc_status.open_loop = 0
#         variables[_cFAC.V_PS_STATUS] = psc_status.ps_status
#         variables[_cFAC.V_I_LOAD1] = variables[_cFAC.V_PS_REFERENCE]
#         variables[_cFAC.V_I_LOAD2] = variables[_cFAC.V_PS_REFERENCE]
#
#     def select_op_mode(self, variables):
#         """Set operation mode."""
#         raise NotImplementedError()
#
#     def reset_interlocks(self, variables):
#         """Reset ps."""
#         ps_status = variables[_cFAC.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         # Set PSController status
#         psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
#         variables[_cFAC.V_PS_STATUS] = psc_status.ps_status
#         # Set Current to 0
#         variables[_cFAC.V_PS_SETPOINT] = 0.0
#         variables[_cFAC.V_PS_REFERENCE] = 0.0
#         variables[_cFAC.V_I_LOAD1] = 0.0
#         variables[_cFAC.V_I_LOAD2] = 0.0
#         # Reset interlocks
#         variables[_cFAC.V_PS_SOFT_INTERLOCKS] = 0
#         variables[_cFAC.V_PS_HARD_INTERLOCKS] = 0
#
#     def set_slowref(self, variables, input_val):
#         """Set current."""
#         raise NotImplementedError()
#
#     def cfg_siggen(self, variables, input_val):
#         """Config siggen."""
#         raise NotImplementedError()
#
#     def set_siggen(self, variables, input_val):
#         """Set siggen parameters in continuos mode."""
#         raise NotImplementedError()
#
#     def enable_siggen(self, variables):
#         """Enable siggen."""
#         variables[_cFAC.V_SIGGEN_ENABLE] = 1
#
#     def disable_siggen(self, variables):
#         """Disable siggen."""
#         variables[_cFAC.V_SIGGEN_ENABLE] = 0
#
#     def _is_on(self, variables):
#         ps_status = variables[_cFAC.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         return psc_status.ioc_pwrstate
#
#     def _is_open_loop(self, variables):
#         ps_status = variables[_cFAC.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         return psc_status.open_loop
#
#
# class FACSlowRefState(_FACState):
#     """FBP SlowRef state."""
#
#     def select_op_mode(self, variables):
#         """Set operation mode."""
#         ps_status = variables[_cFAC.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         psc_status.ioc_opmode = _PSConst.OpMode.SlowRef
#         variables[_cFAC.V_PS_STATUS] = psc_status.ps_status
#         self.set_slowref(variables, variables[_cFAC.V_PS_SETPOINT])
#
#     def set_slowref(self, variables, input_val):
#         """Set current."""
#         variables[_cFAC.V_PS_SETPOINT] = input_val
#         if self._is_on(variables):
#             variables[_cFAC.V_PS_REFERENCE] = input_val
#             if self._is_open_loop(variables) == 0:
#                 # control loop closed
#                 variables[_cFAC.V_I_LOAD1] = input_val
#                 variables[_cFAC.V_I_LOAD2] = input_val
#
#     def cfg_siggen(self, variables, input_val):
#         """Set siggen configuration parameters."""
#         variables[_cFAC.V_SIGGEN_TYPE] = input_val[0]
#         variables[_cFAC.V_SIGGEN_NUM_CYCLES] = input_val[1]
#         variables[_cFAC.V_SIGGEN_FREQ] = input_val[2]
#         variables[_cFAC.V_SIGGEN_AMPLITUDE] = input_val[3]
#         variables[_cFAC.V_SIGGEN_OFFSET] = input_val[4]
#         variables[_cFAC.V_SIGGEN_AUX_PARAM] = input_val[5:]
#
#     def set_siggen(self, variables, input_val):
#         """Set siggen configuration parameters while in continuos mode."""
#         variables[_cFAC.V_SIGGEN_FREQ] = input_val[0]
#         variables[_cFAC.V_SIGGEN_AMPLITUDE] = input_val[1]
#         variables[_cFAC.V_SIGGEN_OFFSET] = input_val[2]
#
#     def trigger(self, variables, value):
#         """Slow Ref does nothing when trigger is received."""
#         if self._is_on(variables):
#             variables[_cFAC.V_PS_REFERENCE] = value
#             if self._is_open_loop(variables) == 0:
#                 # control loop closed
#                 variables[_cFAC.V_I_LOAD1] = value
#                 variables[_cFAC.V_I_LOAD2] = value
#
#
# class FACSlowRefSyncState(_FACState):
#
#     def __init__(self):
#         """Init."""
#         self._last_setpoint = None
#
#     def select_op_mode(self, variables):
#         """Set operation mode."""
#         ps_status = variables[_cFAC.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         psc_status.ioc_opmode = _PSConst.OpMode.SlowRefSync
#         variables[_cFAC.V_PS_STATUS] = psc_status.ps_status
#
#     def set_slowref(self, variables, input_val):
#         """Set current."""
#         self._last_setpoint = input_val
#
#     def trigger(self, variables):
#         """Apply last setpoint received."""
#         if self._last_setpoint is None:
#             self._last_setpoint = variables[_cFAC.V_PS_SETPOINT]
#         variables[_cFAC.V_PS_SETPOINT] = self._last_setpoint
#         if self._is_on(variables):
#             variables[_cFAC.V_PS_REFERENCE] = self._last_setpoint
#             if self._is_open_loop(variables) == 0:
#                 # control loop closed
#                 variables[_cFAC.V_I_LOAD1] = self._last_setpoint
#                 variables[_cFAC.V_I_LOAD2] = self._last_setpoint
#
#
# class FACCycleState(_FACState):
#     """FBP Cycle state."""
#
#     def __init__(self, pru):
#         """Set cycle parameters."""
#         self._siggen_canceled = False
#         self._pru = pru
#
#     def read_variable(self, variables, var_id):
#         """Return variable."""
#         enbl = variables[_cFAC.V_SIGGEN_ENABLE]
#         if enbl and var_id in (_cFAC.V_PS_REFERENCE, _cFAC.V_I_LOAD1,
#                                _cFAC.V_I_LOAD2):
#             value = self._signal.value
#             variables[_cFAC.V_PS_REFERENCE] = value
#             variables[_cFAC.V_I_LOAD1] = value
#             variables[_cFAC.V_I_LOAD2] = value
#             variables[_cFAC.V_SIGGEN_N] += 1
#         return super().read_variable(variables, var_id)
#
#     def select_op_mode(self, variables):
#         """Set operation mode."""
#         ps_status = variables[_cFAC.V_PS_STATUS]
#         psc_status = _PSCStatus(ps_status=ps_status)
#         psc_status.ioc_opmode = _PSConst.OpMode.Cycle
#         variables[_cFAC.V_PS_STATUS] = psc_status.ps_status
#         variables[_cFAC.V_SIGGEN_ENABLE] = 0
#         variables[_cFAC.V_PS_REFERENCE] = 0.0
#         variables[_cFAC.V_I_LOAD1] = 0.0
#         variables[_cFAC.V_I_LOAD2] = 0.0
#         # self._set_signal(variables)
#         # self.enable_siggen(variables)
#
#     def reset_interlocks(self, variables):
#         """Reset interlocks."""
#         super().reset_interlocks(variables)
#         self.disable_siggen(variables)
#
#     def set_slowref(self, variables, input_val):
#         """Set current."""
#         variables[_cFAC.V_PS_SETPOINT] = input_val
#
#     def cfg_siggen(self, variables, input_val):
#         """Set siggen configuration parameters."""
#         if not variables[_cFAC.V_SIGGEN_ENABLE]:
#             variables[_cFAC.V_SIGGEN_TYPE] = input_val[0]
#             variables[_cFAC.V_SIGGEN_NUM_CYCLES] = input_val[1]
#             variables[_cFAC.V_SIGGEN_FREQ] = input_val[2]
#             variables[_cFAC.V_SIGGEN_AMPLITUDE] = input_val[3]
#             variables[_cFAC.V_SIGGEN_OFFSET] = input_val[4]
#             variables[_cFAC.V_SIGGEN_AUX_PARAM] = input_val[5:]
#
#     def set_siggen(self, variables, input_val):
#         """Set siggen configuration parameters while in continuos mode."""
#         if not variables[_cFAC.V_SIGGEN_ENABLE] or \
#                 (variables[_cFAC.V_SIGGEN_ENABLE] and
#                  variables[_cFAC.V_SIGGEN_NUM_CYCLES] == 0):
#             variables[_cFAC.V_SIGGEN_FREQ] = input_val[0]
#             variables[_cFAC.V_SIGGEN_AMPLITUDE] = input_val[1]
#             variables[_cFAC.V_SIGGEN_OFFSET] = input_val[2]
#
#     def enable_siggen(self, variables):
#         """Enable siggen."""
#         # variables[_cFAC.V_SIGGEN_ENABLE] = 1
#         self._siggen_canceled = False
#         thread = _Thread(
#             target=self._finish_siggen,
#             args=(variables, ),
#             daemon=True)
#         thread.start()
#
#     def disable_siggen(self, variables):
#         """Disable siggen."""
#         if variables[_cFAC.V_SIGGEN_ENABLE] == 1:
#             variables[_cFAC.V_SIGGEN_ENABLE] = 0
#             self._siggen_canceled = True
#             self._signal.enable = False
#
#     def _set_signal(self, variables):
#         t = variables[_cFAC.V_SIGGEN_TYPE]
#         n = variables[_cFAC.V_SIGGEN_NUM_CYCLES]
#         f = variables[_cFAC.V_SIGGEN_FREQ]
#         a = variables[_cFAC.V_SIGGEN_AMPLITUDE]
#         o = variables[_cFAC.V_SIGGEN_OFFSET]
#         p = variables[_cFAC.V_SIGGEN_AUX_PARAM]
#         self._signal = _SignalFactory.factory(type=t,
#                                               num_cycles=n,
#                                               freq=f,
#                                               amplitude=a,
#                                               offset=o,
#                                               aux_param=p)
#
#     def _finish_siggen(self, variables):
#         self._set_signal(variables)
#         if self._signal.duration <= 0:
#             return
#         time = self._signal.duration
#         variables[_cFAC.V_SIGGEN_ENABLE] = 1
#         time_up = False
#         elapsed = 0
#         while not time_up:
#             _t.sleep(0.5)
#             elapsed += 0.5
#             if elapsed >= time:
#                 time_up = True
#             if self._siggen_canceled:
#                 return
#         val = self._signal.value
#         variables[_cFAC.V_PS_REFERENCE] = val
#         variables[_cFAC.V_I_LOAD1] = val
#         variables[_cFAC.V_I_LOAD2] = val
#         variables[_cFAC.V_SIGGEN_ENABLE] = 0
#         variables[_cFAC.V_SIGGEN_N] = 0
#
#     def trigger(self, variables):
#         """Trigger received."""
#         self.enable_siggen(variables)
#
