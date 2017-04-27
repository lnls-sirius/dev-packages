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

RFFREQ = 299792458/518.396*864  # This should be read from the RF generator Setpoint
RF_PER = 1/RFFREQ * 1e6         # In micro seconds
D1_STEP = RF_PER * 4
D2_STEP = RF_PER * 4 / 20
D3_STEP = 5e-6                  # five picoseconds


TRIGCH_REGEXP = _re.compile('([a-z]+)([0-9]*)',_re.IGNORECASE)


class EventInterface:

    @classmethod
    def get_database(cls,prefix=''):
        db = dict()
        db[prefix + 'Delay-SP']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us', 'prec': 3}
        db[prefix + 'Delay-RB']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us','prec': 3}
        db[prefix + 'Mode-Sel']      = {'type' : 'enum', 'enums':_tm.MODES, 'value':1}
        db[prefix + 'Mode-Sts']      = {'type' : 'enum', 'enums':_tm.MODES, 'value':1}
        db[prefix + 'DelayType-Sel'] = {'type' : 'enum', 'enums':_tm.DELAY_TYPES, 'value':1}
        db[prefix + 'DelayType-Sts'] = {'type' : 'enum', 'enums':_tm.DELAY_TYPES, 'value':1}

    def __init__(self,name,callback=None):
        self.callback = callback
        self.low_level_code  = _timedata.EVENT_MAPPING[name]
        self.low_level_label = EVG + ':' + _timedata.EVENT_LABEL_TEMPLATE.format(self.code)
        self.low_level_pvs = dict()
        options = dict(callback=self._call_callback, connection_timeout=_TIMEOUT)
        for pv in self.get_database().keys():
            self.low_level_pvs[pv] = _epics.PV(self.low_level_label+pv,**options )

    def get_propty(self,pv):
        return self.low_level_pvs[pv].value

    def set_propty(self,pv, value):
        self.low_level_pvs[pv].value = value

    def _call_callback(self,pv_name,pv_value,**kwargs):
        pv_name = self.low_level_label + pv_name
        if self._callback: self._callback(pv_name,pv_value,**kwargs)


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
        self._HLPROP_FUNS = self._get_hlprop_funs_map()
        self._LLPROP_FUNS = self._get_llprop_funs_map()
        self._LLPROP_2_PVSP = self._get_llprop_2_pvsp_map()
        self._PVSP_2_LLPROP = { val:key for key,val in self._LLPROP_2_PVSP.items() }
        self._LLPROP_2_PVRB = self._get_llprop_2_pvrb_map()
        self._PVRB_2_LLPROP = { val:key for key,val in self._LLPROP_2_PVRB.items() }
        self.callback = callback
        self.prefix = device + ':'
        self._OUTLB = self._OUTTMP.format(num)
        self._INTLB = self._INTTMP.format(self._get_num_int(num))
        self._hl2ll = initial_hl2ll
        self._pvs_sp = dict()
        self._pvs_rb = dict()
        for prop, pv in self._LLPROP_2_PVSP.items():
            self._pvs_sp[prop]  = _epics.PV(self.prefix + pv,
                                            callback = self._pvs_sp_callback,
                                            timeout=_TIMEOUT)
        for prop, pv in self._LLPROP_2_PVRB.items():
            self._pvs_rb[prop]  = _epics.PV(self.prefix + pv,
                                            callback = self._pvs_rb_callback,
                                            timeout=_TIMEOUT)

    def _get_num_int(self,num):
        return self._NUM_OPT + num

    def _get_llprop_2_pvsp_map(self):
        map_ = {
            'internal_trigger' : self._OUTLB + 'IntChan-SP',
            'event'      : self._INTLB + 'Event-SP',
            'delay1'     : self._INTLB + 'Delay-SP',
            'delay2'     : self._OUTLB + 'Delay-SP',
            'delay3'     : self._OUTLB + 'FineDelay-SP',
            'pulses'     : self._INTLB + 'Pulses-Sel',
            'width'      : self._INTLB + 'Width-Sel',
            'state'      : self._INTLB + 'State-Sel',
            'polarity'   : self._INTLB + 'Polrty-Sel',
            }
        for prop in _REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_llprop_2_pvrb_map(self):
        map_ = {
            'internal_trigger' : self._OUTLB + 'IntChan-RB',
            'event'      : self._INTLB + 'Event-RB',
            'delay1'     : self._INTLB + 'Delay-RB',
            'delay2'     : self._OUTLB + 'Delay-RB',
            'delay3'     : self._OUTLB + 'FineDelay-RB',
            'pulses'     : self._INTLB + 'Pulses-Sts',
            'width'      : self._INTLB + 'Width-Sts',
            'state'      : self._INTLB + 'State-Sts',
            'polarity'   : self._INTLB + 'Polrty-Sts',
            }
        for prop in _REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_hlprop_funs_map(self):
        map_ = {
            'work_as'    : lambda x: self._set_int_channel('work_as',x),
            'clock'      : lambda x: self._set_int_channel('clock',x),
            'delay'      : self._set_delay,
            'event'      : lambda x: self._set_simple('event',x),
            'pulses'     : lambda x: self._set_simple('pulses',x),
            'width'      : lambda x: self._set_simple('width',x),
            'state'      : lambda x: self._set_simple('state',x),
            'polarity'   : lambda x: self._set_simple('polarity',x),
            }
        return map_

    def _get_llprop_funs_map(self):
        map_ = {
            'internal_trigger' : self._get_int_channel,
            'event'      : lambda x,ty=None: {'event':x},
            'delay1'     : self._get_delay,
            'delay2'     : self._get_delay,
            'delay3'     : self._get_delay,
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
        props = self._LLPROP_FUNS[ self._PVRB_2_LLPROP[pv.propty] ](pv_value)
        for prop,value in props.items():
            self.callback(pv.dev_name, prop, value)

    def _pvs_sp_callback(self,pv_name,pv_value,**kwargs):
        if not _FORCE_EQUAL: return
        pv = _PVName(pv_name)
        props = self._LLPROP_FUNS[ self._PVSP_2_LLPROP[pv.propty] ](pv_value, ty='sp')
        for prop,value in props.items():
            if self._hl2ll[prop] != value:
                self.set_propty(prop, value)

    def _set_simple(self,prop,value):
        self._hl2ll[prop]   = value
        self.pvs_sp[prop].value = value

    def _get_delay(self, value, ty = None):
        pvs = self._pvs_sp if ty else self._pvs_rb
        delay  = pvs['delay1'].value
        delay += pvs['delay2'].value
        delay += pvs['delay3'].value * 1e-3  # nanoseconds
        return {'delay':delay}

    def _set_delay(self,value):
        delay1  = (value // D1_STEP) * D1_STEP
        value  -= delay1
        delay2  = (value // D2_STEP) * D2_STEP
        value  -= delay2
        delay3  = (value // D3_STEP) * D3_STEP * 1e3 # in nanoseconds

        self._hl2ll['delay'] = delay1 + delay2 + delay3/1e3
        self.pvs_sp['delay1'].value = delay1
        self.pvs_sp['delay2'].value = delay2
        self.pvs_sp['delay3'].value = delay3

    def _get_int_channel(self, value, ty = None):
        pvs = self._pvs_sp if ty else self._pvs_rb
        props = dict()
        if value < self._NUM_INT:
            props['work_as'] = 0
        else:
            props['work_as'] = 1
            props['clock'] = value - self._NUM_INT
        return props

    def _set_int_channel(self,prop,value):
        self._hl2ll[prop] = value
        if not self._hl2ll['work_as']:
            self._pvs_sp['internal_trigger'].value = self._internal_trigger
        else:
            clock_num = self._hl2ll['clock']
            self._pvs_sp['internal_trigger'].value = self._NUM_INT + clock_num

    def set_propty(prop,value):
        self._HLPROP_FUNS[prop](value)


class _LL_TrigEVROPT(_LL_TrigEVRMFO):
    _NUM_OPT   = 12
    _NUM_INT   = 24
    _INTTMP    = 'IntTrig{0:02d}'
    _REMOVE_PROPS = {'delay2','delay3','internal_trigger'}

    def _get_num_int(self,num):
        return num

    def _get_delay(self, value, ty = None):
        pvs = self._pvs_sp if ty else self._pvs_rb
        delay  = pvs['delay1'].value
        return {'delay':delay}

    def _set_delay(self,value):
        delay1  = (value // D1_STEP) * D1_STEP
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
