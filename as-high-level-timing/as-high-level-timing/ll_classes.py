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


def get_ll_trigger_object(channel, callback, init_hl_props, evg_params):
    """Get Low Level trigger objects."""
    LL_TRIGGER_CLASSES = {
        ('EVR', 'OUT'): _LL_TrigEVROUT,
        ('EVR', 'OTP'): _LL_TrigEVROTP,
        ('EVE', 'OUT'): _LL_TrigEVEOUT,
        ('AFC', 'OUT'): _LL_TrigAFCOUT,
        ('AFC', 'FMC'): _LL_TrigAFCFMC,
        }
    chan = _PVName(channel)
    conn_ty, conn_num = IOs.LL_RGX.findall(chan.propty)[0]
    key = (chan.dev_type, conn_ty)
    cls_ = LL_TRIGGER_CLASSES.get(key)
    if not cls_:
        raise Exception('Low Level Trigger Class not defined for device ' +
                        'type '+key[0]+' and connection type '+key[1]+'.')
    return cls_(channel, int(conn_num), callback, init_hl_props, evg_params)


class _LL_Base:
    def __init__(self, callback, init_hl_props):
        """Initialize the Low Level object.

        callback is the callable to be called each time a low level PV changes
        its value.
        init_hl_props is the initial value of the high level properties.
        """
        self._HLPROP_FUNS = self._get_HLPROP_FUNS()
        self._LLPROP_FUNS = self._get_LLPROP_FUNS()
        self._LLPROP_2_PVRB = self._get_LLPROP_2_PVRB()
        self._PVRB_2_LLPROP = {val: key
                               for key, val in self._LLPROP_2_PVRB.items()}
        self.callback = callback
        self._hl_props = init_hl_props
        self._pvs_sp = dict()
        self._pvs_rb = dict()
        self._pvs_sp_canput = dict()
        _log.info(self.channel+': Starting.')
        _log.info(self.channel+': Creating PVs.')
        for prop, pv_name in self._LLPROP_2_PVRB.items():
            _log.debug(self.channel + ' -> creating {0:s}'.format(pv_name))
            self._pvs_rb[prop] = _epics.PV(
                pv_name,
                callback=self._on_change_pvs_rb,
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
        """Convert readback PV names to setpoint PV names."""
        return pvname.replace('-RB', '-SP').replace('-Sts', '-Sel')

    def _get_LLPROP_2_PVRB(self):
        """Define a dictionary for convertion of names.

        The dictionary converts low level properties names to low level PV
        names.
        """
        return dict()

    def _get_HLPROP_FUNS(self):
        """Define a dictionary of functions to convert HL to LL.

        Each function converts the values of High level properties into values
        of Low Level properties. The functions defined in this dictionary are
        called by set_propty and they send to the Low Level IOC the converted
        values.
        """
        return dict()

    def _get_LLPROP_FUNS(self):
        """Define a dictionary of functions to convert LL to HL.

        Each function converts the readback values of Low Level properties into
        values of High Level properties and send them to the High Level classes
        for update of the readback PVs.
        It is called by the on_change_pvs_rb and calls the callback function.
        """
        return dict()

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

    def _on_change_pvs_rb(self, pvname, value, **kwargs):
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
        """Simple setting of Low Level IOC PVs.

        Function called by set_propty when no convertion is needed between
        high and low level properties.
        """
        pv = self._pvs_sp[prop]
        self._hl_props[prop] = value
        self._ll_props[prop] = value
        _log.debug(self.channel + ' Setting PV ' + pv.pvname +
                   ', value = {0:s}.'.format(str(value)))
        self._put_on_pv(pv, value)

    def set_propty(self, prop, value):
        """Set property values in low level IOCS.

        Function called by classes that control high level PVs to transform
        the high level values into low level properties and set the low level
        IOCs accordingly.
        """
        _log.debug(self.channel+' set_propty receive propty = ' +
                   '{0:s}; Value = {1:s}'.format(prop, str(value)))
        fun = self._HLPROP_FUNS.get(prop)
        if fun is None:
            return False
        _Thread(target=fun, args=(value,), daemon=True).start()
        return True


class LL_Clock(_LL_Base):
    """Define the Low Level Clock Class."""

    def __init__(self, channel,  callback, init_hl_props):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_hl_props)

    def _get_LLPROP_2_PVRB(self):
        return {
            'frequency': self.prefix + 'Freq-RB',
            'state': self.prefix + 'State-Sts',
            }

    def _get_HLPROP_FUNS(self):
        return {
            'frequency': lambda x: self._set_simple('frequency', x),
            'state': lambda x: self._set_simple('state', x),
            }

    def _get_LLPROP_FUNS(self):
        return {
            'frequency': lambda x: {'frequency': x},
            'state': lambda x: {'state': x},
            }


