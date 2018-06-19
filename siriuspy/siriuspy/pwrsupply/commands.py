"""Define commands use to maps an epics field to a BSMP entity id.

These classes implement a Command interface, that is, they have
an `execute` method.
"""
import time as _time

# BSMP and PS constants
from siriuspy.pwrsupply import bsmp as _bsmp
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.pwrsupply.status import PSCStatus as _PSCStatus


# TODO: check with ELP group how short these delays can be
_delay_turn_on_off = 0.3  # [s]
_delay_loop_open_close = 0.3  # [s]


class CommandFactory:
    """Build command objects."""

    @staticmethod
    def get(psmodel, epics_field, pru_controller):
        """Return an object that implemets the Command interface."""
        if psmodel == 'FBP':
            return CommandFactory._get_FBP(epics_field, pru_controller)
        elif psmodel == 'FBP_DCLink':
            return CommandFactory._get_FBP_DCLink(epics_field, pru_controller)
        elif psmodel == 'FAC':
            return CommandFactory._get_FAC(epics_field, pru_controller)
        else:
            raise NotImplementedError('Fields not implemented for ' + psmodel)

    def _get_FBP(epics_field, pru_controller):
        _c = _bsmp.ConstFBP
        if epics_field == 'PwrState-Sel':
            return PSPwrState(pru_controller)
        elif epics_field == 'CtrlLoop-Sel':
            return CtrlLoop(pru_controller)
        elif epics_field == 'OpMode-Sel':
            return PSOpMode(Command(pru_controller, _c.F_SELECT_OP_MODE))
        elif epics_field == 'Current-SP':
            return Setpoint(pru_controller)
        elif epics_field == 'Reset-Cmd':
            return Command(pru_controller, _c.F_RESET_INTERLOCKS)
        elif epics_field == 'Abort-Cmd':
            return NullCommand()
        elif epics_field == 'CycleDsbl-Cmd':
            return Command(pru_controller, _c.F_DISABLE_SIGGEN)
        elif epics_field in ('CycleType-Sel', 'CycleNrCycles-SP',
                             'CycleFreq-SP', 'CycleAmpl-SP',
                             'CycleOffset-SP', 'CycleAuxParam-SP'):
            return Command(pru_controller, _c.F_CFG_SIGGEN)
        elif epics_field == 'WfmData-SP':
            return PRUCurveCommand(pru_controller)
        else:
            return NullCommand()

    def _get_FBP_DCLink(epics_field, pru_controller):
        _c = _bsmp.ConstFBP_DCLink
        if epics_field == 'PwrState-Sel':
            return PSPwrStateFBP_DCLink(pru_controller)
        elif epics_field == 'CtrlLoop-Sel':
            return CtrlLoop(pru_controller)
        elif epics_field == 'OpMode-Sel':
            return PSOpMode(Command(pru_controller, _c.F_SELECT_OP_MODE))
        elif epics_field == 'Voltage-SP':
            return Setpoint(pru_controller)
        elif epics_field == 'Reset-Cmd':
            return Command(pru_controller, _c.F_RESET_INTERLOCKS)
        elif epics_field == 'Abort-Cmd':
            return NullCommand()
        else:
            return NullCommand()

    def _get_FAC(epics_field, pru_controller):
        _c = _bsmp.ConstFAC_DCDC
        if epics_field == 'PwrState-Sel':
            return PSPwrState(pru_controller)
        elif epics_field == 'CtrlLoop-Sel':
            return CtrlLoop(pru_controller)
        elif epics_field == 'OpMode-Sel':
            return PSOpMode(Command(pru_controller, _c.F_SELECT_OP_MODE))
        elif epics_field == 'Current-SP':
            return Setpoint(pru_controller)
        elif epics_field == 'Reset-Cmd':
            return Command(pru_controller, _c.F_RESET_INTERLOCKS)
        elif epics_field == 'Abort-Cmd':
            return NullCommand()
        elif epics_field == 'CycleDsbl-Cmd':
            return Command(pru_controller, _c.F_DISABLE_SIGGEN)
        elif epics_field in ('CycleType-Sel', 'CycleNrCycles-SP',
                             'CycleFreq-SP', 'CycleAmpl-SP',
                             'CycleOffset-SP', 'CycleAuxParam-SP'):
            return Command(pru_controller, _c.F_CFG_SIGGEN)
        elif epics_field == 'WfmData-SP':
            return PRUCurveCommand(pru_controller)
        else:
            return NullCommand()


class SimpleCommand:
    """Used PRU controller to execute a function without args."""

    def __init__(self, pru_controller, func_id):
        """Define commands."""
        self.pru_controller = pru_controller
        self.func_id = func_id

    def execute(self, device_ids, value=None):
        """Execute Command."""
        self.pru_controller.exec_functions(device_ids, self.func_id)


