"""Module with main IOC Class."""

import pvs as _pvs
import time as _time
import logging as _log
from siriuspy.timesys.time_data import Connections, Events, Clocks
from siriuspy.namesys import SiriusPVName as _PVName
from data.triggers import get_triggers as _get_triggers
from hl_classes import get_hl_trigger_object, HL_Event, HL_Clock

__version__ = _pvs.__version__
_TIMEOUT = 0.05


def check_triggers_consistency():
    """Check consitency of Triggers definition.

    Check if High Level definition of Triggers is consistent with
    Low Level connections of the timing devices.
    """
    triggers = _get_triggers()
    Connections.add_bbb_info()
    Connections.add_crates_info()
    from_evg = Connections.get_connections_from_evg()
    twds_evg = Connections.get_connections_twds_evg()
    for trig, val in triggers.items():
        chans = {_PVName(chan) for chan in val['channels']}
        for chan in chans:
            tmp = twds_evg.get(chan)
            if tmp is None:
                _log.warning('Device ' + chan +
                             ' defined in the high level trigger ' + trig +
                             ' not specified in timing connections data.')
                return False
            up_dev = tmp.pop()
            diff_devs = from_evg[up_dev] - chans
            if diff_devs and not chan.dev_type.endswith('BPM'):
                _log.warning('Devices: ' + ' '.join(diff_devs) +
                             ' are connected to the same output of ' +
                             up_dev + ' as ' + chan +
                             ' but are not related to the sam trigger (' +
                             trig + ').')
                # return False
    return True


class App:
    """Main Class of the IOC Logic."""

    def get_database(self):
        """Get the database."""
        db = dict()
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
        if not check_triggers_consistency():
            raise Exception('Triggers not consistent.')
        _log.info('Creating High Level Clocks:')
        self._clocks = dict()
        for cl, num in Clocks.HL2LL_MAP.items():
            clock = Clocks.HL_PREF + cl
            self._clocks[clock] = HL_Clock(clock, self._update_driver, num)
        _log.info('Creating High Level Events:')
        self._events = dict()
        for ev, code in Events.HL2LL_MAP.items():
            event = Events.HL_PREF + ev
            self._events[event] = HL_Event(event, self._update_driver, code)
        _log.info('Creating High Level Triggers:')
        self._triggers = dict()
        triggers = _get_triggers()
        for prefix, prop in triggers.items():
            trig = get_hl_trigger_object(prefix, self._update_driver, **prop)
            self._triggers[prefix] = trig

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
        self.check()
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
        """Write PV in database."""
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

    def check(self):
        """Trigger exectution of function to lock external PVs."""
        for ev in self._events.values():
            ev.check()
        for tr in self._triggers.values():
            tr.check()

    def _update_driver(self, pvname, value, **kwargs):
        _log.debug('PV {0:s} updated in driver database with value {1:s}'
                   .format(pvname, str(value)))
        self._driver.setParam(pvname, value)
        self._driver.updatePVs()

    def _isValid(self, reason, value):
        if reason.endswith(('-Sts', '-RB', '-Mon')):
            _log.debug('App: PV {0:s} is read only.'.format(reason))
            return False
        enums = self._database[reason].get('enums')
        if enums is not None:
            len_ = len(enums)
            if int(value) >= len_:
                _log.warning('App: value {0:d} too large for '.format(value) +
                             'PV {0:s} of type enum'.format(reason))
                return False
        return True
