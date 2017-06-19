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

class App:

    ps_devices = _pvs.get_ps_devices()
    pvs_database = _pvs.get_database()

    def __init__(self,driver):
        self._driver = driver
        for psname in _pvs.ps_devices:
            _pvs.ps_devices[psname].add_callback(self._mycallback)

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
        propty = reason.split(':')[-1]
        psname = ':'.join(reason.split(':')[:2])
        ps_propty = propty.replace('-','_').lower()
        #print(psname, ps_propty, value)
        setattr(_pvs.ps_devices[psname], ps_propty, value)
        self._driver.setParam(reason, value)
        self._driver.updatePVs()
        return True

    def _mycallback(self, pvname, value, **kwargs):
        reason = pvname
        prev_value = self._driver.getParam(reason)
        if value != prev_value:
            self._driver.setParam(reason, value)
            self._driver.updatePVs()
