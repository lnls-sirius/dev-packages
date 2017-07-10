import pvs as _pvs
import time as _time

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate seemingly repetitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

__version__ = _pvs.__version__

ttime = 0.0

class App:

    ps_devices = None
    pvs_database = None

    def __init__(self,driver):
        self._driver = driver
        for psname in _pvs.ps_devices:
            _pvs.ps_devices[psname].add_callback(self._mycallback)

    @staticmethod
    def get_pvs_database():
        if App.pvs_database is None:
            App.pvs_database = _pvs.get_database()
        return App.pvs_database

    @staticmethod
    def get_ps_devices():
        if App.ps_devices is None:
            App.ps_devices = _pvs.get_ps_devices()
        return App.ps_devices

    @property
    def driver(self):
        return self._driver

    def process(self,interval):
        _time.sleep(interval)

    def read(self, reason):
        '''psname, prop = reason.split(':')
        if 'Current-SP' in prop:
            return _pvs.ps[psname].current_sp
        elif 'Current-Mon' in prop:
            return _pvs.ps[psname].current_mon'''
        return None

    def write(self, reason, value):
        global ttime
        t0 = _time.time()
        parts = reason.split(':')
        propty = parts[-1]
        psname = ':'.join(parts[:2])
        ps_propty = propty.replace('-','_').lower()
        if isinstance(value, float) or isinstance(value, int):
            print('{0:<15s} {1:s} [{2:f}]: '.format('ioc write', reason, value))
        else:
            print('{0:<15s}: '.format('ioc write'), reason)
        try:
            if ps_propty in ('abort_cmd', 'reset_cmd'):
                setattr(_pvs.ps_devices[psname], ps_propty.replace("_cmd", ""), value)
                return
            setattr(_pvs.ps_devices[psname], ps_propty, value)
            self._driver.setParam(reason, value)
            self._driver.updatePVs()
        except AttributeError:
            print('attr error', ps_propty)

        t1 = _time.time()
        ttime += t1-t0
        #print(ttime)
        return True

    def _mycallback(self, pvname, value, **kwargs):
        print('{0:<15s}: '.format('ioc callback'), pvname, value)
        reason = pvname
        prev_value = self._driver.getParam(reason)
        if value != prev_value:
            self._driver.setParam(reason, value)
            self._driver.updatePVs()
