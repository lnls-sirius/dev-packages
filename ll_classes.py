"""Define the low level classes which will connect to Timing Devices IOC."""

import logging as _log
from threading import Event as _Event
from threading import Thread as _Thread
from pcaspy import Alarm, Severity
import epics as _epics
from siriuspy.epics import connection_timeout as _conn_timeout
from siriuspy.envars import vaca_prefix as LL_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.timesys.time_data import IOs
from siriuspy.timesys.time_data import Events, Triggers, Connections
from siriuspy.timesys.time_data import RF_FREQUENCY as RFFREQ
from siriuspy.timesys.time_data import RF_DIVISION as RFDIV
from siriuspy.timesys.time_data import AC_FREQUENCY as ACFREQ
from siriuspy.timesys.time_data import FINE_DELAY as FDEL

_INTERVAL = 0.1
_DELAY_UNIT_CONV = 1e-6
Connections.add_bbb_info()
Connections.add_crates_info()
EVG_NAME = Connections.get_devices('EVG').pop()
EVRs = Connections.get_devices('EVR')
EVEs = Connections.get_devices('EVE')
AFCs = Connections.get_devices('AFC')
FOUTs = Connections.get_devices('FOUT')
TWDS_EVG = Connections.get_connections_twds_evg()


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


class _Base:

    def __init__(self, callback, init_state):
        """Initialize the Low Level object.

        callback is the callable to be called each time a low level PV changes
        its value.
        init_state is the initial value of the high level properties.
        """
        self._dict_functions_for_write = self._get_dict_for_write()
        self._dict_functions_for_read = self._get_dict_for_read()
        self._dict_convert_prop2pv = self._get_convertion_prop2pv()
        self._dict_convert_pv2prop = {
                val: key for key, val in self._dict_convert_prop2pv.items()}
        self.callback = callback
        self._hl_state = init_state
        self._ll_state = dict()
        self._rf_freq = RFFREQ
        self._rf_div = RFDIV
        _log.info(self.channel+': Starting.')

        PV_Class = _epics.PV
        self._rf_freq_pv = PV_Class(LL_PREFIX + 'SI-03SP:RF-SRFCav:Freq-SP',
                                    connection_timeout=_conn_timeout)
        self._rf_div_pv = PV_Class(LL_PREFIX + EVG_NAME + ':RFDiv-SP',
                                   connection_timeout=_conn_timeout)
        self._set_base_freq()
        self._rf_freq_pv.add_callback(self._set_base_freq)
        self._rf_div_pv.add_callback(self._set_base_freq)

        self._timer = None
        self._initialize_ll_state()

        self._pvs_sp = dict()
        self._pvs_rb = dict()
        _log.info(self.channel+': Creating PVs.')
        for prop, pv_name in self._dict_convert_prop2pv.items():
            pv_name_rb = pv_name_sp = None
            if pv_name.endswith('-RB'):
                pv_name_rb = pv_name
                pv_name_sp = pv_name.replace('-RB', '-SP')
            elif pv_name.endswith('-Sts'):
                pv_name_rb = pv_name
                pv_name_sp = pv_name.replace('-Sts', '-Sel')
            elif pv_name.endswith('-Cmd'):
                pv_name_sp = pv_name
            elif pv_name.endswith('-Mon'):
                pv_name_rb = pv_name
            if pv_name_rb is not None:
                self._pvs_rb[prop] = PV_Class(
                    pv_name_rb,
                    callback=self._on_change_pvs_rb,
                    connection_timeout=_conn_timeout)
            if pv_name_sp is not None:
                self._pvs_sp[prop] = PV_Class(
                    pv_name_sp,
                    callback=self._on_change_pvs_sp,
                    connection_timeout=_conn_timeout)

        # Timer to force equality between high and low level:
        self._timer = _Timer(_INTERVAL, self._force_equal)
        self._timer.start()
        _log.info(self.channel + ': Done.')

    def write(self, prop, value):
        """Set property values in low level IOCS.

        Function called by classes that control high level PVs to transform
        the high level values into low level properties and set the low level
        IOCs accordingly.
        """
        fun = self._dict_functions_for_write[prop]
        fun(value)
        self._start_timer()
        return True

    def _start_timer(self):
        if self._timer is None:
            return
        if self._timer.isAlive():
            self._timer.reset()
        else:
            self._timer = _Timer(_INTERVAL, self._force_equal, niter=10)
            self._timer.start()

    def _set_base_freq(self, **kwargs):
        self._rf_freq = self._rf_freq_pv.get(
                                timeout=_conn_timeout) or self._rf_freq
        self._rf_div = self._rf_div_pv.get(
                                timeout=_conn_timeout) or self._rf_div
        self._base_freq = self._rf_freq / self._rf_div
        self._base_del = 1/self._base_freq
        self._rf_del = self._base_del / self._rf_div / 5

    def _get_convertion_prop2pv(self):
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
                continue
            if not pv.put_complete:
                continue
            v = pv.get(timeout=_conn_timeout)
            if v is None:
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
        pv.put(value, use_complete=True)

    def _on_change_pvs_sp(self, pvname, value, **kwargs):
        self._start_timer()

    def _on_change_pvs_rb(self, pvname, value, **kwargs):
        if value is None:
            return
        fun = self._dict_functions_for_read[
                                self._dict_convert_pv2prop[pvname]]
        props = fun(value)
        for hl_prop, val in props.items():
            if not isinstance(val, dict):
                val = {'value': val}
            self.callback(self.channel, hl_prop, val)

    def _set_simple(self, prop, value, ll_prop=None):
        """Simple setting of Low Level IOC PVs.

        Function called by write when no convertion is needed between
        high and low level properties.
        """
        ll_prop = ll_prop or prop
        self._hl_state[prop] = value
        self._ll_state[ll_prop] = value


