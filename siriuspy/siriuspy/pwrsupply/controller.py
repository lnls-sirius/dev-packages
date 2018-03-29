"""Power supply controller classes."""
import re as _re

from siriuspy import util as _util
from siriuspy.bsmp import SerialError as _SerialError

__version__ = _util.get_last_commit_hash()


class InvalidValue(Exception):
    """Raised when an invalid value is passed as setpoint."""

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
    # Setpoint to readback
    _sp_to_rb_map = {
        'PwrState-Sel': 'PwrState-Sts',
        'OpMode-Sel': 'OpMode-Sts',
        'Current-SP': 'Current-RB',
        'CycleType-Sel': None,
        'WfmData-SP': None,
        'Reset-Cmd': None,
        'Abort-Cmd': None,
        }

    def __init__(self, device):
        """Create BSMP to control a device."""
        self._connected = False
        self._device = device
        self._setpoints = dict()
        for field, db in device.database.items():
            if PSController._sp.match(field):
                self._setpoints[field] = db

        self._init_setpoints()

    # API
    def read(self, field):
        """Read a field from device."""
        try:
            if field in self._setpoints:
                return getattr(self, field.replace('-', '_').lower())
            else:
                return getattr(self.device, field.replace('-', '_').lower())
        except _SerialError:
            self.connected = False
            return None

    def write(self, field, value):
        """Write to device field."""
        if field in self._setpoints:
            try:
                setattr(self, field.replace('-', '_').lower(), value)
                self.connected = True
            except _SerialError:
                self.connected = False
                return False
        return True

    def read_all_variables(self):
        """Return dict with all variables values."""
        try:
            db = self.device.read_all_variables()
        except _SerialError:
            self.connected = False
            return None
        else:
            self.connected = True
            if db is not None:
                for setpoint in self.setpoints:
                    db[setpoint] = self.setpoints[setpoint]['value']
            return db

    @property
    def device(self):
        """Device variables."""
        return self._device

    @property
    def connected(self):
        """Return connection state."""
        return self._connected

    @connected.setter
    def connected(self, value):
        self._connected = value

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
            self.setpoints['PwrState-Sel']['value'] = setpoint
            return
            # raise InvalidValue("Power State Setpoint, {}".format(setpoint))

        if ret:
            self.setpoints['Current-SP']['value'] = 0.0
            self.setpoints['OpMode-Sel']['value'] = 0
            self.setpoints['PwrState-Sel']['value'] = setpoint

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
            self.setpoints['OpMode-Sel']['value'] = setpoint
            # raise InvalidValue("OpMode {} out of range.".format(setpoint))

        if self.device.select_op_mode(setpoint):
            self.setpoints['OpMode-Sel']['value'] = setpoint

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

    @property
    def reset_cmd(self):
        """Return."""
        return self.setpoints['Reset-Cmd']['value']

    @reset_cmd.setter
    def reset_cmd(self, value):
        if value:
            if self.device.reset_interlocks():
                self.setpoints['Reset-Cmd']['value'] += 1

    def _init_setpoints(self):
        try:
            vars = self.device.read_all_variables()
        except Exception:
            pass
        else:
            # Init Setpoints
            for setpoint in self.setpoints:
                readback = PSController._sp_to_rb_map[setpoint]
                if readback:
                    self.setpoints[setpoint]['value'] = vars[readback]
            self._connected = True


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
