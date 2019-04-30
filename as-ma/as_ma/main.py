"""Main module of AS-MA IOC."""
import time as _time
import logging as _log

import siriuspy as _siriuspy
import as_ma.pvs as _pvs

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be
#      easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive'
#      (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes,
#      suffixes, etc)

__version__ = _pvs._COMMIT_HASH


class App:
    """Main application for handling magnet power supplies.

    write:
        writes to MA object and updates db
    read:
        always return None, delegating read to database
    """

    ma_devices = None
    pvs_database = None

    writable_suffixes = ['SP', 'Sel', 'Cmd']

    def __init__(self, driver, *args):
        """Class constructor."""
        # App.init_class()  # Is This really necessary?
        _siriuspy.util.print_ioc_banner(
            ioc_name='AS-MA',
            db=App.pvs_database,
            description='AS-MA Soft IOC',
            version=__version__,
            prefix=_pvs._PREFIX_VACA)
        # _siriuspy.util.save_ioc_pv_list(_pvs._IOC["name"],
        #                                 (_pvs._PREFIX_SECTOR,
        #                                  _pvs._PREFIX_VACA),
        #                                 App.pvs_database)

        self._driver = driver
        self._set_callback()

    @staticmethod
    def init_class(manames):
        """Init class."""
        App.ma_devices = _pvs.get_ma_devices(manames)
        App.pvs_database = _pvs.get_pvs_database(manames)

    @property
    def driver(self):
        """Return driver."""
        return self._driver

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        return None

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        # Get property and suffix
        pvname = _siriuspy.namesys.SiriusPVName(reason)
        # Check if suffix is writable
        if pvname.propty_suffix not in App.writable_suffixes:
            return
        # Update MA Object
        ma = self.ma_devices[pvname.device_name]
        ma.write(pvname.propty, value)
        # setattr(ma, attr, value)
        # value = getattr(ma, attr)
        if isinstance(value, float) or isinstance(value, int):
            _log.info(
                '{0:<15s} {1:s} [{2:f}]: '.format('ioc write', reason, value))
        else:
            _log.info(
                '{0:<15s}: {1:s}'.format('ioc write', reason))
        # Update IOC database
        self._driver.setParam(reason, value)
        self._driver.updatePVs()

        return

    def _set_callback(self):
        for family, device in App.ma_devices.items():
            device.add_callback(self._mycallback)
            # ?
            # if _pvs._PREFIX_SECTOR:
            #     *parts, prefix = device._maname.split(_pvs._PREFIX_SECTOR)
            # else:
            #     prefix = device._maname
            prefix = device._maname
            db = device.get_database(prefix=prefix)
            for reason, ddb in db.items():
                value = ddb['value']
                if value is not None:
                    self._driver.setParam(reason, value)
            self._driver.updatePVs()

    def _mycallback(self, pvname, value, **kwargs):
        pvname = _siriuspy.namesys.SiriusPVName(pvname)
        if pvname.dis == 'PU':
            pvname = pvname.substitute(dis='PM')
        elif pvname.dis == 'PS':
            pvname = pvname.substitute(dis='MA')

        reason = pvname.substitute(prefix='')
        self._driver.setParam(reason, value)
        if 'hilim' in kwargs or 'lolim' in kwargs:
            self._driver.setParamInfo(reason, kwargs)
            # self._driver.callbackPV(reason)
        self._driver.updatePVs()
