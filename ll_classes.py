"""Define the low level classes which will connect to Timing Devices IOC."""

from functools import partial as _partial
import logging as _log
import epics as _epics
from siriuspy.thread import RepeaterThread as _Timer
from siriuspy.thread import QueueThread as _QueueThread
from siriuspy.epics import connection_timeout as _conn_timeout
from siriuspy.envars import vaca_prefix as LL_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName

from siriuspy.csdevice import timesys as _cstime
from siriuspy.search import LLTimeSearch as _LLTimeSearch

_RFFREQ = _cstime.Const.RF_FREQUENCY
_RFDIV = _cstime.Const.RF_DIVISION
_ACFREQ = _cstime.Const.AC_FREQUENCY
_FDEL = _cstime.Const.FINE_DELAY

INTERVAL = 0.1
_DELAY_UNIT_CONV = 1e-6
_LLTimeSearch.add_bbb_info()
_LLTimeSearch.add_crates_info()
EVG_NAME = _LLTimeSearch.get_devices_by_type('EVG').pop()
EVRs = _LLTimeSearch.get_devices_by_type('EVR')
EVEs = _LLTimeSearch.get_devices_by_type('EVE')
AFCs = _LLTimeSearch.get_devices_by_type('AFC')
FOUTs = _LLTimeSearch.get_devices_by_type('FOUT')
TWDS_EVG = _LLTimeSearch.get_connections_twds_evg()


class _Base:

    def __init__(self, callback, init_hl_state, get_ll_state=True):
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
        self._pvs_sp = dict()
        self._pvs_rb = dict()
        self._initialize_my_state_sp(init_hl_state, get_ll_state)
        self.connected = False
        self._queue = _QueueThread()
        self._queue.start()
        self._is_forcing = False

        _log.info(self.channel+': Creating PVs.')
        for prop, pv_name in self._dict_convert_prop2pv.items():
            pv_name_rb = pv_name_sp = None
            if pv_name.endswith('-RB'):
                pv_name_rb = pv_name
                pv_name_sp = pv_name.replace('-RB', '-SP')
            elif pv_name.endswith('-Sts'):
                pv_name_rb = pv_name
                pv_name_sp = pv_name.replace('-Sts', '-Sel')
            elif pv_name.endswith('-Cmd'):  # -Cmd is different!!
                self._pvs_sp[prop] = _epics.PV(
                    pv_name,
                    connection_callback=self._on_connection,
                    connection_timeout=_conn_timeout)
                self._pvs_sp[prop]._initialized = False
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

        # Timer to force equality on low level pvs:
        self._timer = _Timer(INTERVAL, self._force_equal)

        # define if it will start forcing high level state since start.
        if not get_ll_state:
            self._is_forcing = True
            self._timer.start()

    def write(self, prop, value):
        """Set property values in low level IOCS.

        Function called by classes that control high level PVs to transform
        the high level values into low level properties and set the low level
        IOCs accordingly.
        """
        dic_ = self._dict_functions_for_write[prop](value)
        self._my_state_sp.update(dic_)
        for prop, v in dic_.items():
            self._put_on_pv(self._pvs_sp[prop], v)
        return True

    def start_forcing(self):
        self._is_forcing = True
        self._start_timer()

    def stop_forcing(self):
        self._is_forcing = False

    def _start_timer(self):
        if self._timer is None:
            return
        if self._timer.is_alive():
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

    def _get_from_pvs(self, is_sp, ll_prop, def_val=0):
        if is_sp:
            val = self._pvs_sp.get(ll_prop)
        else:
            val = self._pvs_rb.get(ll_prop)
        if val is not None:
            val = val.get(timeout=_conn_timeout)
        return def_val if val is None else val

    def _initialize_my_state_sp(self, init_hl_state, get_ll_state):
        self._initializing = not get_ll_state
        for hl_prop, val in init_hl_state.items():
            dic_ = self._dict_functions_for_write[hl_prop](val)
            self._my_state_sp.update(dic_)
        self._initializing = False

    def _force_equal(self):
        for ll_prop, pv in self._pvs_sp.items():
            if not pv.connected or not pv.put_complete:
                continue
            # skip if pv is a command
            v = pv.get(timeout=_conn_timeout)
            if pv.pvname.endswith('-Cmd') or v is None:
                continue

            my_val = self._my_state_sp.get(ll_prop)
            if my_val is None:
                raise Exception(self.prefix + ' ll_prop = ' +
                                ll_prop + ' not in dict.')
            if pv._initialized and my_val == v:
                continue
            self._put_on_pv(pv, my_val)

    def _put_on_pv(self, pv, value):
        pv.put(value, use_complete=True)
        pv._initialized = True

    def _on_change_pvs_sp(self, pvname, value, **kwargs):
        if self._is_forcing:
            self._start_timer()
        else:
            if pvname.endswith('-Cmd'):
                return  # -Cmd must not change
            self._queue.add_callback(
                    self._on_change_pvs_sp_thread, pvname, value)

    def _on_change_pvs_sp_thread(self, pvname, value, **kwargs):
        pvn = pvname.replace('-SP', '-RB').replace('-Sel', '-Sts')
        if pvn == pvname or value is None:
            return  # make sure no -Cmd passes here
        prop = self._dict_convert_pv2prop[pvn]
        # self._my_state_sp[prop] = value
        fun = self._dict_functions_for_read[prop]
        props = fun(True, value)
        for hl_prop, val in props.items():
            self.callback(self.channel, hl_prop, val, is_sp=True)

    def _on_change_pvs_rb(self, pvname, value, **kwargs):
        if value is None:
            return
        self._queue.add_callback(self._on_change_pvs_rb_thread, pvname, value)

    def _on_change_pvs_rb_thread(self, pvname, value, **kwargs):
        fun = self._dict_functions_for_read[self._dict_convert_pv2prop[pvname]]
        props = fun(False, value)
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
                if self._is_forcing:
                    self._start_timer()

        for pv in self._pvs_rb.values():
            connected &= (conn if pvname == pv.pvname else pv.connected)
            if not connected:
                break
        self.connected = connected
        props = self._get_status('PVsConn', False, connected)
        for hl_prop, val in props.items():
            self.callback(self.channel, hl_prop, val)

    def _set_simple(self, prop, value):
        """Simple setting of Low Level IOC PVs.

        Function called by write when no convertion is needed between
        high and low level properties.
        """
        return {prop: value}

    def _get_simple(self, prop, is_sp, val=None, hl_prop=None):
        hl_prop = prop if hl_prop is None else hl_prop
        if val is None:
            val = self._get_from_pvs(is_sp, prop)
        return {hl_prop: val}

    def _get_status(self, prop, is_sp, value):
        return dict()


