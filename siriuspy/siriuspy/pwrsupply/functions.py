"""Define functions used to map an epics field to a BSMP entity id.

These classes implement a command interface, that is, they have
an `execute` method.
"""
import time as _time

# BSMP and PS constants
from siriuspy.pwrsupply.bsmp import ConstBSMP as _c
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.pwrsupply.status import PSCStatus as _PSCStatus

# _delay_turn_on_off = 0.3  # [s]
# _delay_loop_open_close = 0.3  # [s]
# These updated values are based on what Gabriel indicated.

# NOTE: delete these delays
# the way the communication threads work in PRUController make these
# parameters immaterial for the case of a single beaglebone with multiple
# UDCs.
_delay_turn_on_off = 0.010  # [s]
_delay_loop_open_close = 0.150  # [s]


class Function:
    """Generic function class."""

    def execute(self, value):
        """Execute function."""
        raise NotImplementedError()


class BSMPFunction(Function):
    """Used PRU controller to execute a function."""

    def __init__(self, device_ids, pru_controller, func_id, setpoints=()):
        """Get controller and bsmp function id."""
        self._device_ids = device_ids
        self.pru_controller = pru_controller
        self.func_id = func_id
        self.setpoints = setpoints

    def execute(self, value=None):
        """Execute command."""
        if not self.setpoints or \
                (self.setpoints and self.setpoints.apply(value)):
            if value is None:
                self.pru_controller.exec_functions(
                    self._device_ids, self.func_id)
            else:
                self.pru_controller.exec_functions(
                    self._device_ids, self.func_id, value)


class Command(BSMPFunction):
    """Execute a Cmd type PV."""

    def execute(self, value=None):
        """Execute command."""
        if not self.setpoints or \
                (self.setpoints and self.setpoints.apply(value)):
            self.pru_controller.exec_functions(self._device_ids, self.func_id)


class BSMPFunctionNull(BSMPFunction):
    """Do nothing."""

    def __init__(self):
        """Do nothing."""
        super().__init__(None, None, None)

    def execute(self, value):
        """Do nothing."""
        pass


class PRUCurve(Function):
    """Executes a pru curve write command."""

    def __init__(self, device_ids, pru_controller, setpoints=()):
        """Get pru controller."""
        self._device_ids = device_ids
        self.pru_controller = pru_controller
        self.setpoints = setpoints

    def execute(self, value=None):
        """Execute command."""
        if not self.setpoints or \
                (self.setpoints and self.setpoints.apply(value)):
            for dev_id in self._device_ids:
                self.pru_controller.pru_curve_write(dev_id, value)


class PSCurvesAcqCmd(Function):
    """Executes a ps curve update."""

    def __init__(self, device_ids, pru_controller, setpoints=()):
        """Get pru controller."""
        self._device_ids = device_ids
        self.pru_controller = pru_controller
        self.setpoints = setpoints

    def execute(self, value=None):
        """Execute command."""
        if not self.setpoints or \
                (self.setpoints and self.setpoints.apply(value)):
            self.pru_controller.update_ps_curves(self._device_ids, 0)
            self.pru_controller.update_ps_curves(self._device_ids, 1)
            self.pru_controller.update_ps_curves(self._device_ids, 2)


class PRUProperty(Function):
    """Executes a PRUProperty command."""

    def __init__(self, pru_controller, property_name, setpoints=()):
        """Get pru controller."""
        self.pru_controller = pru_controller
        self.property = property_name
        self.setpoints = setpoints

    def execute(self, value=None):
        """Execute command."""
        if not self.setpoints or \
                (self.setpoints and self.setpoints.apply(value)):
            setattr(self.pru_controller, self.property, value)


class PSPwrState(Function):
    """Adapter to deal with FBP turn on/off functions."""

    def __init__(self, device_ids, pru_controller, setpoints=None):
        """Define function."""
        self._device_ids = device_ids
        self.turn_on = BSMPFunction(
            device_ids, pru_controller, _c.F_TURN_ON)
        self.close_loop = BSMPFunction(
            device_ids, pru_controller, _c.F_CLOSE_LOOP)
        self.turn_off = BSMPFunction(
            device_ids, pru_controller, _c.F_TURN_OFF)
        self.setpoints = setpoints

    def execute(self, value=None):
        """Execute Command."""
        if not self.setpoints or \
                (self.setpoints and self.setpoints.apply(value)):
            if value == 1:
                self.turn_on.execute()
                # _time.sleep(_delay_turn_on_off)
                self.close_loop.execute()
                # _time.sleep(_delay_loop_open_close)
            elif value == 0:
                self.turn_off.execute()
                # _time.sleep(_delay_turn_on_off)


class PSCurvesAcq(Function):
    """Enable/Disable curve acquisition."""

    def __init__(self, device_ids, pru_controller, setpoints=None):
        """Define CurveAcq."""
        self._device_ids = device_ids
        self.enable = BSMPFunction(
            device_ids, pru_controller, _c.F_ENABLE_BUF_SAMPLES)
        self.disable = BSMPFunction(
            device_ids, pru_controller, _c.F_DISABLE_BUF_SAMPLES)
        self.setpoints = setpoints

    def execute(self, value=None):
        """Execute Command."""
        if not self.setpoints or \
                (self.setpoints and self.setpoints.apply(value)):
            if value == 1:
                self.enable.execute()
            elif value == 0:
                self.disable.execute()


