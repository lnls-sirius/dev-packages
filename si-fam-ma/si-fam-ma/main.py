import pvs as _pvs
import time as _time
import siriuspy as _siriuspy
import uuid as _uuid
import re as _re
from siriuspy.search import MASearch as _MASearch
import threading
from epics import caget

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
    strengths = ['Energy', 'KL', 'SL', 'Kick', 'KLRef']
    writable_fields = ['SP', 'Sel']

    def __init__(self, driver):

        _siriuspy.util.print_ioc_banner(
            ioc_name = 'si-ma',
            db = App.pvs_database,#[_pvs._PREFIX],
            description = 'SI Magnet Power Supply Soft IOC',
            version = __version__,
            prefix = _pvs._PREFIX)

        self._driver = driver
        self._set_callback()


    @property
    def driver(self):
        return self._driver

    def process(self, interval):
        _time.sleep(interval)

    def read(self, reason):
        """ Reads from IOC database """
        return None

    def write(self, reason, value):
        """ Write value to reason and let callback update PV database. """
        #Get property and field
        sub_section, discipline, device, propty, field = self._break_name(reason)
        #Check if field is writable
        if field not in App.writable_fields:
            return
        #Build attribute name
        if propty in App.strengths:
            attr = 'strength_' + field
        else:
            attr = propty + '_' + field
        attr = attr.lower()
        #Update MA Object
        slot_name = sub_section + ':' + discipline + '-' + device
        ma = self.ma_devices[slot_name]
        setattr(ma, attr, value)
        #Update IOC database
        self._driver.setParam(reason, value)
        self._driver.updatePVs()
        #Update trim objects
        # if      sub_section == "Fam" and \
        #         propty in (['Current'] + App.strengths) and \
        #         field == 'SP':
        #
        #         self._update_trim(reason)

        return

    def _break_name(self, reason):
        ''' Breaks a reason into its sub parts '''
        sub_section, discdev, pfield = reason.split(':')
        propty, field = pfield.split('-')
        discipline, device = discdev.split('-')
        return (sub_section, discipline, device, propty, field)

    def _update_trim(self, reason):
        """ Update magnet trim objects """
        trims = self._get_trims(reason)
        trims = [x.replace(":PS", ":MA").split('SI-')[1] for x in trims]
        if trims:
            _, _, _, propty, field= self._break_name(reason)
            for trim in trims:
                trim_reason = trim + ':' + propty + '-' + field
                ma = self.ma_devices[trim]
                value = getattr(ma, "strength_" + field.lower())
                self._driver.setParam(trim_reason, value)
                self._driver.updatePVs()

    def _get_trims(self, reason):
        pvname = _pvs._PREFIX + ':'.join(reason.split(':')[:2])
        return _MASearch.conv_maname_2_trims(pvname)

    def _set_callback(self):
        for family, device in App.ma_devices.items():
            device.callback = self._mycallback
            device._controller.update_state()

    def _mycallback(self, pvname, value, **kwargs):
        _, reason = pvname.split('SI-')
        prev_value = self._driver.getParam(reason)
        if value != prev_value:
            self._driver.setParam(reason, value)
            self._driver.updatePVs()
