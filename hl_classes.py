"""Define the high level classes."""

import logging as _log
import copy as _copy
from siriuspy.timesys.time_data import Connections, IOs, Triggers
from siriuspy.timesys.time_data import Clocks, Events
from siriuspy.namesys import SiriusPVName as _PVName
from as_ti_control.ll_classes import get_ll_trigger_object
from as_ti_control.ll_classes import LL_Event, LL_Clock

Connections.add_bbb_info()
Connections.add_crates_info()
EVG = Connections.get_devices('EVG').pop()
EVRs = Connections.get_devices('EVR')
EVEs = Connections.get_devices('EVE')
AFCs = Connections.get_devices('AFC')
twds_evg = Connections.get_connections_twds_evg()


class _HL_Base:

    def get_database(self):
        """Get the database."""
        return dict()   # dictionary must have key fun_set_pv

    def __init__(self, prefix, callback, channels):
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
        self._HLPROP_2_PVRB = self._get_HLPROP_2_PVRB()
        self.callback = callback
        self.prefix = prefix
        self._hl_props = dict()
        self._interface_props = set()
        self._ll_objs_names = self._get_LL_OBJS_NAMES(channels)
        _log.debug(self.prefix + ' LL names: ' +
                   ' '.join([tr for tr in self._ll_objs_names]))
        self._ll_objs = dict()
        self._connect_kwargs = dict()

    def _get_setpoint_name(self, pvname):
        """Convert readback PV names to setpoint PV names."""
        return pvname.replace('-RB', '-SP').replace('-Sts', '-Sel')

    def _get_HLPROP_2_PVRB(self):
        return dict()

    def _get_LL_OBJS_NAMES(self, channels=None):
        return None

    def _get_LL_OBJ(self, **kwargs):
        return None  # must return the low level object.

    def connect(self):
        _log.info(self.prefix+' -> connecting to LL Devices')
        for chan in self._ll_objs_names:
            _log.debug(self.prefix + ' -> connecting to {0:s}'.format(chan))
            self._ll_objs[chan] = self._get_LL_OBJ(
                                channel=chan,
                                callback=self._on_change_pvs_rb,
                                init_hl_props=_copy.deepcopy(self._hl_props),
                                **self._connect_kwargs)

    def _on_change_pvs_rb(self, channel, prop, value):
        if prop not in self._interface_props:
            if self._hl_props[prop] != value:
                _log.warning(self.prefix + ' RB propty = ' + prop +
                             ' (not HL); ' + ' LL Device = ' + channel +
                             '; New Value = ' + str(value) +
                             '; Expected Value = ' + str(self._hl_props[prop]))
            return
        _log.debug(self.prefix +
                   ' RB propty = {0:s};'.format(prop) +
                   ' LL Device = {0:s};'.format(channel) +
                   ' New Value = {0:s}'.format(str(value)))
        self.callback(self.prefix + self._HLPROP_2_PVRB[prop], value)

    def set_propty(self, prop, value):
        """Function to be called by the IOC to set high level properties.

        It not only sets the new high level property value but also forwards it
        to the low level classes.
        """
        _log.debug(self.prefix +
                   ' propty {0:10s};'.format(prop) +
                   ' Value = {0:s}'.format(str(value)))
        if value == self._hl_props[prop]:
            _log.debug(self.prefix+' new value = old value.')
            return True
        _log.debug(self.prefix +
                   ' propty {0:10s};'.format(prop) +
                   ' Value = {0:s}'.format(str(value)))
        self._hl_props[prop] = value
        for dev, obj in self._ll_objs.items():
            _log.debug(self.prefix+' Sending to LL device = {0:s}'.format(dev))
            obj.set_propty(prop, value)
        return True


