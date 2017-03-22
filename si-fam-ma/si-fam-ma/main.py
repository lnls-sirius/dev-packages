import pvs as _pvs
import time as _time
import siriuspy as _siriuspy
import uuid as _uuid

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

__version__  = _pvs.__version__

class App:

    devices = _pvs.get_csdevices()
    pvs_database = _pvs.get_pvs_database()

    def __init__(self,driver):

        self._uuid = _uuid.uuid4()
        self._driver = driver
        self._set_callback()

    def _set_callback(self):
        for family, device in App.devices.items():
            device.add_callback(self._callback, self._uuid)

    @property
    def driver(self):
        return self._driver

    def process(self,interval):
        #_time.sleep(interval)
        pass

    def read(self,reason):
        ps, propty = self._get_dev_propty(reason)
        if propty == 'Current-RB':
            return ps.current_rb
        elif propty == 'Current-SP':
            return ps.current_sp

    @staticmethod
    def _get_dev_propty(reason):
        family, propty = reason.split(':')
        device = App.devices[family]
        return device, propty

    def _callback(self, pvname, value, **kwargs):
        print(pvname, value)


    def write(self,reason,value):
        ps, propty = self._get_dev_propty(reason)
        if propty == 'Current-SP':
            prev_value = ps.current_sp
            ps.current_sp = value
            if ps.current_sp != prev_value:
                self._driver.setParam(reason,value)
                self._driver.updatePVs()
