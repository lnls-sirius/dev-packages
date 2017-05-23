import logging as _log
import time as _time
import sys as _sys
import re as _re
import epics as _epics
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.timesys.time_data import IOs

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

_TIMEOUT = 0.05
_FORCE_EQUAL = False

LL_PREFIX = 'VAF-'

RFFREQ = 299792458/518.396*864  # This should be read from the RF generator Setpoint
RF_PER = 1/RFFREQ * 1e6         # In micro seconds
D1_STEP = RF_PER * 4
D2_STEP = RF_PER * 4 / 20
D3_STEP = 5e-6                  # five picoseconds

def get_ll_trigger_object(channel,callback,connection_callback,initial_hl2ll):
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
    return cls_(channel, int(conn_num), callback, connection_callback, initial_hl2ll)

class _LL_Base:


    def __init__(self, callback, connection_callback, initial_hl2ll):
        self._HLPROP_FUNS = self._get_HLPROP_FUNS()
        self._LLPROP_FUNS = self._get_LLPROP_FUNS()
        self._LLPROP_2_PVSP = self._get_LLPROP_2_PVSP()
        self._channel = { val:key for key,val in self._LLPROP_2_PVSP.items() }
        self._LLPROP_2_PVRB = self._get_LLPROP_2_PVRB()
        self._PVRB_2_LLPROP = { val:key for key,val in self._LLPROP_2_PVRB.items() }
        self.callback = callback
        self.conn_callback = connection_callback
        self._hl2ll = initial_hl2ll
        self._pvs_sp = dict()
        self._pvs_rb = dict()
        self._pvs_conn_sts = dict()
        self._pvs_sp_canput = dict()
        _log.info(self.channel+': Starting.')
        _log.info(self.channel+': Creating PVs.')
        for prop, pv_name in self._LLPROP_2_PVSP.items():
            _log.debug(self.channel +' -> creating {0:s}'.format(pv_name))
            self._pvs_conn_sts[pv_name] = False
            self._pvs_sp_canput[pv_name] = True
            self._pvs_sp[prop]  = _epics.PV(pv_name,
                                            callback = self._pvs_sp_callback,
                                            connection_callback = self._pvs_on_connection,
                                            connection_timeout=_TIMEOUT)
        for prop, pv_name in self._LLPROP_2_PVRB.items():
            _log.debug(self.channel +' -> creating {0:s}'.format(pv_name))
            self._pvs_conn_sts[pv_name] = False
            self._pvs_rb[prop]  = _epics.PV(pv_name,
                                            callback = self._pvs_rb_callback,
                                            connection_callback = self._pvs_on_connection,
                                            connection_timeout=_TIMEOUT)
        _log.info(self.channel + ': Done.')

    def _get_LLPROP_2_PVSP(self):
        map_ = dict()
        return map_

    def _get_LLPROP_2_PVRB(self):
        map_ = dict()
        return map_

    def _get_HLPROP_FUNS(self):
        map_ = dict()
        return map_

    def _get_LLPROP_FUNS(self):
        map_ = dict()
        return map_

    def _pvs_on_connection(self,pvname,conn,pv):
        _log.debug(self.channel+' PV {0:10s} {1:s}connected'.format(pvname, '' if conn else 'dis'))
        previous = all(self._pvs_conn_sts.values())
        self._pvs_conn_sts[pvname] = conn
        current = all(self._pvs_conn_sts.values())
        if current is not previous:
            _log.info(self.channel+' {0:s}all PVs connected.'.format('' if current else 'NOT '))
            self.conn_callback(self.channel,current)

    def check(self):
        for ll_prop,pv in self._pvs_sp.items():
            if pv.connected and self._pvs_sp_canput[pv.pvname]:
                v = pv.get(timeout=_TIMEOUT)
                if v is None:
                    _log.debug(self.channel+' propty = {0:s} is None '.format(ll_prop))
                    continue
                props = self._LLPROP_FUNS[ll_prop](v, ty='sp')
                for hl_prop,val in props.items():
                    my_val = self._hl2ll[hl_prop]
                    if my_val == val: continue
                    _log.debug(self.channel+' propty = {0:s} Value = {1:s} '.format(hl_prop,str(my_val)))
                    self.set_propty(hl_prop, my_val)

    def _pvs_rb_callback(self,pvname,value,**kwargs):
        if value is None:
            _log.debug(self.channel+' pvs_rb_callback; {0:s} received None'.format(pvname))
            return
        _log.debug(self.channel+' pvs_rb_callback; PV = {0:s} New Value = {1:s} '.format(pvname,str(value)))
        props = self._LLPROP_FUNS[ self._PVRB_2_LLPROP[pvname] ](value)
        for hl_prop,val in props.items():
            _log.debug(self.channel+' pvs_rb_callback; Sending to HL;  propty = {0:s} Value = {1:s} '.format(hl_prop,str(val)))
            self.callback(self.channel, hl_prop, val)

    def _pvs_sp_callback(self,pvname,value,**kwargs):
        if value is None:
            _log.debug(self.channel+' pvs_sp_callback; {0:s} received None'.format(pvname))
            return
        _log.debug(self.channel+' pvs_sp_callback; PV = {0:s} New Value = {1:s} '.format(pvname,str(value)))
        if not _FORCE_EQUAL: return
        props = self._LLPROP_FUNS[ self._PVSP_2_LLPROP[pvname] ](value, ty='sp')
        for hl_prop,val in props.items():
            my_val = self._hl2ll[hl_prop]
            if my_val != val:
                _log.debug(self.channel+' pvs_sp_callback; Forcing  propty = {0:s} Value = {1:s} '.format(hl_prop,str(my_val)))
                self.set_propty(hl_prop, my_val)

    def _put_complete(self,pvname,**kwargs):
        self._pvs_sp_canput[pvname] = True

    def _put_on_pv(self,pv,value):
        self._pvs_sp_canput[pv.pvname] = False
        pv.put(value,callback=self._put_complete)

    def _set_simple(self,prop,value):
        _log.debug(self.channel+' propty = {0:s}, value = {1:s}.'.format(prop,str(value)))
        pv = self._pvs_sp[prop]
        if not pv.connected:
            _log.debug(self.channel+' PV '+pv.pvname+' NOT connected.')
            return
        self._hl2ll[prop]   = value
        _log.debug(self.channel+' Setting PV '+pv.pvname+', value = {0:s}.'.format(str(value)))
        self._put_on_pv(pv, value)

    def set_propty(self,prop,value):
        _log.debug(self.channel+' set_propty receive propty = {0:s}; Value = {1:s}'.format(
                                                                prop,str(value)))
        fun = self._HLPROP_FUNS.get(prop)
        if fun is None:  return False
        fun(value)
        return True



