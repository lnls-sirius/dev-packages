"""Define the high level classes."""

import logging as _log
from copy import deepcopy as _dcopy
from siriuspy.timesys.time_data import Triggers
from siriuspy.timesys.time_data import Clocks, Events
from as_ti_control.ll_classes import get_ll_trigger_object
from as_ti_control.ll_classes import get_ll_trigger_obj_names
from as_ti_control.ll_classes import LL_Event, LL_Clock, LL_EVG, EVG_NAME


# HL == High Level
class _HL_Base:
    """Define a High Level interface.

    Determine how to connect the driver with the classes which communicate
    with low level IOCs.
    """

    _SUFFIX_FOR_PROPS = {}

    @staticmethod
    def _get_LL_OBJ(**kwargs):
        return None  # must return the low level object.

    def get_database(self, db):
        """Get the database."""
        db2 = dict()
        for prop_name in self._interface_props:
            name = self.prefix + prop_name + self._SUFFIX_FOR_PROPS[prop_name]
            db2[name] = db[name]
            name = name.replace('-RB', '-SP').replace('-Sts', '-Sel')
            db2[name] = db[name]
        return db2      # dictionary must have key fun_set_pv

    def __init__(self, prefix, callback):
        """Appropriately initialize the instance.

        prefix = is the first part of the pv name of this object.
        callback = is the callable to be called when readbacks are updated.
        channels = is a list of unique identifiers for all the low level
          objects associated with this object:
            Events: low level event code
            Clocks: clock number
            trigger: <DeviceName>:<Output>
        """
        _log.info(prefix + ' Starting.')
        self.callback = callback
        self.prefix = prefix
        self._my_state = dict()
        self._interface_props = set()
        self._ll_objs_names = list()
        self._ll_objs = dict()
        self._connect_kwargs = dict()

    def connect(self):
        _log.info(self.prefix+' -> connecting to LL Devices')
        for chan in self._ll_objs_names:
            self._ll_objs[chan] = self._get_LL_OBJ(
                                channel=chan,
                                callback=self._on_change_pvs_rb,
                                init_state=_dcopy(self._my_state),
                                **self._connect_kwargs)

    def _on_change_pvs_rb(self, channel, prop_name, value):
        if prop_name not in self._interface_props:
            if self._my_state[prop_name] != value['value']:
                _log.warning(self.prefix + prop_name +
                             ' (not HL); ' + ' LL Device = ' + channel +
                             '; New Value = ' + str(value['value']) +
                             '; Expected Value = ' +
                             str(self._my_state[prop_name]))
            return
        self.callback(self.prefix+prop_name+self._SUFFIX_FOR_PROPS[prop_name],
                      **value)

    def write(self, prop_name, value):
        """Function to be called by the IOC to set high level properties.

        It not only sets the new high level property value but also forwards it
        to the low level classes.
        """
        if value == self._my_state[prop_name]:
            return True
        self._my_state[prop_name] = value
        for dev, obj in self._ll_objs.items():
            obj.write(prop_name, value)
        return True


