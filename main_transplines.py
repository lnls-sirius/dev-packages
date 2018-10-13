"""Main Module of the program."""

import time as _time
import logging as _log
from pcaspy import Driver as _PCasDriver
from .orbit import BaseOrbit as _BaseOrbit, EpicsOrbit as _EpicsOrbit
from .base_class import BaseClass as _BaseClass

INTERVAL = 1


class ORB(_BaseClass):
    """Main Class of the IOC."""

    def get_database(self):
        """Get the database of the class."""
        db = self._csorb.get_sofb_database()
        db = super().get_database(db)
        db.update(self.orbit.get_database())
        return db

    def __init__(self, acc, prefix='', callback=None, orbit=None):
        """Initialize Object."""
        super().__init__(acc, prefix=prefix, callback=callback)
        _log.info('Starting ORB...')
        self.add_callback(self._update_driver)
        self._driver = None
        self._orbit = None

        self.orbit = orbit
        if self._orbit is None:
            self.orbit = _EpicsOrbit(
                acc=acc, prefix=self.prefix, callback=self._update_driver)
        self._database = self.get_database()

    @property
    def orbit(self):
        return self._orbit

    @orbit.setter
    def orbit(self, orb):
        if isinstance(orb, _BaseOrbit):
            self._orbit = orb

    @property
    def driver(self):
        """Set the driver of the instance."""
        return self._driver

    @driver.setter
    def driver(self, driver):
        if isinstance(driver, _PCasDriver):
            self._driver = driver

    def write(self, reason, value):
        """Write value in database."""
        if not self._isValid(reason, value):
            return False
        fun_ = self._database[reason].get('fun_set_pv')
        if fun_ is None:
            _log.warning('PV %s does not have a set function.', reason)
            return False
        ret_val = fun_(value)
        if ret_val:
            _log.info('YES Write %s: %s', reason, str(value))
        else:
            value = self._driver.getParam(reason)
            _log.warning('NO write %s: %s', reason, str(value))
        self._update_driver(reason, value)
        return True

    def process(self):
        """Run continuously in the main thread."""
        t0 = _time.time()
        self.status
        tf = _time.time()
        dt = INTERVAL - (tf-t0)
        if dt > 0:
            _time.sleep(dt)
        else:
            _log.debug('App: check took {0:f}ms.'.format((tf-t0)*1000))

    def _update_status(self):
        self._status = bool(self._orbit.status)
        self.run_callbacks('Status-Mon', self._status)

    def _update_driver(self, pvname, value, **kwargs):
        if self._driver is not None:
            self._driver.setParam(pvname, value)
            self._driver.updatePV(pvname)

    def _isValid(self, reason, value):
        if reason.endswith(('-Sts', '-RB', '-Mon')):
            _log.debug('App: PV {0:s} is read only.'.format(reason))
            return False
        enums = self._database[reason].get('enums')
        if enums is not None:
            if isinstance(value, int):
                if value >= len(enums):
                    _log.warning('App: value {0:d} too large '.format(value) +
                                 'for PV {0:s} of type enum'.format(reason))
                    return False
            elif isinstance(value, str):
                if value not in enums:
                    _log.warning('Value {0:s} not permited'.format(value))
                    return False
        return True
