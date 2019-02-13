"""Define the low level classes which will connect to Timing Devices IOC."""
import time as _time
import re as _re
from functools import partial as _partial, reduce as _reduce
from operator import and_ as _and_
import logging as _log
import epics as _epics
from siriuspy.util import update_bit as _update_bit, get_bit as _get_bit
from siriuspy.thread import QueueThread as _QueueThread
from siriuspy.epics import connection_timeout as _conn_timeout
from siriuspy.envars import vaca_prefix as LL_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.csdevice import timesys as _cstime
from siriuspy.search import LLTimeSearch as _LLTimeSearch
from .util import Base as _Base

_RFFREQ = _cstime.Const.RF_FREQUENCY
_RFDIV = _cstime.Const.RF_DIVISION
_ACFREQ = _cstime.Const.AC_FREQUENCY
_FDEL = _cstime.Const.FINE_DELAY
_DELAY_UNIT_CONV = 1e-6


def get_evg_name():
    return _LLTimeSearch.get_device_names({'dev': 'EVG'})[0]


class _BaseLL(_Base):

    def __init__(self, channel, prefix):
        """Initialize the Low Level object.

        callback is the callable to be called each time a low level PV changes
        its value.
        """
        super().__init__()
        self.channel = _PVName(channel)
        self.prefix = prefix
        self._dict_functs_for_write = self._define_dict_for_write()
        self._dict_functs_for_update = self._define_dict_for_update()
        self._dict_functs_for_read = self._define_dict_for_read()
        self._dict_convert_prop2pv = self._define_convertion_prop2pv()
        self._dict_convert_pv2prop = {
                val: key for key, val in self._dict_convert_prop2pv.items()}
        self._config_ok_values = dict()
        self._rf_freq = _RFFREQ
        self._rf_div = _RFDIV

        evg_name = get_evg_name()
        self._rf_freq_pv = _epics.PV(
            LL_PREFIX + 'AS-Glob:RF-Gen:Frequency-SP',
            connection_timeout=_conn_timeout)
        self._rf_div_pv = _epics.PV(
            LL_PREFIX + evg_name + ':RFDiv-SP',
            connection_timeout=_conn_timeout)
        self._update_base_freq()
        self._rf_freq_pv.add_callback(self._update_base_freq)
        self._rf_div_pv.add_callback(self._update_base_freq)

        self._writepvs = dict()
        self._readpvs = dict()
        self._queue = _QueueThread()
        self._queue.start()
        self._locked = False

        _log.info(self.channel+': Creating PVs.')
        for prop, pvname in self._dict_convert_prop2pv.items():
            pvnamerb = pvnamesp = None
            if not self._iswritepv(pvname):
                pvnamerb = pvname
                pvnamesp = self._fromrb2sp(pvname)
            elif self._iscmdpv(pvname):  # -Cmd is different!!
                self._writepvs[prop] = _epics.PV(
                                pvname, connection_timeout=_conn_timeout)

            if pvnamerb is not None:
                self._readpvs[prop] = _epics.PV(
                    pvnamerb,
                    callback=self._on_change_readpv,
                    connection_timeout=_conn_timeout)
            if pvnamesp != pvnamerb:
                self._writepvs[prop] = _epics.PV(
                    pvnamesp,
                    callback=self._on_change_writepv,
                    connection_timeout=_conn_timeout)
                self._writepvs[prop]._initialized = False
                self._writepvs[prop].connection_callbacks.append(
                                            self._on_connection_writepv)

    @property
    def connected(self):
        pvs = list(self._readpvs.values()) + list(self._writepvs.values())
        return _reduce(_and_, map(lambda x: x.connected, pvs))

    @property
    def locked(self):
        return self._locked

    @locked.setter
    def locked(self, value):
        self._locked = bool(value)

    def write(self, prop, value):
        """Set property values in low level IOCS.

        Function called by classes that control high level PVs to transform
        the high level values into low level properties and set the low level
        IOCs accordingly.
        """
        fun = self._dict_functs_for_write.get(prop)
        if fun is None:
            return False
        dic = fun(value)  # dic must be None for -Cmd PVs
        if dic is None:
            return True
        elif isinstance(dic, dict) and not dic:
            return False  # dic is empty in case write was not successfull
        self._config_ok_values.update(dic)
        for prop, val in dic.items():
            pv = self._writepvs.get(prop)
            if pv is None:
                continue
            # I decided not to wait put to finish when writing on LL PVs
            # to make the high level IOC as fast as possible.
            # To guarantee that the desired value will be written on the
            # rather slow LL IOC, I put the setpoint in the verification
            # queue.
            self._put_on_pv(pv, val, wait=False)
            pvname = self._dict_convert_prop2pv[prop]
            self._queue.add_callback(self._lock_thread, pvname)
        return True

    def read(self, prop, is_sp=False):
        """Read HL properties from LL IOCs and return the value. """
        fun = self._dict_functs_for_read[prop]
        if fun is None:
            return None
        return fun(is_sp)[prop]

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

    def _get_from_pvs(self, is_sp, ll_prop, def_val=0):
        if is_sp:
            pv = self._writepvs.get(ll_prop)
        else:
            pv = self._readpvs.get(ll_prop)
        if pv is None or not pv.connected:
            return def_val
        val = pv.get(timeout=_conn_timeout)
        return def_val if val is None else val

    def _lock_thread(self, pvname, value=None):
        prop = self._dict_convert_pv2prop[pvname]
        pv = self._writepvs.get(prop)
        if pv is None:
            return
        if value is None:
            value = self._get_from_pvs(False, prop)
        my_val = self._config_ok_values.get(prop)
        if my_val is not None and (not pv._initialized or my_val != value):
            self._put_on_pv(pv, my_val)
            # I have to keep calling this function over and over again to
            # guarantee that the hardware will go to the desired state.
            # I have to do this because of a problem on the LL IOCs
            # triggered by write commands which do not wait for the put
            # operation to be completed, which is the case for the default
            # behavior of pyepics, pydm, cs-studio...
            # This problem happens when one try to set different properties
            # of the LL IOCs, or the same property twice, in a time interval
            # shorter than the one it takes for LL IOC complete the write on
            # the hardware (~60ms).
            _time.sleep(0.002)  # I wait a little bit to reduce CPU load
            self._queue.add_callback(self._lock_thread, pvname)

    def _put_on_pv(self, pv, value, wait=False):
        if pv.connected and pv.put_complete:
            # wait=True is too slow for the LL Timing IOCs. It is better not
            # to use it.
            pv.put(value, use_complete=True, wait=wait)
            pv._initialized = True

    def _on_change_writepv(self, pvname, value, **kwargs):
        # -Cmd PVs do not have a state associated to them
        if value is None or self._iscmdpv(pvname):
            return
        self._queue.add_callback(self._on_change_pv_thread, pvname, value)

    def _on_change_readpv(self, pvname, value, **kwargs):
        if value is None:
            return
        if self._locked:
            self._queue.add_callback(self._lock_thread, pvname, value)
        self._queue.add_callback(self._on_change_pv_thread, pvname, value)

        # at initialization load _config_ok_values
        prop = self._dict_convert_pv2prop.get(pvname)
        val = self._config_ok_values.get(prop)
        if prop is not None and self._isrbpv(pvname) and val is None:
            self._config_ok_values[prop] = value

    def _on_change_pv_thread(self, pvname, value, **kwargs):
        pvn = self._fromsp2rb(pvname)
        is_sp = self._issppv(pvname)
        fun = self._dict_functs_for_update[self._dict_convert_pv2prop[pvn]]
        props = fun(is_sp, value)
        for hl_prop, val in props.items():
            self.run_callbacks(self.channel, hl_prop, val, is_sp=is_sp)

    def _on_connection_writepv(self, pvname, conn, **kwargs):
        if not self._iscmdpv(pvname):  # -Cmd must not change
            self._queue.add_callback(self._on_connection_thread, pvname, conn)

    def _on_connection_thread(self, pvname, conn):
        prop = self._dict_convert_pv2prop[self._fromsp2rb(pvname)]
        self._writepvs[prop]._initialized = False

    def _set_simple(self, prop, value):
        """Simple setting of Low Level IOC PVs.

        Function called by write when no conversion is needed between
        high and low level properties.
        """
        return {prop: value}

    def _get_simple(self, prop, is_sp, val=None, hl_prop=None):
        hl_prop = prop if hl_prop is None else hl_prop
        if val is None:
            val = self._get_from_pvs(is_sp, prop)
        return {hl_prop: val}


