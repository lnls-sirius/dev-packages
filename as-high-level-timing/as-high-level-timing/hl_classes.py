"""Define the high level classes."""

import logging as _log
import copy as _copy
from siriuspy.timesys.time_data import Connections, IOs, Triggers
from siriuspy.timesys.time_data import Clocks, Events
from siriuspy.namesys import SiriusPVName as _PVName
from ll_classes import get_ll_trigger_object
from ll_classes import LL_Event, LL_Clock

Connections.add_bbb_info()
Connections.add_crates_info()
EVG = Connections.get_devices('EVG').pop()
EVRs = Connections.get_devices('EVR')
EVEs = Connections.get_devices('EVE')
AFCs = Connections.get_devices('AFC')
twds_evg = Connections.get_connections_twds_evg()


class _HL_Base:

    def get_database(self):
        return dict()   # dictionary must have key fun_set_pv

    def __init__(self, prefix, callback, channels):
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
                                init_hl_props=_copy.deepcopy(self._hl_props))

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
        len_rb = len(self._ll_objs_names)
        db[pre + 'Delay-SP'] = {
            'type': 'float', 'count': 1, 'value': 0.0, 'unit': 'us',
            'prec': 3, 'fun_set_pv': lambda x: self.set_propty('delay', x)}
        db[pre + 'Delay-RB'] = {
            'type': 'float', 'count': len_rb,
            'value': 0.0, 'unit': 'us', 'prec': 3}
        db[pre + 'Mode-Sel'] = {
            'type': 'enum', 'enums': Events.MODES, 'value': 1,
            'fun_set_pv': lambda x: self.set_propty('mode', x)}
        db[pre + 'Mode-Sts'] = {'type': 'int', 'value': 1, 'count': len_rb}
        db[pre + 'DelayType-Sel'] = {
            'type': 'enum', 'enums': Events.DELAY_TYPES, 'value': 1,
            'fun_set_pv': lambda x: self.set_propty('delay_type', x)}
        db[pre + 'DelayType-Sts'] = {
            'type': 'int', 'value': 1, 'count': len_rb}
        db[pre + 'Connections-Mon'] = {
            'type': 'int', 'value': 0, 'count': len_rb}
        return db

    def __init__(self, prefix, callback, code):
        """Initialize object."""
        super().__init__(prefix, callback, code)
        self._interface_props = {'delay', 'mode', 'delay_type'}
        self._hl_props = {'delay': 0, 'mode': 0, 'delay_type': 0}

    def _get_setpoint_name(self, pvname):
        """Convert readback PV names to setpoint PV names."""
        return pvname.replace('-RB', '-SP').replace('-Sts', '-Sel')

    def _get_HLPROP_2_PVRB(self):
        return {
            'delay': 'Delay-RB',
            'mode': 'Mode-Sts',
            'delay_type': 'DelayType-Sts',
            }

    def _get_LL_OBJS_NAMES(self, code):
        return [EVG + ':' + Events.LL_TMP.format(code)]

    def _get_LL_OBJ(self, **kwargs):
        return LL_Event(**kwargs)


class HL_Clock(_HL_Base):
    """High Level control of the Clocks of the EVG."""

    def get_database(self):
        """Get the database."""
        db = dict()
        pre = self.prefix
        len_rb = len(self._ll_objs_names)
        db[pre + 'Freq-SP'] = {
            'type': 'float', 'value': 1.0, 'unit': 'kHz', 'prec': 10,
            'fun_set_pv': lambda x: self.set_propty('frequency', x)}
        db[pre + 'Freq-RB'] = {
            'type': 'float', 'count': len_rb, 'value': 0.0,
            'unit': 'kHz', 'prec': 10}
        db[pre + 'State-Sel'] = {
            'type': 'enum', 'enums': Clocks.STATES, 'value': 0,
            'fun_set_pv': lambda x: self.set_propty('state', x)}
        db[pre + 'State-Sts'] = {
            'type': 'int', 'value': 1, 'count': len_rb}
        return db

    def __init__(self, prefix, callback, number):
        """Initialize the instance."""
        super().__init__(prefix, callback, number)
        self._interface_props = {'frequency', 'state'}
        self._hl_props = {'frequency': 0, 'state': 0}

    def _get_HLPROP_2_PVRB(self):
        return {'frequency': 'Freq-RB', 'state': 'State-Sts'}

    def _get_LL_OBJS_NAMES(self, number):
        return [EVG + ':' + Clocks.LL_TMP.format(number)]

    def _get_LL_OBJ(self, **kwargs):
        return LL_Clock(**kwargs)


