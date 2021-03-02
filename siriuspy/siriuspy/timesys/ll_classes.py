"""Define the low level classes which will connect to Timing Devices IOC."""

import re as _re
from functools import partial as _partial
import logging as _log
from threading import Thread as _ThreadBase
from epics.ca import CASeverityException as _CASeverityException

from ..util import update_bit as _update_bit, get_bit as _get_bit
from ..epics import CONNECTION_TIMEOUT as _CONN_TIMEOUT, PV as _PV
from ..envars import VACA_PREFIX as LL_PREFIX
from ..namesys import SiriusPVName as _PVName
from ..search import LLTimeSearch as _LLSearch, HLTimeSearch as _HLSearch
from ..callbacks import Callback as _Callback
from ..devices import Event as _Event
from ..thread import RepeaterThread as _Timer

from .csdev import Const as _TIConst


_RFFREQ = _TIConst.RF_FREQUENCY
_RFDIV = _TIConst.RF_DIVISION
_ACFREQ = _TIConst.AC_FREQUENCY
_US2SEC = 1e-6
_FDEL = _TIConst.FINE_DELAY / _US2SEC


class _Thread(_ThreadBase):

    def __init__(self, **kwargs):
        if 'daemon' not in kwargs:
            kwargs['daemon'] = True
        super().__init__(**kwargs)


