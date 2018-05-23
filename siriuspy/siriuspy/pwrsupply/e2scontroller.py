"""E2SController."""
import numpy as _np
import re as _re
from collections import namedtuple as _namedtuple

from siriuspy.pwrsupply.prucontroller import PRUController as _PRUController
from siriuspy.pwrsupply.commands import CommandFactory as _CommandFactory
from siriuspy.pwrsupply.fields import VariableFactory as _VariableFactory
from siriuspy.pwrsupply.fields import Constant as _Constant


DeviceInfo = _namedtuple('DeviceInfo', 'name, id')


class E2SController:
    """Setpoints and field translation."""

    INTERVAL_SCAN = 1.0/_PRUController.FREQ.SCAN
    _function = _re.compile('^.*-(SP|Sel|Cmd)$')

    def __init__(self, controller, devices_info, model, database):
        """Init."""
        # Properties
        self._pru_controller = controller
        self._devices_info = devices_info
        self._model = model
        self._database = database

        # Data structures
        self._fields = dict()
        self._writers = dict()
        # Fill fields and writes
        self._create_fields()
        # Init setpoint values
        # self._init()

    # --- public interface ---

    @property
    def database(self):
        """Device database."""
        return self._database

    @property
    def pru_controller(self):
        """PRU Controller."""
        return self._pru_controller

    def read(self, device_name, field):
        """Read field from device."""
        return self._fields[field][device_name].read()

    def read_all(self, device_name):
        """Read all fields."""
        values = dict()
        for field in self._fields:
            key = device_name + ':' + field
            values[key] = self.read(device_name, field)
        return values

    def write(self, device_name, field, value):
        """Write value to device."""
        dev_info = self._devices_info[device_name]
        self._write(dev_info.id, field, value)

    def write_to_many(self, devices_names, field, value):
        """Write to value one or many devices' field."""
        devices_names = self._tuplify(devices_names)
        ids = tuple([dev_info.id for dev_info in self._devices_info.values()])
        self._write(ids, field, value)

    def check_connected(self, device_name):
        """Connected."""
        device_id = self._devices_info[device_name].id
        return self._pru_controller.check_connected(device_id)

    # --- private methods ---

    def _write(self, ids, field, value):
        ids = self._tuplify(ids)
        if ids:
            self._writers[field].execute(ids, value)

    def _create_fields(self):
        for field, db in self.database.items():
            if self._function.match(field):
                cmd = _CommandFactory.get(
                    self._model, field, self._pru_controller)
                self._writers[field] = cmd
            else:
                self._fields[field] = dict()
                for device_info in self._devices_info.values():
                    if 'Version-Cte' == field:
                        obj = _VariableFactory.get(
                            self._model, device_info.id,
                            field, self._pru_controller)
                    elif _Constant.match(field):
                        obj = _Constant(db['value'])
                    else:
                        obj = _VariableFactory.get(
                            self._model, device_info.id,
                            field, self._pru_controller)
                    self._fields[field][device_info.name] = obj

    def _tuplify(self, value):
        # Return tuple if value is not iterable
        if not hasattr(value, '__iter__') or \
                isinstance(value, str) or \
                isinstance(value, _np.ndarray) or \
                isinstance(value, DeviceInfo):
            return value,
        return value
