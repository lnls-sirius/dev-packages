"""Power supply controller classes."""
import re as _re

from siriuspy import util as _util

__version__ = _util.get_last_commit_hash()


class InvalidValue(Exception):
    """Raised when an invalid value is passes as setpoint."""

    pass


class PSController:
    """High level PS controller.

    Responsible for keeping track of the setpoints.
    Exposes read/write interface, that maps an epics field to an actual
    variable in the device.
    Also exposes setpoint properties:
        PwrState-Sel
        OpMode-Sel
        Current-SP
        ...

    Maybe generalize to any device?
    """

    # Setpoints regexp pattern
    _sp = _re.compile('^.*-(SP|Sel|Cmd)$')

    def __init__(self, device):
        """Create BSMP to control a device."""
        self._device = device
        self._setpoints = dict()
        for field, db in device.database.items():
            if PSController._sp.match(field):
                self._setpoints[field] = db

    # API
    @property
    def device(self):
        """Device variables."""
        return self._device

    # Setpoints
    @property
    def setpoints(self):
        """Controller variables."""
        return self._setpoints

    @property
    def pwrstate_sel(self):
        """Power State Setpoint."""
        return self.setpoints['PwrState-Sel']['value']

    @pwrstate_sel.setter
    def pwrstate_sel(self, setpoint):
        """Set PwrState setpoint."""
        if setpoint == 1:
            ret = self.device.turn_on()
        elif setpoint == 0:
            ret = self.device.turn_off()
        else:
            raise InvalidValue("Power State Setpoint, {}".format(setpoint))

        if ret:
            self.setpoints['PwrState-Sel']['value'] = setpoint
            return True

        return False

    @property
    def opmode_sel(self):
        """Opertaion mode setpoint."""
        return self.setpoints['OpMode-Sel']['value']

    @opmode_sel.setter
    def opmode_sel(self, setpoint):
        """Operation mode setter."""
        # TODO: enumerate
        if setpoint < 0 or \
                setpoint > len(self.setpoints['OpMode-Sel']['enums']):
            raise InvalidValue("OpMode {} out of range.".format(setpoint))

        if self.device.select_op_mode(setpoint):
            self.setpoints['OpMode-Sel']['value'] = setpoint
            return True

        return False

    @property
    def current_sp(self):
        """Current setpoint."""
        return self._setpoints['Current-SP']['value']

    @current_sp.setter
    def current_sp(self, setpoint):
        setpoint = max(self.setpoints['Current-SP']['lolo'], setpoint)
        setpoint = min(self.setpoints['Current-SP']['hihi'], setpoint)

        if self.device.set_slowref(setpoint):
            self.setpoints['Current-SP']['value'] = setpoint
            return True
        return False

    @property
    def reset_cmd(self):
        """Return."""
        return self.setpoints['Reset-Cmd']['value']

    @reset_cmd.setter
    def reset_cmd(self, value):
        if value:
            if self.device.reset_interlocks():
                self.setpoints['Reset-Cmd']['value'] += 1
                return True
        return False

    # Read and Write map a PV field to proper function
    def read(self, field):
        """Read a field from device.

        Throws SerialError
        """
        if field in self._setpoints:
            return getattr(self, field.replace('-', '_').lower())
        else:
            return getattr(self.device, field.replace('-', '_').lower())

    def write(self, field, value):
        """Write to device field.

        Throws SerialError, InvalidValue
        """
        if field in self._setpoints:
            setattr(self, field.replace('-', '_').lower(), value)
            return True
        else:
            return False

    def read_all_variables(self):
        """Return dict with all variables values."""
        db = self.device.read_all_variables()
        if db is not None:
            for setpoint in self.setpoints:
                db[setpoint] = self.setpoints[setpoint]['value']
        return db


class PSCommInterface:
    """Communication interface class for power supplies."""

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
