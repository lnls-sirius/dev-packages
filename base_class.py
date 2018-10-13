"""Definition module."""
import math as _math
from siriuspy.csdevice.orbitcorr import OrbitCorrDev
from siriuspy.callbacks import Callback as _Callback


class BaseClass(_Callback):
    def __init__(self, acc, prefix='', callback=None):
        super().__init__(callback)
        self._csorb = OrbitCorrDev(acc)
        self._prefix = prefix
        self._status = 0b0

    @property
    def prefix(self):
        return self._prefix

    @property
    def acc(self):
        return self._csorb.acc

    @property
    def status(self):
        self._update_status()
        return self._status

    def run_callbacks(self, pvname, *args, **kwargs):
        super().run_callbacks(self._prefix + pvname, *args, **kwargs)

    def get_database(self, db):
        return {self.prefix + k: v for k, v in db.items()}

    def _update_log(self, value):
        self.run_callbacks('Log-Mon', value)

    def _update_status(self):
        pass


class BaseTimingConfig:

    def __init__(self, acc):
        self._csorb = OrbitCorrDev(acc)
        self._config_ok_vals = {}
        self._config_pvs_rb = {}
        self._config_pvs_sp = {}

    @property
    def connected(self):
        conn = True
        for k, pv in self._config_pvs_rb.items():
            conn &= pv.connected
        for k, pv in self._config_pvs_sp.items():
            conn &= pv.connected
        return conn

    @property
    def is_ok(self):
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
        if not self.connected:
            return False
        for k, pv in self._config_pvs_sp.items():
            pv.value = self._config_ok_vals[k]
        return True
