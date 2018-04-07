"""Define the low level classes which will connect to Timing Devices IOC."""

import logging as _log
import epics as _epics
from siriuspy.thread import RepeaterThread as _Timer
from siriuspy.thread import QueueThread as _QueueThread
from siriuspy.epics import connection_timeout as _conn_timeout
from siriuspy.envars import vaca_prefix as LL_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName

from siriuspy.csdevice import timesys as _cstime
from siriuspy.timesys.time_data import Connections as _Connections
from siriuspy.timesys.time_data import IOs as _IOs
from siriuspy.timesys.time_data import RF_FREQUENCY as _RFFREQ
from siriuspy.timesys.time_data import RF_DIVISION as _RFDIV
from siriuspy.timesys.time_data import AC_FREQUENCY as _ACFREQ
from siriuspy.timesys.time_data import FINE_DELAY as _FDEL

INTERVAL = 0.1
_DELAY_UNIT_CONV = 1e-6
_Connections.add_bbb_info()
_Connections.add_crates_info()
EVG_NAME = _Connections.get_devices('EVG').pop()
EVRs = _Connections.get_devices('EVR')
EVEs = _Connections.get_devices('EVE')
AFCs = _Connections.get_devices('AFC')
FOUTs = _Connections.get_devices('FOUT')
TWDS_EVG = _Connections.get_connections_twds_evg()


