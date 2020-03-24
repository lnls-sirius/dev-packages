"""PVs Configs Handler."""

import time as _time
from epics import get_pv as _get_pv
import numpy as _np
from siriuspy.clientconfigdb import ConfigDBDocument as _ConfigDBDocument


_TIMEOUT = 0.5


class PVsConfig(_ConfigDBDocument):
    """Class to handle PVs configurations."""

    PVs = dict()

    def __init__(self, config_type='global_config', name=None, url=None):
        """Init."""
        super().__init__(config_type, name=name, url=url)

    def connect(self):
        """Create PVs."""
        template = self.get_value_from_template()
        for pvn, _, _ in template['pvs']:
            self._get_pv(pvn)

    @property
    def connected(self):
        template = self.get_value_from_template()
        for pvn, _, _ in template['pvs']:
            pv = self.PVs.get(pvn)
            if pv is None:
                return False
            elif not pv.connected:
                return False
        return True

    def read(self, timeout=_TIMEOUT):
        """Read machine state."""
        new_config_value = dict()
        new_config_value['pvs'] = list()

        template = self.get_value_from_template()

        # connect
        self.connect()

        # read
        pvs_not_read = set()
        for pvn, _, delay in template['pvs']:
            pv = self._get_pv(pvn)
            if pv.wait_for_connection(timeout):
                value = pv.get(timeout=timeout)
            else:
                pvs_not_read.add(pvn)
                value = 0
            new_config_value['pvs'].append([pvn, value, delay])

        if pvs_not_read:
            return False, pvs_not_read

        self.value = new_config_value
        return True, []

    def read_and_save(self, new_name=None):
        """Read machine state and save new configuration in config server."""
        ok, failed_list = self.read()
        if not ok:
            return False, failed_list
        else:
            self.save(new_name)
        return True, []

    def apply(self, timeout=_TIMEOUT):
        """Apply current config value to machine and check if implemented."""
        # connect
        self.connect()

        pvs_not_set = set()

        # set
        for pvn, value, delay in self._value['pvs']:
            pv = self._get_pv(pvn)
            try:
                pv.put(value)
                _time.sleep(delay)
            except TypeError:
                pvs_not_set.add(pvn)

        # wait
        _time.sleep(2.0)

        # check
        for pvn, value, delay in self._value['pvs']:
            if pvn in pvs_not_set:
                continue
            equal = self._check_pv(pvn, value, timeout=timeout)
            if not equal:
                pvs_not_set.add(pvn)

        if pvs_not_set:
            return False, pvs_not_set
        return True, []

    def load_and_apply(self, timeout=_TIMEOUT):
        """Load from server, apply to machine and check if implemented."""
        self.load()
        ok, failed_list = self.apply(timeout=timeout)
        if not ok:
            return False, failed_list
        return True, []

    # ---------- auxiliar methods ----------

    def _get_pv(self, pvname, timeout=_TIMEOUT):
        """Return PV object."""
        pv = self.PVs.get(pvname)
        if pv is None:
            pv = _get_pv(pvname, timeout=_TIMEOUT)
            self.PVs[pvname] = pv
        return pv

    def _check_pv(self, pvname, value, timeout=_TIMEOUT,
                  rel_tol=1e-06, abs_tol=0.0):
        """Check PV value."""
        pv = self._get_pv(pvname)
        pv.wait_for_connection(timeout)
        curr_val = pv.get(timeout=timeout)
        if curr_val is None:
            return False
        elif isinstance(curr_val, (_np.ndarray, list, tuple)) or \
                isinstance(value, (_np.ndarray, list, tuple)):
            try:
                if len(curr_val) != len(value):
                    return False
            except TypeError:
                return False  # one of them is not an array
            return _np.allclose(curr_val, value, rtol=rel_tol, atol=abs_tol)
        elif isinstance(curr_val, float) or isinstance(value, float):
            return _np.isclose(curr_val, value, rtol=rel_tol, atol=abs_tol)
        elif curr_val == value:
            return True
        return False
