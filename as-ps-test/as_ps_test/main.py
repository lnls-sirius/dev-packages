"""Main application."""

import as_ps_test.pvs as _pvs
import time as _time
import siriuspy as _siriuspy
import numpy as _np


# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate seemingly repetitive flat code
#      (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive'
#      (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes,
#      suffixes, etc)

__version__ = _pvs._COMMIT_HASH


class App:
    """App class."""

    ps_devices = None
    pvs_database = None

    def __init__(self, driver):
        """Init."""
        _siriuspy.util.print_ioc_banner(
            ioc_name='PS-TEST',
            db=App.pvs_database[_pvs._PREFIX],
            description='PS-TEST Test Power Supply Soft IOC',
            version=__version__,
            prefix=_pvs._PREFIX)
        _siriuspy.util.save_ioc_pv_list('as-ps-test',
                                        ('',
                                         _pvs._PREFIX),
                                        App.pvs_database[_pvs._PREFIX])
        self._driver = driver
        for psname in _pvs.ps_devices:
            _pvs.ps_devices[psname].add_callback(self._mycallback)

    @staticmethod
    def init_class(bbblist):
        """Init class."""
        App.ps_devices = _pvs.get_ps_devices(bbblist)
        App.pvs_database = _pvs.get_pvs_database(bbblist)

    @staticmethod
    def get_pvs_database():
        """Get pvs database."""
        if App.pvs_database is None:
            App.pvs_database = _pvs.get_pvs_database()
        return App.pvs_database

    @staticmethod
    def get_ps_devices():
        """Get ps devices."""
        if App.ps_devices is None:
            App.ps_devices = _pvs.get_ps_devices()
        return App.ps_devices

    @property
    def driver(self):
        """Driver method."""
        return self._driver

    def process(self, interval):
        """Process method."""
        _time.sleep(interval)

    def read(self, reason):
        """Read pv method."""
        return None

    def write(self, reason, value):
        """Write pv method."""
        print('write', reason, value)
        parts = reason.split(':')
        propty = parts[-1]
        psname = ':'.join(parts[:2])
        ps = _pvs.ps_devices[psname]
        ps.write(field=propty, value=value)
        self._driver.setParam(reason, value)
        self._driver.updatePVs()

        # ps_propty = propty.replace('-', '_').lower()
        # try:
        #     if ps_propty in ('abort_cmd', 'reset_cmd'):
        #         setattr(_pvs.ps_devices[psname],
        #                 ps_propty.replace("_cmd", ""), value)
        #         return
        #     setattr(_pvs.ps_devices[psname], ps_propty, value)
        #     self._driver.setParam(reason, value)
        #     self._driver.updatePVs()
        # except AttributeError:
        #     print('attr error', ps_propty)

        return True

    def _mycallback(self, pvname, value, **kwargs):
        """Mycallback method."""
        # print('{0:<15s}: '.format('ioc callback'), pvname, value)
        reason = pvname
        prev_value = self._driver.getParam(reason)
        if isinstance(value, _np.ndarray):
            if _np.any(value != prev_value):
                self._driver.setParam(reason, value)
                self._driver.updatePVs()
        else:
            if value != prev_value:
                self._driver.setParam(reason, value)
                self._driver.updatePVs()