class _BaseLL(_Callback):

    def __init__(self, channel, prefix):
        """Initialize the Low Level object.

        callback is the callable to be called each time a low level PV changes
        its value.
        """
        super().__init__()
        self._initialized = False
        self.channel = _PVName(channel)
        self.prefix = prefix
        self._dict_functs_for_write = self._define_dict_for_write()
        self._dict_functs_for_update = self._define_dict_for_update()
        self._dict_functs_for_read = self._define_dict_for_read()
        self._dict_convert_prop2pv = self._define_convertion_prop2pv()
        self._dict_convert_pv2prop = {
            val: key for key, val in self._dict_convert_prop2pv.items()}
        self._config_ok_values = dict()
        self._base_freq = _RFFREQ / _RFDIV

        self._writepvs = dict()
        self._readpvs = dict()
        self._locked = False
        self._lock_threads_dict = dict()

        evts = _HLSearch.get_hl_events()
        evts.pop('Dsbl')
        evts.pop('PsMtn')
        self._events = {evt: _Event(evt) for evt in evts}

        evg_name = _LLSearch.get_evg_name()
        self._base_freq_pv = _PV(
            LL_PREFIX + evg_name + ':FPGAClk-Cte')
        self._update_base_freq()
        self._base_freq_pv.add_callback(self._update_base_freq)

        for prop, pvname in self._dict_convert_prop2pv.items():
            pvnamerb = pvnamesp = None
            if not _PVName.is_write_pv(pvname):
                pvnamerb = pvname
                pvnamesp = _PVName.from_rb2sp(pvname)
            elif _PVName.is_cmd_pv(pvname):  # -Cmd is different!!
                self._writepvs[prop] = _PV(pvname)

            if pvnamerb is not None:
                pvo = _PV(pvnamerb)
                pvo.add_callback(self._on_change_readpv)
                pvo.connection_callbacks.append(self._on_connection)
                self._readpvs[prop] = pvo
            if pvnamesp != pvnamerb and not prop.endswith('DevEnbl'):
                pvo = _PV(pvnamesp)
                pvo.initialized = False
                pvo.add_callback(self._on_change_writepv)
                pvo.connection_callbacks.append(self._on_connection_writepv)
                self._writepvs[prop] = pvo
        self._initialized = True

    @property
    def connected(self):
        """."""
        pvs = list(self._readpvs.values()) + list(self._writepvs.values())
        pvs += [self._base_freq_pv, ]
        pvs += list(self._events.values())
        conn = True
        for pv in pvs:
            conn &= pv.connected
            if not pv.connected:
                _log.debug('NOT CONN: {0:s}'.format(pv.pvname))
        return conn

    def wait_for_connection(self, timeout=None):
        """."""
        pvs = list(self._readpvs.values()) + list(self._writepvs.values())
        pvs += [self._base_freq_pv, ]
        pvs += list(self._events.values())
        for pv in pvs:
            if not pv.wait_for_connection(timeout=timeout):
                _log.info(pv.pvname + ' not connected.')
                return False
        return True

    @property
    def locked(self):
        """."""
        return self._locked

    @locked.setter
    def locked(self, value):
        """."""
        self._set_locked(value)

    def write(self, prop, value):
        """Set property values in low level IOCS.

        Function called by classes that control high level PVs to transform
        the high level values into low level properties and set the low level
        IOCs accordingly.
        """
        fun = self._dict_functs_for_write.get(prop)
        if fun is None:
            _log.warning('No write function defined')
            return False
        dic = fun(value)  # dic must be None for -Cmd PVs
        if dic is None:
            return True
        elif isinstance(dic, dict) and not dic:
            _log.warning('Function return value is empty')
            return False  # dic is empty in case write was not successfull
        for prop, val in dic.items():
            self.write_ll(prop, val)
        return True

    def write_ll(self, prop, value):
        self._config_ok_values[prop] = value
        pv = self._writepvs.get(prop)
        if pv is None:
            return
        # I decided not to wait put to finish when writing on LL PVs
        # to make the high level IOC as fast as possible.
        # To guarantee that the desired value will be written on the
        # rather slow LL IOC, I put the setpoint in the verification
        # queue.
        self._put_on_pv(pv, value, wait=False)
        pvname = self._dict_convert_prop2pv[prop]
        self._start_lock_thread(pvname)

    def read(self, prop, is_sp=False):
        """Read HL properties from LL IOCs and return the value."""
        fun = self._dict_functs_for_read[prop]
        if fun is None:
            return None
        dic_ = fun(is_sp)
        if dic_ is None or prop not in dic_:
            return None
        return dic_[prop]

    def _set_locked(self, value):
        self._locked = bool(value)
        self.run_callbacks(self.channel, 'LowLvlLock', value, is_sp=False)
        if not self._locked:
            return
        for prop, val in self._config_ok_values.items():
            if val is None:
                continue
            self.write_ll(prop, val)

    def _update_base_freq(self, **kwargs):
        self._base_freq = self._base_freq_pv.get(
            timeout=_CONN_TIMEOUT) or self._base_freq
        self.base_del = 1 / self._base_freq / _US2SEC
        self._rf_del = self.base_del / 5

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

    def _define_dict_for_update(self):
        """Define a dictionary of functions to convert LL to HL.

        Each function converts the readback values of Low Level properties into
        values of High Level properties and send them to the High Level classes
        for update of the readback PVs.
        It is called by the on_change_pvs_rb and calls the callback function.
        """
        return dict()

    def _define_dict_for_read(self):
        """Define a dictionary of functions to read HL properties from LL PVs.

        The dictionary defined in this function is called by read method.
        """
        return dict()

    def _get_from_pvs(self, is_sp, ll_prop, def_val=None):
        pv = self._writepvs[ll_prop] if is_sp else self._readpvs[ll_prop]
        if not pv.connected:
            return def_val
        val = pv.get(timeout=_CONN_TIMEOUT)
        return def_val if val is None else val

    def _start_lock_thread(self, pvname):
        # I have loop here to guarantee that the hardware will go to the
        # desired state.
        # I have to do this because of a problem on the LL IOCs triggered by
        # write commands which do not wait for the put operation to be
        # completed, which is the case for the default behavior of pyepics,
        # pydm, cs-studio...
        # This problem happens when one try to set different properties of the
        # LL IOCs, or the same property twice, in a time interval shorter than
        # the one it takes for LL IOC complete writing on the hardware (~60ms).
        maxatt = 100
        interv = 1 / 10  # I wait a little bit to reduce CPU load
        timer = self._lock_threads_dict.get(pvname)
        if timer is None or not timer.is_alive():
            timer = _Timer(
                interv, self._do_lock, args=(pvname, ), niter=maxatt)
            self._lock_threads_dict[pvname] = timer
            timer.start()
        else:
            timer.reset()

    def _do_lock(self, pvname):
        timer = self._lock_threads_dict[pvname]

        prop = self._dict_convert_pv2prop[pvname]
        my_val = self._config_ok_values.get(prop)
        pvo = self._writepvs.get(prop)
        if my_val is None or pvo is None:
            timer.stop()
        value = self._get_from_pvs(False, prop)
        if value is None:
            return
        if pvo.initialized and my_val == value:
            timer.stop()
        self._put_on_pv(pvo, my_val)

        if timer.cur_iter == timer.niters-1:
            _log.error(
                f'Could not set PV: {pvo.pvname:s} --> '
                f'my_val: {str(my_val):s} val: {str(value):s} '
                f'put_comp: {str(pvo.put_complete):s} '
                f'initia: {str(pvo.initialized):s} '
                f'conn: {str(pvo.connected):s}')

    def _put_on_pv(self, pvo, value, wait=False):
        if pvo.connected and pvo.put_complete is not False:
            # wait=True is too slow for the LL Timing IOCs. It is better not
            # to use it.
            try:
                pvo.put(value, use_complete=True, wait=wait)
                pvo.initialized = True
            except _CASeverityException:
                _log.error('NO Write Permission to {0:s}'.format(pvo.pvname))

    def _on_change_writepv(self, pvname, value, **kwargs):
        # -Cmd PVs do not have a state associated to them
        if value is None or _PVName.is_cmd_pv(pvname):
            return
        _Thread(target=self._on_change_pv_thread, args=(pvname, value)).start()

    def _on_change_readpv(self, pvname, value, **kwargs):
        if value is None:
            return
        if self._locked:
            self._start_lock_thread(pvname)
        _Thread(target=self._on_change_pv_thread, args=(pvname, value)).start()

        # at initialization load _config_ok_values
        prop = self._dict_convert_pv2prop.get(pvname)
        cond = prop is not None
        cond &= self._config_ok_values.get(prop) is None
        cond &= _PVName.is_rb_pv(pvname)
        cond &= not self._locked
        if cond:
            self._config_ok_values[prop] = value

    def _on_change_pv_thread(self, pvname, value, **kwargs):
        if not self._initialized:
            return

        pvn = _PVName.from_sp2rb(pvname)
        is_sp = _PVName.is_sp_pv(pvname)
        fun = self._dict_functs_for_update[self._dict_convert_pv2prop[pvn]]
        props = fun(is_sp, value)
        for hl_prop, val in props.items():
            if val is not None:
                self.run_callbacks(self.channel, hl_prop, val, is_sp=is_sp)

    def _on_connection_writepv(self, pvname, conn, **kwargs):
        if _PVName.is_cmd_pv(pvname):  # -Cmd must not change
            return
        prop = self._dict_convert_pv2prop[_PVName.from_sp2rb(pvname)]
        self._writepvs[prop].initialized = False  # not self._locked
        self._on_connection(pvname, conn)

    def _on_connection(self, pvname, conn, **kwargs):
        if not self._initialized:
            return
        self.run_callbacks(self.channel, None, None)

    def _set_simple(self, prop, value):
        """Simple setting of Low Level IOC PVs.

        Function called by write when no conversion is needed between
        high and low level properties.
        """
        if value is None:
            return dict()
        return {prop: value}

    def _get_simple(self, prop, is_sp, val=None, hl_prop=None):
        hl_prop = prop if hl_prop is None else hl_prop
        if val is None:
            val = self._get_from_pvs(is_sp, prop)
        if val is None:
            return dict()
        return {hl_prop: val}


