"""Dispatcher bridge the communication between the IOC and a device."""
import re as _re

from siriuspy import util as _util
from siriuspy.bsmp import SerialError as _SerialError

__version__ = _util.get_last_commit_hash()


# class InvalidValue(Exception):
#     """Raised when an invalid value is passed as setpoint."""
#
#     pass


class PSDispatcher:
    """Handle IOC/Device communication.

    Responsibilities:
    - keep track of setpoints;
    - handle requests from IOC routing them to the device;
    """

    # Setpoints regexp pattern
    _sp = _re.compile('^.*-(SP|Sel|Cmd)$')
    # Setpoint to readback
    # _sp_to_rb_map = {
    #     'PwrState-Sel': 'PwrState-Sts',
    #     'OpMode-Sel': 'OpMode-Sts',
    #     'Current-SP': 'Current-RB',
    #     'CycleEnbl-Cmd': None,
    #     'CycleDsbl-Cmd': None,
    #     'CycleType-Sel': 'CycleType-Sts',
    #     'CycleNrCycles-SP': 'CycleNrCycles-RB',
    #     'CycleFreq-SP': 'CycleFreq-RB',
    #     'CycleAmpl-SP': 'CycleAmpl-RB',
    #     'CycleOffset-SP': 'CycleOffset-RB',
    #     'CycleAuxParam-SP': 'CycleAuxParam-RB',
    #     'WfmData-SP': None,
    #     'Reset-Cmd': None,
    #     'Abort-Cmd': None,
    #     }

    def __init__(self, device, database=None):
        """Create BSMP to control a device."""
        self._connected = False
        self._device = device
        self._database = database
        self._setpoints = dict()
        for field, db in self.database.items():
            if PSDispatcher._sp.match(field):
                self._setpoints[field] = db

        self._init_setpoints()

    # API
    def read(self, field):
        """Read a field from device."""
        try:
            if field in self._setpoints:
                return self.setpoints[field]['value']
                # return getattr(self, field.replace('-', '_').lower())
            else:
                return getattr(self.device, field.replace('-', '_').lower())
        except _SerialError:
            self.connected = False
            return None

    def write(self, field, value):
        """Write to device field."""
        if field in self._setpoints:
            try:
                # setattr(self, field.replace('-', '_').lower(), value)
                self._write_setpoint(field, value)
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
    def database(self):
        """Device database."""
        return self._database

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

    def _write_setpoint(self, field, setpoint):
        """Write operation."""
        # Switch field
        if field == 'PwrState-Sel':
            return self._set_pwrstate(setpoint)
        elif field == 'OpMode-Sel':
            return self._set_opmode(setpoint)
        elif field == 'Current-SP':
            return self._set_current(setpoint)
        elif field == 'Reset-Cmd':
            return self._reset(setpoint)
        elif field == 'CycleEnbl-Cmd':
            return self._enable_cycle(setpoint)
        elif field == 'CycleDsbl-Cmd':
            return self._disable_cycle(setpoint)
        elif field == 'CycleType-Sel':
            return self._set_cycle_type(setpoint)
        elif field == 'CycleNrCycles-SP':
            return self._set_cycle_nr_cycles(setpoint)
        elif field == 'CycleFreq-SP':
            return self._set_cycle_frequency(setpoint)
        elif field == 'CycleAmpl-SP':
            return self._set_cycle_amplitude(setpoint)
        elif field == 'CycleOffset-SP':
            return self._set_cycle_offset(setpoint)
        elif field == 'CycleAuxParam-SP':
            return self._set_cycle_aux_params(setpoint)

    def _set_pwrstate(self, setpoint):
        """Set PwrState setpoint."""
        if setpoint == 1:
            ret = self.device.turn_on()
        elif setpoint == 0:
            ret = self.device.turn_off()
        else:
            self.setpoints['PwrState-Sel']['value'] = setpoint
            return

        if ret:
            self.setpoints['Current-SP']['value'] = 0.0
            self.setpoints['OpMode-Sel']['value'] = 0
            self.setpoints['PwrState-Sel']['value'] = setpoint

    def _set_opmode(self, setpoint):
        """Operation mode setter."""
        # TODO: enumerate
        if setpoint < 0 or \
                setpoint > len(self.setpoints['OpMode-Sel']['enums']):
            self.setpoints['OpMode-Sel']['value'] = setpoint
            # raise InvalidValue("OpMode {} out of range.".format(setpoint))

        if self.device.select_op_mode(setpoint):
            self.setpoints['OpMode-Sel']['value'] = setpoint

    def _set_current(self, setpoint):
        """Set current."""
        setpoint = max(self.setpoints['Current-SP']['lolo'], setpoint)
        setpoint = min(self.setpoints['Current-SP']['hihi'], setpoint)

        if self.device.set_slowref(setpoint):
            self.setpoints['Current-SP']['value'] = setpoint

    def _reset(self, setpoint):
        """Reset command."""
        if setpoint:
            if self.device.reset_interlocks():
                self.setpoints['Reset-Cmd']['value'] += 1

    def _enable_cycle(self, setpoint):
        """Enable cycle command."""
        if setpoint:
            if self.device.enable_siggen():
                self.setpoints['CycleEnbl-Cmd']['value'] += 1

    def _disable_cycle(self, setpoint):
        """Disable cycle command."""
        if setpoint:
            if self.device.disable_siggen():
                self.setpoints['CycleDsbl-Cmd']['value'] += 1

    def _set_cycle_type(self, setpoint):
        """Set cycle type."""
        self.setpoints['CycleType-Sel']['value'] = setpoint
        # if setpoint < 0 or \
        #         setpoint > len(self.setpoints['CycleType-Sel']['enums']):
        #     return
        return self._cfg_siggen()

    def _set_cycle_nr_cycles(self, setpoint):
        """Set number of cycles."""
        self.setpoints['CycleNrCycles-SP']['value'] = setpoint
        return self._cfg_siggen()

    def _set_cycle_frequency(self, setpoint):
        """Set cycle frequency."""
        self.setpoints['CycleFreq-SP']['value'] = setpoint
        return self._cfg_siggen()

    def _set_cycle_amplitude(self, setpoint):
        """Set cycle amplitude."""
        self.setpoints['CycleAmpl-SP']['value'] = setpoint
        return self._cfg_siggen()

    def _set_cycle_offset(self, setpoint):
        """Set cycle offset."""
        self.setpoints['CycleOffset-SP']['value'] = setpoint
        return self._cfg_siggen()

    def _set_cycle_aux_params(self, setpoint):
        """Set cycle offset."""
        self.setpoints['CycleAuxParam-SP']['value'] = setpoint
        return self._cfg_siggen()

    def _cfg_siggen(self):
        """Get cfg_siggen args and execute it."""
        t_siggen = self.setpoints['CycleType-Sel']['value']
        num_cycles = self.setpoints['CycleNrCycles-SP']['value']
        frequency = self.setpoints['CycleFreq-SP']['value']
        amplitude = self.setpoints['CycleAmpl-SP']['value']
        offset = self.setpoints['CycleOffset-SP']['value']
        aux_params = self.setpoints['CycleAuxParam-SP']['value']
        return self.device.cfg_siggen(
            t_siggen, num_cycles, frequency, amplitude, offset, aux_params)

    def _init_setpoints(self):
        try:
            values = self.device.read_all_variables()
        except Exception:
            pass
        else:
            # Init Setpoints
            for setpoint in self.setpoints:
                if '-Cmd' in setpoint:
                    continue
                readback = \
                    setpoint.replace('-Sel', '-Sts').replace('-SP', '-RB')
                try:
                    self.setpoints[setpoint]['value'] = values[readback]
                except KeyError:
                    continue
            self._connected = True