class Command:
    """Used PRU controller to execute a function."""

    def __init__(self, pru_controller, bsmp_id):
        """Get controller and bsmp function id."""
        self.pru_controller = pru_controller
        self.bsmp_id = bsmp_id

    def execute(self, device_ids, value=None):
        """Execute command."""
        if value is None:
            self.pru_controller.exec_functions(device_ids, self.bsmp_id)
        else:
            self.pru_controller.exec_functions(device_ids, self.bsmp_id, value)


class NullCommand(Command):
    """Do nothing."""

    def __init__(self):
        """Do nothing."""
        super().__init__(None, None)

    def execute(self, device_ids, value=None):
        """Do nothing."""
        pass


class PRUCurveCommand:
    """Executes a pru curve write command."""

    def __init__(self, pru_controller):
        """Get pru controller."""
        self.pru_controller = pru_controller

    def execute(self, device_ids, value=None):
        """Execute command."""
        if value is not None:
            for device_id in device_ids:
                self.pru_controller.pru_curve_write(device_id, value)


class CtrlLoop:
    """Adapter to close or open control loops."""

    def __init__(self, pru_controller):
        """Define commands."""
        self.pru_controller = pru_controller
        self.open_loop = Command(pru_controller, _bsmp.ConstBSMP.F_OPEN_LOOP)
        self.close_loop = Command(pru_controller, _bsmp.ConstBSMP.F_CLOSE_LOOP)

    def execute(self, device_ids, value=None):
        """Execute Command."""
        if value == 1:
            self.open_loop.execute(device_ids)
            _time.sleep(_delay_loop_open_close)
        elif value == 0:
            self.close_loop.execute(device_ids)
            _time.sleep(_delay_loop_open_close)


class PSPwrState:
    """Adapter to deal with FBP and FAC turn on/off commands."""

    def __init__(self, pru_controller):
        """Define commands."""
        self.turn_on = Command(pru_controller, _bsmp.ConstBSMP.F_TURN_ON)
        self.turn_off = Command(pru_controller, _bsmp.ConstBSMP.F_TURN_OFF)
        self.close_loop = Command(pru_controller, _bsmp.ConstBSMP.F_CLOSE_LOOP)

    def execute(self, device_ids, value=None):
        """Execute Command."""
        if value == 1:
            self.turn_on.execute(device_ids)
            _time.sleep(_delay_turn_on_off)
            self.close_loop.execute(device_ids)
            _time.sleep(_delay_loop_open_close)
        elif value == 0:
            self.turn_off.execute(device_ids)
            _time.sleep(_delay_turn_on_off)


class PSPwrStateFBP_DCLink:
    """Adapter to deal with FBP_DCLink turn on/off commands."""

    def __init__(self, pru_controller):
        """Define commands."""
        self.turn_on = Command(pru_controller, _bsmp.ConstBSMP.F_TURN_ON)
        self.turn_off = Command(pru_controller, _bsmp.ConstBSMP.F_TURN_OFF)
        self.open_loop = Command(pru_controller, _bsmp.ConstBSMP.F_OPEN_LOOP)

    def execute(self, device_ids, value=None):
        """Execute Command."""
        if value == 1:
            self.turn_on.execute(device_ids)
            _time.sleep(_delay_turn_on_off)
            self.open_loop.execute(device_ids)
            _time.sleep(_delay_loop_open_close)
        elif value == 0:
            self.turn_off.execute(device_ids)
            _time.sleep(_delay_turn_on_off)


class PSOpMode:
    """Decorate a command."""

    def __init__(self, command):
        """Command."""
        self.command = command
        self.disable_siggen = Command(command.pru_controller, 26)

    def execute(self, device_ids, value=None):
        """Parse before executing."""
        op_mode = value
        if value in (0, 3, 4):
            self._operation_mode = value
            op_mode = 0
        self.command.execute(device_ids, op_mode + 3)

        if value == _PSConst.OpMode.SlowRef:
            self.disable_siggen.execute(device_ids)


class Setpoint:
    """Command to set Setpoint."""

    def __init__(self, pru_controller):
        """Create command to set setpoint."""
        self.pru_controller = pru_controller
        self.set_setpoint = Command(pru_controller,
                                    _bsmp.ConstBSMP.F_SET_SLOWREF)

    def execute(self, device_ids, value=None):
        """Execute command."""
        op_modes = [_PSCStatus(self.pru_controller.read_variables(
            device_id, 0)).ioc_opmode
            for device_id in device_ids]
        slowsync = False
        if _PSConst.OpMode.SlowRefSync in op_modes:
            slowsync = True
            self.pru_controller.pru_sync_stop()

        self.set_setpoint.execute(device_ids, value)

        if slowsync:
            self.pru_controller.pru_sync_start(0x5B)
