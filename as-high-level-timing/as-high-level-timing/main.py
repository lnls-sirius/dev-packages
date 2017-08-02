"""Module with main IOC Class."""

import time as _time
import logging as _log
from siriuspy.timesys.time_data import Events, Clocks, Triggers
from hl_classes import HL_Event, HL_Clock, HL_Trigger

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

_TIMEOUT = 0.05


class App:
    """Main Class of the IOC Logic."""

    def get_database(self):
        """Get the database."""
        db = {'Version-Cte': {'type': 'string', 'value': __version__}}
        for cl in self._clocks.values():
            db.update(cl.get_database())
        for ev in self._events.values():
            db.update(ev.get_database())
        for trig in self._triggers.values():
            db.update(trig.get_database())
        return db

    def __init__(self, driver=None):
        """Initialize the instance."""
        _log.info('Starting App...')
        self._driver = driver
        _log.info('Creating High Level Clocks:')
        self._clocks = dict()
        for cl_hl, cl_ll in Clocks.HL2LL_MAP.items():
            clock = Clocks.HL_PREF + cl_hl
            self._clocks[clock] = HL_Clock(clock, self._update_driver, cl_ll)
        _log.info('Creating High Level Events:')
        self._events = dict()
        for ev_hl, ev_ll in Events.HL2LL_MAP.items():
            event = Events.HL_PREF + ev_hl
            self._events[event] = HL_Event(event, self._update_driver, ev_ll)
        _log.info('Creating High Level Triggers:')
        self._triggers = dict()
        for pref, prop in Triggers().hl_triggers.items():
            self._triggers[pref] = HL_Trigger(
                                            pref, self._update_driver, **prop)
        self._database = self.get_database()

    def connect(self):
        """Trigger connection to external PVs in other classes."""
        _log.info('Connecting to Low Level Clocks:')
        for key, val in self._clocks.items():
            val.connect()
        _log.info('All Clocks connection opened.')
        _log.info('Connecting to Low Level Events:')
        for key, val in self._events.items():
            val.connect()
        _log.info('All Events connection opened.')
        _log.info('Connecting to Low Level Triggers:')
        for key, val in self._triggers.items():
            val.connect()
        _log.info('All Triggers connection opened.')

    @property
    def driver(self):
        """Set the driver of the App."""
        return self._driver

    @driver.setter
    def driver(self, driver):
        _log.debug("Setting App's driver.")
        self._driver = driver

    def process(self, interval):
        """Run continuously in the main thread."""
        t0 = _time.time()
        # _log.debug('App: Executing check.')
        tf = _time.time()
        dt = (tf-t0)
        if dt > 0.2:
            _log.debug('App: check took {0:f}ms.'.format(dt*1000))
        dt = interval - dt
        if dt > 0:
            _time.sleep(dt)

    def read(self, reason):
        """Read PV from database."""
        # _log.debug("PV {0:s} read from App.".format(reason))
        return None  # Driver will read from database

    def write(self, reason, value):
        """Write PV in the model."""
        _log.debug('App: Writing PV {0:s} with value {1:s}'
                   .format(reason, str(value)))
        if not self._isValid(reason, value):
            return False
        fun_ = self._database[reason].get('fun_set_pv')
        if fun_ is None:
            _log.warning('App: Write unsuccessful. PV ' +
                         '{0:s} does not have a set function.'.format(reason))
            return False
        ret_val = fun_(value)
        if ret_val:
            _log.debug('App: Write complete.')
        else:
            _log.warning('App: Unsuccessful write of PV {0:s}; value = {1:s}.'
                         .format(reason, str(value)))
        return ret_val

    def _update_driver(self, pvname, value, **kwargs):
        _log.debug('PV {0:s} updated in driver database with value {1:s}'
                   .format(pvname, str(value)))
        self._driver.setParam(pvname, value)
        self._driver.updatePVs()

    def _isValid(self, reason, value):
        if reason.endswith(('-Sts', '-RB', '-Mon')):
            _log.debug('App: PV {0:s} is read only.'.format(reason))
            return False
        enums = (self._database[reason].get('enums') or
                 self._database[reason].get('Enums'))
        if enums is not None:
            if isinstance(value, int):
                len_ = len(enums)
                if value >= len_:
                    _log.warning('App: value {0:d} too large '.format(value) +
                                 'for PV {0:s} of type enum'.format(reason))
                    return False
            elif isinstance(value, str):
                if value not in enums:
                    _log.warning('Value {0:s} not permited'.format(value))
                    return False
        return True