class _EVROUT(_BaseLL):
    _REMOVE_PROPS = {}

    def __init__(self, channel, source_enums):
        fout_chan = _LLSearch.get_fout_channel(channel)
        self._fout_out = int(fout_chan.propty[3:])
        evg_chan = _LLSearch.get_evg_channel(channel)
        self._evg_out = int(evg_chan.propty[3:])
        self._source_enums = source_enums
        self._duration = None  # I keep this to avoid rounding errors

        prefix = LL_PREFIX + _PVName(channel).device_name + ':'
        super().__init__(channel, prefix)
        # self._config_ok_values['DevEnbl'] = 1
        # self._config_ok_values['FoutDevEnbl'] = 1
        # self._config_ok_values['EVGDevEnbl'] = 1
        if self.channel.propty.startswith('OUT'):
            intrg = _LLSearch.get_channel_internal_trigger_pvname(self.channel)
            intrg = int(intrg.propty[-2:])  # get internal trigger number
            self._config_ok_values['SrcTrig'] = intrg
            # Stop using FineDelay and RF Delay to ease consistency:
            self._config_ok_values['FineDelay'] = 0
            self._config_ok_values['RFDelay'] = 0

    def write(self, prop, value):
        # keep this info for recalculating Width whenever necessary
        if prop == 'Duration':
            self._duration = value
        return super().write(prop, value)

    def _define_convertion_prop2pv(self):
        intlb = _LLSearch.get_channel_internal_trigger_pvname(self.channel)
        outlb = _LLSearch.get_channel_output_port_pvname(self.channel)
        intlb = intlb.propty
        outlb = outlb.propty

        evg_chan = _LLSearch.get_evg_channel(self.channel)
        _evg_prefix = LL_PREFIX + evg_chan.device_name + ':'
        fout_chan = _LLSearch.get_fout_channel(self.channel)
        _fout_prefix = LL_PREFIX + fout_chan.device_name + ':'
        map_ = {
            'State': self.prefix + intlb + 'State-Sts',
            'Evt': self.prefix + intlb + 'Evt-RB',
            'Width': self.prefix + intlb + 'WidthRaw-RB',
            'Polarity': self.prefix + intlb + 'Polarity-Sts',
            'NrPulses': self.prefix + intlb + 'NrPulses-RB',
            'Delay': self.prefix + intlb + 'DelayRaw-RB',
            'Src': self.prefix + outlb + 'Src-Sts',
            'SrcTrig': self.prefix + outlb + 'SrcTrig-RB',
            'RFDelay': self.prefix + outlb + 'RFDelayRaw-RB',
            'FineDelay': self.prefix + outlb + 'FineDelayRaw-RB',
            'RFDelayType': self.prefix + outlb + 'RFDelayType-Sts',
            # connection status PVs
            'DevEnbl': self.prefix + 'DevEnbl-Sts',
            'Network': self.prefix + 'Network-Mon',
            'Link': self.prefix + 'LinkStatus-Mon',
            'Intlk': self.prefix + 'IntlkStatus-Mon',
            'Los': self.prefix + 'Los-Mon',
            'EVGLos': _evg_prefix + 'Los-Mon',
            'FoutLos': _fout_prefix + 'Los-Mon',
            'FoutDevEnbl': _fout_prefix + 'DevEnbl-Sts',
            'EVGDevEnbl': _evg_prefix + 'DevEnbl-Sts',
            }
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _define_dict_for_write(self):
        map_ = {
            # 'DevEnbl': _partial(self._set_simple, 'DevEnbl'),
            # 'EVGDevEnbl': _partial(self._set_simple, 'EVGDevEnbl'),
            # 'FoutDevEnbl': _partial(self._set_simple, 'FoutDevEnbl'),
            'State': _partial(self._set_simple, 'State'),
            'Src': self._set_source,
            'Duration': self._set_duration,
            'Polarity': _partial(self._set_simple, 'Polarity'),
            'NrPulses': self._set_nrpulses,
            'Delay': _partial(self._set_delay, raw=False),
            'DelayRaw': _partial(self._set_delay, raw=True),
            'RFDelayType': _partial(self._set_simple, 'RFDelayType'),
            'LowLvlLock': self._set_locked,
            }
        return map_

    def _define_dict_for_update(self):
        map_ = {
            'State': _partial(self._get_simple, 'State'),
            'Evt': _partial(self._process_source, 'Evt'),
            'Width': _partial(self._get_duration_pulses, 'Width'),
            'Polarity': _partial(self._get_simple, 'Polarity'),
            'NrPulses': _partial(self._get_duration_pulses, 'NrPulses'),
            'Delay': _partial(self._get_delay, 'Delay'),
            'Src': _partial(self._process_source, 'Src'),
            'SrcTrig': _partial(self._process_source, 'SrcTrig'),
            'RFDelay': _partial(self._get_delay, 'RFDelay'),
            'FineDelay': _partial(self._get_delay, 'FineDelay'),
            'RFDelayType': _partial(self._get_simple, 'RFDelayType'),
            'DevEnbl': _partial(self._get_status, 'DevEnbl'),
            'Network': _partial(self._get_status, 'Network'),
            'Link': _partial(self._get_status, 'Link'),
            'Intlk': _partial(self._get_status, 'Intlk'),
            'Los': _partial(self._get_status, 'Los'),
            'EVGLos': _partial(self._get_status, 'EVGLos'),
            'FoutLos': _partial(self._get_status, 'FoutLos'),
            'EVGDevEnbl': _partial(self._get_status, 'EVGDevEnbl'),
            'FoutDevEnbl': _partial(self._get_status, 'FoutDevEnbl'),
            }
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _define_dict_for_read(self):
        map_ = {
            'State': _partial(self._get_simple, 'State'),
            'Duration': _partial(self._get_duration_pulses, ''),
            'Polarity': _partial(self._get_simple, 'Polarity'),
            'NrPulses': _partial(self._get_duration_pulses, ''),
            'Delay': _partial(self._get_delay, 'Delay'),
            'DelayRaw': _partial(self._get_delay, 'Delay'),
            'TotalDelay': _partial(self._get_delay, 'Delay'),
            'TotalDelayRaw': _partial(self._get_delay, 'Delay'),
            'Src': _partial(self._process_source, ''),
            'RFDelayType': _partial(self._get_simple, 'RFDelayType'),
            'Status': _partial(self._get_status, ''),
            'InInjTable': _partial(self._get_status, ''),
            'LowLvlLock': lambda is_sp: {'LowLvlLock': self.locked},
            }
        return map_

    def _get_status(self, prop, is_sp, value=None):
        dic_ = dict()
        dic_['DevEnbl'] = self._get_from_pvs(is_sp, 'DevEnbl', def_val=0)
        dic_['EVGDevEnbl'] = self._get_from_pvs(is_sp, 'EVGDevEnbl', def_val=0)
        dic_['FoutDevEnbl'] = self._get_from_pvs(
            is_sp, 'FoutDevEnbl', def_val=0)
        dic_['Network'] = self._get_from_pvs(False, 'Network', def_val=0)
        dic_['Link'] = self._get_from_pvs(False, 'Link', def_val=0)
        dic_['PVsConn'] = self.connected
        dic_['PVsConn'] &= all([x.connected for x in self._events.values()])

        dic_['Intlk'] = 0
        if 'Intlk' not in self._REMOVE_PROPS:
            dic_['Intlk'] = self._get_from_pvs(False, 'Intlk', def_val=1)

        prt_num = 0
        dic_['Los'] = 0b00000000
        if 'Los' not in self._REMOVE_PROPS:
            prt_num = int(self.channel[-1])  # get OUT number for EVR
            dic_['Los'] = self._get_from_pvs(
                False, 'Los', def_val=0b11111111)
        dic_['EVGLos'] = self._get_from_pvs(
            False, 'EVGLos', def_val=0b11111111)
        dic_['FoutLos'] = self._get_from_pvs(
            False, 'FoutLos', def_val=0b11111111)

        if value is not None:
            dic_[prop] = value

        dic_['Los'] = _get_bit(dic_['Los'], prt_num)
        dic_['EVGLos'] = _get_bit(dic_['EVGLos'], self._evg_out)
        dic_['FoutLos'] = _get_bit(dic_['FoutLos'], self._fout_out)

        prob, bit = 0, 0
        prob, bit = _update_bit(prob, bit, not dic_['PVsConn']), bit+1
        prob, bit = _update_bit(prob, bit, not dic_['DevEnbl']), bit+1
        prob, bit = _update_bit(prob, bit, not dic_['FoutDevEnbl']), bit+1
        prob, bit = _update_bit(prob, bit, not dic_['EVGDevEnbl']), bit+1
        prob, bit = _update_bit(prob, bit, not dic_['Network']), bit+1
        prob, bit = _update_bit(prob, bit, not dic_['Link']), bit+1
        prob, bit = _update_bit(prob, bit, dic_['Los']), bit+1
        prob, bit = _update_bit(prob, bit, dic_['FoutLos']), bit+1
        prob, bit = _update_bit(prob, bit, dic_['EVGLos']), bit+1
        prob, bit = _update_bit(prob, bit, dic_['Intlk']), bit+1

        dic = {'Status': prob}
        dic.update(self._get_in_inj_table())
        return dic

    def _get_in_inj_table(self):
        src = self._process_source('', False).get('Src')
        if src is None:
            return dict()
        src_str = self._source_enums[src]
        ininj = False
        if src_str in self._events:
            ininj = self._events[src_str].is_in_inj_table
        ininj &= self._get_simple('State', False).get('State', False)
        return {'InInjTable': int(ininj)}

    def _get_delay(self, prop, is_sp, value=None):
        dic_ = dict()
        dic_['Delay'] = self._get_from_pvs(is_sp, 'Delay')
        dic_['RFDelay'] = self._get_from_pvs(is_sp, 'RFDelay', def_val=0)
        dic_['FineDelay'] = self._get_from_pvs(is_sp, 'FineDelay', def_val=0)
        dic_['RFDelayType'] = self._get_from_pvs(
            is_sp, 'RFDelayType', def_val=0)
        if value is not None:
            dic_[prop] = value
        if dic_['Delay'] is None:
            return dict()
        delay = dic_['Delay']*self.base_del + dic_['FineDelay']*_FDEL
        if not dic_['RFDelayType']:
            delay += dic_['RFDelay']*self._rf_del
        dic = {'Delay': delay, 'DelayRaw': dic_['Delay']}
        if not is_sp:
            dic = self._get_total_delay(dic)
        return dic

    def _get_total_delay(self, dic):
        src = self._process_source('', False).get('Src')
        if src is None:
            return dic
        src_str = self._source_enums[src]
        evt_del = 0
        if src_str in self._events:
            evt = self._events[src_str]
            evt_del = evt.delay_raw if evt.is_in_inj_table else 0
        dic['TotalDelayRaw'] = dic['DelayRaw'] + evt_del
        dic['TotalDelay'] = dic['Delay'] + evt_del*self.base_del
        return dic

    def _set_delay(self, value, raw=False):
        dic_ = {'RFDelay': 0, 'FineDelay': 0}
        if value is None:
            return dic_
        value = value if raw else round(value / self.base_del)
        dic_['Delay'] = int(value)
        return dic_

    def _process_source(self, prop, is_sp, value=None):
        dic_ = {'SrcTrig': 30, 'Src': None, 'Evt': None}
        if 'SrcTrig' not in self._REMOVE_PROPS:
            dic_['SrcTrig'] = self._get_from_pvs(is_sp, 'SrcTrig')
        if 'Src' not in self._REMOVE_PROPS:
            dic_['Src'] = self._get_from_pvs(is_sp, 'Src')
        if 'Evt' not in self._REMOVE_PROPS:
            dic_['Evt'] = self._get_from_pvs(is_sp, 'Evt')
        if value is not None:
            dic_[prop] = value

        if any(map(lambda x: x is None, dic_.values())):
            return dict()

        ret = self._process_src_trig(dic_['SrcTrig'], is_sp)
        if ret is not None:
            return ret
        ret = self._process_src(dic_['Src'], is_sp)
        if ret is not None:
            return ret
        return self._process_evt(dic_['Evt'], is_sp)

    def _process_evt(self, evt, _):
        invalid = len(self._source_enums)-1  # Invalid option
        if evt not in _TIConst.EvtLL:
            return {'Src': invalid}
        evt_st = _TIConst.EvtLL._fields[_TIConst.EvtLL.index(evt)]
        if evt_st not in _TIConst.EvtLL2HLMap or \
                _TIConst.EvtLL2HLMap[evt_st] not in self._source_enums:
            return {'Src': invalid}
        else:
            ev_num = self._source_enums.index(_TIConst.EvtLL2HLMap[evt_st])
            return {'Src': ev_num}

    def _process_src_trig(self, src_trig, _):
        invalid = len(self._source_enums)-1  # Invalid option
        intrg = _LLSearch.get_channel_internal_trigger_pvname(self.channel)
        intrg = int(intrg.propty[-2:])  # get internal trigger number for EVR
        if src_trig != intrg:
            return {'Src': invalid}

    def _process_src(self, src, _):
        invalid = len(self._source_enums)-1  # Invalid option
        if src is None:
            return {'Src': invalid}

        # BUG: I noticed that differently from the EVR and EVE IOCs,
        # the AMCFPGAEVR do not have a 'Dsbl' as first option of the enums
        # list. So I have to create this offset to fix this...
        offset = 0
        if self.channel.dev.startswith('AMCFPGAEVR'):
            offset = 1
        try:
            source = _TIConst.TrigSrcLL._fields[src+offset]
        except IndexError:
            source = ''
        if not source:
            return {'Src': invalid}
        elif source.startswith(('Dsbl', 'Clock')):
            return {'Src': self._source_enums.index(source)}

    def _set_source(self, value):
        if value is None:
            return dict()
        # BUG: I noticed that differently from the EVR and EVE IOCs,
        # the AMCFPGAEVR do not have a 'Dsbl' as first option of the enums
        # list. So I have to create this offset to fix this...
        offset = int(self.channel.dev.startswith('AMCFPGAEVR'))

        if value >= (len(self._source_enums)-1):
            return dict()
        pname = self._source_enums[value]
        n = _TIConst.TrigSrcLL._fields.index('Trigger')
        if pname.startswith('Dsbl'):
            dic_ = {'Src': n, 'Evt': _TIConst.EvtLL.Evt00}
        if pname.startswith('Clock'):
            n = _TIConst.TrigSrcLL._fields.index(pname)
            n -= offset
            dic_ = {'Src': n}
        else:
            n -= offset
            evt = int(_TIConst.EvtHL2LLMap[pname][-2:])
            dic_ = {'Src': n, 'Evt': evt}
        if 'SrcTrig' in self._dict_convert_prop2pv.keys():
            intrg = _LLSearch.get_channel_internal_trigger_pvname(
                self.channel)
            intrg = int(intrg[-2:])  # get internal trigger number for EVR
            dic_['SrcTrig'] = intrg
        return dic_

    def _get_duration_pulses(self, prop, is_sp, value=None):
        dic_ = dict()
        dic_['NrPulses'] = self._get_from_pvs(is_sp, 'NrPulses')
        dic_['Width'] = self._get_from_pvs(is_sp, 'Width')
        for k, v in dic_.items():
            if v == 0:  # BUG: handle cases where LL sets these value to 0
                dic_[k] = 1
        if value is not None:
            dic_[prop] = value
        if any(map(lambda x: x is None, dic_.values())):
            return dict()
        return {
            'Duration': 2*dic_['Width']*self.base_del*dic_['NrPulses'],
            'NrPulses': dic_['NrPulses'],
            }

    def _set_duration(self, value, pul=None):
        if value is None:
            return dict()
        pul = pul or self._config_ok_values.get('NrPulses')
        pul = pul or 1  # BUG: handle cases where LL sets this value to 0
        wid = value / self.base_del / pul / 2
        wid = round(wid) if wid >= 1 else 1
        return {'Width': wid}

    def _set_nrpulses(self, pul):
        if pul is None or pul < 1:
            return dict()
        pul = int(pul)
        dic = {'NrPulses': pul}

        # at initialization, try to set _duration
        if self._duration is None:
            # BUG: handle cases where LL sets these value to 0
            wid = self._config_ok_values.get('Width') or 1
            self._duration = wid * pul * 2 * self.base_del

        if self._duration is not None:
            dic.update(self._set_duration(self._duration, pul=pul))
        return dic