class LL_EVG(_Base):
    """Define the Low Level EVG Class."""

    def __init__(self, channel,  callback, init_state):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_state)

    def _get_convertion_prop2pv(self):
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


class LL_Clock(_Base):
    """Define the Low Level Clock Class."""

    def __init__(self, channel,  callback, init_state):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_state)

    def _get_convertion_prop2pv(self):
        return {
            'MuxDiv': self.prefix + 'MuxDiv-RB',
            'MuxEnbl': self.prefix + 'MuxEnbl-Sts',
            }

    def _get_dict_for_write(self):
        return {
            'Freq': self._set_frequency,
            'State': lambda x: self._set_simple('State', x, ll_prop='MuxEnbl'),
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


class LL_Event(_Base):
    """Define the Low Level Event Class."""

    def __init__(self, channel, callback, init_state):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_state)

    def _get_convertion_prop2pv(self):
        return {
            'Delay': self.prefix + 'Delay-RB',
            'Mode': self.prefix + 'Mode-Sts',
            'DelayType': self.prefix + 'DelayType-Sts',
            'ExtTrig': self.prefix + 'ExtTrig-Cmd',
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
        value *= _DELAY_UNIT_CONV  # us
        n = int(value // self._base_del)
        self._hl_state['Delay'] = n * self._base_del * 1e6
        self._ll_state['Delay'] = n

    def _get_delay(self, value):
        return {'Delay': value * self._base_del * 1e6}


class _EVROUT(_Base):
    _NUM_OTP = 12
    _REMOVE_PROPS = {}

    def __init__(self, channel, conn_num, callback,
                 init_state, source_enums):
        self._internal_trigger = self._get_num_int(conn_num)
        self.prefix = LL_PREFIX + _PVName(channel).device_name + ':'
        chan_tree = Connections.get_device_tree(channel)
        fout_name = [chan.device_name for chan in chan_tree
                     if chan.device_name in FOUTs][0]
        self._fout_prefix = LL_PREFIX + fout_name + ':'
        self._evg_prefix = LL_PREFIX + EVG_NAME + ':'
        self.channel = channel
        self._source_enums = source_enums
        init_state['DevEnbl'] = 1
        init_state['FOUTDevEnbl'] = 1
        init_state['EVGDevEnbl'] = 1
        super().__init__(callback, init_state)

    def _INTLB_formatter(self):
        return 'OTP{0:02d}'.format(self._internal_trigger)

    def _OUTLB_formatter(self):
        return 'OUT{0:d}'.format(self._internal_trigger - self._NUM_OTP)

    def _get_num_int(self, num):
        return self._NUM_OTP + num

    def _get_convertion_prop2pv(self):
        intlb = self._INTLB_formatter()
        outlb = self._OUTLB_formatter()
        map_ = {
            'State': self.prefix + intlb + 'State-Sts',
            'Evt': self.prefix + intlb + 'Evt-Sts',
            'Width': self.prefix + intlb + 'Width-RB',
            'Polarity': self.prefix + intlb + 'Polarity-Sts',
            'Pulses': self.prefix + intlb + 'Pulses-RB',
            'Delay': self.prefix + intlb + 'Delay-RB',
            'Intlk': self.prefix + outlb + 'Intlk-Sts',
            'Src': self.prefix + outlb + 'Src-Sts',
            'SrcTrig': self.prefix + outlb + 'SrcTrig-RB',
            'RFDelay': self.prefix + outlb + 'RFDelay-RB',
            'FineDelay': self.prefix + outlb + 'FineDelay-RB',
            # connection status PVs
            'DevEnbl': self.prefix + 'DevEnbl-Sts',
            'Network': self.prefix + 'Network-Mon',
            'Link': self.prefix + 'Link-Mon',
            'Los': self.prefix + 'Los-Mon',
            'IntlkMon': self.prefix + 'Intlk-Mon',
            'FOUTDevEnbl': self._fout_prefix + 'DevEnbl-Sts',
            'EVGDevEnbl': self._evg_prefix + 'DevEnbl-Sts',
            }
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_dict_for_write(self):
        map_ = {
            'DevEnbl': lambda x: self._set_simple('DevEnbl', x),
            'FOUTDevEnbl': lambda x: self._set_simple('FOUTDevEnbl', x),
            'EVGDevEnbl': lambda x: self._set_simple('EVGDevEnbl', x),
            'State': lambda x: self._set_simple('State', x),
            'Src': self._set_source,
            'Duration': self._set_duration,
            'Polarity': lambda x: self._set_simple('Polarity', x),
            'Pulses': self._set_pulses,
            'Intlk': lambda x: self._set_simple('Intlk', x),
            'Delay': self._set_delay,
            'DelayType': self._set_delay_type,
            }
        return map_

    def _get_dict_for_read(self):
        map_ = {
            'State': lambda x: {'State': x},
            'Evt': self._process_source,
            'Width': self._get_duration,
            'Polrty': lambda x: {'Polrty': x},
            'Pulses': lambda x: {'Pulses': x},
            'Delay': self._get_delay,
            'Intlk': lambda x: {'Intlk': x},
            'Src': self._process_source,
            'SrcTrig': self._process_source,
            'RFDelay': self._get_delay,
            'FineDelay': self._get_delay,
            'DevEnbl': self._get_conn_status,
            'FOUTDevEnbl': self._get_conn_status,
            'EVGDevEnbl': self._get_conn_status,
            'Network': self._get_conn_status,
            'Link': self._get_conn_status,
            'Los': self._get_conn_status,
            'IntlkMon': self._get_conn_status,
            }
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_conn_status(self, value):
        pvs = self._pvs_rb
        devsts = pvs['DevEnbl'].get(timeout=_conn_timeout) or 1
        foutsts = pvs['FOUTDevEnbl'].get(timeout=_conn_timeout) or 1
        evgsts = pvs['EVGDevEnbl'].get(timeout=_conn_timeout) or 1
        if not all((devsts, foutsts, evgsts)):
            return {'ConnStatus': {
                        'value': 1,
                        'alarm': Alarm.DISABLE_ALARM,
                        'severity': Severity.MAJOR_ALARM}
                    }  # Dev Dsbl
        network = pvs['Network'].get(timeout=_conn_timeout) or 1
        if not network:
            return {'ConnStatus': {
                        'value': 2,
                        'alarm': Alarm.COMM_ALARM,
                        'severity': Severity.MINOR_ALARM}
                    }  # Network Discon
        intlk = pvs['IntlkMon'].get(timeout=_conn_timeout) or 1
        if intlk:
            return {'ConnStatus': {
                        'value': 3,
                        'alarm': Alarm.STATE_ALARM,
                        'severity': Severity.MINOR_ALARM}
                    }  # Intlk Actve
        link = pvs['Link'].get(timeout=_conn_timeout) or 1
        if link:
            return {'ConnStatus': {
                        'value': 4,
                        'alarm': Alarm.LINK_ALARM,
                        'severity': Severity.MAJOR_ALARM}
                    }  # Up Link Discon
        los = pvs.get('Los')
        if los is not None:
            los = los.get(timeout=_conn_timeout) or 0
            num = self._internal_trigger - self._NUM_OTP
            if (los >> num) % 2:
                return {'ConnStatus': {
                            'value': 5,
                            'alarm': Alarm.LINK_ALARM,
                            'severity': Severity.MAJOR_ALARM}
                        }  # Down Link Discon
        return {'ConnStatus': {
                    'value': 0,
                    'alarm': Alarm.NO_ALARM,
                    'severity': Severity.NO_ALARM}
                }  # Connection OK

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
        value *= _DELAY_UNIT_CONV  # us
        delay1 = int(value // self._base_del)
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

    def _process_source(self, value):
        src_len = len(self._source_enums)
        trig = self.pvs_rb['SrcTrig'].get(timeout=_conn_timeout) or 30
        if trig != self._internal_trigger:
            return {'Src': src_len}  # invalid

        source = self.pvs_rb['Src'].get(timeout=_conn_timeout, as_string=True)
        if not source:
            return {'Src': src_len}  # invalid
        elif source.startswith(('Dsbl', 'Clock')):
            return {'Src': self._source_enums.index(source)}

        event = self.pvs_rb['Evt'].get(timeout=_conn_timeout) or 0
        event = Events.LL_TMP.format(event)
        if event not in Events.LL2HL_MAP:
            return {'Src': src_len}
        elif Events.LL2HL_MAP[event] not in self._source_enums:
            return {'Src': src_len}
        else:
            ev_num = self._source_enums.index(Events.LL2HL_MAP[event])
            return {'Src': ev_num}

    def _set_source(self, value):
        self._hl_state['Src'] = value
        pname = self._source_enums[value]
        if pname.startswith(('Clock', 'Dsbl')):
            self._ll_state['Src'] = Triggers.SRC_LL.index(pname)
        else:
            self._ll_state['Src'] = Triggers.SRC_LL.index('Trigger')
            self._ll_state['Evt'] = int(Events.HL2LL_MAP[pname][-2:])
        self._ll_state['SrcTrig'] = self._internal_trigger

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


class _EVROTP(_EVROUT):
    _REMOVE_PROPS = {'RFDelay', 'FineDelay', 'Src', 'SrcTrig', 'Intlk'}

    def _get_num_int(self, num):
        return num

    def _get_delay(self, value):
        return {'Delay': value * self._base_del * 1e6}

    def _set_delay(self, value):
        value *= _DELAY_UNIT_CONV
        delay1 = int(value // self._base_del)
        self._hl_state['Delay'] = delay1 * self._base_del * 1e6
        self._ll_state['Delay'] = delay1

    def _set_delay_type(self, value):
        self._hl_state['DelayType'] = 0

    def _process_source(self, value):
        src_len = len(self._source_enums)
        event = self.pvs_rb['Evt'].get(timeout=_conn_timeout) or 0
        event = Events.LL_TMP.format(event)
        if event not in Events.LL2HL_MAP:
            return {'Src': src_len}
        elif Events.LL2HL_MAP[event] not in self._source_enums:
            return {'Src': src_len}
        else:
            ev_num = self._source_enums.index(Events.LL2HL_MAP[event])
            return {'Src': ev_num}

    def _set_source(self, value):
        self._hl_state['Src'] = value
        pname = self._source_enums[value]
        self._ll_state['Evt'] = int(Events.HL2LL_MAP[pname][-2:])


class _EVEOUT(_EVROUT):
    _NUM_OTP = 0


class _AFCCRT(_EVROUT):
    _NUM_OTP = 0
    _REMOVE_PROPS = {'RFDelay', 'FineDelay', 'SrcTrig', 'Intlk'}

    def _INTLB_formatter(self):
        return 'CRT{0:d}'.format(self._internal_trigger)

    def _OUTLB_formatter(self):
        return self._INTLB_formatter()

    def _get_delay(self, value):
        return {'Delay': value * self._base_del * 1e6}

    def _set_delay(self, value):
        value *= _DELAY_UNIT_CONV
        delay1 = int(value // self._base_del)
        self._hl_state['Delay'] = delay1 * self._base_del * 1e6
        self._ll_state['Delay'] = delay1

    def _set_delay_type(self, value):
        self._hl_state['DelayType'] = 0

    def _process_source(self, value):
        src_len = len(self._source_enums)
        source = self.pvs_rb['Src'].get(timeout=_conn_timeout, as_string=True)
        if not source:
            return {'Src': src_len}  # invalid
        elif source.startswith(('Dsbl', 'Clock')):
            return {'Src': self._source_enums.index(source)}

        event = self.pvs_rb['Evt'].get(timeout=_conn_timeout) or 0
        event = Events.LL_TMP.format(event)
        if event not in Events.LL2HL_MAP:
            return {'Src': src_len}
        elif Events.LL2HL_MAP[event] not in self._source_enums:
            return {'Src': src_len}
        else:
            ev_num = self._source_enums.index(Events.LL2HL_MAP[event])
            return {'Src': ev_num}

    def _set_source(self, value):
        self._hl_state['Src'] = value
        pname = self._source_enums[value]
        if pname.startswith(('Clock', 'Dsbl')):
            self._ll_state['Src'] = Triggers.SRC_LL.index(pname)
        else:
            self._ll_state['Src'] = Triggers.SRC_LL.index('Trigger')
            self._ll_state['Evt'] = int(Events.HL2LL_MAP[pname][-2:])


class _AFCFMC(_AFCCRT):

    def _INTLB_formatter(self):
        fmc = (self._internal_trigger // 5) + 1
        ch = (self._internal_trigger % 5) + 1
        return 'FMC{0:d}CH{1:d}'.format(fmc, ch)


def get_ll_trigger_object(channel, callback, init_state, source_enums):
    """Get Low Level trigger objects."""
    LL_TRIGGER_CLASSES = {
        ('EVR', 'OUT'): _EVROUT,
        ('EVR', 'OTP'): _EVROTP,
        ('EVE', 'OUT'): _EVEOUT,
        ('AFC', 'CRT'): _AFCCRT,
        ('AFC', 'FMC'): _AFCFMC,
        }
    chan = _PVName(channel)
    match = IOs.LL_RGX.findall(chan.propty)
    if match[0][0] == 'FMC':
        conn_ty = match[0][0]
        conn_num = int(match[0][1]-1) + 5*(int(match[1][1])-1)
    else:
        conn_ty = match[0][0]
        conn_num = match[0][1]
    key = (chan.dev, conn_ty)
    cls_ = LL_TRIGGER_CLASSES.get(key)
    if not cls_:
        raise Exception('Low Level Trigger Class not defined for device ' +
                        'type '+key[0]+' and connection type '+key[1]+'.')
    return cls_(channel, int(conn_num), callback, init_state, source_enums)


def get_ll_trigger_obj_names(chans):
    channels = set()
    for chan in chans:
        chan_tree = Connections.get_device_tree(chan)
        for up_chan in chan_tree:
            if up_chan.device_name in EVRs | EVEs | AFCs:
                channels |= {up_chan}
                break
    return sorted(channels)
