"""Define the low level classes which will connect to Timing Devices IOC."""

import logging as _log
from threading import Event as _Event
from threading import Thread as _Thread
import epics as _epics
from siriuspy.epics import connection_timeout as _conn_timeout
from siriuspy.envars import vaca_prefix as LL_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.timesys.time_data import IOs
from siriuspy.timesys.time_data import Clocks, Events
from siriuspy.timesys.time_data import RF_FREQUENCY as RFFREQ
from siriuspy.timesys.time_data import RF_DIVISION as RFDIV
from siriuspy.timesys.time_data import AC_FREQUENCY as ACFREQ
from siriuspy.timesys.time_data import FINE_DELAY as FDEL

_INTERVAL = 0.1


class _Timer(_Thread):
    def __init__(self, interval, function, args=tuple(), niter=100):
        super().__init__(daemon=True)
        self.interval = interval
        self.function = function
        self.args = args
        self.niters = niter
        self.cur_iter = 0
        self.stopped = _Event()

    def run(self):
        self.function(*self.args)
        while ((not self.stopped.wait(self.interval)) and
               self.niters > self.cur_iter):
            self.cur_iter += 1
            self.function(*self.args)

    def reset(self):
        self.cur_iter = 0

    def stop(self):
        self.stopped.set()


def get_ll_trigger_object(channel, callback, init_state, evg_params):
    """Get Low Level trigger objects."""
    LL_TRIGGER_CLASSES = {
        ('EVR', 'OUT'): _LL_TrigEVROUT,
        ('EVR', 'OTP'): _LL_TrigEVROTP,
        ('EVE', 'OUT'): _LL_TrigEVEOUT,
        ('AFC', 'CRT'): _LL_TrigAFCCRT,
        ('AFC', 'FMC'): _LL_TrigAFCFMC,
        }
    chan = _PVName(channel)
    conn_ty, conn_num = IOs.LL_RGX.findall(chan.propty)[0]
    key = (chan.dev, conn_ty)
    cls_ = LL_TRIGGER_CLASSES.get(key)
    if not cls_:
        raise Exception('Low Level Trigger Class not defined for device ' +
                        'type '+key[0]+' and connection type '+key[1]+'.')
    return cls_(channel, int(conn_num), callback, init_state, evg_params)


