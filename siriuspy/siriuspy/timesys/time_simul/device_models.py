"""Define Classes to simulate timing objects."""

import time as _time
from copy import deepcopy as _dcopy
import uuid as _uuid
from threading import Thread as _Thread
from siriuspy.timesys.time_data import Events, Clocks
from siriuspy.timesys.time_data import TimingDevDb
from siriuspy.timesys.time_data import AC_FREQUENCY as _PwrFreq
from siriuspy.timesys.time_data import FINE_DELAY as _FINE_DELAY_STEP

_OTP_SIM_TMP = 'OTP{0:02d}'
_OUT_SIM_TMP = 'OUT{0:d}'


class CallBack:
    """Base Class for all Timing Simulation."""

    def __init__(self, callbacks=None, prefix=None):
        """Initialize the instance."""
        self.prefix = prefix or ''
        self.uuid = _uuid.uuid4()
        self._callbacks = dict(callbacks) if callbacks else dict()

    def _call_callbacks(self, propty, value, **kwargs):
        for uuid, callback in self._callbacks.items():
            callback(self.prefix + propty, value, **kwargs)

    def add_callback(self, *args):
        """Add callbacks."""
        if len(args) < 2 and isinstance(args[0], dict):
            self._callbacks.update(args[0])
        elif len(args) == 2:
            uuid, callback = args
            self._callbacks[uuid] = callback
        else:
            raise Exception('wrong input for add_callback')

    def remove_callback(self, uuid):
        """Remove callbacks."""
        self._callbacks.pop(uuid)


class _BaseIOC(CallBack):

    _attr2pvname = dict()

    def __init__(self, callbacks=None, prefix=None):
        super().__init__(callbacks, prefix=prefix)
        self._pvname2attr = {value: key
                             for key, value in self._attr2pvname.items()}
        self._attr2expr = self._get_attr2expression()
        self._set_init_values()

    def __getattr__(self, name):
        if name in self.__class__._attr2pvname.keys():
            return self.__dict__['_'+name]
        else:
            return super().__getattr__(name)

    def __setattr__(self, name, value):
        if name in self.__class__._attr2pvname.keys():
            f_ = self._attr2expr.get(name)
            pvalue = f_(value)
            if name.endswith(('_sp', '_sel')):
                self.__dict__['_'+name] = value
                name_rb = name.replace('_sp', '_rb').replace('_sel', '_rb')
                setattr(self, name_rb, pvalue)
            elif name.endswith(('_rb', '_mon')):
                self.__dict__['_'+name] = pvalue
                self._call_callbacks(self._attr2pvname[name], pvalue)
            elif name.endswith(('_cmd',)):
                self.__dict__['_'+name] = pvalue
        else:
            super().__setattr__(name, value)

    def get_propty(self, reason):
        reason = reason[len(self.prefix):]
        if reason in self._pvname2attr.keys():
            return getattr(self, self._pvname2attr[reason])

    def set_propty(self, reason, value):
        reason = reason[len(self.prefix):]
        cond = (reason not in self._pvname2attr.keys() or
                reason.endswith(('-RB', '-Sts', '-Mon')))
        if cond:
            return False
        setattr(self, self._pvname2attr[reason], value)
        return True

    def _set_init_values(self):
        db = self.get_database(prefix='')
        for attr, pv in self._attr2pvname.items():
            if attr.endswith(('_sp', '_sel')):
                setattr(self, attr, db[pv]['value'])

    def _get_attr2expression(self):
        return dict()


# #############################################################
# ############# Event Generator Part ##########################
# #############################################################
class _ClockIOC(_BaseIOC):

    _attr2pvname = {
        'frequency_sp': 'MuxDiv-SP',
        'frequency_rb': 'MuxDiv-RB',
        'state_sp': 'MuxEnbl-Sel',
        'state_rb': 'MuxEnbl-Sts',
        }

    @staticmethod
    def get_database(prefix=''):
        return TimingDevDb.get_clock_database(prefix=prefix)

    def __init__(self, base_freq, callbacks=None, prefix=None):
        self.base_freq = base_freq
        super().__init__(callbacks, prefix=prefix)

    def generate(self):
        if self._state_rb > 0:
            return {'frequency': self.base_freq/self._frequency_rb}

    def _get_attr2expression(self):
        return {
            'frequency_sp': lambda x: int(x),
            'frequency_rb': lambda x: x,
            'state_sp': lambda x: int(x),
            'state_rb': lambda x: x,
            }