class LL_EVG(_Base):
    """Define the Low Level EVG Class."""

    def __init__(self, channel,  callback, init_hl_state, get_ll_state=True):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_hl_state, get_ll_state)

    def _define_convertion_prop2pv(self):
        return {'ACDiv': self.prefix + 'ACDiv-RB'}

    def _define_dict_for_write(self):
        return {'RepRate': self._set_frequency}

    def _define_dict_for_read(self):
        return {'ACDiv': self._get_frequency}

    def _set_frequency(self, value):
        n = round(_ACFREQ/value)
        return {'ACDiv': n}

    def _get_frequency(self, is_sp, val=None):
        if val is None:
            val = self._get_from_pvs(is_sp, 'ACDiv', def_val=1)
        return {'RepRate': _ACFREQ / val}


class LL_Clock(_Base):
    """Define the Low Level Clock Class."""

    def __init__(self, channel,  callback, init_hl_state, get_ll_state=True):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_hl_state, get_ll_state)

    def _define_convertion_prop2pv(self):
        return {
            'MuxDiv': self.prefix + 'MuxDiv-RB',
            'MuxEnbl': self.prefix + 'MuxEnbl-Sts',
            }

    def _define_dict_for_write(self):
        return {
            'Freq': self._set_frequency,
            'State': _partial(self._set_simple, 'MuxEnbl'),
            }

    def _define_dict_for_read(self):
        return {
            'MuxDiv': self._get_frequency,
            'MuxEnbl': _partial(self._get_simple, 'MuxEnbl', hl_prop='State'),
            }

    def _set_frequency(self, value):
        value *= 1e3  # kHz
        n = round(self._base_freq/value)
        return {'MuxDiv': n}

    def _get_frequency(self, is_sp, val=None):
        if val is None:
            val = self._get_from_pvs(is_sp, 'MuxDiv', def_val=1)
        return {'Freq': self._base_freq / val * 1e-3}