class _LL_Base:
    def __init__(self, callback, init_state):
        """Initialize the Low Level object.

        callback is the callable to be called each time a low level PV changes
        its value.
        init_state is the initial value of the high level properties.
        """
        self._dict_functions_for_write = self._get_dict_for_write()
        self._dict_functions_for_read = self._get_dict_for_read()
        self._dict_convert_prop2pvrb = self._get_convertion_prop2pvrb()
        self._dict_convert_pvrb2prop = {
                val: key for key, val in self._dict_convert_prop2pvrb.items()}
        self.callback = callback
        self._hl_state = init_state
        self._ll_state = dict()
        self._rf_freq = RFFREQ
        self._rf_div = RFDIV
        self._rf_freq_pv = _epics.PV(LL_PREFIX + 'SI-03SP:RF-SRFCav:Freq-SP',
                                     connection_timeout=_conn_timeout)
        self._rf_div_pv = _epics.PV(LL_PREFIX + 'AS-Glob:TI-EVG:RFDiv-SP',
                                    connection_timeout=_conn_timeout)
        self._set_base_freq()
        self._rf_freq_pv.add_callback(self._set_base_freq)
        self._rf_div_pv.add_callback(self._set_base_freq)
        self.timer = None
        self._initialize_ll_state()
        self._pvs_sp = dict()
        self._pvs_rb = dict()
        _log.info(self.channel+': Starting.')
        _log.info(self.channel+': Creating PVs.')
        for prop, pv_name in self._dict_convert_prop2pvrb.items():
            _log.debug(self.channel + ' -> creating {0:s}'.format(pv_name))
            self._pvs_rb[prop] = _epics.PV(
                pv_name,
                callback=self._on_change_pvs_rb,
                connection_timeout=_conn_timeout)
            # Now the setpoints
            pv_name_sp = pv_name.replace('-RB', '-SP').replace('-Sts', '-Sel')
            _log.debug(self.channel + ' -> creating {0:s}'.format(pv_name_sp))
            self._pvs_sp[prop] = _epics.PV(
                pv_name_sp,
                callback=self._on_change_pvs_sp,
                connection_timeout=_conn_timeout)
        # Timer to force equality between high and low level:
        _log.debug('Starting Timer.')
        self.timer = _Timer(_INTERVAL, self._force_equal)
        self.timer.start()
        self.start_timer()
        _log.info(self.channel + ': Done.')

    def start_timer(self):
        if self.timer is None:
            return
        _log.debug('Starting Timer.')
        if self.timer.isAlive():
            self.timer.reset()
        else:
            self.timer = _Timer(_INTERVAL, self._force_equal, niter=10)
            self.timer.start()

    def _set_base_freq(self, **kwargs):
        self._rf_freq = self._rf_freq_pv.get(
                                timeout=_conn_timeout) or self._rf_freq
        self._rf_div = self._rf_div_pv.get(
                                timeout=_conn_timeout) or self._rf_div
        self._base_freq = self._rf_freq / self._rf_div
        self._base_del = 1/self._base_freq
        self._rf_del = self._base_del / 20

    def _get_convertion_prop2pvrb(self):
        """Define a dictionary for convertion of names.

        The dictionary converts low level properties names to low level PV
        names.
        """
        return dict()

    def _get_dict_for_write(self):
        """Define a dictionary of functions to convert HL to LL.

        Each function converts the values of High level properties into values
        of Low Level properties. The functions defined in this dictionary are
        called by write and they send to the Low Level IOC the converted
        values.
        """
        return dict()

    def _get_dict_for_read(self):
        """Define a dictionary of functions to convert LL to HL.

        Each function converts the readback values of Low Level properties into
        values of High Level properties and send them to the High Level classes
        for update of the readback PVs.
        It is called by the on_change_pvs_rb and calls the callback function.
        """
        return dict()

    def _initialize_ll_state(self):
        for hl_prop, val in self._hl_state.items():
            self.write(hl_prop, val)

    def _force_equal(self):
        for ll_prop, pv in self._pvs_sp.items():
            if not pv.connected:
                _log.debug(self.prefix + 'll_prop = ' +
                           ll_prop + 'not connected.')
                continue
            if not pv.put_complete:
                continue
            v = pv.get(timeout=_conn_timeout)
            if v is None:
                _log.debug(self.channel +
                           ' propty = {0:s} is None '.format(ll_prop))
                continue
            my_val = self._ll_state.get(ll_prop)
            if my_val is None:
                raise Exception(self.prefix + ' ll_prop = ' +
                                ll_prop + ' not in dict.')
            if my_val == v:
                continue
            # If pv is a command, it must be sent only once
            if pv.pvname.endswith('-Cmd'):
                if self._ll_state[ll_prop]:
                    self._put_on_pv(pv, self._ll_state[ll_prop])
                    self._ll_state[ll_prop] = 0
                return
            self._put_on_pv(pv, my_val)

    def _put_on_pv(self, pv, value):
        _log.debug(self.channel + ' Setting PV ' + pv.pvname +
                   ', value = {0:s}.'.format(str(value)))
        pv.put(value, use_complete=True)

    def _on_change_pvs_sp(self, pvname, value, **kwargs):
        _log.debug('PV: '+pvname+'.  Calling Timer.')
        self.start_timer()

    def _on_change_pvs_rb(self, pvname, value, **kwargs):
        if value is None:
            _log.debug(self.channel+' pvs_rb_callback; {0:s} received None'
                       .format(pvname))
            return
        _log.debug(self.channel+' pvs_rb_callback; ' +
                   'PV = {0:s} New Value = {1:s} '.format(pvname, str(value)))
        fun = self._dict_functions_for_read[
                                self._dict_convert_pvrb2prop[pvname]]
        props = fun(value)
        for hl_prop, val in props.items():
            _log.debug(
                self.channel+' pvs_rb_callback; Sending to HL; ' +
                'propty = {0:s} Value = {1:s} '.format(hl_prop, str(val)))
            self.callback(self.channel, hl_prop, val)

    def _set_simple(self, prop, value):
        """Simple setting of Low Level IOC PVs.

        Function called by write when no convertion is needed between
        high and low level properties.
        """
        self._hl_state[prop] = value
        self._ll_state[prop] = value

    def write(self, prop, value):
        """Set property values in low level IOCS.

        Function called by classes that control high level PVs to transform
        the high level values into low level properties and set the low level
        IOCs accordingly.
        """
        _log.debug(self.channel+' receive propty = ' +
                   '{0:s}; Value = {1:s}'.format(prop, str(value)))
        fun = self._dict_functions_for_write.get(prop)
        if fun is None:
            return False
        fun(value)
        self.start_timer()
        return True


