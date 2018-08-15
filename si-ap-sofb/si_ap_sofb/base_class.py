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

    @property
    def status(self):
        self._update_status()
        return self._status

    def get_database(self):
        return dict()

    def _update_status(self):
        pass