class HL_Event(_HL_Base):
    """High Level control of the Events of the EVG."""

    def get_database(self):
        """Create the database of the class."""
        db = dict()
        pre = self.prefix
        db[pre + 'Delay-SP'] = {
            'type': 'float', 'value': self._hl_props['delay'], 'unit': 'us',
            'prec': 3, 'fun_set_pv': lambda x: self.set_propty('delay', x)}
        db[pre + 'Delay-RB'] = {
            'type': 'float', 'value': self._hl_props['delay'],
            'unit': 'us', 'prec': 3}
        db[pre + 'Mode-Sel'] = {
            'type': 'enum', 'enums': Events.MODES,
            'value': self._hl_props['mode'],
            'fun_set_pv': lambda x: self.set_propty('mode', x)}
        db[pre + 'Mode-Sts'] = {
            'type': 'enum', 'enums': Events.MODES,
            'value': self._hl_props['mode']}
        db[pre + 'DelayType-Sel'] = {
            'type': 'enum', 'enums': Events.DELAY_TYPES,
            'value': self._hl_props['delay_type'],
            'fun_set_pv': lambda x: self.set_propty('delay_type', x)}
        db[pre + 'DelayType-Sts'] = {
            'type': 'enum', 'enums': Events.DELAY_TYPES,
            'value': self._hl_props['delay_type']}
        db[pre + 'ExtTrig-Cmd'] = {
            'type': 'int', 'value': self._hl_props['ext_trig'],
            'unit': 'When in External Mode generates Event.',
            'fun_set_pv': lambda x: self.set_propty('ext_trig', x)}
        return db

    def __init__(self, prefix, callback, code):
        """Initialize object."""
        super().__init__(prefix, callback, code)
        self._interface_props = {'delay', 'mode', 'delay_type', 'ext_trig'}
        self._hl_props = {'delay': 0, 'mode': 1,
                          'delay_type': 1, 'ext_trig': 0}

    def _get_HLPROP_2_PVRB(self):
        return {
            'delay': 'Delay-RB',
            'mode': 'Mode-Sts',
            'delay_type': 'DelayType-Sts',
            'ext_trig': 'ExtTrig-Cmd',
            }

    def _get_LL_OBJS_NAMES(self, ev_ll):
        return [EVG + ':' + ev_ll]

    def _get_LL_OBJ(self, **kwargs):
        return LL_Event(**kwargs)


class HL_Clock(_HL_Base):
    """High Level control of the Clocks of the EVG."""

    def get_database(self):
        """Get the database."""
        db = dict()
        pre = self.prefix
        db[pre + 'Freq-SP'] = {
            'type': 'float', 'value': self._hl_props['frequency'],
            'unit': 'kHz', 'prec': 10,
            'fun_set_pv': lambda x: self.set_propty('frequency', x)}
        db[pre + 'Freq-RB'] = {
            'type': 'float', 'value': self._hl_props['frequency'],
            'unit': 'kHz', 'prec': 10}
        db[pre + 'State-Sel'] = {
            'type': 'enum', 'enums': Clocks.STATES,
            'value': self._hl_props['state'],
            'fun_set_pv': lambda x: self.set_propty('state', x)}
        db[pre + 'State-Sts'] = {
            'type': 'enum', 'enums': Clocks.STATES,
            'value': self._hl_props['state']}
        return db

    def __init__(self, prefix, callback, number):
        """Initialize the instance."""
        super().__init__(prefix, callback, number)
        self._interface_props = {'frequency', 'state'}
        self._hl_props = {'frequency': 1.0, 'state': 0}

    def _get_HLPROP_2_PVRB(self):
        return {'frequency': 'Freq-RB', 'state': 'State-Sts'}

    def _get_LL_OBJS_NAMES(self, cl_ll):
        return [EVG + ':' + cl_ll]

    def _get_LL_OBJ(self, **kwargs):
        return LL_Clock(**kwargs)


