import pvs as _pvs
import time as _time
import siriuspy as _siriuspy

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

    pvs_database = _pvs.get_pvs_database()
    magnet_ps_family_names = _pvs.get_magnet_ps_family_names()

    def __init__(self,driver):

        self._driver = driver
        self._magnet_ps = _pvs.get_magnet_power_supplies()

    @property
    def driver(self):
        return self._driver

    def process(self,interval):
        #_time.sleep(interval)
        pass

    def read(self,reason):
        ps_fam_name, propty = reason.split(':')
        if ps_fam_name in App.magnet_ps_family_names:
            return self._magnet_ps[ps_fam_name][propty]
        else:
            return None

    def write(self,reason,value):
        ps_fam_name, propty = reason.split(':')
        if ps_fam_name in App.magnet_ps_family_names:
            self._magnet_ps[fam_name][propty] = value
            self._driver.updatePVs()