class LL_Clock(_LL_Base):

    def __init__(self, channel,  callback, connection_callback, initial_hl2ll):
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback,connection_callback,initial_hl2ll)

    def _get_LLPROP_2_PVSP(self):
        map_ = {
            'frequency' : self.prefix + 'Freq-SP',
            'state'     : self.prefix + 'State-Sel',
            }
        return map_

    def _get_LLPROP_2_PVRB(self):
        map_ = {
            'frequency' : self.prefix + 'Freq-RB',
            'state'     : self.prefix + 'State-Sts',
            }
        return map_

    def _get_HLPROP_FUNS(self):
        map_ = {
            'frequency' : lambda x: self._set_simple('frequency',x),
            'state'     : lambda x: self._set_simple('state',x),
            }
        return map_

    def _get_LLPROP_FUNS(self):
        map_ = {
            'frequency' : lambda x,ty=None: {'frequency':x},
            'state'     : lambda x,ty=None: {'state':x},
            }
        return map_


class LL_Event(_LL_Base):

    def __init__(self, channel,  callback, connection_callback, initial_hl2ll):
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback,connection_callback,initial_hl2ll)

    def _get_LLPROP_2_PVSP(self):
        map_ = {
            'delay'      : self.prefix + 'Delay-SP',
            'mode'       : self.prefix + 'Mode-Sel',
            'delay_type' : self.prefix + 'DelayType-Sel',
            }
        return map_

    def _get_LLPROP_2_PVRB(self):
        map_ = {
            'delay'      : self.prefix + 'Delay-RB',
            'mode'       : self.prefix + 'Mode-Sts',
            'delay_type' : self.prefix + 'DelayType-Sts',
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
            'delay'      : lambda x,ty=None: {'delay':x},
            'mode'       : lambda x,ty=None: {'mode':x},
            'delay_type' : lambda x,ty=None: {'delay_type':x},
            }
        return map_


