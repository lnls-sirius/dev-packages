"""Definition module."""
import math as _math
import logging as _log
from siriuspy.csdevice.orbitcorr import SOFBFactory as _SOFBFactory
from siriuspy.callbacks import Callback as _Callback


class BaseClass(_Callback):
    """Base Class."""

    def __init__(self, acc, prefix='', callback=None):
        """Init method."""
        super().__init__(callback)
        self._csorb = _SOFBFactory.create(acc)
        self._prefix = prefix
        self._status = 0b0

    @property
    def prefix(self):
        """Prefix."""
        return self._prefix

    @property
    def acc(self):
        """Accelerator name."""
        return self._csorb.acc

    @property
    def acc_idx(self):
        """Accelerator index."""
        return self._csorb.acc_idx

    @property
    def isring(self):
        """Ring accelerator status."""
        return self._csorb.isring()

    @property
    def status(self):
        """Status."""
        self._update_status()
        return self._status

    def run_callbacks(self, pvname, *args, **kwargs):
        """Run callback functions."""
        super().run_callbacks(self._prefix + pvname, *args, **kwargs)

    def get_database(self, db):
        """Return database."""
        return {self.prefix + k: v for k, v in db.items()}

    def _update_log(self, value):
        self.run_callbacks('Log-Mon', value)

    def _update_status(self):
        pass


class BaseTimingConfig:
    """Base timing configuration class."""

    def __init__(self, acc):
        """Init method."""
        self._csorb = _SOFBFactory.create(acc)
        self._config_ok_vals = {}
        self._config_pvs_rb = {}
        self._config_pvs_sp = {}

    @property
    def connected(self):
        """Status connected."""
        conn = True
        for k, pv in self._config_pvs_rb.items():
            if not pv.connected:
                _log.debug('NOT CONN: ' + pv.pvname)
            conn &= pv.connected
        for k, pv in self._config_pvs_sp.items():
            if not pv.connected:
                _log.debug('NOT CONN: ' + pv.pvname)
            conn &= pv.connected
        return conn

    @property
    def is_ok(self):
        """Ok status."""
        ok = True
        for k, val in self._config_ok_vals.items():
            pv = self._config_pvs_rb[k]
            pvval = None
            if pv.connected:
                pvval = pv.value
            if pvval is None:
                okay = False
                pvval = 'None'
            elif isinstance(val, float):
                okay = _math.isclose(val, pvval, rel_tol=1e-2)
            else:
                okay = val == pvval
            if not okay:
                _log.debug('NOT CONF: {0:s} okv = {1:f}, v = {2}'.format(
                    pv.pvname, val, pvval))
            ok &= okay
            if not ok:
                break
        return ok

    def configure(self):
        """Configure method."""
        if not self.connected:
            return False
        for k, pv in self._config_pvs_sp.items():
            pv.value = self._config_ok_vals[k]
        return True