class HL_EVG(_HL_Base):
    """High Level control of the EVG.

    Designed to convert the repetition rate to Hz instead of the low level
    integer representing the numtiple of the AC line period.

    All other PVs of EVG, like bucket list, are read directly from the
    low level IOC.
    """

    _SUFFIX_FOR_PROPS = {'RepRate': '-RB'}

    @staticmethod
    def _get_LL_OBJ(**kwargs):
        return LL_EVG(**kwargs)

    def get_database(self):
        """Get the database."""
        db = dict()
        pre = self.prefix
        dic_ = {'type': 'float', 'value': self._my_state['RepRate'],
                'unit': 'Hz', 'prec': 6,
                'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
                'hilim': 60, 'high': 60, 'hihi': 60}
        db[pre + 'RepRate-RB'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('RepRate', x)
        db[pre + 'RepRate-SP'] = dic_
        return super().get_database(db)

    def __init__(self, callback):
        """Initialize the instance."""
        super().__init__(EVG_NAME + ':', callback)
        self._interface_props = {'RepRate'}
        self._my_state = {'RepRate': 2.0}
        self._ll_objs_names = [EVG_NAME + ':', ]


class HL_Clock(_HL_Base):
    """High Level control of the Clocks of the EVG."""

    _SUFFIX_FOR_PROPS = {'Freq': '-RB', 'State': '-Sts'}

    @staticmethod
    def _get_LL_OBJ(**kwargs):
        return LL_Clock(**kwargs)

    def get_database(self):
        """Get the database."""
        db = dict()
        pre = self.prefix
        dic_ = {
            'type': 'float', 'value': self._my_state['Freq'],
            'unit': 'kHz', 'prec': 6,
            'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 125000000, 'high': 125000000, 'hihi': 125000000}
        db[pre + 'Freq-RB'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Freq', x)
        db[pre + 'Freq-SP'] = dic_

        db[pre + 'State-Sel'] = {
            'type': 'enum', 'enums': Clocks.STATES,
            'value': self._my_state['State'],
            'fun_set_pv': lambda x: self.write('State', x)}
        db[pre + 'State-Sts'] = {
            'type': 'enum', 'enums': Clocks.STATES,
            'value': self._my_state['State']}
        return super().get_database(db)

    def __init__(self, prefix, callback, cl_ll):
        """Initialize the instance."""
        super().__init__(prefix, callback)
        self._interface_props = {'Freq', 'State'}
        self._my_state = {'Freq': 1.0, 'State': 0}
        self._ll_objs_names = [EVG_NAME + ':' + cl_ll]


class HL_Event(_HL_Base):
    """High Level control of the Events of the EVG.

    Creates
    """

    _SUFFIX_FOR_PROPS = {
        'Delay': '-RB',
        'Mode': '-Sts',
        'DelayType': '-Sts',
        'ExtTrig': '-Cmd'}

    @staticmethod
    def _get_LL_OBJ(**kwargs):
        return LL_Event(**kwargs)

    def get_database(self):
        """Create the database of the class."""
        db = dict()
        pre = self.prefix

        dic_ = {'type': 'float', 'unit': 'us', 'prec': 4,
                'value': self._my_state['Delay'],
                'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
                'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
        db[pre + 'Delay-RB'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Delay', x)
        db[pre + 'Delay-SP'] = dic_

        dic_ = {'type': 'enum', 'enums': Events.MODES,
                'value': self._my_state['Mode'],
                'states': ()}
        db[pre + 'Mode-Sts'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Mode', x)
        db[pre + 'Mode-Sel'] = dic_

        dic_ = {'type': 'enum', 'enums': Events.DELAY_TYPES,
                'value': self._my_state['DelayType']}
        db[pre + 'DelayType-Sts'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('DelayType', x)
        db[pre + 'DelayType-Sel'] = dic_

        db[pre + 'ExtTrig-Cmd'] = {
            'type': 'int', 'value': self._my_state['ExtTrig'],
            'unit': 'When in External Mode generates Event.',
            'fun_set_pv': self.set_ext_trig}
        return super().get_database(db)

    def __init__(self, prefix, callback, ev_ll):
        """Initialize object."""
        super().__init__(prefix, callback)
        self._interface_props = {'Delay', 'DelayType', 'Mode', 'ExtTrig'}
        self._my_state = {'Delay': 0, 'Mode': 1,
                          'DelayType': 1, 'ExtTrig': 0}
        self._ll_objs_names = [EVG_NAME + ':' + ev_ll]

    def set_ext_trig(self, value):
        """Set the external trigger command."""
        self._my_state['ExtTrig'] = 0
        return self.write('ExtTrig', value)


class HL_Trigger(_HL_Base):
    """High level Trigger interface."""

    _SUFFIX_FOR_PROPS = {
        'State': '-Sts',
        'Src': '-Sts',
        'Duration': '-RB',
        'Polarity': '-Sts',
        'Pulses': '-RB',
        'Intlk': '-Sts',
        'Delay': '-RB',
        'DelayType': '-Sts',
        'ConnStatus': '-Mon',
        }

    @staticmethod
    def _get_LL_OBJ(**kwargs):
        return get_ll_trigger_object(**kwargs)

    @staticmethod
    def _get_ll_obj_names(chans):
        return get_ll_trigger_obj_names(chans)

    def get_database(self):
        """Get the database."""
        db = dict()
        pre = self.prefix

        dic_ = {'type': 'enum', 'enums': Triggers.STATES}
        dic_.update(self._pvs_config['State'])
        db[pre + 'State-Sts'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('State', x)
        db[pre + 'State-Sel'] = dic_

        dic_ = {'type': 'enum'}
        dic_.update(self._pvs_config['Src'])
        db[pre + 'Src-Sts'] = _dcopy(dic_)
        db[pre + 'Src-Sts']['enums'] += ('Invalid', )  # for completeness
        dic_['fun_set_pv'] = lambda x: self.write('Src', x)
        db[pre + 'Src-Sel'] = dic_

        dic_ = {'type': 'float', 'unit': 'ms', 'prec': 6,
                'lolo': 0.000008, 'low': 0.000008, 'lolim': 0.000008,
                'hilim': 500, 'high': 1000, 'hihi': 10000}
        dic_.update(self._pvs_config['Duration'])
        db[pre + 'Duration-RB'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Duration', x)
        db[pre + 'Duration-SP'] = dic_

        dic_ = {'type': 'enum', 'enums': Triggers.POLARITIES}
        dic_.update(self._pvs_config['Polarity'])
        db[pre + 'Polarity-Sts'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Polarity', x)
        db[pre + 'Polarity-Sel'] = dic_

        dic_ = {'type': 'int', 'unit': 'numer of pulses',
                'lolo': 1, 'low': 1, 'lolim': 1,
                'hilim': 2001, 'high': 10000, 'hihi': 100000}
        dic_.update(self._pvs_config['Pulses'])
        db[pre + 'Pulses-RB'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Pulses', x)
        db[pre + 'Pulses-SP'] = dic_

        dic_ = {'type': 'enum', 'enums': Triggers.INTLK}
        dic_.update(self._pvs_config['Intlk'])
        db[pre + 'Intlk-Sts'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Intlk', x)
        db[pre + 'Intlk-Sel'] = dic_

        dic_ = {'type': 'float', 'unit': 'us', 'prec': 6,
                'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
                'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
        dic_.update(self._pvs_config['Delay'])
        db[pre + 'Delay-RB'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Delay', x)
        db[pre + 'Delay-SP'] = dic_

        dic_ = {'type': 'enum'}
        dic_.update(self._pvs_config['DelayType'])
        db[pre + 'DelayType-Sts'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('DelayType', x)
        db[pre + 'DelayType-Sel'] = dic_

        dic_ = {
            'type': 'enum',
            'enums': ('Conn OK', 'Dev Dsbl', 'Net Disconn', 'Intlk Actv',
                      'UpLink Disconn', 'DownLink Disconn'),
            'states': (0, 2, 1, 1, 2, 2, ),
            }
        db[pre + 'ConnStatus-Mon'] = _dcopy(dic_)

        return super().get_database(db)

    def __init__(self, prefix, callback, channels, hl_props, pvs_config):
        """Appropriately initialize the instance.

        hl_props = is a set with high level properties that will be available
          for changes in the High Level Interface. All the possible values are:
            {'State', 'Src', 'Duration', 'Polarity', 'Pulses', 'Intlk',
             'Delay', 'DelayType'}
        pvs_config = initial values for all the high level properties.
        """
        super().__init__(prefix, callback)

        self._interface_props = hl_props | {'ConnStatus'}
        self._pvs_config = pvs_config
        self._ll_objs_names = self._get_ll_obj_names(channels)
        self._my_state = {k: v['value'] for k, v in pvs_config.items()}
        self._set_non_homogeneous_params()
        self._connect_kwargs = {'source_enums': self._source_enums}

    def _has_delay_type(self, name):
        if name.dev in ('EVR', 'EVE') and name.propty.startswith('OUT'):
            return True
        else:
            return False

    def _has_clock(self, name):
        if name.dev in {'EVE', 'AFC'}:
            return True
        elif name.dev == 'EVR':
            return True if name.propty.startswith('OUT') else False
        else:
            raise Exception('Error: ' + name)

    def _set_non_homogeneous_params(self):
        has_clock = []
        has_delay_type = []
        for name in self._ll_objs_names:
            has_clock.append(self._has_clock(name))
            has_delay_type.append(self._has_delay_type(name))
        dic_ = self._pvs_config['Src']
        # EVG_params_ENUMS
        if all(has_clock):
            dic_['enums'] += tuple(sorted(Clocks.HL2LL_MAP.keys()))+('Dsbl', )
        elif any(has_clock):
            _log.warning('Some triggers of ' + self.prefix +
                         ' are connected to unsimiliar low level devices.')
        self._source_enums = list(dic_['enums'])
        # Delay Typess
        dic_ = self._pvs_config['DelayType']
        dic_['enums'] = (Triggers.DELAY_TYPES[0], )
        if all(has_delay_type):
            dic_['enums'] = Triggers.DELAY_TYPES
        elif any(has_delay_type):
            _log.warning('Some triggers of ' + self.prefix +
                         ' are connected to unsimiliar low level devices.')
        return