class LL_EVG(_LL_Base):
    """Define the Low Level EVG Class."""

    def __init__(self, channel,  callback, init_state):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_state)

    def _get_convertion_prop2pvrb(self):
        return {'ACDiv': self.prefix + 'ACDiv-RB'}

    def _get_dict_for_write(self):
        return {'RepRate': self._set_frequency}

    def _get_dict_for_read(self):
        return {'ACDiv': self._get_frequency}

    def _set_frequency(self, value):
        n = round(ACFREQ/value)
        self._hl_state['RepRate'] = ACFREQ / n
        self._ll_state['ACDiv'] = n

    def _get_frequency(self, value):
        return {'RepRate': ACFREQ / value}


class LL_Clock(_LL_Base):
    """Define the Low Level Clock Class."""

    def __init__(self, channel,  callback, init_state):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_state)

    def _get_convertion_prop2pvrb(self):
        return {
            'MuxDiv': self.prefix + 'MuxDiv-RB',
            'MuxEnbl': self.prefix + 'MuxEnbl-Sts',
            }

    def _get_dict_for_write(self):
        return {
            'Freq': self._set_frequency,
            'State': lambda x: self._set_simple('State', x),
            }

    def _get_dict_for_read(self):
        return {
            'MuxDiv': self._get_frequency,
            'MuxEnbl': lambda x: {'State': x},
            }

    def _set_frequency(self, value):
        value *= 1e3  # kHz
        n = round(self._base_freq/value)
        self._hl_state['Freq'] = self._base_freq / n * 1e-3
        self._ll_state['MuxDiv'] = n

    def _get_frequency(self, value):
        return {'Freq': self._base_freq / value * 1e-3}


class LL_Event(_LL_Base):
    """Define the Low Level Event Class."""

    def __init__(self, channel, callback, init_state):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_state)

    def _get_convertion_prop2pvrb(self):
        return {
            'Delay': self.prefix + 'Delay-RB',
            'Mode': self.prefix + 'Mode-Sts',
            'Delay_type': self.prefix + 'DelayType-Sts',
            'ext_trig': self.prefix + 'ExtTrig-Cmd',
            }

    def _get_dict_for_write(self):
        return {
            'Delay': self._set_delay,
            'Mode': lambda x: self._set_simple('Mode', x),
            'DelayType': lambda x: self._set_simple('DelayType', x),
            'ExtTrig': lambda x: self._set_simple('ExtTrig', x),
            }

    def _get_dict_for_read(self):
        return {
            'Delay': self._get_delay,
            'Mode': lambda x: {'Mode': x},
            'DelayType': lambda x: {'DelayType': x},
            'ExtTrig': lambda x: {'ExtTrig': x},
            }

    def _set_delay(self, value):
        value *= 1e-6  # us
        n = round(value / self._base_del)
        self._hl_state['Delay'] = n * self._base_del * 1e6
        self._ll_state['Delay'] = n

    def _get_delay(self, value):
        return {'Delay': value * self._base_del * 1e6}