class _EventIOC(_BaseIOC):

    _attr2pvname = {
        'delay_sp': 'Delay-SP',
        'delay_rb': 'Delay-RB',
        'mode_sp': 'Mode-Sel',
        'mode_rb': 'Mode-Sts',
        'delay_type_sp': 'DelayType-Sel',
        'delay_type_rb': 'DelayType-Sts',
        'description_sp': 'Desc-SP',
        'description_rb': 'Desc-RB',
        'exttrig_cmd': 'ExtTrig-Cmd'
        }

    @staticmethod
    def get_database(prefix=''):
        return TimingDevDb.get_event_database(prefix=prefix)

    def __init__(self, base_freq, callbacks=None, prefix=None):
        self.base_freq = base_freq
        super().__init__(callbacks, prefix=prefix)

    def generate(self):
        if self._mode_rb > 0:
            return {'delay': self._delay_rb/self.base_freq}

    def _get_attr2expression(self):
        return {
            'delay_sp': lambda x: int(x),
            'delay_rb': lambda x: x,
            'mode_sp': lambda x: int(x),
            'mode_rb': lambda x: x,
            'delay_type_sp': lambda x: int(x),
            'delay_type_rb': lambda x: x,
            'description_sp': lambda x: str(x),
            'description_rb': lambda x: x,
            'exttrig_cmd': lambda x: x,
            }


