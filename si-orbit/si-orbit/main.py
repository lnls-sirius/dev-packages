"""Main Module of the program."""
import time as _time
import logging as _log
import epics as _epics
from siriuspy.diagnostics import bpmsdata as _bpmsdata


with open('VERSION') as f:
    __version__ = f.read()
_TIMEOUT = 0.05

TINY_INTERVAL = 0.001
NUM_TIMEOUT = 2000


class App:
    """Main Class of the IOC."""

    def get_database(self):
        """Get the database of the class."""
        db = dict()
        pre = self.prefix
        db[pre + 'Log-Mon'] = {'type': 'string', 'value': ''}
        db[pre + 'NumBPM-Cte'] = {
            'type': 'int', 'value': self.nr_bpms}
        db[pre + 'OrbitX-Mon'] = {
            'type': 'float', 'unit': 'nm',
            'count': self.nr_bpms, 'value': self.nr_bpms*[0]}
        db[pre + 'OrbitY-Mon'] = {
            'type': 'float', 'unit': 'nm',
            'count': self.nr_bpms, 'value': self.nr_bpms*[0]}
        db[pre + 'PosS-Cte'] = {
            'type': 'float', 'unit': 'm',
            'count': self.nr_bpms, 'value': self.bpm_pos}
        return db

    def __init__(self, driver=None):
        """Initialize the instance."""
        _log.info('Starting App...')
        self.bpm_names = _bpmsdata.get_names()
        self.bpm_pos = _bpmsdata.get_positions()
        self.nr_bpms = len(self.bpm_names)
        self.orbx = self.nr_bpms*[0.0]  # _np.zeros(self.nr_bpms, dtype=float)
        self.orby = self.nr_bpms*[0.0]  # _np.zeros(self.nr_bpms, dtype=float)
        self._driver = driver
        self.prefix = 'SI-Glob:AP-Orbit:'
        self._database = self.get_database()

    @property
    def driver(self):
        """Set the driver of the app."""
        return self._driver

    @driver.setter
    def driver(self, driver):
        _log.debug("Setting App's driver.")
        self._driver = driver

    def write(self, reason, value):
        """Write the PV on memory."""
        _log.debug(
            'App: Writing PV {0:s} with value {1:s}'.format(reason, str(value))
            )
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
            _log.warning('App: Unsuccessful write of PV ' +
                         '{0:s}; value = {1:s}.'.format(reason, str(value)))
        return ret_val

    def process(self, interval):
        """Run repeatitively on the main thread."""
        t0 = _time.time()
        self._update_orbits()
        tf = _time.time()
        dt = (tf-t0)
        if dt > interval:
            _log.debug('App: process took {0:f}ms.'.format(dt*1000))
        dt = interval - dt
        if dt > 0:
            _time.sleep(dt)

    def connect(self):
        """Trigger connections to external PVs in other classes."""
        _log.info('Connecting to Orbit PVs:')
        self._call_callback('Log-Mon', 'Connecting to Low Level PVs')
        self.pvs_posx = {name: _epics.PV(name+':PosX-Mon')
                         for name in self.bpm_names}
        self.pvs_posy = {name: _epics.PV(name+':PosY-Mon')
                         for name in self.bpm_names}
        _log.info('All Orbit connection opened.')

    def _call_callback(self, pv, value):
        self._update_driver(self.prefix + pv, value)

    def _update_driver(self, pvname, value, **kwargs):
        _log.debug('PV {0:s} updated in driver '.format(pvname) +
                   'database with value {0:s}'.format(str(value)))
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

    def _update_orbits(self):
        for i, name in enumerate(self.bpm_names):
            pvx = self.pvs_posx[name]
            pvy = self.pvs_posy[name]
            self.orbx[i] = pvx.value if pvx.connected else 0.0
            self.orby[i] = pvy.value if pvy.connected else 0.0
        self._call_callback('OrbitX-Mon', self.orbx)
        self._call_callback('OrbitY-Mon', self.orby)