class LL_Event(_Base):
    """Define the Low Level Event Class."""

    def __init__(self, channel, callback, init_hl_state, get_ll_state=True):
        """Initialize the instance."""
        self.prefix = LL_PREFIX + channel
        self.channel = channel
        super().__init__(callback, init_hl_state, get_ll_state)

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
            'Mode': _partial(self._set_simple, 'Mode'),
            'DelayType': _partial(self._set_simple, 'DelayType'),
            'ExtTrig': self._set_ext_trig,
            }

    def _define_dict_for_read(self):
        return {
            'Delay': self._get_delay,
            'Mode': _partial(self._get_simple, 'Mode'),
            'DelayType': _partial(self._get_simple, 'DelayType'),
            'ExtTrig': _partial(self._get_simple, 'ExtTrig'),
            }

    def _set_delay(self, value):
        value *= _DELAY_UNIT_CONV  # us
        n = int(value // self._base_del)
        return {'Delay': n}

    def _get_delay(self, is_sp, value):
        return {'Delay': value * self._base_del * 1e6}

    def _set_ext_trig(self, value):
        return {'ExtTrig': 0} if value else dict()


class _EVROUT(_Base):
    _NUM_OTP = 12
    _REMOVE_PROPS = {}

    def __init__(self, channel, conn_num, callback,
                 init_hl_state, source_enums, get_ll_state=True):
        self._internal_trigger = self._define_num_int(conn_num)
        self.prefix = LL_PREFIX + _PVName(channel).device_name + ':'
        chan_tree = _LLTimeSearch.get_device_tree(channel)
        for chan in chan_tree:
            if chan.device_name in FOUTs:
                self._fout_prefix = LL_PREFIX + chan.device_name + ':'
                self._fout_out = int(chan.propty[3:])
            elif chan.device_name == EVG_NAME:
                self._evg_out = int(chan.propty[3:])
        self._evg_prefix = LL_PREFIX + EVG_NAME + ':'
        self.channel = channel
        self._source_enums = source_enums
        init_hl_state['DevEnbl'] = 1
        init_hl_state['FOUTDevEnbl'] = 1
        init_hl_state['EVGDevEnbl'] = 1
        super().__init__(callback, init_hl_state, get_ll_state)

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
            'FOUTLos': self._fout_prefix + 'Los-Mon',
            'EVGLos': self._evg_prefix + 'Los-Mon',
            'IntlkMon': self.prefix + 'Intlk-Mon',
            'FOUTDevEnbl': self._fout_prefix + 'DevEnbl-Sts',
            'EVGDevEnbl': self._evg_prefix + 'DevEnbl-Sts',
            }
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _define_dict_for_write(self):
        map_ = {
            'DevEnbl': _partial(self._set_simple, 'DevEnbl'),
            'FOUTDevEnbl': _partial(self._set_simple, 'FOUTDevEnbl'),
            'EVGDevEnbl': _partial(self._set_simple, 'EVGDevEnbl'),
            'State': _partial(self._set_simple, 'State'),
            'Src': self._set_source,
            'Duration': self._set_duration,
            'Polarity': _partial(self._set_simple, 'Polarity'),
            'Pulses': self._set_pulses,
            'Intlk': _partial(self._set_simple, 'Intlk'),
            'Delay': self._set_delay,
            'DelayType': self._set_delay_type,
            }
        return map_

    def _define_dict_for_read(self):
        map_ = {
            'State': _partial(self._get_simple, 'State'),
            'Evt': _partial(self._process_source, 'Evt'),
            'Width': _partial(self._get_duration_pulses, 'Width'),
            'Polarity': _partial(self._get_simple, 'Polarity'),
            'Pulses': _partial(self._get_duration_pulses, 'Pulses'),
            'Delay': _partial(self._get_delay, 'Delay'),
            'Intlk': _partial(self._get_simple, 'Intlk'),
            'Src': _partial(self._process_source, 'Src'),
            'SrcTrig': _partial(self._process_source, 'SrcTrig'),
            'RFDelay': _partial(self._get_delay, 'RFDelay'),
            'FineDelay': _partial(self._get_delay, 'FineDelay'),
            'DevEnbl': _partial(self._get_status, 'DevEnbl'),
            'Network': _partial(self._get_status, 'Network'),
            'Link': _partial(self._get_status, 'Link'),
            'Los': _partial(self._get_status, 'Los'),
            'FOUTLos': _partial(self._get_status, 'FOUTLos'),
            'EVGLos': _partial(self._get_status, 'EVGLos'),
            'IntlkMon': _partial(self._get_status, 'IntlkMon'),
            'FOUTDevEnbl': _partial(self._get_status, 'FOUTDevEnbl'),
            'EVGDevEnbl': _partial(self._get_status, 'EVGDevEnbl'),
            }
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _get_status(self, prop, is_sp, value=None):
        dic_ = dict()
        dic_['DevEnbl'] = self._get_from_pvs(is_sp, 'DevEnbl')
        dic_['FOUTDevEnbl'] = self._get_from_pvs(is_sp, 'FOUTDevEnbl')
        dic_['EVGDevEnbl'] = self._get_from_pvs(is_sp, 'EVGDevEnbl')
        dic_['Network'] = self._get_from_pvs(is_sp, 'Network')
        dic_['IntlkMon'] = self._get_from_pvs(is_sp, 'IntlkMon', def_val=1)
        dic_['Link'] = self._get_from_pvs(is_sp, 'Link')
        dic_['Los'] = self._get_from_pvs(is_sp, 'Los', def_val=None)
        dic_['FOUTLos'] = self._get_from_pvs(is_sp, 'FOUTLos', def_val=None)
        dic_['EVGLos'] = self._get_from_pvs(is_sp, 'EVGLos', def_val=None)
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
        if dic_['FOUTLos'] is not None:
            num = self._fout_out
            if num >= 0 and (dic_['FOUTLos'] >> num) % 2:
                status |= (1 << 8)
        if dic_['EVGLos'] is not None:
            num = self._evg_out
            if num >= 0 and (dic_['EVGLos'] >> num) % 2:
                status |= (1 << 9)
        return {'Status': status}

    def _get_delay(self, prop, is_sp, value=None):
        dic_ = dict()
        dic_['Delay'] = self._get_from_pvs(is_sp, 'Delay')
        dic_['RFDelay'] = self._get_from_pvs(is_sp, 'RFDelay')
        dic_['FineDelay'] = self._get_from_pvs(is_sp, 'FineDelay')
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
        dic_ = {'Delay': delay1}
        # Initialization issue
        if self._initializing:
            del_type = self._my_state_sp.get('RFDelay', 0)
        else:
            del_type = self._get_from_pvs(True, 'RFDelay')
        if del_type != 31:
            value -= delay1 * self._base_del
            delay2 = value // self._rf_del
            value -= delay2 * self._rf_del
            delay3 = round(value / _FDEL)
            dic_['RFDelay'] = delay2
            dic_['FineDelay'] = delay3
        return dic_

    def _set_delay_type(self, value):
        if value:
            return {'RFDelay': 31, 'FineDelay': 0}
        else:
            return {'RFDelay': 0}

    def _process_source(self, prop, is_sp, value=None):
        dic_ = dict()
        dic_['SrcTrig'] = self._get_from_pvs(is_sp, 'SrcTrig', def_val=30)
        dic_['Src'] = self._get_from_pvs(is_sp, 'Src', def_val=None)
        dic_['Evt'] = self._get_from_pvs(is_sp, 'Evt')
        if value is not None:
            dic_[prop] = value

        ret = self._process_src_trig(dic_['SrcTrig'], is_sp)
        if ret is not None:
            return ret
        ret = self._process_src(dic_['Src'], is_sp)
        if ret is not None:
            return ret
        return self._process_evt(dic_['Evt'], is_sp)

    def _process_evt(self, evt, is_sp):
        src_len = len(self._source_enums) if not is_sp else 0
        event = _cstime.events_ll_tmp.format(evt)
        if event not in _cstime.events_ll2hl_map:
            return {'Src': src_len}
        elif _cstime.events_ll2hl_map[event] not in self._source_enums:
            return {'Src': src_len}
        else:
            ev_num = self._source_enums.index(_cstime.events_ll2hl_map[event])
            return {'Src': ev_num}

    def _process_src_trig(self, src_trig, is_sp):
        src_len = len(self._source_enums) if not is_sp else 0
        if src_trig != self._internal_trigger:
            return {'Src': src_len}  # invalid

    def _process_src(self, src, is_sp):
        src_len = len(self._source_enums) if not is_sp else 0
        source = _cstime.triggers_src_ll[src]
        if not source:
            return {'Src': src_len}  # invalid
        elif source.startswith(('Dsbl', 'Clock')):
            return {'Src': self._source_enums.index(source)}

    def _set_source(self, value):
        pname = self._source_enums[value]
        if pname.startswith(('Clock', 'Dsbl')):
            n = _cstime.triggers_src_ll.index(pname)
            dic_ = {'Src': n}
        else:
            n = _cstime.triggers_src_ll.index('Trigger')
            evt = int(_cstime.events_hl2ll_map[pname][-2:])
            dic_ = {'Src': n, 'Evt': evt}
        if 'SrcTrig' in self._dict_convert_prop2pv.keys():
            dic_['SrcTrig'] = self._internal_trigger
        return dic_

    def _get_duration_pulses(self, prop, is_sp, value=None):
        dic_ = dict()
        dic_['Pulses'] = self._get_from_pvs(is_sp, 'Pulses', def_val=1)
        dic_['Width'] = self._get_from_pvs(is_sp, 'Width', def_val=1)
        if value is not None:
            dic_[prop] = value
        return {
            'Duration': 2*dic_['Width']*self._base_del*dic_['Pulses']*1e3,
            'Pulses': dic_['Pulses'],
            }

    def _set_duration(self, value):
        value *= 1e-3  # ms
        # Initialization issue
        if self._initializing:
            pul = self._my_state_sp.get('Pulses', 1)
        else:
            pul = self._get_from_pvs(True, 'Pulses', def_val=1)
        n = int(round(value / self._base_del / pul / 2))
        n = n if n >= 1 else 1
        return {'Width': n}

    def _set_pulses(self, value):
        if value < 1:
            return dict()
        # Initialization issue
        if self._initializing:
            old_pul = self._my_state_sp.get('Pulses', 1)
            old_wid = self._my_state_sp.get('Width', 1)
        else:
            old_pul = self._get_from_pvs(True, 'Pulses', def_val=1)
            old_wid = self._get_from_pvs(True, 'Width', def_val=1)
        return {
            'Pulses': int(value),
            'Width': int(round(old_wid*old_pul/value))
            }


