"""Definition module."""
import math as _math
from siriuspy.csdevice.orbitcorr import OrbitCorrDevFactory as \
    _OrbitCorrDevFactory
from siriuspy.callbacks import Callback as _Callback


class BaseClass(_Callback):
    """Base Class."""

    def __init__(self, acc, prefix='', callback=None):
        """Init method."""
        super().__init__(callback)
        self._csorb = _OrbitCorrDevFactory.create(acc)
        self._prefix = prefix
        self._status = 0b0
        self._isring = self._csorb.acc_idx in self._csorb.Rings

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
        return self._isring

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
        self._csorb = _OrbitCorrDevFactory.create(acc)
        self._config_ok_vals = {}
        self._config_pvs_rb = {}
        self._config_pvs_sp = {}

    @property
    def connected(self):
        """Status connected."""
        conn = True
        for k, pv in self._config_pvs_rb.items():
            conn &= pv.connected
        for k, pv in self._config_pvs_sp.items():
            conn &= pv.connected
        return conn

    @property
    def is_ok(self):
        """Ok status."""
        ok = True
        for k, val in self._config_ok_vals.items():
            pv = self._config_pvs_rb[k]
            pvval = pv.value
            if isinstance(val, float):
                ok &= _math.isclose(val, pvval, rel_tol=1e-2)
            else:
                ok &= val == pvval
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
