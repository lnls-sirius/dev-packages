"""Define the low level classes which will connect to Timing Devices IOC."""

import logging as _log
import epics as _epics
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.timesys.time_data import IOs
from siriuspy.timesys.time_data import Clocks, Events
from threading import Event as _Event
from threading import Thread as _Thread

_TIMEOUT = 0.05
_FORCE_EQUAL = False
_INTERVAL = 0.1

LL_PREFIX = 'VAF-'

RFFREQ = 299792458/518.396*864  # Should be read from the RF generator Setpoint
RF_PER = 1/RFFREQ * 1e6         # In micro seconds
D1_STEP = RF_PER * 4
D2_STEP = RF_PER * 4 / 20
D3_STEP = 5e-6                  # five picoseconds


class _Timer(_Thread):
    def __init__(self, interval, function, args=tuple()):
        super().__init__(daemon=True)
        self.interval = interval
        self.function = function
        self.args = args
        self.stopped = _Event()

    def run(self):
        while not self.stopped.wait(self.interval):
            self.function(*self.args)

    def stop(self):
        self.stopped.set()


def get_ll_trigger_object(channel, callback, initial_hl2ll):
    """Get Low Level trigger objects."""
    LL_TRIGGER_CLASSES = {
        ('EVR', 'OUT'): _LL_TrigEVROUT,
        ('EVR', 'OTP'): _LL_TrigEVROTP,
        ('EVE', 'OUT'): _LL_TrigEVEOUT,
        ('AFC', 'OUT'): _LL_TrigAFCOUT,
        ('AFC', 'FMC'): _LL_TrigAFCFMC,
        }
    chan = _PVName(channel)
    conn_ty, conn_conf, conn_num = IOs.LL_RGX.findall(chan.propty)[0]
    key = (chan.dev_type, conn_ty)
    cls_ = LL_TRIGGER_CLASSES.get(key)
    if not cls_:
        raise Exception('Low Level Trigger Class not defined for device ' +
                        'type '+key[0]+' and connection type '+key[1]+'.')
    return cls_(channel, int(conn_num), callback, initial_hl2ll)