class _LL_TrigEVRMF(_LL_Base):
    _NUM_OPT   = 12
    _NUM_INT   = 24
    _INTTMP    = 'IntTrig{0:02d}'
    _OUTTMP    = 'MFO{0:d}'
    _REMOVE_PROPS = {}

    def __init__(self, channel, conn_num,  callback, connection_callback, initial_hl2ll):
        self._internal_trigger = self._get_num_int(conn_num)
        self._OUTLB = self._OUTTMP.format(conn_num)
        self._INTLB = self._INTTMP.format(self._internal_trigger)
        self.prefix = LL_PREFIX + _PVName(channel).dev_name + ':'
        self.channel = channel
        super().__init__(callback,connection_callback,initial_hl2ll)

    def _get_num_int(self,num):
        return self._NUM_OPT + num

    def _get_LLPROP_2_PVSP(self):
        map_ = {
            'int_trig'   : self.prefix + self._OUTLB + 'IntChan-Sel',
            'event'      : self.prefix + self._INTLB + 'Event-Sel',
            'delay1'     : self.prefix + self._INTLB + 'Delay-SP',
            'delay2'     : self.prefix + self._OUTLB + 'Delay-SP',
            'delay3'     : self.prefix + self._OUTLB + 'FineDelay-SP',
            'pulses'     : self.prefix + self._INTLB + 'Pulses-SP',
            'width'      : self.prefix + self._INTLB + 'Width-SP',
            'state'      : self.prefix + self._INTLB + 'State-Sel',
            'polarity'   : self.prefix + self._INTLB + 'Polrty-Sel',
            }
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_LLPROP_2_PVRB(self):
        map_ = {
            'int_trig'   : self.prefix + self._OUTLB + 'IntChan-Sts',
            'event'      : self.prefix + self._INTLB + 'Event-Sts',
            'delay1'     : self.prefix + self._INTLB + 'Delay-RB',
            'delay2'     : self.prefix + self._OUTLB + 'Delay-RB',
            'delay3'     : self.prefix + self._OUTLB + 'FineDelay-RB',
            'pulses'     : self.prefix + self._INTLB + 'Pulses-RB',
            'width'      : self.prefix + self._INTLB + 'Width-RB',
            'state'      : self.prefix + self._INTLB + 'State-Sts',
            'polarity'   : self.prefix + self._INTLB + 'Polrty-Sts',
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
            'int_trig'   : self._get_int_channel,
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

    def _get_delay(self, value, ty = None):
        pvs = self._pvs_sp if ty else self._pvs_rb
        delay  =  pvs['delay1'].get(timeout=_TIMEOUT) or 0.0
        delay +=  pvs['delay2'].get(timeout=_TIMEOUT) or 0.0
        delay += (pvs['delay3'].get(timeout=_TIMEOUT)  or 0.0)*1e-6  # picoseconds
        return {'delay':delay}

    def _set_delay(self,value):
        _log.debug(self.channel+' Setting propty = {0:s}, value = {1:s}.'.format('delay',str(value)))
        delay1  = (value // D1_STEP) * D1_STEP
        value  -= delay1
        delay2  = (value // D2_STEP) * D2_STEP
        value  -= delay2
        delay3  = (value // D3_STEP) * D3_STEP * 1e3 # in nanoseconds

        self._hl2ll['delay'] = delay1 + delay2 + delay3/1e3
        pv1 = self._pvs_sp['delay1']
        pv2 = self._pvs_sp['delay2']
        pv3 = self._pvs_sp['delay3']
        if not pv1.connected: _log.debug(self.channel+' PV '+pv1.pvname+' NOT connected.')
        if not pv2.connected: _log.debug(self.channel+' PV '+pv2.pvname+' NOT connected.')
        if not pv3.connected: _log.debug(self.channel+' PV '+pv3.pvname+' NOT connected.')

        if pv1.connected and pv2.connected and pv3.connected:
            _log.debug(self.channel+' Delay1 = {}, Delay2 = {}, Delay3 = {}.'.format(
                                        str(delay1),str(delay2),str(delay3)))
            self._put_on_pv(pv1, delay1)
            self._put_on_pv(pv2, delay2)
            self._put_on_pv(pv3, delay3)

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
        _log.debug(self.channel+' Setting propty = {0:s}, value = {1:s}.'.format(prop,str(value)))
        self._hl2ll[prop] = value
        int_trig = self._pvs_sp.get('int_trig')
        if int_trig is None:
            _log.debug(self.channel+' Internal Channel NOT Existent.')
            return
        if not int_trig.connected:
            _log.debug(self.channel+' PV '+int_trig.pvname+' NOT connected.')
            return
        if not self._hl2ll['work_as']:
             val = self._internal_trigger
        else:
            clock_num = self._hl2ll['clock']
            val = self._NUM_INT + clock_num
        self._put_on_pv(int_trig, val)


class _LL_TrigEVROPT(_LL_TrigEVRMF):
    _NUM_OPT   = 12
    _NUM_INT   = 24
    _INTTMP    = 'IntTrig{0:02d}'
    _REMOVE_PROPS = {'delay2','delay3','int_trig'}

    def _get_num_int(self,num):
        return num

    def _get_LLPROP_FUNS(self):
        map_ = super()._get_LLPROP_FUNS()
        map_['delay1'] = lambda x,ty=None: {'delay':x}
        return map_

    def _set_delay(self,value):
        _log.debug(self.channel+' Setting propty = {0:s}, value = {1:s}.'.format('delay',str(value)))
        pv = self._pvs_sp['delay1']
        if not pv.connected:
            _log.debug(self.channel+' PV '+pv.pvname+' NOT connected.')
            return
        delay1  = (value // D1_STEP) * D1_STEP
        _log.debug(self.channel+' Delay1 = {}.'.format(str(delay1)))
        self._hl2ll['delay'] = delay1
        self._put_on_pv(pv, delay1)


class _LL_TrigEVELVE(_LL_TrigEVRMF):
    _NUM_OPT   = 0
    _NUM_INT   = 16
    _INTTMP    = 'IntTrig{0:02d}'
    _OUTTMP    = 'LVEO{0:d}'


class _LL_TrigAFCLVE(_LL_TrigEVRMF):
    _NUM_OPT   = 0
    _NUM_INT   = 256
    _INTTMP    = 'LVEIO{0:d}'
    _REMOVE_PROPS = {'delay2','delay3','int_trig'}

    def _get_LLPROP_2_PVSP(self):
        map_ = super()._get_LLPROP_2_PVSP()
        map_['event'] = self.prefix + self._INTLB + 'Event-Sel'#'EVGParam-SP'
        return map_

    def _get_LLPROP_2_PVRB(self):
        map_ = super()._get_LLPROP_2_PVRB()
        map_['event'] = self.prefix + self._INTLB + 'Event-Sts'#'EVGParam-RB'
        return map_

    def _get_HLPROP_FUNS(self):
        map_ = super()._get_HLPROP_FUNS()
        map_['work_as'] = lambda x: self._set_channel_to_listen('work_as',x)
        map_['event']   = lambda x: self._set_channel_to_listen('event',x)
        map_['clock']   = lambda x: self._set_channel_to_listen('clock',x)
        return map_

    def _get_LLPROP_FUNS(self):
        map_ = super()._get_LLPROP_FUNS()
        map_['event']  = self._get_channel_to_listen
        map_['delay1'] = lambda x,ty=None: {'delay':x}
        return map_

    def _set_delay(self,value):
        _log.debug(self.channel+' Setting propty = {0:s}, value = {1:s}.'.format('delay',str(value)))
        pv = self._pvs_sp['delay1']
        if not pv.connected:
            if not pv1.connected: _log.debug(self.channel+' PV '+pv.pvname+' NOT connected.')
            return
        delay1  = (value // D1_STEP) * D1_STEP
        _log.debug(self.channel+' Delay1 = {}.'.format(str(delay1)))
        self._hl2ll['delay'] = delay1
        self._put_on_pv(pv, delay1)

    def _get_channel_to_listen(self, value, ty = None):
        if value is None: return
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
        _log.debug(self.channel+' Setting propty = {0:s}, value = {1:s}.'.format(prop,str(value)))
        pv = self._pvs_sp['event']
        if not pv.connected:
            _log.debug(self.channel+' PV '+pv.pvname+' NOT connected.')
            return
        self._hl2ll[prop] = value
        if not self._hl2ll['work_as']:
            val = self._hl2ll['event']
        else:
            clock_num = self._hl2ll['clock']
            val = self._NUM_INT + clock_num
        self._put_on_pv(pv, val)


class _LL_TrigAFCOPT(_LL_TrigAFCLVE):
    _INTTMP = 'OPTO{0:02d}'
