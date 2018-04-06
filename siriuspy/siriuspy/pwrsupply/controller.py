"""Power supply controller classes."""
from siriuspy import util as _util
from siriuspy.bsmp import Response, BSMP
from siriuspy.pwrsupply.bsmp import FBPEntities
from siriuspy.pwrsupply.status import Status as _Status
from siriuspy.pwrsupply.bsmp import Const as _c

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


class ControllerSim:
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
        return Response.ok, [self._variables[id] for id in ids]

    def create_groups(self, var_ids):
        """Create new group."""
        self.entities.add_group(var_ids)
        return Response.ok, None

    def execute_function(self, func_id, input_val=None):
        """Execute a function."""
        raise NotImplementedError()


class FBPControllerSim(ControllerSim):
    """Simulate a PS controller."""

    def __init__(self):
        """Use FBPEntities."""
        super().__init__(FBPEntities())
        firmware = [b'S', b'i', b'm']
        while len(firmware) < 128:
            firmware.append('\x00'.encode())
        self._variables = [
            0, 0.0, 0.0, firmware, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0,
            [0.0, 0.0, 0.0, 0.0], 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0,
            0, 0, 0, 0.0, 0.0, 0.0, 0.0]

    def execute_function(self, func_id, input_val=None):
        """Execute a function."""
        # Switch FBP func ids
        if func_id == _c.TURN_ON:
            status = self._variables[_c.PS_STATUS]
            if _Status.pwrstate(status) == 0:
                self._variables[_c.PS_STATUS] = _Status.set_pwrstate(status, 1)
                self._variables[_c.PS_SETPOINT] = 0.0
                self._variables[_c.PS_REFERENCE] = 0.0
                self._variables[_c.I_LOAD] = 0.0
        elif func_id == _c.TURN_OFF:
            status = self._variables[_c.PS_STATUS]
            if _Status.pwrstate(status) == 1:
                self._variables[_c.PS_STATUS] = _Status.set_pwrstate(status, 0)
                self._variables[_c.PS_SETPOINT] = 0.0
                self._variables[_c.PS_REFERENCE] = 0.0
                self._variables[_c.I_LOAD] = 0.0
        elif func_id == _c.SELECT_OP_MODE:
            status = self._variables[_c.PS_STATUS]
            if _Status.pwrstate(status) == 1:
                print(input_val)
                self._variables[_c.PS_STATUS] = \
                    _Status.set_opmode(status, input_val-3)
        elif func_id == _c.RESET_INTERLOCKS:
            self._variables[_c.PS_SOFT_INTERLOCKS] = 0
            self._variables[_c.PS_HARD_INTERLOCKS] = 0
        elif func_id == _c.SET_SLOWREF:
            status = self._variables[_c.PS_STATUS]
            if _Status.pwrstate(status) == 1:
                self._variables[_c.PS_SETPOINT] = input_val
                self._variables[_c.PS_REFERENCE] = input_val
                self._variables[_c.I_LOAD] = input_val
        elif func_id == _c.CFG_SIGGEN:
            self._variables[_c.SIGGEN_TYPE] = input_val[0]
            self._variables[_c.SIGGEN_NUM_CYCLES] = input_val[1]
            self._variables[_c.SIGGEN_FREQ] = input_val[2]
            self._variables[_c.SIGGEN_AMPLITUDE] = input_val[3]
            self._variables[_c.SIGGEN_OFFSET] = input_val[4]
            self._variables[_c.SIGGEN_AUX_PARAM] = input_val[5]
        elif func_id == _c.SET_SIGGEN:
            self._variables[_c.SIGGEN_FREQ] = input_val[0]
            self._variables[_c.SIGGEN_AMPLITUDE] = input_val[1]
            self._variables[_c.SIGGEN_OFFSET] = input_val[2]
        elif func_id == _c.ENABLE_SIGGEN:
            # implement sim siggen
            self._variables[_c.SIGGEN_ENABLE] = 1
        elif func_id == _c.DISABLE_SIGGEN:
            self._variables[_c.SIGGEN_ENABLE] = 0

        return Response.ok, None