class EVGIOC(_BaseIOC):
    """Class to Simulate the EVG."""

    _attr2pvname = {
        'state_sp': 'DevEnbl-Sel',
        'state_rb': 'DevEnbl-Sts',
        'continuous_sp': 'ContinuousEvt-Sel',
        'continuous_rb': 'ContinuousEvt-Sts',
        'bucket_list_sp': 'BucketList-SP',
        'bucket_list_rb': 'BucketList-RB',
        'bucket_list_len_mon': 'BucketListLen-Mon',
        'injection_sp': 'InjectionEvt-Sel',
        'injection_rb': 'InjectionEvt-Sts',
        'repeat_bucket_list_sp': 'RepeatBucketList-SP',
        'repeat_bucket_list_rb': 'RepeatBucketList-RB',
        'repetition_rate_sp': 'ACDiv-SP',
        'repetition_rate_rb': 'ACDiv-RB',
        'rf_division_sp': 'RFDiv-SP',
        'rf_division_rb': 'RFDiv-RB',
        'loss_down_conn_mon': 'Los-Mon',
        'alive_mon': 'Alive-Mon',
        'network_mon': 'Network-Mon',
        'rf_status_mon': 'RFStatus-Mon',
        'state_machine_mon': 'StateMachine-Mon',
        }

    @staticmethod
    def get_database(prefix=''):
        """Get the database."""
        return TimingDevDb.get_evg_database(prefix=prefix)

    def __init__(self, base_freq, callbacks=None, prefix=None):
        """Initialize instance."""
        self.base_freq = base_freq
        self._pending_devices_callbacks = dict()
        self._injection_callbacks = dict()
        super().__init__(callbacks=callbacks, prefix=prefix)

        self.events = dict()
        for ev in Events.LL_EVENTS:
            self.events[ev] = _EventIOC(
                self.base_freq/self._rf_division_rb,
                callbacks={self.uuid: self._call_callbacks},
                prefix=ev)
        self.clocks = dict()
        for clc in sorted(Clocks.LL2HL_MAP.keys()):
            self.clocks[clc] = _ClockIOC(
                self.base_freq/self._rf_division_rb,
                callbacks={self.uuid: self._call_callbacks},
                prefix=clc)

    def _get_attr2expression(self):
        return {
            'state_sp': lambda x: int(x),
            'state_rb': lambda x: x,
            'continuous_sp': lambda x: int(x),
            'continuous_rb': lambda x: x,
            'bucket_list_sp': self._bucket_list_setter,
            'bucket_list_rb': lambda x: x,
            'bucket_list_len_mon': lambda x: x,
            'injection_sp': lambda x: int(x),
            'injection_rb': lambda x: x,
            'repeat_bucket_list_sp': lambda x: int(x),
            'repeat_bucket_list_rb': lambda x: x,
            'repetition_rate_sp': lambda x: int(x),
            'repetition_rate_rb': lambda x: x,
            'rf_division_sp': lambda x: int(x),
            'rf_division_rb': lambda x: x,
            'loss_down_conn_mon': lambda x: x,
            'alive_mon': lambda x: x,
            'network_mon': lambda x: x,
            'rf_status_mon': lambda x: x,
            'state_machine_mon': lambda x: x,
            }

    def __setattr__(self, attr, value):
        if attr == 'injection_sp':
            if value:
                if not self._injection_rb and self._continuous_rb:
                    super().__setattr__(attr, value)
                    _Thread(target=self._injection_fun).start()
                    return
        super().__setattr__(attr, value)

    def _bucket_list_setter(self, value):
        bucket = []
        if isinstance(value, (int, float, str)):
            value = [value, ]
        for i in range(min(len(value), 864)):
            if 0 < value[i] <= 864:
                bucket.append(int(value[i]))
            else:
                break
        self.bucket_list_len_mon = len(bucket)
        return bucket

    def add_pending_devices_callback(self, uuid, callback):
        """Add pending devices callback."""
        self._pending_devices_callbacks.update({uuid: callback})

    def remove_pending_devices_callback(self, uuid):
        """Remove pending devices callback."""
        self._pending_devices_callbacks.pop(uuid, None)

    # ########## Functions related to Single Pulse simulation #############
    def add_injection_callback(self, uuid, callback):
        """Add injection callback."""
        self._injection_callbacks.update({uuid: callback})

    def remove_injection_callback(self, uuid):
        """Remove injection callback."""
        self._injection_callbacks.pop(uuid, None)

    def get_propty(self, reason):
        """Get propty."""
        reason2 = reason[len(self.prefix):]
        if reason2.startswith(tuple(self.clocks.keys())):
            leng = len(Clocks.LL_TMP.format(0))
            return self.clocks[reason2[: leng]].get_propty(reason2)
        elif reason2.startswith(tuple(self.events.keys())):
            leng = len(Events.LL_TMP.format(0))
            return self.events[reason2[: leng]].get_propty(reason2)
        else:
            return super().get_propty(reason)

    def set_propty(self, reason, value):
        """Set propty."""
        reason2 = reason[len(self.prefix):]
        if reason2.startswith(tuple(self.clocks.keys())):
            leng = len(Clocks.LL_TMP.format(0))
            return self.clocks[reason2[: leng]].set_propty(reason2, value)
        elif reason2.startswith(tuple(self.events.keys())):
            leng = len(Events.LL_TMP.format(0))
            return self.events[reason2[: leng]].set_propty(reason2, value)
        else:
            return super().set_propty(reason, value)

    def _injection_fun(self):
        idx = 0
        while True:
            idx += 1
            if not len(self._bucket_list_rb):
                _time.sleep(0.1)
            for i in self._bucket_list_rb:
                if not self._can_inject():
                    return
                if i <= 0:
                    break
                evnts = self._generate_events((1, 2))
                triggers = dict()
                for callback in self._pending_devices_callbacks.values():
                    triggers.update(callback(i, evnts))
                for callback in self._injection_callbacks.values():
                    callback(i, triggers)
                _time.sleep(self._repetition_rate_rb/_PwrFreq)
            if 0 < self._repeat_bucket_list_rb <= idx:
                self._injection_sp = 0
                self._call_callbacks('InjectionEvt-Sel', 0)
                return

    def _can_inject(self):
        if not self._continuous_rb or not self._injection_rb:
            return False
        return True
    ######################################################################

    def _generate_events(self, tables):
        tables = tables if isinstance(tables, (list, tuple)) else (tables,)
        events = dict()
        for i, ev in enumerate(self.events):
            lab = Events.LL_EVENTS[i]
            if ev.mode_rb not in tables:
                continue
            dic = ev.generate()
            if not dic:
                continue
            events.update({lab: dic})
        for i, cl in enumerate(self.clocks):
            dic = cl.generate()
            if not dic:
                continue
            lab = Clocks.LL_TMP.format(i)
            events.update({lab: dic})
        return events


