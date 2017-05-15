import re as _re
import epics as _epics
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.timesys.time_data import Connections, IOs, Events

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

_TIMEOUT = 0.05
_FORCE_EQUAL = True

LL_PREFIX = 'VAF-'

RFFREQ = 299792458/518.396*864  # This should be read from the RF generator Setpoint
RF_PER = 1/RFFREQ * 1e6         # In micro seconds
D1_STEP = RF_PER * 4
D2_STEP = RF_PER * 4 / 20
D3_STEP = 5e-6                  # five picoseconds

EVG  = Connections.get_devices('EVG').pop()


def get_ll_trigger_object(channel,callback,initial_hl2ll):
    LL_TRIGGER_CLASSES = {
        ('EVR','MF'): _LL_TrigEVRMF,
        ('EVR','OPT'): _LL_TrigEVROPT,
        ('EVE','LVE'): _LL_TrigEVELVE,
        ('AFC','LVE'): _LL_TrigAFCLVE,
        ('AFC','OPT'): _LL_TrigAFCOPT,
        }
    chan = _PVName(channel)
    conn_ty,conn_conf, conn_num = IOs.LL_RGX.findall(chan.propty)[0]
    key = (chan.dev_type, conn_ty)
    cls_ = LL_TRIGGER_CLASSES.get(key)
    if not cls_:
        raise Exception('Low Level Trigger Class not defined for device type '+key[0]+' and connection type '+key[1]+'.')
    return cls_(channel, int(conn_num), callback, initial_hl2ll)


class _LL_TrigEVRMF:
    _NUM_OPT   = 12
    _NUM_INT   = 24
    _INTTMP    = 'IntTrig{0:02d}'
    _OUTTMP    = 'MFO{0:d}'
    _REMOVE_PROPS = {}

    def __init__(self, channel, conn_num,  callback, initial_hl2ll):
        self._internal_trigger = self._get_num_int(conn_num)
        self._OUTLB = self._OUTTMP.format(conn_num)
        self._INTLB = self._INTTMP.format(self._internal_trigger)
        self._HLPROP_FUNS = self._get_HLPROP_FUNS()
        self._LLPROP_FUNS = self._get_LLPROP_FUNS()
        self._LLPROP_2_PVSP = self._get_LLPROP_2_PVSP()
        self._PVSP_2_LLPROP = { val:key for key,val in self._LLPROP_2_PVSP.items() }
        self._LLPROP_2_PVRB = self._get_LLPROP_2_PVRB()
        self._PVRB_2_LLPROP = { val:key for key,val in self._LLPROP_2_PVRB.items() }
        self.callback = callback
        self.prefix = _PVName(channel).dev_name + ':'
        self._hl2ll = initial_hl2ll
        self._pvs_sp = dict()
        self._pvs_rb = dict()
        print('     creating PVs :')
        for prop, pv in self._LLPROP_2_PVSP.items():
            pv_name = LL_PREFIX + self.prefix + pv
            self._pvs_sp[prop]  = _epics.PV(pv_name,
                                            callback = self._pvs_sp_callback,
                                            connection_timeout=_TIMEOUT)
            print(8*' ' + '{0:45s}{1:s}connected'.format(
                        pv_name,'' if self._pvs_sp[prop].connected else 'dis'))
        for prop, pv in self._LLPROP_2_PVRB.items():
            pv_name = LL_PREFIX + self.prefix + pv
            self._pvs_rb[prop]  = _epics.PV(pv_name,
                                            callback = self._pvs_rb_callback,
                                            connection_timeout=_TIMEOUT)
            print(8*' ' + '{0:45s}{1:s}connected'.format(
                        pv_name,'' if self._pvs_sp[prop].connected else 'dis'))
        print('\n')

    def _get_num_int(self,num):
        return self._NUM_OPT + num

    def _get_LLPROP_2_PVSP(self):
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
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_LLPROP_2_PVRB(self):
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
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_HLPROP_FUNS(self):
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

    def _get_LLPROP_FUNS(self):
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
        for prop in self._REMOVE_PROPS:
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
        pv = self._pvs_sp[prop]
        if pv.connected: pv.value = value

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
        pv = self._pvs_sp['delay1']
        if pv.connected:
            pv.value = delay1
            self._pvs_sp['delay2'].value = delay2
            self._pvs_sp['delay3'].value = delay3

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
        int_trig = self._pvs_sp.get('internal_trigger')
        if int_trig is None: return
        if not self._hl2ll['work_as']:
             val = self._internal_trigger
        else:
            clock_num = self._hl2ll['clock']
            val = self._NUM_INT + clock_num

        if int_trig.connected: int_trig.value = val

    def set_propty(self,prop,value):
        fun = self._HLPROP_FUNS.get(prop)
        if fun is None:  return False
        fun(value)
        return True


class _LL_TrigEVROPT(_LL_TrigEVRMF):
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
        pv = self._pvs_sp['delay1']
        if pv.connected:
            pv.value = delay1


class _LL_TrigEVELVE(_LL_TrigEVRMF):
    _NUM_OPT   = 0
    _NUM_INT   = 16
    _INTTMP    = 'IntTrig{0:02d}'
    _OUTTMP    = 'LVEO{0:d}'