class _Base:

    def __init__(self, callback, init_hl_state):
        """Initialize the Low Level object.

        callback is the callable to be called each time a low level PV changes
        its value.
        init_hl_state is the initial value of the high level properties.
        """
        self._dict_functions_for_write = self._define_dict_for_write()
        self._dict_functions_for_read = self._define_dict_for_read()
        self._dict_convert_prop2pv = self._define_convertion_prop2pv()
        self._dict_convert_pv2prop = {
                val: key for key, val in self._dict_convert_prop2pv.items()}
        self.callback = callback
        self._my_state_sp = dict()
        self._rf_freq = _RFFREQ
        self._rf_div = _RFDIV

        self._rf_freq_pv = _epics.PV(LL_PREFIX + 'AS-Glob:RF-Gen:Freq-SP',
                                     connection_timeout=_conn_timeout)
        self._rf_div_pv = _epics.PV(LL_PREFIX + EVG_NAME + ':RFDiv-SP',
                                    connection_timeout=_conn_timeout)
        self._update_base_freq()
        self._rf_freq_pv.add_callback(self._update_base_freq)
        self._rf_div_pv.add_callback(self._update_base_freq)

        self._timer = None
        self._initialize_my_state_sp(init_hl_state)

        self._pvs_sp = dict()
        self._pvs_rb = dict()
        self.connected = False
        self._queue = _QueueThread()
        self._queue.start()
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
            elif pv_name.endswith(('-Mon', '-Cte')):
                pv_name_rb = pv_name
            if pv_name_rb is not None:
                self._pvs_rb[prop] = _epics.PV(
                    pv_name_rb,
                    callback=self._on_change_pvs_rb,
                    connection_callback=self._on_connection,
                    connection_timeout=_conn_timeout)
            if pv_name_sp is not None:
                self._pvs_sp[prop] = _epics.PV(
                    pv_name_sp,
                    callback=self._on_change_pvs_sp,
                    connection_callback=self._on_connection,
                    connection_timeout=_conn_timeout)
                self._pvs_sp[prop]._initialized = False

        # Timer to force equality between high and low level:
        self._timer = _Timer(INTERVAL, self._force_equal)
        self._timer.start()

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
            self._timer = _Timer(INTERVAL, self._force_equal, niter=10)
            self._timer.start()

    def _update_base_freq(self, **kwargs):
        self._rf_freq = self._rf_freq_pv.get(
                                timeout=_conn_timeout) or self._rf_freq
        self._rf_div = self._rf_div_pv.get(
                                timeout=_conn_timeout) or self._rf_div
        self._base_freq = self._rf_freq / self._rf_div
        self._base_del = 1/self._base_freq
        self._rf_del = self._base_del / self._rf_div / 5

    def _define_convertion_prop2pv(self):
        """Define a dictionary for convertion of names.

        The dictionary converts low level properties names to low level PV
        names.
        """
        return dict()

    def _define_dict_for_write(self):
        """Define a dictionary of functions to convert HL to LL.

        Each function converts the values of High level properties into values
        of Low Level properties. The functions defined in this dictionary are
        called by write and they send to the Low Level IOC the converted
        values.
        """
        return dict()

    def _define_dict_for_read(self):
        """Define a dictionary of functions to convert LL to HL.

        Each function converts the readback values of Low Level properties into
        values of High Level properties and send them to the High Level classes
        for update of the readback PVs.
        It is called by the on_change_pvs_rb and calls the callback function.
        """
        return dict()

    def _get_from_pvs_rb(self, ll_prop, def_val=0):
        val = self._pvs_rb.get(ll_prop)
        if val is not None:
            val = val.get(timeout=_conn_timeout)
        return def_val if val is None else val

    def _initialize_my_state_sp(self, init_hl_state):
        for hl_prop, val in init_hl_state.items():
            fun = self._dict_functions_for_write[hl_prop]
            fun(val)
        self._start_timer()

    def _force_equal(self):
        for ll_prop, pv in self._pvs_sp.items():
            if not pv.connected:
                continue
            if not pv.put_complete:
                continue
            v = pv.get(timeout=_conn_timeout)
            if v is None:
                continue
            my_val = self._my_state_sp.get(ll_prop)
            if my_val is None:
                raise Exception(self.prefix + ' ll_prop = ' +
                                ll_prop + ' not in dict.')
            if pv._initialized and my_val == v:
                continue
            # If pv is a command, it must be sent only once
            if pv.pvname.endswith('-Cmd'):
                if self._my_state_sp[ll_prop]:
                    self._put_on_pv(pv, self._my_state_sp[ll_prop])
                    self._my_state_sp[ll_prop] = 0
                return
            self._put_on_pv(pv, my_val)

    def _put_on_pv(self, pv, value):
        pv.put(value, use_complete=True)
        pv._initialized = True

    def _on_change_pvs_sp(self, pvname, value, **kwargs):
        self._start_timer()

    def _on_change_pvs_rb(self, pvname, value, **kwargs):
        if value is None:
            return
        self._queue.add_callback(self._on_change_pvs_rb_thread, pvname, value)

    def _on_change_pvs_rb_thread(self, pvname, value, **kwargs):
        fun = self._dict_functions_for_read[self._dict_convert_pv2prop[pvname]]
        props = fun(value)
        for hl_prop, val in props.items():
            self.callback(self.channel, hl_prop, val)

    def _on_connection(self, pvname, conn, **kwargs):
        self._queue.add_callback(self._on_connection_thread, pvname, conn)

    def _on_connection_thread(self, pvname, conn):
        connected = True
        for prop, pv in self._pvs_sp.items():
            connected &= (conn if pvname == pv.pvname else pv.connected)
            if conn and pvname == pv.pvname:
                self._pvs_sp[prop]._initialized = False
                self._start_timer()

        for pv in self._pvs_rb.values():
            connected &= (conn if pvname == pv.pvname else pv.connected)
            if not connected:
                break
        self.connected = connected
        props = self._get_status('PVsConn', connected)
        for hl_prop, val in props.items():
            self.callback(self.channel, hl_prop, val)

    def _set_simple(self, prop, value):
        """Simple setting of Low Level IOC PVs.

        Function called by write when no convertion is needed between
        high and low level properties.
        """
        self._my_state_sp[prop] = value

    def _get_simple(self, prop, val=None, hl_prop=None):
        hl_prop = prop if hl_prop is None else hl_prop
        return {hl_prop: self._get_from_pvs_rb(prop) if val is None else val}

    def _get_status(self, prop, value):
        return dict()


