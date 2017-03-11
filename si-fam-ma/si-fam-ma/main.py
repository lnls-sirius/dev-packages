import pvs as _pvs
import time as _time
import siriuspy as _siriuspy
import epics as _epics

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

__version__  = _pvs.__version__
_timeout     = 0
_ioc_prefix  = _siriuspy.envars.vaca_prefix





_family_properties = tuple(_pvs.get_family_database('').keys())


class App:

    pvs_database = _pvs.create_pvs_database()
    magnet_families = _pvs.magnet_families
    family_properties = tuple(_pvs.get_family_database('').keys())

    def __init__(self,driver):


        self._driver = driver
            ma_pv_name = family + ':' + prop
            pv_dict = {}
            ps_pv_name = _ioc_prefix + 'SI-Fam:PS-' + ma_pv_name
            pv_dict['ps_pv_name'] = ps_pv_name
            pv_dict['epics_objc'] = _epics.PV(ps_pv_name, connection_timeout=_timeout);
            self.pvs[ma_pv_name] = pv_dict


        # create epics PVs associated with family power supplies
        self.pvs = {}
        for family in App.magnet_families:
            for prop in App.family_properties:
                ma_pv_name = family + ':' + prop
                pv_dict = {}
                ps_pv_name = _ioc_prefix + 'SI-Fam:PS-' + ma_pv_name
                pv_dict['ps_pv_name'] = ps_pv_name
                pv_dict['epics_objc'] = _epics.PV(ps_pv_name, connection_timeout=_timeout);
                self.pvs[ma_pv_name] = pv_dict
        print('ok')

    @property
    def driver(self):
        return self._driver

    def process(self,interval):
        #_time.sleep(interval)
        pass

    def read(self,reason):
        if reason == 'IOC:Version-Cte':
            ts = _siriuspy.util.get_timestamp(); print(ts)
            changed = self.process_all_pvs()
            if changed:
                self.driver.updatePVs()
            return None
        return None

    def write(self,reason,value):
        status_mon = self.driver.getParam('IOC:Status-Mon')
        if status_mon != 'ok':
            return False # when returning True super().write of PCASDrive is invoked

        self.pvs[reason]['epics_objc'].put(value)

        # implementation here
        #self.driver.updatePVs() # this should be used in case PV states change.
        return True # when returning True super().write of PCASDrive is invoked

    def process_all_pvs(self):

        status_mon = 'ok'
        changed = False
        for ma_pv_name, pv_dict in self.pvs.items():
            #print(ma_pv_name)
            #print('ok1')
            value_ps = pv_dict['epics_objc'].get()
            #print('ok2')
            if value_ps is not None:
                value_ma = self.driver.getParam(ma_pv_name)
                if value_ps != value_ma:
                    self.driver.setParam(pv_dict['ma_pv_name'], value_ps)
                    changed = True
            else:
                status_mon = ma_pv_name + ' not connected!'
                changed = True
            pass

        # updates Status-mon of the Soft IOC, if necessary
        prev_value = self.driver.getParam('IOC:Status-Mon')
        if status_mon != prev_value:
            self.driver.setParam('IOC:Status-Mon', status_mon)
            changed = True

        return changed
