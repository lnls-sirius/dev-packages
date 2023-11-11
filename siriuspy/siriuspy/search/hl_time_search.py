"""Define properties of all timing devices and their connections."""

import ast as _ast
from copy import deepcopy as _dcopy
from threading import Lock as _Lock
from siriuspy import clientweb as _web
from siriuspy.namesys import SiriusPVName as _PVName, Filter as _Filter
from .ll_time_search import LLTimeSearch as _LLSearch

_timeout = 1.0


class HLTimeSearch:
    """Contain properties of the triggers."""

    _hl_triggers = dict()
    _hl_events = dict()
    COMMOM_EVTS = ('Dsbld', 'RmpBO', 'Linac', 'Study')

    _lock = _Lock()

    @classmethod
    def get_hl_events(cls):
        """Return a dictionary with high level events."""
        cls._init()
        return _dcopy(cls._hl_events)

    @classmethod
    def get_configurable_hl_events(cls):
        """Return a dictionary with configurable high level events."""
        cls._init()
        return {e: c for e, c in cls._hl_events.items() if 0 < int(c[3:]) < 64}

    @classmethod
    def get_hl_triggers(cls, filters=None, sorting=None):
        """Return a dictionary with high level triggers."""
        cls._init()
        all_devs = sorted(cls._hl_triggers.keys())
        return _Filter.process_filters(
            all_devs, filters=filters, sorting=sorting)

    @classmethod
    def get_hl_trigger_predef_db(cls, hl_trigger, has_commom_evts=True):
        """Return the default database of the high level trigger."""
        cls._init()
        dic_ = _dcopy(cls._hl_triggers[hl_trigger]['database'])
        src = dic_['Src']
        if has_commom_evts:
            src['enums'] = cls.COMMOM_EVTS + src['enums']
        return dic_

    @classmethod
    def get_hl_trigger_allowed_evts(cls, hl_trigger):
        """Return the possible events of the high level trigger."""
        cls._init()
        enums = cls._hl_triggers[hl_trigger]['database']['Src']['enums']
        return _dcopy(enums)

    @classmethod
    def get_hl_trigger_prop_value(cls, hl_trigger, prop='Delay'):
        """Return the default value of the property prop of the HL trigger."""
        cls._init()
        val = cls._hl_triggers[hl_trigger]['database'][prop]['value']
        if prop == 'Src':
            val += 1 if cls.has_clock(hl_trigger) else 0
        return val

    @classmethod
    def get_hl_trigger_prop_limits(cls, hl_trigger, prop='Delay'):
        """Return the default limits of the property prop of the HL trigger."""
        cls._init()
        dic_ = dict()
        for lim in {'lolo', 'hihi', 'high', 'low', 'lolim', 'hilim'}:
            val = cls._hl_triggers[hl_trigger]['database'][prop].get(lim)
            if val is not None:
                dic_[lim] = val
        return dic_

    @classmethod
    def get_ll_trigger_names(cls, hl_trigger):
        """Get Low Level trigger object names."""
        cls._init()
        return sorted(cls._hl2ll_trigs.get(hl_trigger, list()))

    @classmethod
    def get_hl_from_ll_triggers(cls, channel):
        cls._init()
        # channel = _LLSearch.get_channel_output_port_pvname(channel)
        prpt = channel.propty
        if prpt.startswith('OTP'):
            val = int(prpt[3:]) - 12
            newprpt = 'OUT'+str(val) if 0 <= val < 8 else 'OTP'+str(val+12)
            channel = channel.substitute(propty=newprpt)
        return cls._ll2hl_trigs.get(channel, '')

    @classmethod
    def get_hl_trigger_channels(cls, hl_trigger):
        cls._init()
        ret = cls._hl_triggers.get(hl_trigger)
        chans = ret['channels'] if ret else list()
        return sorted(chans)

    @classmethod
    def is_digital_input(cls, hl_trigger):
        """Return True if hl_trigger is of type Digital Input."""
        cls._init()
        ll_chans = cls.get_ll_trigger_names(hl_trigger)
        return any([_LLSearch.is_digital_input(name) for name in ll_chans])

    @classmethod
    def has_delay_type(cls, hl_trigger):
        """Return True if hl_trigger has property delayType."""
        cls._init()
        ll_chans = cls.get_ll_trigger_names(hl_trigger)
        return all([_LLSearch.has_delay_type(name) for name in ll_chans])

    @classmethod
    def has_direction(cls, hl_trigger):
        """Return True if hl_trigger has property direction."""
        cls._init()
        ll_chans = cls.get_ll_trigger_names(hl_trigger)
        return all([_LLSearch.has_direction(name) for name in ll_chans])

    @classmethod
    def has_clock(cls, hl_trigger):
        """Return True if hl_trigger can listen to Clocks from EVG."""
        cls._init()
        ll_chans = cls.get_ll_trigger_names(hl_trigger)
        return all([_LLSearch.has_clock(name) for name in ll_chans])

    @classmethod
    def has_log(cls, hl_trigger):
        """Return True if hl_trigger can listen to Clocks from EVG."""
        cls._init()
        ll_chans = cls.get_ll_trigger_names(hl_trigger)
        return all([_LLSearch.has_log(name) for name in ll_chans])

    @classmethod
    def check_hl_triggers_consistency(cls):
        """Check consitency of Triggers definition.

        Check if High Level definition of Triggers is consistent with
        Low Level connections of the timing devices.
        """
        cls._init()
        twds_evg = _LLSearch.get_connections_twds_evg()
        from_evg = _LLSearch.get_connections_from_evg()
        for trig, val in cls._hl_triggers.items():
            chans = {_PVName(chan) for chan in val['channels']}
            for chan in chans:
                tmp = twds_evg.get(chan)
                if tmp is None:
                    raise Exception(
                        chan + ' is used in HL trigger ' + trig +
                        ' but not specified in timing connections data.')
                if not tmp:
                    raise Exception(
                        chan + ' which is used in HL trigger ' + trig +
                        ' maybe were already used somewhere else.')
                up_dev = tmp.pop()
                diff_devs = from_evg[up_dev] - chans
                if diff_devs and not chan.dev.endswith('BPM'):
                    raise Exception(
                        'Devices: ' + ' '.join(diff_devs) +
                        ' are connected to the same output of ' +
                        up_dev + ' as ' + chan +
                        ' but are not related to the same trigger ('+trig+').')

    @classmethod
    def reset(cls):
        cls._hl_triggers = dict()
        cls._init()

    @classmethod
    def _init(cls):
        """Initialize the Instance."""
        with cls._lock:
            if cls._hl_triggers:
                return
            if not _web.server_online():
                raise Exception('Could not connect with Consts Server!!')
            text1 = _web.high_level_triggers(timeout=_timeout)
            text2 = _web.high_level_events(timeout=_timeout)
            temp_dict = _ast.literal_eval(text1)
            hl_trigs = dict()
            for k, vs in temp_dict.items():
                vs['channels'] = tuple(map(_PVName, vs['channels']))
                hl_trigs[_PVName(k)] = vs
            cls._hl_triggers = hl_trigs
            cls._hl_events = _ast.literal_eval(text2)

            hl2ll = dict()
            for hlt, val in cls._hl_triggers.items():
                chans = val['channels']
                hl2ll[hlt] = {_LLSearch.get_trigger_name(c) for c in chans}
            ll2hl = dict()
            for k, vs in hl2ll.items():
                ll2hl.update({v: k for v in vs})
            cls._hl2ll_trigs = hl2ll
            cls._ll2hl_trigs = ll2hl