class LL_Event(_LL_Base):
    """Define the Low Level Event Class."""

    def __init__(self, channel, callback, init_hl_props):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_hl_props)

    def _get_LLPROP_2_PVRB(self):
        return {
            'delay': self.prefix + 'Delay-RB',
            'mode': self.prefix + 'Mode-Sts',
            'delay_type': self.prefix + 'DelayType-Sts',
            'ext_trig': self.prefix + 'ExtTrig-Cmd',
            }

    def _get_HLPROP_FUNS(self):
        return {
            'delay': lambda x: self._set_simple('delay', x),
            'mode': lambda x: self._set_simple('mode', x),
            'delay_type': lambda x: self._set_simple('delay_type', x),
            'ext_trig': lambda x: self._set_simple('ext_trig', x),
            }

    def _get_LLPROP_FUNS(self):
        return {
            'delay': lambda x: {'delay': x},
            'mode': lambda x: {'mode': x},
            'delay_type': lambda x: {'delay_type': x},
            'ext_trig': lambda x: {'ext_trig': x},
            }


class _LL_TrigEVROUT(_LL_Base):
    _NUM_OPT = 12
    _INTTMP = 'IntTrig{0:02d}'
    _OUTTMP = 'OUT{0:d}'
    _REMOVE_PROPS = {}

    def __init__(self, channel, conn_num, callback,
                 init_hl_props, evg_params):
        self._internal_trigger = self._get_num_int(conn_num)
        self._OUTLB = self._OUTTMP.format(conn_num)
        self._INTLB = self._INTTMP.format(self._internal_trigger)
        self.prefix = LL_PREFIX + _PVName(channel).dev_name + ':'
        self.channel = channel
        self._EVGParam_ENUMS = evg_params
        super().__init__(callback, init_hl_props)

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
            'evg_param': self._set_evg_param,
            'delay': self._set_delay,
            'pulses': lambda x: self._set_simple('pulses', x),
            'duration': self._set_duration,
            'state': lambda x: self._set_simple('state', x),
            'polarity': lambda x: self._set_simple('polarity', x),
            }
        return map_

    def _get_LLPROP_FUNS(self):
        map_ = {
            'int_trig': self._process_int_trig,
            'event': self._process_event,
            'delay1': self._get_delay,
            'delay2': self._get_delay,
            'delay3': self._get_delay,
            'pulses': lambda x: {'pulses': x},
            'width': self._get_duration,
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

        self._hl_props['delay'] = delay1 + delay2 + delay3/1e3
        pv1 = self._pvs_sp['delay1']
        pv2 = self._pvs_sp['delay2']
        pv3 = self._pvs_sp['delay3']
        if pv1.connected and pv2.connected and pv3.connected:
            _log.debug(self.channel+' Delay1 = {}, Delay2 = {}, Delay3 = {}.'
                       .format(str(delay1), str(delay2), str(delay3)))
            self._put_on_pv(pv1, delay1)
            self._put_on_pv(pv2, delay2)
            self._put_on_pv(pv3, delay3)

    def _process_int_trig(self, value):
        if value == self._INTLB:
            return {'evg_param': self.pvs_rb['event'].get(timeout=_TIMEOUT)}
        elif value.startswith('Clock'):
            return {'evg_param': Clocks.LL2HL_MAP[value]}
        else:
            _log.warning(self.prefix + ' Low Level Event set is not allowed.')
            return dict()

    def _process_event(self, x):
        if self._hl_props['evg_param'].startswith('Clock'):
            return dict()
        _log.debug(self.prefix + ' ll_event = ' + str(x))
        if x not in Events.LL2HL_MAP.keys():
            _log.warning(self.prefix + 'Low Level event not in ' +
                         'High Level list os possible events.')
        pname = Events.LL2HL_MAP[x]
        _log.debug(self.prefix + ' hl_event = ' + pname)
        if pname not in self._EVGParam_ENUMS:
            _log.warning(self.prefix + 'High Level event not in allowed' +
                         ' list os possible events for this trigger.')
            return dict()
        return {'evg_param': self._EVGParam_ENUMS.index(pname)}

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
            int_trig = self._pvs_sp.get('int_trig')
            if int_trig is not None:
                self._ll_props['int_trig'] = self._INTLB
                self._put_on_pv(int_trig, self._INTLB)

    def _get_duration(self, width):
        return {'duration': width / 1e3 * self._hl_props['pulses']}

    def _set_duration(self, value):
        self._hl_props['duration'] = value
        self._ll_props['width'] = value*1e3/self._hl_props['pulses']
        self.put_on_pv(self._pvs_sp['width'], self._ll_props['width'])


class _LL_TrigEVROTP(_LL_TrigEVROUT):
    _NUM_OPT = 12
    _INTTMP = 'IntTrig{0:02d}'
    _REMOVE_PROPS = {'delay2', 'delay3', 'int_trig'}

    def _get_num_int(self, num):
        return num

    def _get_LLPROP_FUNS(self):
        map_ = super()._get_LLPROP_FUNS()
        map_['delay1'] = lambda x: {'delay': x}
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
        self._hl_props['delay'] = delay1
        self._put_on_pv(pv, delay1)


class _LL_TrigEVEOUT(_LL_TrigEVROUT):
    _NUM_OPT = 0
    _INTTMP = 'IntTrig{0:02d}'
    _OUTTMP = 'OUT{0:d}'


class _LL_TrigAFCOUT(_LL_TrigEVROUT):
    _NUM_OPT = 0
    _INTTMP = 'OUT{0:d}'
    _REMOVE_PROPS = {'delay2', 'delay3', 'int_trig'}

    def _get_LLPROP_2_PVRB(self):
        map_ = super()._get_LLPROP_2_PVRB()
        map_['event'] = self.prefix + self._INTLB + 'EVGParam-Sts'
        return map_

    def _get_HLPROP_FUNS(self):
        map_ = super()._get_HLPROP_FUNS()
        map_['event'] = self._set_evg_param
        map_['delay'] = self._set_delay
        return map_

    def _get_LLPROP_FUNS(self):
        map_ = super()._get_LLPROP_FUNS()
        map_['event'] = self._process_event
        map_['delay1'] = lambda x: {'delay': x}
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
        self._hl_props['delay'] = delay1
        self._ll_props['delay1'] = delay1
        self._put_on_pv(pv, delay1)

    def _process_event(self, evg_par_str):
        if evg_par_str.startswith('Clock'):
            val = Clocks.LL2HL_MAP[evg_par_str]
        else:
            if evg_par_str not in Events.LL2HL_MAP.keys():
                _log.warning(self.prefix + 'Low Level event not in ' +
                             'High Level list os possible events.')
                return
            val = Events.LL2HL_MAP[evg_par_str]
        if val not in self._EVGParam_ENUMS:
            _log.warning(self.prefix + 'EVG param ' + val +
                         ' Not allowed for this trigger.')
            return
        return {'evg_param': self._EVGParam_ENUMS.index(val)}

    def _set_evg_param(self, value):
        _log.debug(self.channel +
                   ' Setting evg_param, value = {0:s}.'.format(str(value)))
        self._hl_props['evg_param'] = value
        pname = self._EVGParam_ENUMS[value]
        if pname.startswith('Clock'):
            val = Clocks.HL2LL_MAP[pname]
        else:
            val = Events.HL2LL_MAP[pname]
        self._ll_props['event'] = val
        event_pv = self._pvs_sp['event']
        self._put_on_pv(event_pv, val)


class _LL_TrigAFCFMC(_LL_TrigAFCOUT):
    _INTTMP = 'FMC{0:d}'