class LL_EVG(_Base):
    """Define the Low Level EVG Class."""

    def __init__(self, channel,  callback, init_hl_state):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_hl_state)

    def _define_convertion_prop2pv(self):
        return {'ACDiv': self.prefix + 'ACDiv-RB'}

    def _define_dict_for_write(self):
        return {'RepRate': self._set_frequency}

    def _define_dict_for_read(self):
        return {'ACDiv': self._get_frequency}

    def _set_frequency(self, value):
        n = round(_ACFREQ/value)
        self._my_state_sp['ACDiv'] = n

    def _get_frequency(self, val=None):
        fr = self._get_from_pvs_rb('ACDiv', def_val=1) if val is None else val
        return {'RepRate': _ACFREQ / fr}


class LL_Clock(_Base):
    """Define the Low Level Clock Class."""

    def __init__(self, channel,  callback, init_hl_state):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_hl_state)

    def _define_convertion_prop2pv(self):
        return {
            'MuxDiv': self.prefix + 'MuxDiv-RB',
            'MuxEnbl': self.prefix + 'MuxEnbl-Sts',
            }

    def _define_dict_for_write(self):
        return {
            'Freq': self._set_frequency,
            'State': lambda x: self._set_simple('MuxEnbl', x),
            }

    def _define_dict_for_read(self):
        return {
            'MuxDiv': self._get_frequency,
            'MuxEnbl': lambda x: self._get_simple('MuxEnbl', x, 'State'),
            }

    def _set_frequency(self, value):
        value *= 1e3  # kHz
        n = round(self._base_freq/value)
        self._my_state_sp['MuxDiv'] = n

    def _get_frequency(self, val=None):
        fr = self._get_from_pvs_rb('MuxDiv', def_val=1) if val is None else val
        return {'Freq': self._base_freq / fr * 1e-3}