# #############################################################
# ############# Event Receivers Part ##########################
# #############################################################
class _OTP_IOC(_BaseIOC):

    _attr2pvname = {
        'state_sp': 'State-Sel',
        'state_rb': 'State-Sts',
        'width_sp': 'Width-SP',
        'width_rb': 'Width-RB',
        'delay_sp': 'Delay-SP',
        'delay_rb': 'Delay-RB',
        'polarity_sp': 'Polarity-Sel',
        'polarity_rb': 'Polarity-Sts',
        'event_sp': 'Evt-SP',
        'event_rb': 'Evt-RB',
        'pulses_sp': 'Pulses-SP',
        'pulses_rb': 'Pulses-RB',
        }

    @staticmethod
    def get_database(prefix=''):
        """Get the database."""
        return TimingDevDb.get_otp_database(prefix=prefix)

    def __init__(self, base_freq, callbacks=None, prefix=None):
        self.base_freq = base_freq
        super().__init__(callbacks, prefix=prefix)

    def receive_events(self, bucket, events):
        if self._state_rb == 0:
            return
        ev = events.get(Events.LL_TMP.format(self._event_rb), None)
        if ev is None:
            return
        delay = ev['delay'] + self._delay_rb/self.base_freq
        return dict({'pulses': self._pulses_rb,
                     'width': self._width_rb/self.base_freq,
                     'delay': delay})

    def _get_attr2expression(self):
        return {
            'state_sp': lambda x: int(x),
            'state_rb': lambda x: x,
            'width_sp': lambda x: int(x),
            'width_rb': lambda x: x,
            'delay_sp': lambda x: int(x),
            'delay_rb': lambda x: x,
            'polarity_sp': lambda x: int(x),
            'polarity_rb': lambda x: x,
            'event_sp': lambda x: x,
            'event_rb': lambda x: x,
            'pulses_sp': lambda x: int(x),
            'pulses_rb': lambda x: x,
            }


class _EVROUT_IOC(_BaseIOC):

    _attr2pvname = {
        'interlock_sp':  'Intlk-Sel',
        'interlock_rb':  'Intlk-Sts',
        'source_sp':     'Src-Sel',
        'source_rb':     'Src-Sts',
        'trigger_sp':    'SrcTrig-SP',
        'trigger_rb':    'SrcTrig-RB',
        'rf_delay_sp':   'RFDelay-SP',
        'rf_delay_rb':   'RFDelay-RB',
        'fine_delay_sp': 'FineDelay-SP',
        'fine_delay_rb': 'FineDelay-RB',
        }

    @staticmethod
    def get_database(prefix=''):
        """Get the database."""
        return TimingDevDb.get_out_database(prefix=prefix, equip='EVR')

    def __init__(self, base_freq, callbacks=None, prefix=None):
        self.base_freq = base_freq
        super().__init__(callbacks, prefix=prefix)

    def receive_events(self, bucket, opts):
        lab = None
        if self._source_rb == 1:
            lab = _OTP_SIM_TMP.format(self._trigger_rb)
        if 1 < self._source_rb <= 9:
            lab = Clocks.LL_TMP.format(self._source_rb - 2)

        dic = _dcopy(opts.get(lab, None))
        if dic is not None:
            delay = dic.get('delay', 0.0)
            dic['delay'] = (delay + self._rf_delay_rb/self.base_freq +
                            self._fine_delay_rb * _FINE_DELAY_STEP)
            return dic

    def _get_attr2expression(self):
        return {
            'interlock_sp': lambda x: int(x),
            'interlock_rb': lambda x: x,
            'source_sp': lambda x: int(x),
            'source_rb': lambda x: x,
            'trigger_sp': lambda x: int(x),
            'trigger_rb': lambda x: x,
            'rf_delay_sp': lambda x: int(x),
            'rf_delay_rb': lambda x: x,
            'fine_delay_sp': lambda x: int(x),
            'fine_delay_rb': lambda x: x,
            }