class _EVROTP(_EVROUT):
    _REMOVE_PROPS = {'RFDelay', 'FineDelay', 'Src', 'SrcTrig', 'Intlk'}

    def _define_num_int(self, num):
        return num

    def _get_delay(self, prop, is_sp, val=None):
        if val is None:
            val = self._get_from_pvs(is_sp, 'Delay')
        return {'Delay': val * self._base_del * 1e6}

    def _set_delay(self, value):
        value *= _DELAY_UNIT_CONV
        delay1 = int(value // self._base_del)
        return {'Delay': delay1}

    def _set_delay_type(self, value):
        return dict()

    def _process_source(self, prop, is_sp, val=None):
        if val is None:
            val = self._get_from_pvs(is_sp, 'Evt')
        return self._process_evt(val, is_sp)

    def _set_source(self, value):
        pname = self._source_enums[value]
        dic_ = dict()
        if not pname.startswith(('Clock', 'Dsbl')):
            dic_['Evt'] = int(_cstime.events_hl2ll_map[pname][-2:])
        return dic_


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

    def _get_delay(self, prop, is_sp, value=None):
        return _EVROTP._get_delay(self, prop, value)

    def _set_delay(self, value):
        return _EVROTP._set_delay(self, value)

    def _set_delay_type(self, value):
        return _EVROTP._set_delay_type(self, value)

    def _process_source(self, prop, is_sp, value=None):
        dic_ = dict()
        dic_['Src'] = self._get_from_pvs(is_sp, 'Src')
        dic_['Evt'] = self._get_from_pvs(is_sp, 'Evt')
        if value is not None:
            dic_[prop] = value

        ret = self._process_src(dic_['Src'], is_sp)
        if ret is not None:
            return ret
        return self._process_evt(dic_['Evt'], is_sp)


class _AFCFMC(_AFCCRT):

    def _INTLB_formatter(self):
        fmc = (self._internal_trigger // 5) + 1
        ch = (self._internal_trigger % 5) + 1
        return 'FMC{0:d}CH{1:d}'.format(fmc, ch)


def get_ll_trigger_object(
            channel, callback, init_hl_state, get_ll_state, source_enums
            ):
    """Get Low Level trigger objects."""
    LL_TRIGGER_CLASSES = {
        ('EVR', 'OUT'): _EVROUT,
        ('EVR', 'OTP'): _EVROTP,
        ('EVE', 'OUT'): _EVEOUT,
        ('AFC', 'CRT'): _AFCCRT,
        ('AFC', 'FMC'): _AFCFMC,
        }
    chan = _PVName(channel)
    match = _LLTimeSearch.ll_rgx.findall(chan.propty)
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
    return cls_(
        channel, int(conn_num), callback,
        init_hl_state, source_enums, get_ll_state)