class LL_Event(_Base):
    """Define the Low Level Event Class."""

    def __init__(self, channel, callback, init_hl_state):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_hl_state)

    def _define_convertion_prop2pv(self):
        return {
            'Delay': self.prefix + 'Delay-RB',
            'Mode': self.prefix + 'Mode-Sts',
            'DelayType': self.prefix + 'DelayType-Sts',
            'ExtTrig': self.prefix + 'ExtTrig-Cmd',
            }

    def _define_dict_for_write(self):
        return {
            'Delay': self._set_delay,
            'Mode': lambda x: self._set_simple('Mode', x),
            'DelayType': lambda x: self._set_simple('DelayType', x),
            'ExtTrig': lambda x: self._set_simple('ExtTrig', x),
            }

    def _define_dict_for_read(self):
        return {
            'Delay': self._get_delay,
            'Mode': lambda x: self._get_simple('Mode',  x),
            'DelayType': lambda x: self._get_simple('DelayType', x),
            'ExtTrig': lambda x: self._get_simple('ExtTrig', x),
            }

    def _set_delay(self, value):
        value *= _DELAY_UNIT_CONV  # us
        n = int(value // self._base_del)
        self._my_state_sp['Delay'] = n

    def _get_delay(self, value):
        return {'Delay': value * self._base_del * 1e6}


class _EVROUT(_Base):
    _NUM_OTP = 12
    _REMOVE_PROPS = {}

    def __init__(self, channel, conn_num, callback,
                 init_hl_state, source_enums):
        self._internal_trigger = self._define_num_int(conn_num)
        self.prefix = LL_PREFIX + _PVName(channel).device_name + ':'
        chan_tree = _Connections.get_device_tree(channel)
        fout_name = [chan.device_name for chan in chan_tree
                     if chan.device_name in FOUTs][0]
        self._fout_prefix = LL_PREFIX + fout_name + ':'
        self._evg_prefix = LL_PREFIX + EVG_NAME + ':'
        self.channel = channel
        self._source_enums = source_enums
        init_hl_state['DevEnbl'] = 1
        init_hl_state['FOUTDevEnbl'] = 1
        init_hl_state['EVGDevEnbl'] = 1
        super().__init__(callback, init_hl_state)

    def _INTLB_formatter(self):
        return 'OTP{0:02d}'.format(self._internal_trigger)

    def _OUTLB_formatter(self):
        return 'OUT{0:d}'.format(self._internal_trigger - self._NUM_OTP)

    def _define_num_int(self, num):
        return self._NUM_OTP + num

    def _define_convertion_prop2pv(self):
        intlb = self._INTLB_formatter()
        outlb = self._OUTLB_formatter()
        map_ = {
            'State': self.prefix + intlb + 'State-Sts',
            'Evt': self.prefix + intlb + 'Evt-RB',
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

    def _define_dict_for_write(self):
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

    def _define_dict_for_read(self):
        map_ = {
            'State': lambda x: self._get_simple('State', x),
            'Evt': lambda x: self._process_source('Evt', x),
            'Width': lambda x: self._get_duration_pulses('Width', x),
            'Polarity': lambda x: self._get_simple('Polarity', x),
            'Pulses': lambda x: self._get_duration_pulses('Pulses', x),
            'Delay': lambda x: self._get_delay('Delay', x),
            'Intlk': lambda x: self._get_simple('Intlk', x),
            'Src': lambda x: self._process_source('Src', x),
            'SrcTrig': lambda x: self._process_source('SrcTrig', x),
            'RFDelay': lambda x: self._get_delay('RFDelay', x),
            'FineDelay': lambda x: self._get_delay('FineDelay', x),
            'DevEnbl': lambda x: self._get_status('DevEnbl', x),
            'Network': lambda x: self._get_status('Network', x),
            'Link': lambda x: self._get_status('Link', x),
            'Los': lambda x: self._get_status('Los', x),
            'IntlkMon': lambda x: self._get_status('IntlkMon', x),
            'FOUTDevEnbl': lambda x: self._get_status('FOUTDevEnbl', x),
            'EVGDevEnbl': lambda x: self._get_status('EVGDevEnbl', x),
            }
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_status(self, prop, value=None):
        dic_ = dict()
        dic_['DevEnbl'] = self._get_from_pvs_rb('DevEnbl', def_val=0)
        dic_['FOUTDevEnbl'] = self._get_from_pvs_rb('FOUTDevEnbl', def_val=0)
        dic_['EVGDevEnbl'] = self._get_from_pvs_rb('EVGDevEnbl', def_val=0)
        dic_['Network'] = self._get_from_pvs_rb('Network', def_val=0)
        dic_['IntlkMon'] = self._get_from_pvs_rb('IntlkMon', def_val=1)
        dic_['Link'] = self._get_from_pvs_rb('Link', def_val=0)
        dic_['Los'] = self._get_from_pvs_rb('Los', def_val=None)
        dic_['PVsConn'] = self.connected
        if value is not None:
            dic_[prop] = value

        status = 0
        status |= ((not dic_['PVsConn']) << 0)
        status |= ((not dic_['DevEnbl']) << 1)
        status |= ((not dic_['FOUTDevEnbl']) << 2)
        status |= ((not dic_['EVGDevEnbl']) << 3)
        status |= ((not dic_['Network']) << 4)
        status |= ((dic_['IntlkMon']) << 5)
        status |= ((not dic_['Link']) << 6)
        if dic_['Los'] is not None:
            num = self._internal_trigger - self._NUM_OTP
            if num >= 0 and (dic_['Los'] >> num) % 2:
                status |= (1 << 7)
        return {'Status': status}

    def _get_delay(self, prop, value=None):
        dic_ = dict()
        dic_['Delay'] = self._get_from_pvs_rb('Delay', def_val=0)
        dic_['RFDelay'] = self._get_from_pvs_rb('RFDelay', def_val=0)
        dic_['FineDelay'] = self._get_from_pvs_rb('FineDelay', def_val=0)
        if value is not None:
            dic_[prop] = value

        delay = (dic_['Delay']*self._base_del + dic_['FineDelay']*_FDEL) * 1e6
        if dic_['RFDelay'] == 31:
            return {'Delay': delay, 'DelayType': 1}
        else:
            delay += dic_['RFDelay']*self._rf_del * 1e6
            return {'Delay': delay, 'DelayType': 0}

    def _set_delay(self, value):
        value *= _DELAY_UNIT_CONV  # us
        delay1 = int(value // self._base_del)
        self._my_state_sp['Delay'] = delay1
        del_type = self._my_state_sp.get('RFDelay', 0)  # Initialization issue
        if del_type != 31:
            value -= delay1 * self._base_del
            delay2 = value // self._rf_del
            value -= delay2 * self._rf_del
            delay3 = round(value / _FDEL)
            self._my_state_sp['RFDelay'] = delay2
            self._my_state_sp['FineDelay'] = delay3

    def _set_delay_type(self, value):
        if value:
            self._my_state_sp['RFDelay'] = 31
            self._my_state_sp['FineDelay'] = 0
        else:
            self._my_state_sp['RFDelay'] = 0

    def _process_source(self, prop, value=None):
        dic_ = dict()
        dic_['SrcTrig'] = self._get_from_pvs_rb('SrcTrig', def_val=30)
        dic_['Src'] = self._get_from_pvs_rb('Src', def_val=None)
        dic_['Evt'] = self._get_from_pvs_rb('Evt', def_val=0)
        if value is not None:
            dic_[prop] = value

        ret = self._process_src_trig(dic_['SrcTrig'])
        if ret is not None:
            return ret
        ret = self._process_src(dic_['Src'])
        if ret is not None:
            return ret
        return self._process_evt(dic_['Evt'])

    def _process_evt(self, evt):
        src_len = len(self._source_enums)
        event = _cstime.events_ll_tmp.format(evt)
        if event not in _cstime.events_ll2hl_map:
            return {'Src': src_len}
        elif _cstime.events_ll2hl_map[event] not in self._source_enums:
            return {'Src': src_len}
        else:
            ev_num = self._source_enums.index(_cstime.events_ll2hl_map[event])
            return {'Src': ev_num}

    def _process_src_trig(self, src_trig):
        src_len = len(self._source_enums)
        if src_trig != self._internal_trigger:
            return {'Src': src_len}  # invalid

    def _process_src(self, src):
        src_len = len(self._source_enums)
        source = _cstime.triggers_src_ll[src]
        if not source:
            return {'Src': src_len}  # invalid
        elif source.startswith(('Dsbl', 'Clock')):
            return {'Src': self._source_enums.index(source)}

    def _set_source(self, value):
        pname = self._source_enums[value]
        if pname.startswith(('Clock', 'Dsbl')):
            self._my_state_sp['Src'] = _cstime.triggers_src_ll.index(pname)
        else:
            self._my_state_sp['Src'] = _cstime.triggers_src_ll.index('Trigger')
            self._my_state_sp['Evt'] = int(_cstime.events_hl2ll_map[pname][-2:])
        if 'SrcTrig' in self._dict_convert_prop2pv.keys():
            self._my_state_sp['SrcTrig'] = self._internal_trigger

    def _get_duration_pulses(self, prop, value=None):
        dic_ = dict()
        dic_['Pulses'] = self._get_from_pvs_rb('Pulses', def_val=0)
        dic_['Width'] = self._get_from_pvs_rb('Width', def_val=0)
        if value is not None:
            dic_[prop] = value
        return {
            'Duration': 2*dic_['Width']*self._base_del*dic_['Pulses']*1e3,
            'Pulses': dic_['Pulses'],
            }

    def _set_duration(self, value):
        value *= 1e-3  # ms
        pul = self._my_state_sp.get('Pulses', 1)  # Initialization issue
        n = int(round(value / self._base_del / pul / 2))
        n = n if n >= 1 else 1
        self._my_state_sp['Width'] = n

    def _set_pulses(self, value):
        if value < 1:
            return
        old_pul = self._my_state_sp.get('Pulses', 1)  # Initialization issue
        self._my_state_sp['Pulses'] = int(value)
        old_wid = self._my_state_sp.get('Width', 1)  # Initialization issue
        self._my_state_sp['Width'] = int(round(old_wid*old_pul/value))


class _EVROTP(_EVROUT):
    _REMOVE_PROPS = {'RFDelay', 'FineDelay', 'Src', 'SrcTrig', 'Intlk'}

    def _define_num_int(self, num):
        return num

    def _get_delay(self, prop, val=None):
        d = self._get_from_pvs_rb('Delay', def_val=0) if val is None else val
        return {'Delay': d * self._base_del * 1e6}

    def _set_delay(self, value):
        value *= _DELAY_UNIT_CONV
        delay1 = int(value // self._base_del)
        self._my_state_sp['Delay'] = delay1

    def _set_delay_type(self, value):
        return

    def _process_source(self, prop, val=None):
        event = self._get_from_pvs_rb('Evt', def_val=0) if val is None else val
        return self._process_evt(event)

    def _set_source(self, value):
        pname = self._source_enums[value]
        if not pname.startswith(('Clock', 'Dsbl')):
            self._my_state_sp['Evt'] = int(
                            _cstime.events_hl2ll_map[pname][-2:]
                            )


class _EVEOUT(_EVROUT):
    _NUM_OTP = 0
    _REMOVE_PROPS = {'Los', }


class _AFCCRT(_EVROUT):
    _NUM_OTP = 0
    _REMOVE_PROPS = {'RFDelay', 'FineDelay', 'SrcTrig', 'Intlk'}

    def _INTLB_formatter(self):
        return 'CRT{0:d}'.format(self._internal_trigger)

    def _OUTLB_formatter(self):
        return self._INTLB_formatter()

    def _get_delay(self, prop, value=None):
        return _EVROTP._get_delay(self, prop, value)

    def _set_delay(self, value):
        _EVROTP._set_delay(self, value)

    def _set_delay_type(self, value):
        _EVROTP._set_delay_type(self, value)

    def _process_source(self, prop, value=None):
        dic_ = dict()
        dic_['Src'] = self._get_from_pvs_rb('Src', def_val=None)
        dic_['Evt'] = self._get_from_pvs_rb('Evt', def_val=0)
        if value is not None:
            dic_[prop] = value

        ret = self._process_src(dic_['Src'])
        if ret is not None:
            return ret
        return self._process_evt(dic_['Evt'])


class _AFCFMC(_AFCCRT):

    def _INTLB_formatter(self):
        fmc = (self._internal_trigger // 5) + 1
        ch = (self._internal_trigger % 5) + 1
        return 'FMC{0:d}CH{1:d}'.format(fmc, ch)


def get_ll_trigger_object(channel, callback, init_hl_state, source_enums):
    """Get Low Level trigger objects."""
    LL_TRIGGER_CLASSES = {
        ('EVR', 'OUT'): _EVROUT,
        ('EVR', 'OTP'): _EVROTP,
        ('EVE', 'OUT'): _EVEOUT,
        ('AFC', 'CRT'): _AFCCRT,
        ('AFC', 'FMC'): _AFCFMC,
        }
    chan = _PVName(channel)
    match = _IOs.LL_RGX.findall(chan.propty)
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
    return cls_(channel, int(conn_num), callback, init_hl_state, source_enums)