class _EVEOUT_IOC(_EVROUT_IOC):

    @staticmethod
    def get_database(prefix=''):
        """Get the database."""
        return TimingDevDb.get_out_database(prefix=prefix, equip='EVE')


class _AFCOUT_IOC(_BaseIOC):

    _attr2pvname = {
        'source_sp': 'Src-Sel',
        'source_rb': 'Src-Sts',
        'state_sp': 'State-Sel',
        'state_rb': 'State-Sts',
        'width_sp': 'Width-SP',
        'width_rb': 'Width-RB',
        'delay_sp': 'Delay-SP',
        'delay_rb': 'Delay-RB',
        'polarity_sp': 'Polarity-Sel',
        'polarity_rb': 'Polarity-Sts',
        'event_sp': 'Evt-SP',
        'event_rb': 'Evt-RB',
        'pulses_sp': 'Pulses-SP',
        'pulses_rb': 'Pulses-RB',
        }

    @staticmethod
    def get_database(prefix=''):
        """Get the database."""
        return TimingDevDb.get_afc_out_database(prefix=prefix)

    def __init__(self, base_freq, callbacks=None, prefix=None):
        self.base_freq = base_freq
        super().__init__(callbacks, prefix=prefix)

    def receive_events(self, bucket, opts):
        lab = None
        if self._source_rb == 1:
            lab = Events.LL_TMP.format(self._event_rb)
        if 1 < self._source_rb <= 9:
            lab = Clocks.LL_TMP.format(self._source_rb - 2)

        dic = _dcopy(opts.get(lab, None))
        if dic is not None:
            delay = dic.get('delay', 0.0)
            dic['delay'] = delay + self._delay_rb/self.base_freq
            return dic

    def _get_attr2expression(self):
        return {
            'source_sp': lambda x: int(x),
            'source_rb': lambda x: x,
            'state_sp': lambda x: int(x),
            'state_rb': lambda x: x,
            'width_sp': lambda x: int(x),
            'width_rb': lambda x: x,
            'delay_sp': lambda x: int(x),
            'delay_rb': lambda x: x,
            'polarity_sp': lambda x: int(x),
            'polarity_rb': lambda x: x,
            'event_sp': lambda x: x,
            'event_rb': lambda x: x,
            'pulses_sp': lambda x: int(x),
            'pulses_rb': lambda x: x,
            }