class LLEvent(_BaseLL):
    """Define the Low Level Event Class."""

    def __init__(self, channel):
        """Initialize the instance."""
        prefix = LL_PREFIX + channel
        super().__init__(channel, prefix)

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

    def _define_dict_for_update(self):
        return {
            'Delay': self._get_delay,
            'Mode': _partial(self._get_simple, 'Mode'),
            'DelayType': _partial(self._get_simple, 'DelayType'),
            'ExtTrig': _partial(self._get_simple, 'ExtTrig'),
            }

    def _define_dict_for_read(self):
        return self._define_dict_for_update()

    def _set_delay(self, value):
        value *= _DELAY_UNIT_CONV  # us
        n = int(value // self._base_del)
        return {'Delay': n}

    def _get_delay(self, is_sp, val=None):
        if val is None:
            val = self._get_from_pvs(is_sp, 'Delay', def_val=0)
        return {'Delay': val * self._base_del * 1e6}

    def _set_ext_trig(self, value):
        pv = self._writepvs.get('ExtTrig')
        self._put_on_pv(pv, value)
        return None  # -Cmd must not return any state


class _EVROUT(_BaseLL):
    _REMOVE_PROPS = {}

    def __init__(self, channel, source_enums):
        fout_chan = _LLTimeSearch.get_fout_channel(channel)
        self._foutexist = bool(fout_chan)
        if self._foutexist:
            self._fout_out = int(fout_chan.propty[3:])
        evg_chan = _LLTimeSearch.get_evg_channel(channel)
        self._evg_out = int(evg_chan.propty[3:])
        self._source_enums = source_enums
        self._duration = None  # I keep this for avoid rounding errors

        prefix = LL_PREFIX + _PVName(channel).device_name + ':'
        super().__init__(channel, prefix)
        self._config_ok_values['DevEnbl'] = 1
        if self._foutexist:
            self._config_ok_values['FoutDevEnbl'] = 1
        self._config_ok_values['EVGDevEnbl'] = 1

    def write(self, prop, value):
        # keep this info for recalculating Width whenever necessary
        if prop == 'Duration':
            self._duration = value
        return super().write(prop, value)

    def _define_convertion_prop2pv(self):
        intlb = _LLTimeSearch.get_channel_internal_trigger_pvname(self.channel)
        outlb = _LLTimeSearch.get_channel_output_port_pvname(self.channel)
        intlb = intlb.propty
        outlb = outlb.propty

        evg_chan = _LLTimeSearch.get_evg_channel(self.channel)
        _evg_prefix = LL_PREFIX + evg_chan.device_name + ':'
        map_ = {
            'State': self.prefix + intlb + 'State-Sts',
            'Evt': self.prefix + intlb + 'Evt-RB',
            'Width': self.prefix + intlb + 'Width-RB',
            'Polarity': self.prefix + intlb + 'Polarity-Sts',
            'NrPulses': self.prefix + intlb + 'NrPulses-RB',
            'Delay': self.prefix + intlb + 'Delay-RB',
            'ByPassIntlk': self.prefix + intlb + 'ByPassIntlk-Sts',
            'Src': self.prefix + outlb + 'Src-Sts',
            'SrcTrig': self.prefix + outlb + 'SrcTrig-RB',
            'RFDelay': self.prefix + outlb + 'RFDelay-RB',
            'FineDelay': self.prefix + outlb + 'FineDelay-RB',
            'RFDelayType': self.prefix + outlb + 'RFDelayType-Sts',
            # connection status PVs
            'DevEnbl': self.prefix + 'DevEnbl-Sts',
            'Network': self.prefix + 'Network-Mon',
            'Link': self.prefix + 'Link-Mon',
            'Los': self.prefix + 'Los-Mon',
            'EVGLos': _evg_prefix + 'Los-Mon',
            'IntlkMon': self.prefix + 'Intlk-Mon',
            'EVGDevEnbl': _evg_prefix + 'DevEnbl-Sts',
            }
        if self._foutexist:
            fout_chan = _LLTimeSearch.get_fout_channel(self.channel)
            _fout_prefix = LL_PREFIX + fout_chan.device_name + ':'
            map_.update({
                'FoutLos': _fout_prefix + 'Los-Mon',
                'FoutDevEnbl': _fout_prefix + 'DevEnbl-Sts',
                })
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _define_dict_for_write(self):
        map_ = {
            'DevEnbl': _partial(self._set_simple, 'DevEnbl'),
            'EVGDevEnbl': _partial(self._set_simple, 'EVGDevEnbl'),
            'State': _partial(self._set_simple, 'State'),
            'ByPassIntlk': _partial(self._set_simple, 'ByPassIntlk'),
            'Src': self._set_source,
            'Duration': self._set_duration,
            'Polarity': _partial(self._set_simple, 'Polarity'),
            'NrPulses': self._set_nrpulses,
            'Delay': self._set_delay,
            'RFDelayType': _partial(self._set_simple, 'RFDelayType'),
            }
        if self._foutexist:
            map_.update({
                'FoutDevEnbl': _partial(self._set_simple, 'FoutDevEnbl'),
                })
        return map_

    def _define_dict_for_update(self):
        map_ = {
            'State': _partial(self._get_simple, 'State'),
            'Evt': _partial(self._process_source, 'Evt'),
            'Width': _partial(self._get_duration_pulses, 'Width'),
            'Polarity': _partial(self._get_simple, 'Polarity'),
            'NrPulses': _partial(self._get_duration_pulses, 'NrPulses'),
            'ByPassIntlk': _partial(self._get_simple, 'ByPassIntlk'),
            'Delay': _partial(self._get_delay, 'Delay'),
            'Src': _partial(self._process_source, 'Src'),
            'SrcTrig': _partial(self._process_source, 'SrcTrig'),
            'RFDelay': _partial(self._get_delay, 'RFDelay'),
            'FineDelay': _partial(self._get_delay, 'FineDelay'),
            'RFDelayType': _partial(self._get_simple, 'RFDelayType'),
            'DevEnbl': _partial(self._get_status, 'DevEnbl'),
            'Network': _partial(self._get_status, 'Network'),
            'Link': _partial(self._get_status, 'Link'),
            'Los': _partial(self._get_status, 'Los'),
            'EVGLos': _partial(self._get_status, 'EVGLos'),
            'IntlkMon': _partial(self._get_status, 'IntlkMon'),
            'EVGDevEnbl': _partial(self._get_status, 'EVGDevEnbl'),
            }
        if self._foutexist:
            map_.update({
                'FoutLos': _partial(self._get_status, 'FoutLos'),
                'FoutDevEnbl': _partial(self._get_status, 'FoutDevEnbl'),
                })
        for prop in self._REMOVE_PROPS:
            map_.pop(prop)
        return map_

    def _define_dict_for_read(self):
        map_ = {
            'State': _partial(self._get_simple, 'State'),
            'Duration': _partial(self._get_duration_pulses, ''),
            'Polarity': _partial(self._get_simple, 'Polarity'),
            'NrPulses': _partial(self._get_duration_pulses, ''),
            'ByPassIntlk': _partial(self._get_simple, 'ByPassIntlk'),
            'Delay': _partial(self._get_delay, 'Delay'),
            'Src': _partial(self._process_source, ''),
            'RFDelayType': _partial(self._get_simple, 'RFDelayType'),
            'Status': _partial(self._get_status, ''),
            }
        return map_

    def _get_status(self, prop, is_sp, value=None):
        dic_ = dict()
        dic_['DevEnbl'] = self._get_from_pvs(is_sp, 'DevEnbl')
        dic_['EVGDevEnbl'] = self._get_from_pvs(is_sp, 'EVGDevEnbl')
        dic_['Network'] = self._get_from_pvs(is_sp, 'Network')
        dic_['IntlkMon'] = self._get_from_pvs(is_sp, 'IntlkMon', def_val=1)
        dic_['Link'] = self._get_from_pvs(is_sp, 'Link')
        dic_['Los'] = self._get_from_pvs(is_sp, 'Los', def_val=None)
        dic_['EVGLos'] = self._get_from_pvs(is_sp, 'EVGLos', def_val=None)
        dic_['PVsConn'] = self.connected
        if self._foutexist:
            dic_['FoutDevEnbl'] = self._get_from_pvs(is_sp, 'FoutDevEnbl')
            dic_['FoutLos'] = self._get_from_pvs(
                                    is_sp, 'FoutLos', def_val=None)
        else:
            dic_['FoutDevEnbl'] = True
            dic_['FoutLos'] = 0
        if value is not None:
            dic_[prop] = value
        status, bit = 0, 0
        status = _update_bit(status, bit, not dic_['PVsConn'])
        bit += 1
        status = _update_bit(status, bit, not dic_['DevEnbl'])
        bit += 1
        status = _update_bit(status, bit, not dic_['FoutDevEnbl'])
        bit += 1
        status = _update_bit(status, bit, not dic_['EVGDevEnbl'])
        bit += 1
        status = _update_bit(status, bit, not dic_['Network'])
        bit += 1
        status = _update_bit(status, bit, not dic_['Link'])
        bit += 1
        if dic_['Los'] is not None:
            num = int(self.channel[-1])  # get OUT number for EVR
            status = _update_bit(status, bit, _get_bit(dic_['Los'], num))
        bit += 1
        if dic_['FoutLos'] is not None:
            num = self._fout_out if self._foutexist else 1
            status = _update_bit(status, bit, _get_bit(dic_['FoutLos'], num))
        bit += 1
        if dic_['EVGLos'] is not None:
            num = self._evg_out
            status = _update_bit(status, bit, _get_bit(dic_['EVGLos'], num))
        bit += 1
        status = _update_bit(status, bit, dic_['IntlkMon'])
        return {'Status': status}

    def _get_delay(self, prop, is_sp, value=None):
        dic_ = dict()
        dic_['Delay'] = self._get_from_pvs(is_sp, 'Delay')
        dic_['RFDelay'] = self._get_from_pvs(is_sp, 'RFDelay')
        dic_['FineDelay'] = self._get_from_pvs(is_sp, 'FineDelay')
        if value is not None:
            dic_[prop] = value

        delay = (dic_['Delay']*self._base_del + dic_['FineDelay']*_FDEL) * 1e6
        delay += dic_['RFDelay']*self._rf_del * 1e6
        return {'Delay': delay}

    def _set_delay(self, value):
        value *= _DELAY_UNIT_CONV  # us
        delay1 = int(value // self._base_del)
        dic_ = {'Delay': delay1}
        value -= delay1 * self._base_del
        delay2 = value // self._rf_del
        value -= delay2 * self._rf_del
        delay3 = round(value / _FDEL)
        dic_['RFDelay'] = delay2
        dic_['FineDelay'] = delay3
        return dic_

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
        invalid = len(self._source_enums)-1  # Invalid option
        if evt not in _cstime.Const.EvtLL:
            return {'Src': invalid}
        evt_st = _cstime.Const.EvtLL._fields[_cstime.Const.EvtLL.index(evt)]
        if evt_st not in _cstime.Const.EvtLL2HLMap or \
           _cstime.Const.EvtLL2HLMap[evt_st] not in self._source_enums:
            return {'Src': invalid}
        else:
            ev_num = self._source_enums.index(
                                    _cstime.Const.EvtLL2HLMap[evt_st])
            return {'Src': ev_num}

    def _process_src_trig(self, src_trig, is_sp):
        invalid = len(self._source_enums)-1  # Invalid option
        intrg = _LLTimeSearch.get_channel_internal_trigger_pvname(self.channel)
        intrg = int(intrg.propty[-2])  # get internal trigger number for EVR
        if src_trig != intrg:
            return {'Src': invalid}

    def _process_src(self, src, is_sp):
        invalid = len(self._source_enums)-1  # Invalid option
        # BUG: I noticed that differently from the EVR and EVE IOCs,
        # the AMCFPGAEVR do not have a 'Dsbl' as first option of the enums
        # list. So I have to create this offset to fix this...
        offset = 0
        if self.channel.dev.startswith('AMCFPGAEVR'):
            offset = 1
        try:
            source = _cstime.Const.TrigSrcLL._fields[src+offset]
        except IndexError:
            source = ''
        if not source:
            return {'Src': invalid}
        elif source.startswith(('Dsbl', 'Clock')):
            return {'Src': self._source_enums.index(source)}

    def _set_source(self, value):
        # BUG: I noticed that differently from the EVR and EVE IOCs,
        # the AMCFPGAEVR do not have a 'Dsbl' as first option of the enums
        # list. So I have to create this offset to fix this...
        offset = 0
        if self.channel.dev.startswith('AMCFPGAEVR'):
            offset = 1

        if value >= (len(self._source_enums)-1):
            return dict()
        pname = self._source_enums[value]
        n = _cstime.Const.TrigSrcLL._fields.index('Trigger')
        if pname.startswith('Dsbl'):
            dic_ = {'Src': n, 'Evt': _cstime.Const.EvtLL.Evt00}
        if pname.startswith('Clock'):
            n = _cstime.Const.TrigSrcLL._fields.index(pname)
            n -= offset
            dic_ = {'Src': n}
        else:
            n -= offset
            evt = int(_cstime.Const.EvtHL2LLMap[pname][-2:])
            dic_ = {'Src': n, 'Evt': evt}
        if 'SrcTrig' in self._dict_convert_prop2pv.keys():
            intrg = _LLTimeSearch.get_channel_internal_trigger_pvname(
                                                                self.channel)
            intrg = int(intrg[-2:])  # get internal trigger number for EVR
            dic_['SrcTrig'] = intrg
        return dic_

    def _get_duration_pulses(self, prop, is_sp, value=None):
        dic_ = dict()
        dic_['NrPulses'] = self._get_from_pvs(is_sp, 'NrPulses', def_val=1)
        dic_['Width'] = self._get_from_pvs(is_sp, 'Width', def_val=1)
        for k, v in dic_.items():
            if v == 0:  # BUG: handle cases where LL sets these value to 0
                dic_[k] = 1
        if value is not None:
            dic_[prop] = value
        return {
            'Duration': 2*dic_['Width']*self._base_del*dic_['NrPulses']*1e6,
            'NrPulses': dic_['NrPulses'],
            }

    def _set_duration(self, value, pul=None):
        value *= 1e-6  # us
        if pul is None:
            pul = self._config_ok_values.get('NrPulses')
        if pul is None:
            return dict()
        pul = pul or 1  # BUG: handle cases where LL sets this value to 0
        wid = value / self._base_del / pul / 2
        wid = round(wid) if wid >= 1 else 1
        return {'Width': wid}

    def _set_nrpulses(self, value):
        if value < 1:
            return dict()
        dic = {'NrPulses': int(value)}

        # at initialization, try to set _duration
        if self._duration is None:
            # BUG: handle cases where LL sets these value to 0
            wid = self._config_ok_values.get('Width') or 1
            pul = self._config_ok_values.get('NrPulses') or 1
            if wid is not None and pul is not None:
                self._duration = wid * pul * 2 * self._base_del

        if self._duration is not None:
            dic.update(self._set_duration(self._duration, pul=int(value)))
        return dic


class _EVROTP(_EVROUT):
    _REMOVE_PROPS = {
        'RFDelay', 'FineDelay', 'Src', 'SrcTrig', 'RFDelayType', 'Los'}

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

    def _process_source(self, prop, is_sp, val=None):
        if val is None:
            val = self._get_from_pvs(is_sp, 'Evt')
        return self._process_evt(val, is_sp)

    def _process_src(self, src, is_sp):
        return None

    def _set_source(self, value):
        if value >= (len(self._source_enums)-1):
            return dict()
        pname = self._source_enums[value]
        dic_ = dict()
        reg = _re.compile('[0-9]+')
        if pname.startswith('Dsbl'):
            dic_['Evt'] = 0
        if not pname.startswith('Clock'):
            mat = reg.findall(_cstime.Const.EvtHL2LLMap[pname])
            dic_['Evt'] = int(mat[0])
        return dic_


class _EVEOTP(_EVROTP):
    pass


class _EVEOUT(_EVROUT):
    _REMOVE_PROPS = {'Los', }


class _AMCFPGAEVRAMC(_EVROUT):
    _REMOVE_PROPS = {
        'RFDelay', 'FineDelay', 'SrcTrig', 'ByPassIntlk', 'RFDelayType', 'Los'}

    def _get_delay(self, prop, is_sp, value=None):
        return _EVROTP._get_delay(self, prop, is_sp, value)

    def _set_delay(self, value):
        return _EVROTP._set_delay(self, value)

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
        raise Exception('Low Level Trigger Class not defined for device ' +
                        'type '+key[0]+' and connection type '+key[1]+'.')
    return cls_(channel, source_enums)