class _EVROTP(_EVROUT):
    _REMOVE_PROPS = {
        'RFDelay', 'FineDelay', 'Src', 'SrcTrig', 'RFDelayType', 'Los'}

    def _get_delay(self, prop, is_sp, val=None):
        if val is None:
            val = self._get_from_pvs(is_sp, 'Delay')
        if val is None:
            return dict()
        dic = {'Delay': val * self.base_del, 'DelayRaw': val}
        if not is_sp:
            dic = self._get_total_delay(dic)
        return dic

    def _set_delay(self, value, raw=False):
        return {'Delay': int(value if raw else round(value / self.base_del))}

    def _process_source(self, prop, is_sp, val=None):
        if val is None:
            val = self._get_from_pvs(is_sp, 'Evt')
        if val is None:
            return dict()
        return self._process_evt(val, is_sp)

    def _process_src(self, src, _):
        return dict()

    def _set_source(self, value):
        if value >= (len(self._source_enums)-1):
            return dict()
        pname = self._source_enums[value]
        dic_ = dict()
        reg = _re.compile('[0-9]+')
        if pname.startswith('Dsbl'):
            dic_['Evt'] = 0
        if not pname.startswith('Clock'):
            mat = reg.findall(_TIConst.EvtHL2LLMap[pname])
            dic_['Evt'] = int(mat[0])
        return dic_