class HL_Trigger(_HL_Base):
    """High level Trigger interface."""

    def get_database(self):
        db = dict()
        pre = self.prefix
        db[pre + 'State-Sel'] = {
            'type': 'enum', 'value': 0, 'enums': Triggers.STATES,
            'fun_set_pv': lambda x: self.set_propty('state', x)}
        db[pre + 'State-Sts'] = {
            'type': 'int',  'value': 0}
        db[pre + 'EVGParam-Sel'] = {
            'type': 'enum', 'value': 0, 'enums': self._EVGParam_ENUMS,
            'fun_set_pv': lambda x: self.set_propty('evg_param', x)}
        db[pre + 'EVGParam-Sts'] = {
            'type': 'enum',  'value': 0, 'enums': self._EVGParam_ENUMS}
        db[pre + 'Delay-SP'] = {
            'type': 'float', 'value': 0.0, 'unit': 'us', 'prec': 4,
            'fun_set_pv': lambda x: self.set_propty('delay', x)}
        db[pre + 'Delay-RB'] = {
            'type': 'float', 'value': 0.0, 'unit': 'us', 'prec': 4}
        db[pre + 'Pulses-SP'] = {
            'type': 'int',  'value': 1,
            'fun_set_pv': lambda x: self.set_propty('pulses', x)}
        db[pre + 'Pulses-RB'] = {
            'type': 'int',  'value': 1}
        db[pre + 'Duration-SP'] = {
            'type': 'float', 'value': 0.0, 'unit': 'ms', 'prec': 4,
            'fun_set_pv': lambda x: self.set_propty('duration', x)}
        db[pre + 'Duration-RB'] = {
            'type': 'float', 'value': 0.0, 'unit': 'ms', 'prec': 4}
        db[pre + 'Polrty-Sel'] = {
            'type': 'enum', 'value': 0, 'enums': Triggers.POLARITIES,
            'fun_set_pv': lambda x: self.set_propty('polarity', x)}
        db[pre + 'Polrty-Sts'] = {
            'type': 'int',  'value': 0}
        db2 = dict()
        for prop in self._interface_props:
            rb_name = self._HLPROP_2_PVRB[prop]
            name = pre + rb_name
            db2[name] = db[name]
            name = pre + self._get_setpoint_name(rb_name)
            db2[name] = db[name]
        return db2

    def __init__(self, prefix, callback, channels,
                 events, hl_props, init_vals):
        super().__init__(prefix, callback, channels)
        #  {'evg_param', 'delay', 'pulses', 'duration', 'state', 'polarity'}
        self._interface_props = hl_props
        self._EVENTS = events
        self._hl_props = init_vals
        self._set_EVGParams_ENUMS()

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
        self._EVGParam_ENUMS = list(self._EVENTS)
        if all(has_clock):
            self._EVGParam_ENUMS += sorted(Clocks.HL2LL_MAP.keys())
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
        print(channels)
        return sorted(channels)

    def _get_LL_OBJ(self, **kwargs):
        return get_ll_trigger_object(**kwargs)

    def connect(self):
        _log.info(self.prefix+' -> connecting to LL Devices')
        for chan in self._ll_objs_names:
            _log.debug(self.prefix + ' -> connecting to {0:s}'.format(chan))
            self._ll_objs[chan] = self._get_LL_OBJ(
                                channel=chan,
                                callback=self._on_change_pvs_rb,
                                init_hl_props=_copy.deepcopy(self._hl_props),
                                evg_params=self._EVGParam_ENUMS)