class EVRIOC(_BaseIOC):
    """Class to simulate the EVR."""

    _NR_INTERNAL_OTP_CHANNELS = 24
    _NR_OTP_CHANNELS = 12
    _NR_OUT_CHANNELS = 8
    _ClassOutIOC = _EVROUT_IOC
    _ClassIntTrigIOC = _OTP_IOC

    @staticmethod
    def _OUTTMP(x):
        return 'OUT{0:d}'.format(x)

    @staticmethod
    def _INTTMP(x):
        return 'OTP{0:02d}'.format(x)

    _attr2pvname = {
        'state_sp': 'DevEnbl-Sel',
        'state_rb': 'DevEnbl-Sts',
        'loss_down_conn_mon': 'Los-Mon',
        'alive_mon': 'Alive-Mon',
        'network_mon': 'Network-Mon',
        'link_mon': 'Link-Mon',
        'interlock_mon': 'Intlk-Mon',
        }

    @staticmethod
    def get_database(prefix=''):
        """Get the database."""
        return TimingDevDb.get_evr_database(prefix=prefix)

    def __init__(self, base_freq, callbacks=None, prefix=None):
        """Initialize the instance."""
        self.base_freq = base_freq
        super().__init__(callbacks=callbacks, prefix=prefix)

        self.internal_triggers = dict()
        for i in range(self._NR_INTERNAL_OTP_CHANNELS):
            name = self._INTTMP(i)
            self.internal_triggers[name] = self._ClassIntTrigIOC(
                self.base_freq,
                callbacks={self.uuid: self._call_callbacks},
                prefix=name)
        self.main_outputs = dict()
        for i in range(self._NR_OUT_CHANNELS):
            name = self._OUTTMP(i)
            self.main_outputs[name] = self._ClassOutIOC(
                self.base_freq,
                callbacks={self.uuid: self._call_callbacks},
                prefix=name)

    def get_propty(self, reason):
        """Get properties by PV name."""
        reason2 = reason[len(self.prefix):]
        if reason2.startswith(tuple(self.main_outputs.keys())):
            leng = len(self._OUTTMP(0))
            # Not general enough
            return self.main_outputs[reason2[: leng]].get_propty(reason2)
        elif reason2.startswith(tuple(self.internal_triggers.keys())):
            leng = len(self._INTTMP(0))
            # Absolutely not general enough
            return self.internal_triggers[reason2[: leng]].get_propty(reason2)
        else:
            return super().get_propty(reason)

    def set_propty(self, reason, value):
        """Set properties by PV name."""
        reason2 = reason[len(self.prefix):]
        if reason2.startswith(tuple(self.main_outputs.keys())):
            leng = len(self._OUTTMP(0))
            return self.main_outputs[reason2[:leng]].set_propty(reason2,
                                                                value)
        elif reason2.startswith(tuple(self.internal_triggers.keys())):
            leng = len(self._INTTMP(0))
            return self.internal_triggers[reason2[:leng]].set_propty(reason2,
                                                                     value)
        else:
            return super().set_propty(reason, value)

    def receive_events(self, bucket, events):
        """Receive the events from the EVG."""
        if not self._state_rb:
            return
        triggers = dict()
        inp_dic = dict(events)
        for i, opt_ch in enumerate(self.internal_triggers):
            opt = opt_ch.receive_events(bucket, inp_dic)
            if opt is None:
                continue
            lab = _OTP_SIM_TMP.format(i)
            inp_dic.update({lab: opt})
            if i < self._NR_OTP_CHANNELS:
                triggers.update({lab: opt})
        for tri_ch in self.main_outputs:
            out = tri_ch.receive_events(bucket, inp_dic)
            if out is None:
                continue
            lab = _OUT_SIM_TMP.format(i)
            triggers.update({lab: out})
        return {self.prefix: triggers}

    def _get_attr2expression(self):
        return {
            'state_sp': lambda x: int(x),
            'state_rb': lambda x: x,
            'loss_down_conn_mon': lambda x: x,
            'alive_mon': lambda x: x,
            'network_mon': lambda x: x,
            'link_mon': lambda x: x,
            'interlock_mon': lambda x: x,
            }


class EVEIOC(EVRIOC):
    """Class to simulate the EVE."""

    _NR_INTERNAL_OTP_CHANNELS = 16
    _NR_OTP_CHANNELS = 0
    _NR_OUT_CHANNELS = 8
    _ClassOutIOC = _EVEOUT_IOC

    _attr2pvname = {
        'rfout_sp': 'RFOut-Sel',
        'rfout_rb': 'RFOut-Sts',
    }
    _attr2pvname.update(EVRIOC._attr2pvname)
    _attr2pvname.pop('loss_down_conn_mon')

    @staticmethod
    def get_database(prefix=''):
        """Get the database."""
        return TimingDevDb.get_eve_database(prefix=prefix)

    def _get_attr2expression(self):
        dic_ = super()._get_attr2expression()
        dic_.pop('loss_down_conn_mon')
        dic_.update({
            'rfout_sp': lambda x: int(x),
            'rfout_rb': lambda x: x,
        })
        return dic_


class AFCIOC(EVRIOC):
    """Class to simulate the AFC."""

    _NR_INTERNAL_OTP_CHANNELS = 10
    _NR_OTP_CHANNELS = 10
    _NR_OUT_CHANNELS = 8
    _ClassOutIOC = _AFCOUT_IOC
    _ClassIntTrigIOC = _AFCOUT_IOC

    @staticmethod
    def _OUTTMP(x):
        return 'CRT{0:d}'.format(x)

    @staticmethod
    def _INTTMP(x):
        fmc = (x // 5) + 1
        ch = (x % 5) + 1
        return 'FMC{0:d}CH{1:d}'.format(fmc, ch)

    @staticmethod
    def get_database(prefix=''):
        """Get the database."""
        return TimingDevDb.get_afc_database(prefix=prefix)
