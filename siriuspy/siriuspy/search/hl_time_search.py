"""Define properties of all timing devices and their connections."""

import ast as _ast
from copy import deepcopy as _dcopy
from siriuspy import servweb as _web
from siriuspy.namesys import SiriusPVName as _PVName, Filter as _Filter
from .ll_time_search import LLTimeSearch as _LLSearch

_timeout = 1.0


class HLTimeSearch:
    """Contain properties of the triggers."""

    _hl_triggers = dict()

    @classmethod
    def get_hl_triggers(cls, filters=None, sorting=None):
        """Dictionary with high level triggers."""
        cls._init()
        all_devs = sorted(cls._hl_triggers.keys())
        return _Filter.process_filters(
                    all_devs, filters=filters, sorting=sorting)

    @classmethod
    def get_hl_trigger_predef_db(cls, hl_trigger):
        """Return the default database of the high level trigger."""
        cls._init()
        dic_ = _dcopy(cls._hl_triggers[hl_trigger]['database'])
        dic_['Src']['enums'] = ('Dsbl', ) + dic_['Src']['enums']
        dic_['Src']['value'] += 1
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
    def get_ll_trigger_names(cls, hl_trigger=None, channels=None):
        """Get Low Level trigger object names."""
        cls._init()
        ret = cls._hl_triggers.get(hl_trigger)
        chans = ret['channels'] if ret else (channels or list())
        return sorted({_LLSearch.get_trigger_name(chan) for chan in chans})

    @classmethod
    def get_hl_trigger_channels(cls, hl_trigger):
        cls._init()
        ret = cls._hl_triggers.get(hl_trigger)
        chans = ret['channels'] if ret else list()
        return sorted(chans)

    @classmethod
    def has_delay_type(cls, hl_trigger):
        """Return True if hl_trigger has property delayType."""
        cls._init()
        ll_chans = cls.get_ll_trigger_names(hl_trigger)
        has_ = [_LLSearch.has_delay_type(name) for name in ll_chans]
        if not any(has_):
            return False
        elif not all(has_):
            raise Exception(
                'Some triggers of ' + hl_trigger +
                ' are connected to unsimiliar low level devices.')
        return True

    @classmethod
    def has_bypass_interlock(cls, hl_trigger):
        """Return True if hl_trigger has property delayType."""
        cls._init()
        ll_chans = cls.get_ll_trigger_names(hl_trigger)
        has_ = [_LLSearch.has_bypass_interlock(name) for name in ll_chans]
        if not any(has_):
            return False
        elif not all(has_):
            raise Exception(
                'Some triggers of ' + hl_trigger +
                ' are connected to unsimiliar low level devices.')
        return True

    @classmethod
    def has_clock(cls, hl_trigger):
        """Return True if hl_trigger can listen to Clocks from EVG."""
        cls._init()
        ll_chans = cls.get_ll_trigger_names(hl_trigger)
        has_ = [_LLSearch.has_clock(name) for name in ll_chans]
        if all(has_):
            return True
        elif any(has_):
            raise Exception(
                'Some triggers of ' + hl_trigger +
                ' are connected to unsimiliar low level devices.')
        return False

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
    def _init(cls):
        """Initialize the Instance."""
        if cls._hl_triggers:
            return
        text = ''
        if _web.server_online():
            text = _web.high_level_triggers(timeout=_timeout)
        temp_dict = _ast.literal_eval(text)
        for k, vs in temp_dict.items():
            vs['channels'] = tuple(map(_PVName, vs['channels']))
            cls._hl_triggers[_PVName(k)] = vs
