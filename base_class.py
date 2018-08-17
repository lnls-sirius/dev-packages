"""Definition module."""
import siriuspy.csdevice.orbitcorr as _csorb
from siriuspy.callbacks import Callback as _Callback


class BaseClass(_Callback):
    def __init__(self, acc, prefix='', callback=None):
        super().__init__(callback)
        self._acc = acc
        self._const = _csorb.get_consts(acc)
        self._prefix = prefix
        self._status = 0b0
        self.add_callback(callback)

    @property
    def prefix(self):
        return self._prefix

    @property
    def acc(self):
        return self._acc

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
