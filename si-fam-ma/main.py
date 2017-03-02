import epics as _epics
import psirius as _psirius
import math as _math
import pvs as _pvs
import time

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)


_timeout = None
_disconnected_value = 0 # float('NaN')
_ioc_prefix = 'VA-'

class App:

    def __init__(self,driver):
        self.driver = driver
        self.pv_database = _pvs.pvdb
        self.current_pvs_sp = {}
        self.current_pvs_rb = {}
        for family in _pvs.magnet_families:
            self.current_pvs_sp[family] = _epics.PV(_ioc_prefix+'SI-Fam:PS-'+family+':Current-SP', connection_timeout=_timeout); self.current_pvs_sp[family].value;
            self.current_pvs_rb[family] = _epics.PV(_ioc_prefix+'SI-Fam:PS-'+family+':Current-RB', connection_timeout=_timeout); self.current_pvs_rb[family].value;

    def process(self,interval):
        time.sleep(interval)

    def read(self,reason):
        #st = _psirius.util.get_timestamp(); print('read at ' + st)
        if reason == 'IOC:Version':
            self._process_all_pvs()
            self.driver.updatePVs()

    def write(self,reason,value):

        pvtype = _utils.get_prop_suffix(reason)
        if pvtype == 'SP':
            if not self._write_sp(reason,value): return False
            return True
        elif pvtype == 'Sel':
            if not self._write_sel(reason,value): return False
            return True
        else:
            st = _utils.get_timestamp()
            print(st + ': App::write - invoked for read-only pv "' + _utils.PREFIX + reason + '"!')
            return False

    def _write_sp(self,reason,value):
        for family, pv in self.current_pvs_sp.items():
            if reason == family + ':Current-SP':
                if pv.connected:
                    if self.driver.getParam(family+':State-Sts') == 1: # PS is On
                        pv.value = value
                        return True
                    return False
                else:
                    st = _utils.get_timestamp()
                    print(st + ': App::write_sp - "' + _utils.PREFIX + reason + '" not connected to its low-level PV!')
                    return False

    def _write_sel(self,reason,value):

        for family, pv in self.current_pvs_sp.items():
            if reason == family+':State-Sel':
                if pv.connected:
                    if value == 0: # Off
                        pv.value = 0 # set PS to zero
                    self.driver.setParam(family+':State-Sts', value) # set local Sts accordingly
                    return True
                else:
                    st = _utils.get_timestamp()
                    print(st + ': App::write_sel - "' + _utils.PREFIX + reason + '" not connected to its low-level PV!')
                    return False

    def _process_all_pvs(self):

        for family in self.current_pvs_sp.keys():
            if self.current_pvs_sp[family].connected:
                self.driver.setParam(family+':Current-SP', self.current_pvs_sp[family].value)
                self.driver.setParam(family+':Current-RB', self.current_pvs_rb[family].value)
