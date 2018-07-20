"""Define properties of all timing devices and their connections."""

from copy import deepcopy as _dcopy
from siriuspy import servweb as _web
from siriuspy.namesys import SiriusPVName as _PVName
from .ll_time_search import LLTimeSearch as _LLTimeSearch

_timeout = 1.0


class HLTimeSearch:
    """Contain properties of the triggers."""

    _TWDS_EVG = None
    _FROM_EVG = None
    _EVRs = None
    _EVEs = None
    _AFCs = None
    _hl_triggers = None

    @classmethod
    def get_hl_triggers(cls):
        """Dictionary with high level triggers."""
        cls._init()
        return _dcopy(cls._hl_triggers)

    @classmethod
    def get_hl_trigger_database(cls, hl_trigger):
        """Return the default database of the high level trigger."""
        cls._init()
        return _dcopy(cls._hl_triggers[hl_trigger]['database'])

    @classmethod
    def get_hl_trigger_sources(cls, hl_trigger):
        """Return the possible sources of the high level trigger."""
        cls._init()
        enums = cls._hl_triggers[hl_trigger]['database']['Src']['enums']
        if cls.has_clock(hl_trigger):
            clocks = ['Clock{0:d}'.format(i) for i in range(8)]
            enums = ('Dsbl', ) + enums + tuple(clocks)
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
    def get_hl_trigger_interface(cls, hl_trigger):
        """Return the properties defining the interface of the HL trigger."""
        cls._init()
        dic_ = cls._hl_triggers[hl_trigger]['database']
        interface = dic_.keys() | {'Status'}

        if not cls.has_delay_type(hl_trigger):
            interface.discard('DelayType')
            interface.discard('Intlk')
        return interface

    @classmethod
    def get_ll_trigger_names(cls, hl_trigger=None, channels=None):
        """Get Low Level trigger object names."""
        cls._init()
        cls._get_constants()
        ret = cls._hl_triggers.get(hl_trigger)
        chans = ret['channels'] if ret else (channels or list())

        out_chans = set()
        for chan in chans:
            chan_tree = _LLTimeSearch.get_device_tree(chan)
            for up_chan in chan_tree:
                if up_chan.device_name in cls._EVRs | cls._EVEs | cls._AFCs:
                    out_chans |= {up_chan}
                    break
        return sorted(out_chans)

    @classmethod
    def has_delay_type(cls, hl_trigger):
        """Return True if hl_trigger has property delayType."""
        def get_ll(ll_trigger):
            name = _PVName(ll_trigger)
            return name.dev in ('EVR', 'EVE') and name.propty.startswith('OUT')

        cls._init()
        ll_chans = cls.get_ll_trigger_names(hl_trigger)
        has_ = [get_ll(name) for name in ll_chans]
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
        def get_ll(ll_trigger):
            name = _PVName(ll_trigger)
            if name.dev in {'EVE', 'AFC'}:
                return True
            elif name.dev == 'EVR':
                return name.propty.startswith('OUT')
            else:
                raise Exception('Error: ' + name)

        cls._init()
        ll_chans = cls.get_ll_trigger_names(hl_trigger)
        has_ = [get_ll(name) for name in ll_chans]
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
        cls._get_constants()
        for trig, val in cls._hl_triggers.items():
            chans = {_PVName(chan) for chan in val['channels']}
            for chan in chans:
                tmp = cls._TWDS_EVG.get(chan)
                if tmp is None:
                    raise Exception(
                        'Device ' + chan +
                        ' defined in the high level trigger ' +
                        trig + ' not specified in timing connections data.')
                if not tmp:
                    raise Exception('Device ' + chan +
                                    ' defined in the high level trigger ' +
                                    trig + ' maybe were already used.')
                up_dev = tmp.pop()
                diff_devs = cls._FROM_EVG[up_dev] - chans
                if diff_devs and not chan.dev.endswith('BPM'):
                    raise Exception(
                        'Devices: ' + ' '.join(diff_devs) +
                        ' are connected to the same output of ' +
                        up_dev + ' as ' + chan +
                        ' but are not related to the sam trigger (' +
                        trig + ').')

    @classmethod
    def _get_constants(cls):
        if cls._TWDS_EVG:
            return
        _LLTimeSearch.add_bbb_info()
        _LLTimeSearch.add_crates_info()
        cls._TWDS_EVG = _LLTimeSearch.get_connections_twds_evg()
        cls._FROM_EVG = _LLTimeSearch.get_connections_from_evg()
        cls._EVRs = _LLTimeSearch.get_device_names({'dev': 'EVR'})
        cls._EVEs = _LLTimeSearch.get_device_names({'dev': 'EVE'})
        cls._AFCs = _LLTimeSearch.get_device_names({'dev': 'AFC'})

    @classmethod
    def _init(cls):
        """Initialize the Instance."""
        if cls._hl_triggers:
            return
        text = ''
        if _web.server_online():
            text = _web.high_level_triggers(timeout=_timeout)
        # the execution of text will create the HL_TRIGGS variable.
        exec(text)
        cls._hl_triggers = locals()['HL_TRIGGS']
