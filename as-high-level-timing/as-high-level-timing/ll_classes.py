import re as _re
import epics as _epics
from siriuspy.namesys import SiriusPVName as _PVName

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

_TIMEOUT = 0.05

RFFREQ = 299792458/518.396*864

TRIGCH_REGEXP = _re.compile('([a-z]+)([0-9]*)',_re.IGNORECASE)

_LOW_LEVEL_TRIGGER_CLASSES = {
    ('evr','mfo'): _LL_TrigEVRMFO,
    ('evr','opt'): _LL_TrigEVROPT,
    ('eve','elp'): _LL_TrigEVRELP,
    ('eve','opt'): _LL_TrigEVROPT,
    ('afc','elp'): _LL_TrigEVRELP,
    ('afc','opt'): _LL_TrigEVROPT,
    }
def get_low_level_trigger_object(device,callback,initial_hl2ll):
    dev = _PVName(device)
    conn, num = TRIGCH_REGEXP.findall(dev.propty.lower())
    key = (dev.dev_type.lower(), conn)
    cls_ = _LOW_LEVEL_TRIGGER_CLASSES.get(key)
    if not cls_:
        raise Exception('Low Level Trigger Class not defined for device type '+key[0]+' and connection type '+key[1]+'.')
    return cls_(dev.dev_name, conn, num, callback, initial_hl2ll)