class _LL_TrigEVROUT(_LL_Base):
    _NUM_OPT = 12
    _REMOVE_PROPS = {}

    def __init__(self, channel, conn_num, callback,
                 init_state, evg_params):
        self._internal_trigger = self._get_num_int(conn_num)
        self.prefix = LL_PREFIX + _PVName(channel).device_name + ':'
        self.channel = channel
        self._EVGParam_ENUMS = evg_params
        super().__init__(callback, init_state)

    def _INTLB_formatter(self):
        return 'IntTrig{0:02d}'.format(self._internal_trigger)

    def _OUTLB_formatter(self):
        return 'OUT{0:d}'.format(self._internal_trigger)

    def _get_num_int(self, num):
        return self._NUM_OPT + num

    def _get_convertion_prop2pvrb(self):
        intlb = self._INTLB_formatter()
        outlb = self._OUTLB_formatter()
        map_ = {
            'IntChan': self.prefix + outlb + 'IntChan-Sts',
            'Event': self.prefix + intlb + 'Event-Sts',
            'Delay': self.prefix + intlb + 'Delay-RB',
            'RFDelay': self.prefix + outlb + 'RFDelay-RB',
            'FineDelay': self.prefix + outlb + 'FineDelay-RB',
            'Pulses': self.prefix + intlb + 'Pulses-RB',
            'Width': self.prefix + intlb + 'Width-RB',
            'State': self.prefix + intlb + 'State-Sts',
            'Polrty': self.prefix + intlb + 'Polrty-Sts',
            }
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_dict_for_write(self):
        map_ = {
            'EVGParam': self._set_evg_param,
            'Delay': self._set_delay,
            'DelayType': self._set_delay_type,
            'Pulses': self._set_pulses,
            'Duration': self._set_duration,
            'State': lambda x: self._set_simple('State', x),
            'Polrty': lambda x: self._set_simple('Polrty', x),
            }
        return map_

    def _get_dict_for_read(self):
        map_ = {
            'IntChan': self._process_int_trig,
            'Event': self._process_event,
            'Delay': self._get_delay,
            'RFDelay': self._get_delay,
            'FineDelay': self._get_delay,
            'Pulses': lambda x: {'Pulses': x},
            'Width': self._get_duration,
            'State': lambda x: {'State': x},
            'Polrty': lambda x: {'Polrty': x},
            }
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_delay(self, value):
        pvs = self._pvs_rb
        delay1 = pvs['Delay'].get(timeout=_conn_timeout) or 0
        delay2 = pvs['RFDelay'].get(timeout=_conn_timeout) or 0
        delay3 = pvs['FineDelay'].get(timeout=_conn_timeout) or 0
        if delay2 == 31:
            delay = (delay1*self._base_del + delay3*FDEL) * 1e6
            return {'Delay': delay, 'DelayType': 1}
        else:
            delay = (delay1*self._base_del +
                     delay2*self._rf_del +
                     delay3*FDEL) * 1e6
            return {'Delay': delay, 'DelayType': 0}

    def _set_delay(self, value):
        _log.debug(self.channel+' Setting propty =' +
                   ' {0:s}, value = {1:s}.'.format('Delay', str(value)))
        value *= 1e-6  # us
        delay1 = value // self._base_del
        self._ll_state['Delay'] = delay1
        if not self._hl_state['DelayType']:
            value -= delay1 * self._base_del
            delay2 = value // self._rf_del
            value -= delay2 * self._rf_del
            delay3 = round(value / FDEL)
            delay = (delay1*self._base_del +
                     delay2*self._rf_del +
                     delay3*FDEL) * 1e6
            self._hl_state['Delay'] = delay
            self._ll_state['RFDelay'] = delay2
            self._ll_state['FineDelay'] = delay3
        else:
            self._hl_state['Delay'] = delay1 * self._base_del * 1e6
            self._ll_state['RFDelay'] = 31
            self._ll_state['FineDelay'] = 0

    def _set_delay_type(self, value):
        self._hl_state['DelayType'] = value
        self._set_delay(self._hl_state['Delay'])

    def _process_int_trig(self, value):
        if value == self._INTLB_formatter():
            val = self._pvs_rb['Event'].get(timeout=_conn_timeout)
            if val is None:
                _log.debug(self.channel + 'read None from PV ' +
                           self._pvs_rb['Event'].pvname)
                return dict()
            hl_val = Events.LL2HL_MAP[val]
        elif value.startswith('Clock'):
            hl_val = Clocks.LL2HL_MAP.get(value)
        else:
            _log.warning(self.prefix + ' Low Level Event set is not allowed.')
            return dict()

        if hl_val is None:
            _log.warning(self.channel + val + ' not in LL2HL_MAP.')
            return dict()
        if hl_val not in self._EVGParam_ENUMS:
            _log.warning(self.channel + hl_val + ' is not allowed.')
            return dict()
        return {'EVGParam': self._EVGParam_ENUMS.index(hl_val)}

    def _process_event(self, x):
        _log.debug(self.prefix + ' ll_event = ' + str(x))
        pname = self._EVGParam_ENUMS[self._hl_state['EVGParam']]
        if pname.startswith('Clock'):
            _log.debug(self.prefix + ' a clock is set in EVGParam: ' +
                       pname)
            return dict()
        if x not in Events.LL2HL_MAP.keys():
            _log.warning(self.prefix + 'Low Level event not in ' +
                         'High Level list of possible events.')
            return dict()
        pname = Events.LL2HL_MAP[x]
        _log.debug(self.prefix + ' hl_event = ' + pname)
        if pname not in self._EVGParam_ENUMS:
            _log.warning(self.prefix + 'High Level event not in allowed' +
                         ' list os possible events for this trigger.')
            return dict()
        return {'EVGParam': self._EVGParam_ENUMS.index(pname)}

    def _set_evg_param(self, value):
        _log.debug(self.channel+' Setting EVGParam, value = {0:s}.'
                   .format(str(value)))
        self._hl_state['EVGParam'] = value
        pname = self._EVGParam_ENUMS[value]
        if pname.startswith('Clock'):
            self._ll_state['IntChan'] = Clocks.HL2LL_MAP[pname]
        else:
            self._ll_state['Event'] = Events.HL2LL_MAP[pname]
            if 'IntChan' in self._dict_functions_for_read.keys():
                self._ll_state['IntChan'] = self._INTLB_formatter()

    def _get_duration(self, width):
        return {'Duration':
                2*width*self._base_del*self._hl_state['Pulses']*1e3}

    def _set_duration(self, value):
        value *= 1e-3  # ms
        pul = self._hl_state['Pulses']
        n = round(value / self._base_del / pul / 2)
        n = n if n >= 1 else 1
        self._hl_state['Duration'] = 2 * n * self._base_del * pul * 1e3
        self._ll_state['Width'] = n

    def _set_pulses(self, value):
        self._hl_state['Pulses'] = value
        self._ll_state['Pulses'] = value
        self._set_duration(self._hl_state['Duration'])