class HL_Trigger(_HL_Base):
    """High level Trigger interface."""

    def get_database(self):
        """Get the database."""
        db = dict()
        pre = self.prefix

        dic_ = {'type': 'enum', 'enums': Triggers.STATES}
        dic_.update(self._ioc_params['state'])
        db[pre + 'State-Sts'] = _copy.deepcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.set_propty('state', x)
        db[pre + 'State-Sel'] = dic_

        dic_ = {'type': 'enum'}
        dic_.update(self._ioc_params['evg_param'])
        db[pre + 'EVGParam-Sts'] = _copy.deepcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.set_propty('evg_param', x)
        db[pre + 'EVGParam-Sel'] = dic_

        dic_ = {'type': 'float', 'unit': 'us', 'prec': 4,
                'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
                'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
        dic_.update(self._ioc_params['delay'])
        db[pre + 'Delay-RB'] = _copy.deepcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.set_propty('delay', x)
        db[pre + 'Delay-SP'] = dic_

        dic_ = {'type': 'int', 'unit': 'numer of pulses', 'prec': 0,
                'lolo': 1, 'low': 1, 'lolim': 1,
                'hilim': 2001, 'high': 10000, 'hihi': 100000}
        dic_.update(self._ioc_params['pulses'])
        db[pre + 'Pulses-RB'] = _copy.deepcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.set_propty('pulses', x)
        db[pre + 'Pulses-SP'] = dic_

        dic_ = {'type': 'float', 'unit': 'ms', 'prec': 4,
                'lolo': 0.008, 'low': 0.008, 'lolim': 0.008,
                'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
        dic_.update(self._ioc_params['duration'])
        db[pre + 'Duration-RB'] = _copy.deepcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.set_propty('duration', x)
        db[pre + 'Duration-SP'] = dic_

        dic_ = {'type': 'enum', 'enums': Triggers.POLARITIES}
        dic_.update(self._ioc_params['polarity'])
        db[pre + 'Polrty-Sts'] = _copy.deepcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.set_propty('polarity', x)
        db[pre + 'Polrty-Sel'] = dic_

        db2 = dict()
        for prop in self._interface_props:
            rb_name = self._HLPROP_2_PVRB[prop]
            name = pre + rb_name
            db2[name] = db[name]
            name = pre + self._get_setpoint_name(rb_name)
            db2[name] = db[name]
        return db2

    def __init__(self, prefix, callback, channels, hl_props, ioc_params):
        """Appropriately initialize the instance.

        hl_props = is a set with high level properties that will be available
          for changes in the High Level Interface. All the possible values are:
            {'evg_param', 'delay', 'pulses', 'duration', 'state', 'polarity'}
        ioc_params = initial values for all the high level properties.
        """
        super().__init__(prefix, callback, channels)

        self._interface_props = hl_props
        self._ioc_params = ioc_params
        self._hl_props = {k: v['value'] for k, v in ioc_params.items()}
        self._set_EVGParams_ENUMS()
        self._connect_kwargs = {'evg_params': self._EVGParam_ENUMS}

    def _set_EVGParams_ENUMS(self):
        has_clock = []
        for name in self._ll_objs_names:
            if name.dev_type in {'EVE', 'AFC'}:
                has_clock.append(True)
            elif name.dev_type == 'EVR':
                if name.propty.startswith('OUT'):
                    has_clock.append(True)
                else:
                    has_clock.append(False)
            else:
                raise Exception('Error: ' + name)
        dic_ = self._ioc_params['evg_param']
        if all(has_clock):
            dic_['enums'] += tuple(sorted(Clocks.HL2LL_MAP.keys()))
        self._EVGParam_ENUMS = list(dic_['enums'])
        if any(has_clock):
            _log.warning('Some triggers of ' + self.prefix +
                         ' are connected to unsimiliar low level devices.')

    def _get_HLPROP_2_PVRB(self):
        return {
            'evg_param': 'EVGParam-Sts',
            'delay': 'Delay-RB',
            'delay_type': 'DelayType-Sts',
            'pulses': 'Pulses-RB',
            'duration': 'Duration-RB',
            'state': 'State-Sts',
            'polarity': 'Polrty-Sts',
            }

    def _get_LL_OBJS_NAMES(self, chans):
        channels = set()
        for chan in chans:
            up_dev = _PVName(list(twds_evg[chan])[0])
            while up_dev.dev_name not in EVRs | EVEs | AFCs:
                tmp_ = IOs.O2I_MAP[up_dev.dev_type]
                conn_up = tmp_.get(up_dev.propty)
                if conn_up is None:
                    print(IOs.O2I_MAP)
                    print(up_dev.dev_type, up_dev.propty)
                up_dev = _PVName(list(twds_evg[up_dev.dev_name +
                                               ':' + conn_up])[0])
            channels |= {up_dev}
        # print(channels)
        return sorted(channels)

    def _get_LL_OBJ(self, **kwargs):
        return get_ll_trigger_object(**kwargs)