class _LL_TrigEVRMFO:
    _NUM_OPT   = 12
    _NUM_INT   = 24
    _INTTMP    = 'IntTrig{0:02d}'
    _OUTTMP    = 'MFO{0:d}'
    _REMOVE_PROPS = {}

    def __init__(self, device, conn, num,  callback, initial_hl2ll):
        self._WRITE_FUNS = self._get_write_funs_map()
        self._READ_FUNS = self._get_read_funs_map()
        self._WRITE_PVS_MAP     = self.get_map_pvs_sp()
        self._WRITE_PVS_MAP_INV = { val:key for key,val in self._WRITE_PVS_MAP.items() }
        self._READ_PVS_MAP      = self.get_map_pvs_rb()
        self._READ_PVS_MAP_INV  = { val:key for key,val in self._READ_PVS_MAP.items() }
        self.callback = callback
        self.prefix = device + ':'
        self._OUTLB = self._OUTTMP.format(num)
        self._INTLB = self._INTTMP.format(self._get_num_int(num))
        self._hl2ll = initial_hl2ll
        self._pvs_sp = dict()
        self._pvs_rb = dict()
        for prop, pv in self._WRITE_PVS_MAP.items():
            self._pvs_sp[prop]  = _epics.PV(self.prefix + pv,
                                            callback = self._pvs_sp_callback,
                                            timeout=_TIMEOUT)
        for prop, pv in self._READ_PVS_MAP.items():
            self._pvs_rb[prop]  = _epics.PV(self.prefix + pv,
                                            callback = self._pvs_rb_callback,
                                            timeout=_TIMEOUT)

    def _get_num_int(self,num):
        return self._NUM_OPT + num

    def _get_map_pvs_sp(self):
        map_ = {
            'internal_trigger' : self._OUTLB + 'IntChan-SP',
            'event'      : self._INTLB + 'Event-SP',
            'delay1'     : self._INTLB + 'Delay-SP',
            'delay2'     : self._OUTLB + 'Delay-SP',
            'delay3'     : self._OUTLB + 'FineDelay-SP',
            'delay_type' : self._INTLB + 'DelayType-Sel',
            'pulses'     : self._INTLB + 'Pulses-Sel',
            'width'      : self._INTLB + 'Width-Sel',
            'state'      : self._INTLB + 'State-Sel',
            'polarity'   : self._INTLB + 'Polrty-Sel',
            }
        for prop in _REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_map_pvs_rb(self):
        map_ = {
            'internal_trigger' : self._OUTLB + 'IntChan-RB',
            'event'      : self._INTLB + 'Event-RB',
            'delay1'     : self._INTLB + 'Delay-RB',
            'delay2'     : self._OUTLB + 'Delay-RB',
            'delay3'     : self._OUTLB + 'FineDelay-RB',
            'delay_type' : self._INTLB + 'DelayType-Sts',
            'pulses'     : self._INTLB + 'Pulses-Sts',
            'width'      : self._INTLB + 'Width-Sts',
            'state'      : self._INTLB + 'State-Sts',
            'polarity'   : self._INTLB + 'Polrty-Sts',
            }
        for prop in _REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_write_funs_map(self):
        map_ = {
            'work_as'    : lambda x: self.set_int_channel('work_as',x),
            'clock'      : lambda x: self.set_int_channel('clock',x),
            'delay'      : self.set_delay,
            'event'      : lambda x: self.set_simple('event',x),
            'delay_type' : lambda x: self.set_simple('delay_type',x),
            'pulses'     : lambda x: self.set_simple('pulses',x),
            'width'      : lambda x: self.set_simple('width',x),
            'state'      : lambda x: self.set_simple('state',x),
            'polarity'   : lambda x: self.set_simple('polarity',x),
            }
        return map_

    def _get_read_funs_map(self):
        map_ = {
            'internal_trigger' : self.get_int_channel,
            'event'      : lambda x,ty=None: {'event':x},
            'delay1'     : self.get_delay,
            'delay2'     : self.get_delay,
            'delay3'     : self.get_delay,
            'delay_type' : lambda x,ty=None: {'delay_type':x},
            'pulses'     : lambda x,ty=None: {'pulses':x},
            'width'      : lambda x,ty=None: {'width':x},
            'state'      : lambda x,ty=None: {'state':x},
            'polarity'   : lambda x,ty=None: {'polarity':x},
            }
        for prop in _REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _pvs_rb_callback(self,pv_name,pv_value,**kwargs):
        pv = _PVName(pv_name)
        props = self._READ_FUNS[ self._READ_PVS_MAP_INV[pv.propty] ](pv_value)
        for prop,value in props.items():
            self.callback(pv.dev_name, prop, value)

    def _pvs_sp_callback(self,pv_name,pv_value,**kwargs):
        if not _FORCE_EQUAL: return
        pv = _PVName(pv_name)
        props = self._READ_FUNS[ self._WRITE_PVS_MAP_INV[pv.propty] ](pv_value, ty='sp')
        for prop,value in props.items():
            if self._hl2ll[prop] != value:
                self.set_propty(prop, value)

    def set_simple(self,prop,value):
        self._hl2ll[prop]   = value
        self.pvs_sp[prop].value = value

    def get_delay(self, value, ty = None):
        pvs = self._pvs_sp if ty else self._pvs_rb
        delay  = pvs['delay1'].value
        delay += pvs['delay2'].value
        delay += pvs['delay3'].value * 1e-3  # nanoseconds
        return {'delay':delay}

    def set_delay(self,value):
        rf_per = 1/RFFREQ * 1e6
        delay1_unit = rf_per * 4
        delay2_unit = rf_per * 4 / 20
        delay1_unit = 5e-6 # five picoseconds

        delay1  = (value // delay1_unit) * delay1_unit
        value  -= delay1
        delay2  = (value // delay2_unit) * delay2_unit
        value  -= delay2
        delay3  = (value // delay3_unit) * delay3_unit * 1e3 # in nanoseconds

        self._hl2ll['delay'] = delay1 + delay2 + delay3/1e3
        self.pvs_sp['delay1'].value = delay1
        self.pvs_sp['delay2'].value = delay2
        self.pvs_sp['delay3'].value = delay3

    def get_int_channel(self, value, ty = None):
        pvs = self._pvs_sp if ty else self._pvs_rb
        props = dict()
        if value < self._NUM_INT:
            props['work_as'] = 0
        else:
            props['work_as'] = 1
            props['clock'] = value - self._NUM_INT
        return props

    def set_int_channel(self,prop,value):
        self._hl2ll[prop] = value
        if not self._hl2ll['work_as']:
            self._pvs_sp['internal_trigger'].value = self._internal_trigger
        else:
            clock_num = self._hl2ll['clock']
            self._pvs_sp['internal_trigger'].value = self._NUM_INT + clock_num

    def _pvs_values_rb(self, channel, prop, value):
        if prop not in self._WRITABLE_PROPS: return
        ind = self._channel_names.index(channel)
        self._values_rb[prop][ind] = self._READ_FUNS[prop](value,ind)
        self.callback( self.prefix + self._READ_MAP[prop], self._values_rb[prop]  )

    def set_propty(prop,value):
        self._WRITE_FUNS[prop](value)


class _LL_TrigEVROPT(_LL_TrigEVRMFO):
    _NUM_OPT   = 12
    _NUM_INT   = 24
    _INTTMP    = 'IntTrig{0:02d}'
    _REMOVE_PROPS = {'delay2','delay3','internal_trigger'}

    def _get_num_int(self,num):
        return num

    def get_delay(self, value, ty = None):
        pvs = self._pvs_sp if ty else self._pvs_rb
        delay  = pvs['delay1'].value
        return {'delay':delay}

    def set_delay(self,value):
        rf_per = 1/RFFREQ * 1e6
        delay1_unit = rf_per * 4
        delay1  = (value // delay1_unit) * delay1_unit
        self._hl2ll['delay'] = delay1
        self.pvs_sp['delay1'].value = delay1


class _LL_TrigEVELVEO(_LL_TrigEVRMFO):
    _NUM_OPT   = 0
    _NUM_INT   = 16
    _INTTMP    = 'IntTrig{0:02d}'
    _OUTTMP    = 'LVEO{0:d}'


class _LL_TrigAFCLVEO(_LL_TrigEVRMFO):
    _NUM_OPT   = 0
    _NUM_INT   = 18
    _INTTMP    = 'LVEO{0:02d}'
    _OUTTMP    = 'LVEO{0:02d}'
    _REMOVE_PROPS = {'delay2','delay3','internal_trigger'}