class _LL_TrigAFCLVE(_LL_TrigEVRMF):
    _NUM_OPT   = 0
    _NUM_INT   = 256
    _INTTMP    = 'LVEO{0:02d}'
    _REMOVE_PROPS = {'delay2','delay3','internal_trigger'}

    def _get_LLPROP_2_PVSP(self):
        map_ = super()._get_LLPROP_2_PVSP()
        map_['event'] = self._INTLB + 'EVGParam-SP'
        return map_

    def _get_LLPROP_2_PVRB(self):
        map_ = super()._get_LLPROP_2_PVRB()
        map_['event'] = self._INTLB + 'EVGParam-RB'
        return map_

    def _get_HLPROP_FUNS(self):
        map_ = super()._get_HLPROP_FUNS()
        map_['work_as'] = lambda x: self._set_channel_to_listen('work_as',x)
        map_['event']   = lambda x: self._set_channel_to_listen('event',x)
        map_['clock']   = lambda x: self._set_channel_to_listen('clock',x)
        return map_

    def _get_LLPROP_FUNS(self):
        map_ = super()._get_LLPROP_FUNS()
        map_['event'] = self._get_channel_to_listen
        return map_

    def _get_delay(self, value, ty = None):
        pvs = self._pvs_sp if ty else self._pvs_rb
        delay  = pvs['delay1'].value
        return {'delay':delay}

    def _set_delay(self,value):
        delay1  = (value // D1_STEP) * D1_STEP
        self._hl2ll['delay'] = delay1
        pv = self._pvs_sp['delay1']
        if pv.connected:
            pv.value = delay1

    def _get_channel_to_listen(self, value, ty = None):
        pvs = self._pvs_sp if ty else self._pvs_rb
        props = dict()
        if value < self._NUM_INT:
            props['work_as'] = 0
            props['event'] = value
        else:
            props['work_as'] = 1
            props['clock'] = value - self._NUM_INT
        return props

    def _set_channel_to_listen(self,prop,value):
        self._hl2ll[prop] = value
        if not self._hl2ll['work_as']:
            val = self._hl2ll['event']
        else:
            clock_num = self._hl2ll['clock']
            val = self._NUM_INT + clock_num

        pv = self._pvs_sp['event']
        if pv.connected:
            pv.value = val


class _LL_TrigAFCOPT(_LL_TrigAFCLVE):
    _INTTMP = 'OPT{0:02d}'


class LL_Event:

    def __init__(self, code,  callback, initial_hl2ll):
        self._HLPROP_FUNS = self._get_HLPROP_FUNS()
        self._LLPROP_FUNS = self._get_LLPROP_FUNS()
        self._LLPROP_2_PVSP = self._get_LLPROP_2_PVSP()
        self._PVSP_2_LLPROP = { val:key for key,val in self._LLPROP_2_PVSP.items() }
        self._LLPROP_2_PVRB = self._get_LLPROP_2_PVRB()
        self._PVRB_2_LLPROP = { val:key for key,val in self._LLPROP_2_PVRB.items() }
        self.callback = callback
        self.prefix = EVG + ':' + Events.LL_TMP.format(code)
        print('   Connecting to Low Level Object '+self.prefix)
        self._hl2ll = initial_hl2ll
        self._pvs_sp = dict()
        self._pvs_rb = dict()
        print('     creating PVs :')
        for prop, pv in self._LLPROP_2_PVSP.items():
            pv_name = LL_PREFIX + self.prefix + pv
            self._pvs_sp[prop]  = _epics.PV(pv_name,
                                            # callback = self._pvs_sp_callback,
                                            connection_timeout=_TIMEOUT)
            self._pvs_sp[prop].get()
            print(8*' ' + '{0:45s}{1:s}connected'.format(
                        pv_name,'' if self._pvs_sp[prop].connected else 'dis'))
        for prop, pv in self._LLPROP_2_PVRB.items():
            pv_name = LL_PREFIX + self.prefix + pv
            self._pvs_rb[prop]  = _epics.PV(pv_name,
                                            # callback = self._pvs_rb_callback,
                                            connection_timeout=_TIMEOUT)
            self._pvs_sp[prop].get()
            print(8*' ' + '{0:45s}{1:s}connected'.format(
                        pv_name,'' if self._pvs_sp[prop].connected else 'dis'))
        print('\n')

    def _get_LLPROP_2_PVSP(self):
        map_ = {
            'delay'      : 'Delay-SP',
            'mode'       : 'Mode-Sel',
            'delay_type' : 'DelayType-Sel',
            }
        return map_

    def _get_LLPROP_2_PVRB(self):
        map_ = {
            'delay'      : 'Delay-RB',
            'mode'       : 'Mode-Sts',
            'delay_type' : 'DelayType-Sts',
            }
        return map_

    def _get_HLPROP_FUNS(self):
        map_ = {
            'delay'      : lambda x: self._set_simple('delay',x),
            'mode'       : lambda x: self._set_simple('mode',x),
            'delay_type' : lambda x: self._set_simple('delay_type',x),
            }
        return map_

    def _get_LLPROP_FUNS(self):
        map_ = {
            'delay'      : lambda x: x,
            'mode'       : lambda x: x,
            'delay_type' : lambda x: x,
            }
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
        pv = self._pvs_sp[prop]
        if pv.connected: pv.value = value

    def set_propty(self,prop,value):
        fun = self._HLPROP_FUNS.get(prop)
        if fun is None:  return False
        fun(value)
        return True