class BSMPComm(Function):
    """Adapter to deal with turning PRUController BSMP comm on and off."""

    def __init__(self, pru_controller, setpoints=None):
        """Init."""
        self.pru_controller = pru_controller
        self.setpoints = setpoints

    def execute(self, value=None):
        """Execute command."""
        if not self.setpoints or \
                self.setpoints.apply(value):
            if value == 1:
                self.pru_controller.bsmpcomm = True
            elif value == 0:
                self.pru_controller.bsmpcomm = False


class PSPwrStateFBP_DCLink(Function):
    """Adapter to deal with FBP_DCLink turn on/off functions."""

    def __init__(self, device_ids, pru_controller, setpoints=None):
        """Define function."""
        self.setpoints = setpoints
        self.turn_on = BSMPFunction(
            device_ids, pru_controller, _c.F_TURN_ON)
        self.turn_off = BSMPFunction(
            device_ids, pru_controller, _c.F_TURN_OFF)
        self.open_loop = BSMPFunction(
            device_ids, pru_controller, _c.F_OPEN_LOOP)

    def execute(self, value=None):
        """Execute Command."""
        if not self.setpoints or \
                (self.setpoints and self.setpoints.apply(value)):
            if value == _PSConst.PwrStateSel.On:
                self.turn_on.execute()
            elif value == _PSConst.PwrStateSel.Off:
                self.turn_off.execute()


class CtrlLoop(Function):
    """Adapter to close or open control loops."""

    def __init__(self, device_ids, pru_controller, setpoints=None):
        """Define function."""
        self.pru_controller = pru_controller
        self.setpoints = setpoints
        self.open_loop = BSMPFunction(
            device_ids, pru_controller, _c.F_OPEN_LOOP)
        self.close_loop = BSMPFunction(
            device_ids, pru_controller, _c.F_CLOSE_LOOP)

    def execute(self, value=None):
        """Execute Command."""
        if not self.setpoints or \
                (self.setpoints and self.setpoints.apply(value)):
            if value == 1:
                self.open_loop.execute(None)
                # _time.sleep(_delay_loop_open_close)
            elif value == 0:
                self.close_loop.execute(None)
                # _time.sleep(_delay_loop_open_close)


class PSOpMode(Function):
    """Decorate a function."""

    def __init__(self, device_ids, function, setpoints=None):
        """Command."""
        self._device_ids = device_ids
        self.function = function
        self.disable_siggen = \
            BSMPFunction(device_ids, function.pru_controller,
                         _c.F_DISABLE_SIGGEN)
        self.setpoints = setpoints

    def execute(self, value=None):
        """Parse before executing."""
        if not self.setpoints or \
                (self.setpoints and self.setpoints.apply(value)):
            op_mode = value
            if value == _PSConst.OpMode.SlowRef:
                op_mode = _PSConst.States.SlowRef
            elif value == _PSConst.OpMode.SlowRefSync:
                op_mode = _PSConst.States.SlowRefSync
            elif value == _PSConst.OpMode.Cycle:
                op_mode = _PSConst.States.Cycle
            elif value == _PSConst.OpMode.RmpWfm:
                op_mode = _PSConst.States.SlowRef  # RmpWfm -> SlowRef
                # op_mode = _PSConst.States.FastRef  # RmpWfm -> FastRef
            elif value == _PSConst.OpMode.MigWfm:
                op_mode = _PSConst.States.SlowRef  # MigWfm -> SlowRef
                # op_mode = _PSConst.States.FastRef  # MigWfm -> FastRef
            else:
                op_mode = value

            self.function.execute(op_mode)

            # NOTE: should this be set only when changing to SlowRef?
            if value == _PSConst.OpMode.SlowRef:
                self.disable_siggen.execute(None)


class Current(Function):
    """Command to set current in PSs linked to magnets."""

    def __init__(self, device_ids, pru_controller, setpoints=None):
        """Create command to set current."""
        self._device_ids = device_ids
        self.pru_controller = pru_controller
        self.set_current = BSMPFunction(
            device_ids, pru_controller, _c.F_SET_SLOWREF)
        self.setpoints = setpoints

    def execute(self, value=None):
        """Execute command."""
        if not self.setpoints or \
                (self.setpoints and self.setpoints.apply(value)):
            op_modes = [_PSCStatus(self.pru_controller.read_variables(
                device_id, 0)).state for device_id in self._device_ids]
            slowsync = False
            if _PSConst.States.SlowRefSync in op_modes:
                slowsync = True
                self.pru_controller.pru_sync_stop()

            self.set_current.execute(value)

            if slowsync:
                self.pru_controller.pru_sync_start(0x5B)


class Voltage(Function):
    """Command to set voltage in DCLink type PS."""

    def __init__(self, device_ids, pru_controller, setpoints=None):
        """Create command to set voltage."""
        self.device_ids = device_ids
        func_id = _c.F_SET_SLOWREF
        self.set_voltage = BSMPFunction(device_ids, pru_controller, func_id)
        self.setpoints = setpoints

    def execute(self, value=None):
        """Execute command."""
        if not self.setpoints or \
                (self.setpoints and self.setpoints.apply(value)):
            self.set_voltage.execute()


class CfgSiggen(Function):
    """Command to configure siggen."""

    def __init__(self, device_ids, pru_controller, idx, setpoints=None):
        """Init."""
        self._idx = idx
        self._setpoints = setpoints
        self._cfg = BSMPFunction(
            device_ids, pru_controller, _c.F_CFG_SIGGEN)

    def execute(self, value=None):
        """Execute command."""
        if self._idx == 5:
            if not self._setpoints or \
                    (self._setpoints and
                     self._setpoints.apply(value[self._idx:])):
                self._cfg.execute(value)
        else:
            if not self._setpoints or \
                    (self._setpoints and
                     self._setpoints.apply(value[self._idx])):
                self._cfg.execute(value)