class _LL_TrigEVROTP(_LL_TrigEVROUT):
    _NUM_OPT = 12
    _REMOVE_PROPS = {'RFDelay', 'FineDelay', 'IntChan'}

    def _INTLB_formatter(self):
        return 'IntTrig{0:02d}'.format(self._internal_trigger)

    def _get_num_int(self, num):
        return num

    def _get_dict_for_read(self):
        map_ = super()._get_dict_for_read()
        map_['Delay'] = self._get_delay
        return map_

    def _get_delay(self, value):
        return {'Delay': value * self._base_del * 1e6}

    def _set_delay(self, value):
        _log.debug(self.channel+' Setting propty = {0:s}, value = {1:s}.'
                   .format('Delay', str(value)))
        value *= 1e-6
        delay1 = round(value // self._base_del)
        _log.debug(self.channel+' Delay1 = {}.'.format(str(delay1)))
        self._hl_state['Delay'] = delay1 * self._base_del * 1e6
        self._ll_state['Delay'] = delay1

    def _set_delay_type(self, value):
        self._hl_state['DelayType'] = 0


class _LL_TrigEVEOUT(_LL_TrigEVROUT):
    _NUM_OPT = 0

    def _INTLB_formatter(self):
        return 'IntTrig{0:02d}'.format(self._internal_trigger)


class _LL_TrigAFCCRT(_LL_TrigEVROUT):
    _NUM_OPT = 0
    _REMOVE_PROPS = {'RFDelay', 'FineDelay', 'IntChan'}

    def _INTLB_formatter(self):
        return 'CRT{0:d}'.format(self._internal_trigger)

    def _get_convertion_prop2pvrb(self):
        map_ = super()._get_convertion_prop2pvrb()
        map_['Event'] = self.prefix + self._INTLB_formatter() + 'EVGParam-Sts'
        return map_

    def _get_dict_for_write(self):
        map_ = super()._get_dict_for_write()
        map_['Event'] = self._set_evg_param
        map_['Delay'] = self._set_delay
        return map_

    def _get_dict_for_read(self):
        map_ = super()._get_dict_for_read()
        map_['Event'] = self._process_event
        map_['Delay'] = self._get_delay
        return map_

    def _get_delay(self, value):
        return {'Delay': value * self._base_del * 1e6}

    def _set_delay(self, value):
        _log.debug(self.channel+' Setting propty = {0:s}, value = {1:s}.'
                   .format('Delay', str(value)))
        value *= 1e-6
        delay1 = round(value // self._base_del)
        _log.debug(self.channel+' Delay1 = {}.'.format(str(delay1)))
        self._hl_state['Delay'] = delay1 * self._base_del * 1e6
        self._ll_state['Delay'] = delay1

    def _set_delay_type(self, value):
        self._hl_state['DelayType'] = 0

    def _process_event(self, evg_par_str):
        if evg_par_str.startswith('Clock'):
            val = Clocks.LL2HL_MAP[evg_par_str]
        else:
            if evg_par_str not in Events.LL2HL_MAP.keys():
                _log.warning(self.prefix + 'Low Level event not in ' +
                             'High Level list of possible events.')
                return dict()
            val = Events.LL2HL_MAP[evg_par_str]
        if val not in self._EVGParam_ENUMS:
            _log.warning(self.prefix + 'EVG param ' + val +
                         ' Not allowed for this trigger.')
            return dict()
        return {'EVGParam': self._EVGParam_ENUMS.index(val)}

    def _set_evg_param(self, value):
        _log.debug(self.channel +
                   ' Setting EVGParam, value = {0:s}.'.format(str(value)))
        self._hl_state['EVGParam'] = value
        pname = self._EVGParam_ENUMS[value]
        if pname.startswith('Clock'):
            val = Clocks.HL2LL_MAP[pname]
        else:
            val = Events.HL2LL_MAP[pname]
        self._ll_state['Event'] = val


class _LL_TrigAFCFMC(_LL_TrigAFCCRT):

    def _INTLB_formatter(self):
        fmc = (self._internal_trigger // 5) + 1
        ch = (self._internal_trigger % 5) + 1
        return 'FMC{0:d}CH{1:d}'.format(fmc, ch)