class _EVEOTP(_EVROTP):
    pass


class _EVEOUT(_EVROUT):
    _REMOVE_PROPS = {'Los', }


class _AMCFPGAEVRAMC(_EVROUT):
    _REMOVE_PROPS = {
        'RFDelay', 'FineDelay', 'SrcTrig', 'RFDelayType', 'Intlk', 'Los'}

    def _get_delay(self, prop, is_sp, value=None):
        return _EVROTP._get_delay(self, prop, is_sp, value)

    def _set_delay(self, value, raw=False):
        return _EVROTP._set_delay(self, value, raw=raw)

    def _define_convertion_prop2pv(self):
        map_ = super()._define_convertion_prop2pv()
        map_['Network'] = map_['Network'].replace('Network', 'RefClkLocked')
        return map_

    def _process_source(self, prop, is_sp, value=None):
        dic_ = dict()
        dic_['Src'] = self._get_from_pvs(is_sp, 'Src')
        dic_['Evt'] = self._get_from_pvs(is_sp, 'Evt')
        if value is not None:
            dic_[prop] = value
        if any(map(lambda x: x is None, dic_.values())):
            return dict()
        ret = self._process_src(dic_['Src'], is_sp)
        if ret is not None:
            return ret
        return self._process_evt(dic_['Evt'], is_sp)


class _AMCFPGAEVRFMC(_AMCFPGAEVRAMC):
    pass


def get_ll_trigger(channel, source_enums):
    """Get Low Level trigger objects."""
    LL_TRIGGER_CLASSES = {
        ('EVR', 'OUT'): _EVROUT,
        ('EVR', 'OTP'): _EVROTP,
        ('EVE', 'OTP'): _EVEOTP,
        ('EVE', 'OUT'): _EVEOUT,
        ('AMCFPGAEVR', 'CRT'): _AMCFPGAEVRAMC,
        ('AMCFPGAEVR', 'FMC'): _AMCFPGAEVRFMC,
        }
    chan = _PVName(channel)
    key = (chan.dev, chan.propty[:3])
    cls_ = LL_TRIGGER_CLASSES.get(key)
    if not cls_:
        raise Exception(
            'Low Level Trigger Class not defined for device ' +
            'type '+key[0]+' and connection type '+key[1]+'.')
    return cls_(channel, source_enums)