class _LL_Base:
    def __init__(self, callback, initial_hl2ll):
        self._HLPROP_FUNS = self._get_HLPROP_FUNS()
        self._LLPROP_FUNS = self._get_LLPROP_FUNS()
        self._LLPROP_2_PVRB = self._get_LLPROP_2_PVRB()
        self._PVRB_2_LLPROP = {val: key
                               for key, val in self._LLPROP_2_PVRB.items()}
        self.callback = callback
        self._hl_props = initial_hl2ll
        self._pvs_sp = dict()
        self._pvs_rb = dict()
        self._pvs_sp_canput = dict()
        _log.info(self.channel+': Starting.')
        _log.info(self.channel+': Creating PVs.')
        for prop, pv_name in self._LLPROP_2_PVRB.items():
            _log.debug(self.channel + ' -> creating {0:s}'.format(pv_name))
            self._pvs_rb[prop] = _epics.PV(
                pv_name,
                callback=self._pvs_rb_callback,
                connection_timeout=_TIMEOUT)
            # Now the setpoints
            _log.debug(self.channel + ' -> creating {0:s}'.format(pv_name))
            self._pvs_sp_canput[pv_name] = True
            self._pvs_sp[prop] = _epics.PV(
                self._get_setpoint_name(pv_name),
                connection_timeout=_TIMEOUT)
        _log.info(self.channel + ': Done.')
        if _FORCE_EQUAL:
            self.timer = _Timer(_INTERVAL, self._force_equal)
            self.timer.start()

    def _get_setpoint_name(self, pvname):
        pvname = pvname.replace('-RB', '-SP')
        return pvname.replace('-Sts', '-Sel')

    def _get_LLPROP_2_PVRB(self):
        map_ = dict()
        return map_

    def _get_HLPROP_FUNS(self):
        map_ = dict()
        return map_

    def _get_LLPROP_FUNS(self):
        map_ = dict()
        return map_

    def _force_equal(self):
        for ll_prop, pv in self._pvs_sp.items():
            if not pv.connected or not self._pvs_sp_canput[pv.pvname]:
                continue
            v = pv.get(timeout=_TIMEOUT)
            if v is None:
                _log.debug(self.channel +
                           ' propty = {0:s} is None '.format(ll_prop))
                continue
            my_val = self._ll_props[ll_prop]
            if my_val == v:
                continue
            self._put_on_pv(pv, my_val)

    def _pvs_rb_callback(self, pvname, value, **kwargs):
        if value is None:
            _log.debug(self.channel+' pvs_rb_callback; {0:s} received None'
                       .format(pvname))
            return
        _log.debug(self.channel+' pvs_rb_callback; ' +
                   'PV = {0:s} New Value = {1:s} '.format(pvname, str(value)))
        props = self._LLPROP_FUNS[self._PVRB_2_LLPROP[pvname]](value)
        for hl_prop, val in props.items():
            _log.debug(
                self.channel+' pvs_rb_callback; Sending to HL; ' +
                'propty = {0:s} Value = {1:s} '.format(hl_prop, str(val)))
            self.callback(self.channel, hl_prop, val)

    def _put_complete(self, pvname, **kwargs):
        self._pvs_sp_canput[pvname] = True

    def _put_on_pv(self, pv, value):
        if not pv.connected:
            _log.debug(self.channel + ' PV ' +
                       pv.pvname + ' NOT connected.')
            return
        self._pvs_sp_canput[pv.pvname] = False
        pv.put(value, callback=self._put_complete)

    def _set_simple(self, prop, value):
        pv = self._pvs_sp[prop]
        self._hl_props[prop] = value
        self._ll_props[prop] = value
        _log.debug(self.channel + ' Setting PV ' + pv.pvname +
                   ', value = {0:s}.'.format(str(value)))
        self._put_on_pv(pv, value)

    def set_propty(self, prop, value):
        _log.debug(self.channel+' set_propty receive propty = ' +
                   '{0:s}; Value = {1:s}'.format(prop, str(value)))
        fun = self._HLPROP_FUNS.get(prop)
        if fun is None:
            return False
        _Thread(target=fun, args=(value,), daemon=True).start()
        return True


class LL_Clock(_LL_Base):
    """Define the Low Level Clock Class."""

    def __init__(self, channel,  callback, initial_hl2ll):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, initial_hl2ll)

    def _get_LLPROP_2_PVRB(self):
        map_ = {
            'frequency': self.prefix + 'Freq-RB',
            'state': self.prefix + 'State-Sts',
            }
        return map_

    def _get_HLPROP_FUNS(self):
        map_ = {
            'frequency': lambda x: self._set_simple('frequency', x),
            'state': lambda x: self._set_simple('state', x),
            }
        return map_

    def _get_LLPROP_FUNS(self):
        map_ = {
            'frequency': lambda x: {'frequency': x},
            'state': lambda x: {'state': x},
            }
        return map_


class LL_Event(_LL_Base):
    """Define the Low Level Event Class."""

    def __init__(self, channel, callback, initial_hl2ll):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, initial_hl2ll)

    def _get_LLPROP_2_PVRB(self):
        map_ = {
            'delay': self.prefix + 'Delay-RB',
            'mode': self.prefix + 'Mode-Sts',
            'delay_type': self.prefix + 'DelayType-Sts',
            }
        return map_

    def _get_HLPROP_FUNS(self):
        map_ = {
            'delay': lambda x: self._set_simple('delay', x),
            'mode': lambda x: self._set_simple('mode', x),
            'delay_type': lambda x: self._set_simple('delay_type', x),
            }
        return map_

    def _get_LLPROP_FUNS(self):
        map_ = {
            'delay': lambda x: {'delay': x},
            'mode': lambda x: {'mode': x},
            'delay_type': lambda x: {'delay_type': x},
            }
        return map_


