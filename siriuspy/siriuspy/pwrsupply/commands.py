"""Define commands use to maps an epics field to a BSMP entity id.

These classes implement a Command interface, that is, they an execute method.
"""
import time as _time

# BSMP and PS constants
from siriuspy.pwrsupply.bsmp import Const as _c
from siriuspy.csdevice.pwrsupply import Const as _PSConst


class CommandFactory:
    """Build command objects."""

    @staticmethod
    def get(ps_model, epics_field, pru_controller):
        """Return an object that implemets the Command interface."""
        if epics_field == 'PwrState-Sel':
            return PSPwrState(pru_controller)
        elif epics_field == 'OpMode-Sel':
            return PSOpMode(Command(pru_controller, _c.F_SELECT_OP_MODE))
        elif epics_field == 'Current-SP':
            return Command(pru_controller, _c.F_SET_SLOWREF)
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


class PSPwrState:
    """Adapter to deal with turn on/off commands."""

    def __init__(self, pru_controller):
        """Define commands."""
        self.turn_on = Command(pru_controller, 0)
        self.close_loop = Command(pru_controller, 3)
        self.turn_off = Command(pru_controller, 1)

    def execute(self, device_ids, value=None):
        """Execute Command."""
        if value == 1:
            self.turn_on.execute(device_ids)
            _time.sleep(0.3)
            self.close_loop.execute(device_ids)
        elif value == 0:
            self.turn_off.execute(device_ids)


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
