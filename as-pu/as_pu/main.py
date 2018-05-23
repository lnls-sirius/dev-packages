"""Main application."""

import time as _time
import numpy as _np
import logging as _log
# from collections import deque as _deque
# from collections import namedtuple as _namedtuple
# from threading import Thread as _Thread
# from threading import Lock as _Lock

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

# import as_ps.pvs as _pvs
import siriuspy as _siriuspy
import siriuspy.util as _util

__version__ = _util.get_last_commit_hash()

# FREQUENCY_SCAN = 10.0  # [Hz]
# FREQUENCY_RAMP = 2.0  # [Hz]


class Dispatcher:
    """Links ioc to device."""

    def __init__(self, devices_map):
        """Save devices_map reference."""
        self._devices_map = devices_map

    def read(self, reason):
        """Read reason value."""
        pass

    def write(self, reason, value):
        """Write value to reason."""
        device_name, field = self._split_reason(reason)
        device = self._devices_map[device_name]
        # Switch field
        if field == 'PwrState-Sel':
            device.set_pwrstate(value)
        elif field == 'Voltage-SP':
            device.set_voltage(value)
        elif field == 'Pulse-Sel':
            device.set_pulsed(value)
        elif field == 'Reset-Cmd':
            device.reset()

    def _split_reason(self, reason):
        split = reason.split(':')
        return ':'.join(split[:2]), split[-1]


class App:
    """Responsible for updating the IOC database.

    Update values and parameters such as alarms.
    """

    def __init__(self, driver, devices, dbset, prefix):
        """Create Power Supply controllers."""
        self._driver = driver
        self._devices = {}
        for device in devices:
            self._devices[device.name] = device

        self._dispatcher = Dispatcher(self._devices)

        # print info about the IOC
        _siriuspy.util.print_ioc_banner(
            ioc_name='BeagleBone',
            db=dbset[prefix],
            description='Pulsed Power Supply IOC',
            version=__version__,
            prefix=prefix)

        # save file with PVs list
        _siriuspy.util.save_ioc_pv_list('as-pu',
                                        ('',
                                         prefix),
                                        dbset[prefix])

    # API
    @property
    def driver(self):
        """Pcaspy driver."""
        return self._driver

    def process(self, interval):
        """Process all read and write requests in queue."""
        for device in self._devices.values():
            self._scan_device(device)
        self.driver.updatePVs()
        _time.sleep(0.05)

    def read(self, reason):
        """Read from database."""
        _log.info("[{:.2s}] - {:.32s} = {:.50s}".format(
            'R ', reason, str(self.driver.getParam(reason))))
        return None

    def write(self, reason, value):
        """Enqueue write request."""
        if '-SP' in reason or '-Sel' in reason:
            _log.info("[{:.2s}] - {:.32s} = {:.50s}".format(
                'W ', reason, str(value)))
            self._dispatcher.write(reason, value)
            self.driver.setParam(reason, value)
        elif '-Cmd' in reason:
            _log.info("[{:.2s}] - {:.32s} = {:.50s}".format(
                'W ', reason, str(value)))
            self._dispatcher.write(reason, value)
            value = self.driver.getParam(reason)
            self.driver.setParam(reason, value + 1)
        else:
            _log.info("Cannot write to {}".format(reason))

    # Private
    def _check_value_changed(self, reason, new_value):
        return True
        # TODO: Is it necessary to check?
        old_value = self.driver.getParam(reason)
        if isinstance(new_value, _np.ndarray):
            # TODO: check for ndarray
            return True
        else:
            if new_value != old_value:
                return True
        return False

    def _update_ioc_database(self, bbb, device_name):
        # Return dict idexed with reason
        for reason, new_value in bbb.read(device_name).items():
            if self._check_value_changed(reason, new_value):
                self.driver.setParam(reason, new_value)
                self.driver.setParamStatus(
                    reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)

    def _scan_device(self, device):
        for reason, value in device.read_all().items():
            self.driver.setParam(reason, value)
