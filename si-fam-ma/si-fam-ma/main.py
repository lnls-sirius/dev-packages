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

    ma_devices = _pvs.get_ma_devices()
    pvs_database = _pvs.get_pvs_database()

    def __init__(self,driver):

        self._driver = driver
        self._set_callbacks()

    def _set_callbacks(self):
        for family, device in App.ma_devices.items():
            device.set_callback(self._mycallback)
            device.update_state()

    @property
    def driver(self):
        return self._driver

    def process(self,interval):
        #_time.sleep(interval)
        pass

    def read(self,reason):
        ma, ps, propty = self._get_dev_propty(reason)
        if propty == 'CtrlMode-Mon':
            return ps.ctrlmode_mon
        elif propty == 'PwrState-Sel':
            return ps.pwrstate_sel
        elif propty == 'PwtState-Sts':
            return ps.pwrstate_sts
        elif propty == 'OpMode-Sel':
            return ps.opmode_sel
        elif propty == 'OpMode-Sts':
            return ps.opmode_sts
        elif propty == 'Current-RB':
            return ps.current_rb
        elif propty == 'Current-SP':
            return ps.current_sp
        elif propty in ('KL-SP','SL-SP'):
            return ma.kl_sp
        elif propty == ('KL-RB', 'SL-RB'):
            return ma.kl_rb
        return None

    @staticmethod
    def _get_dev_propty(reason):
        family, propty = reason.split(':')
        ma = App.ma_devices[family]
        ps = ma.get_ps('SI-Fam:PS-'+family)
        return ma, ps, propty

    def _mycallback(self, pvname, value, **kwargs):
        _, reason = pvname.split('PS-')
        prev_value = self._driver.getParam(reason)
        if value != prev_value:
             #print(reason, value)
             self._driver.setParam(reason, value)
             self._driver.updatePVs()

    def write(self,reason,value):
        """Write value to reason and let callback update PV database."""
        ma, ps, propty = self._get_dev_propty(reason)
        if propty == 'PwrState-Sel':
            ps.pwrstate_sel = value
        elif propty == 'OpMode-Sel':
            ps.opmode_sel = value
        elif propty == 'Current-SP':
            ps.current_sp = value
        else:
            return