class _LL_TrigEVROUT(_LL_Base):
    _NUM_OPT = 12
    _NUM_INT = 24
    _INTTMP = 'IntTrig{0:02d}'
    _OUTTMP = 'OUT{0:d}'
    _REMOVE_PROPS = {}

    def __init__(self, channel, conn_num, callback, initial_hl2ll, evg_params):
        self._internal_trigger = self._get_num_int(conn_num)
        self._OUTLB = self._OUTTMP.format(conn_num)
        self._INTLB = self._INTTMP.format(self._internal_trigger)
        self.prefix = LL_PREFIX + _PVName(channel).dev_name + ':'
        self.channel = channel
        self._EVGParam_ENUMS = evg_params
        super().__init__(callback, initial_hl2ll)

    def _get_num_int(self, num):
        return self._NUM_OPT + num

    def _get_LLPROP_2_PVRB(self):
        map_ = {
            'int_trig': self.prefix + self._OUTLB + 'IntChan-Sts',
            'event': self.prefix + self._INTLB + 'Event-Sts',
            'delay1': self.prefix + self._INTLB + 'Delay-RB',
            'delay2': self.prefix + self._OUTLB + 'Delay-RB',
            'delay3': self.prefix + self._OUTLB + 'FineDelay-RB',
            'pulses': self.prefix + self._INTLB + 'Pulses-RB',
            'width': self.prefix + self._INTLB + 'Width-RB',
            'state': self.prefix + self._INTLB + 'State-Sts',
            'polarity': self.prefix + self._INTLB + 'Polrty-Sts',
            }
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_HLPROP_FUNS(self):
        map_ = {
            'evg_param': lambda x: self._set_evg_param,
            'delay': self._set_delay,
            'pulses': lambda x: self._set_simple('pulses', x),
            'duration': lambda x: self._set_duration,
            'state': lambda x: self._set_simple('state', x),
            'polarity': lambda x: self._set_simple('polarity', x),
            }
        return map_

    def _get_LLPROP_FUNS(self):
        map_ = {
            'int_trig': self._get_int_channel,
            'event': lambda x: {'event': x},
            'delay1': self._get_delay,
            'delay2': self._get_delay,
            'delay3': self._get_delay,
            'pulses': lambda x: {'pulses': x},
            'width': lambda x: {'width': x},
            'state': lambda x: {'state': x},
            'polarity': lambda x: {'polarity': x},
            }
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_delay(self, value, ty=None):
        pvs = self._pvs_rb
        delay = pvs['delay1'].get(timeout=_TIMEOUT) or 0.0
        delay += pvs['delay2'].get(timeout=_TIMEOUT) or 0.0
        delay += (pvs['delay3'].get(timeout=_TIMEOUT) or 0.0)*1e-6  # psec
        return {'delay': delay}

    def _set_delay(self, value):
        _log.debug(self.channel+' Setting propty = {0:s}, value = {1:s}.'
                   .format('delay', str(value)))
        delay1 = (value // D1_STEP) * D1_STEP
        value -= delay1
        delay2 = (value // D2_STEP) * D2_STEP
        value -= delay2
        delay3 = (value // D3_STEP) * D3_STEP * 1e3  # in nanoseconds

        self._hl2ll['delay'] = delay1 + delay2 + delay3/1e3
        pv1 = self._pvs_sp['delay1']
        pv2 = self._pvs_sp['delay2']
        pv3 = self._pvs_sp['delay3']
        if pv1.connected and pv2.connected and pv3.connected:
            _log.debug(self.channel+' Delay1 = {}, Delay2 = {}, Delay3 = {}.'
                       .format(str(delay1), str(delay2), str(delay3)))
            self._put_on_pv(pv1, delay1)
            self._put_on_pv(pv2, delay2)
            self._put_on_pv(pv3, delay3)

    def _get_int_channel(self, value, ty=None):
        props = dict()
        if value < self._NUM_INT:
            props['work_as'] = 0
        else:
            props['work_as'] = 1
            props['clock'] = value - self._NUM_INT
        return props

    def _set_evg_param(self, value):
        _log.debug(self.channel+' Setting evg_param, value = {0:s}.'
                   .format(str(value)))
        self._hl_props['evg_param'] = value
        pname = self._EVGParam_ENUMS[value]
        if pname.startswith('Clock'):
            int_trig = self._pvs_sp['int_trig']
            self._ll_props['int_trig'] = Clocks.HL2LL_MAP[pname]
            self._put_on_pv(int_trig, self._ll_props['int_trig'])
        else:
            ev = Events.HL2LL_MAP[pname]
            self._ll_props['event'] = ev
            event_pv = self._pvs_sp['event']
            self._put_on_pv(event_pv, ev)
            val = self._internal_trigger
            self._ll_props['int_trig'] = val
            int_trig = self._pvs_sp.get('int_trig')
            if int_trig is not None:
                self._put_on_pv(int_trig, val)

    def _set_duration(self, value):
        self._hl_props['duration'] = value
        self._ll_props['width'] = value*1e3/self._hl2ll['pulses']
        self.put_on_pv(self._pvs_sp['width'], self._ll_props['width'])


class _LL_TrigEVROTP(_LL_TrigEVROUT):
    _NUM_OPT = 12
    _NUM_INT = 24
    _INTTMP = 'IntTrig{0:02d}'
    _REMOVE_PROPS = {'delay2', 'delay3', 'int_trig'}

    def _get_num_int(self, num):
        return num

    def _get_LLPROP_FUNS(self):
        map_ = super()._get_LLPROP_FUNS()
        map_['delay1'] = lambda x, ty=None: {'delay': x}
        return map_

    def _set_delay(self, value):
        _log.debug(self.channel+' Setting propty = {0:s}, value = {1:s}.'
                   .format('delay', str(value)))
        pv = self._pvs_sp['delay1']
        if not pv.connected:
            _log.debug(self.channel+' PV '+pv.pvname+' NOT connected.')
            return
        delay1 = (value // D1_STEP) * D1_STEP
        _log.debug(self.channel+' Delay1 = {}.'.format(str(delay1)))
        self._hl2ll['delay'] = delay1
        self._put_on_pv(pv, delay1)


class _LL_TrigEVEOUT(_LL_TrigEVROUT):
    _NUM_OPT = 0
    _NUM_INT = 16
    _INTTMP = 'IntTrig{0:02d}'
    _OUTTMP = 'LVEO{0:d}'


class _LL_TrigAFCOUT(_LL_TrigEVROUT):
    _NUM_OPT = 0
    _NUM_INT = 256
    _INTTMP = 'LVEIO{0:d}'
    _REMOVE_PROPS = {'delay2', 'delay3', 'int_trig'}

    def _get_LLPROP_2_PVRB(self):
        map_ = super()._get_LLPROP_2_PVRB()
        # 'EVGParam-RB'
        map_['event'] = self.prefix + self._INTLB + 'Event-Sts'
        return map_

    def _get_HLPROP_FUNS(self):
        map_ = super()._get_HLPROP_FUNS()
        map_['work_as'] = lambda x: self._set_channel_to_listen('work_as', x)
        map_['event'] = lambda x: self._set_channel_to_listen('event', x)
        map_['clock'] = lambda x: self._set_channel_to_listen('clock', x)
        return map_

    def _get_LLPROP_FUNS(self):
        map_ = super()._get_LLPROP_FUNS()
        map_['event'] = self._get_channel_to_listen
        map_['delay1'] = lambda x, ty=None: {'delay': x}
        return map_

    def _set_delay(self, value):
        _log.debug(self.channel+' Setting propty = {0:s}, value = {1:s}.'
                   .format('delay', str(value)))
        pv = self._pvs_sp['delay1']
        if not pv.connected:
            _log.debug(self.channel+' PV '+pv.pvname+' NOT connected.')
            return
        delay1 = (value // D1_STEP) * D1_STEP
        _log.debug(self.channel+' Delay1 = {}.'.format(str(delay1)))
        self._hl2ll['delay'] = delay1
        self._put_on_pv(pv, delay1)

    def _get_channel_to_listen(self, value, ty=None):
        if value is None:
            return
        props = dict()
        if value < self._NUM_INT:
            props['work_as'] = 0
            props['event'] = value
        else:
            props['work_as'] = 1
            props['clock'] = value - self._NUM_INT
        return props

    def _set_channel_to_listen(self, prop, value):
        _log.debug(self.channel+' Setting propty = {0:s}, value = {1:s}.'
                   .format(prop, str(value)))
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


class _LL_TrigAFCFMC(_LL_TrigAFCOUT):
    _INTTMP = 'OPTO{0:02d}'
