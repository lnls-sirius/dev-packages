"""Controller defitions."""
from epics import PV as _PV
import time as _time
import uuid as _uuid
import random as _random
import numpy as _np
import re as _re

from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.magnet import util as _mutil
from siriuspy.epics.computed_pv import ComputedPV as _ComputedPV
from siriuspy.pwrsupply import sync as _sync
from siriuspy.factory import NormalizerFactory as _NormalizerFactory
from siriuspy.csdevice.pwrsupply import default_wfmlabels as _default_wfmlabels
from siriuspy.csdevice.pwrsupply import default_wfmsize as _default_wfmsize
from siriuspy.csdevice.pwrsupply import default_intlklabels as \
    _default_intlklabels
from siriuspy.pwrsupply_orig.waveform import PSWaveForm as _PSWaveForm
from siriuspy.pwrsupply_orig.cycgen import PSCycGenerator as _PSCycGenerator
from siriuspy.pulsedps.model import PulsedPowerSupplySim

_trigger_timeout_default = 0.002  # [seconds]
_trigger_interval_default = 0.490/_default_wfmsize  # [seconds]




class Controller:
    """Base class defining controller interface."""

    def read(self, field):
        """Return field value."""
        raise NotImplementedError

    def write(self, field, value):
        """Write value to a field."""
        raise NotImplementedError

    def add_callback(self, func):
        """Add callback function."""
        raise NotImplementedError


class PSEpicsController(Controller):
    """Create real PVs to control PS attributes."""

    _is_strength = _re.compile('(Energy|KL|SL|Kick).+$')

    def __init__(self, psnames, fields, prefix='', device_name=''):
        """Create epics PVs and expose them through public controller API."""
        # Attributes use build a full PV address
        self._psnames = psnames
        self._fields = fields
        self._sort_fields()
        self._prefix = prefix
        if device_name:
            self.device_name = device_name
        else:
            self.device_name = self._psnames[0]
        # Holds PVs objects
        self._pvs = dict()
        self._create_pvs()

    # Public controller API
    def read(self, field):
        """Read a field value."""
        if self._pvs[field].connected:
            return self._pvs[field].get()
        else:
            print("Not connected")

    def write(self, field, value):
        """Write a value to a field."""
        if self._pvs[field].connected:
            self._pvs[field].put(value)
        else:
            print("Not connected")

    def add_callback(self, func):
        """Add callback to field."""
        if not callable(func):
            raise ValueError("Tried to set non callable as a callback")
        else:
            for pv in self._pvs.values():
                pv.add_callback(func)

    # Private
    def _create_pvs(self):
        # Normally create normal PV objects
        # In case more than one source is supplied creates a SyncPV
        # In case the device is a Magnet with a normalized force being supplied
        # as one of the fields, a NormalizedPV is created
        for field in self._fields:
            self._pvs[field] = self._create_pv(field)

    def _sort_fields(self):
        fields = []
        for field in self._fields:
            if not self._is_strength.match(field):
                fields.insert(0, field)
            else:
                fields.append(field)

        self.fields = fields

    def _get_sync_obj(self, field):
        # Return SyncWrite or SyncRead object
        if "SP" in field or "Sel" in field or "Cmd" in field:
            return _sync.SyncWrite()
        else:
            return _sync.SyncRead()

    def _create_pv(self, field):
        # Build either a real or computed PV
        if len(self._psnames) > 1:
            # Sync object used to sync pvs
            sync = self._get_sync_obj(field)
            # Real PVs(names) supplied to ComputedPV
            pvs = [self._prefix + device_name + ":" + field
                   for device_name in self._psnames]
            # Name of the ComputedPV
            pvname = self.device_name + ":" + field
            # Create a virtual PV (ComputedPV)
            x = _ComputedPV(pvname, sync, *pvs)
            return x
        else:
            return _PV(self._prefix + self.device_name + ":" + field)


class MAEpicsController(PSEpicsController):
    """Create real PVs to control PS attributes."""

    def __init__(self, maname, **kwargs):
        """Create epics PVs and expose them through public controller API."""
        # Attributes use build a full PV address
        self._maname = _SiriusPVName(maname)
        super().__init__(
            self._psnames(),
            device_name=self._maname.replace("MA", "PS").replace("PM", "PU"),
            **kwargs)

    def _create_pv(self, field):
        # Build either a real or computed PV
        if MAEpicsController._is_strength.match(field):  # NormalizedPV
            # if len(self._maname) > 1:
            #     raise ValueError("Syncing Magnets?")
            pvname = self._prefix + self._maname + ":" + field
            str_obj = self._get_normalizer(self._maname)
            pvs = self._get_str_pv(field)
            return _ComputedPV(pvname, str_obj, *pvs)
        else:
            return super()._create_pv(field)

    def _get_normalizer(self, device_name):
        # Return Normalizer object
        return _NormalizerFactory.factory(device_name)

    def _get_str_pv(self, field):
        ma_class = _mutil.magnet_class(self._maname)
        if 'dipole' == ma_class:
            return [self._pvs[field.replace('Energy', 'Current')], ]
        elif 'pulsed' == ma_class:
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self._prefix + dipole_name
            return [self._pvs[field.replace('Kick', 'Voltage')],
                    dipole + ":" + field.replace('Kick', 'Current')]
        elif 'trim' == ma_class:
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self._prefix + dipole_name
            fam_name = _mutil.get_magnet_family_name(self._maname)
            fam = self._prefix + fam_name
            field = field.replace('KL', 'Current')
            return [self._pvs[field],
                    dipole + ':' + field,
                    fam + ':' + field]
        else:
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self._prefix + dipole_name
            field = field.replace('KL', 'Current').replace('SL', 'Current')\
                .replace('Kick', 'Current')
            return [self._pvs[field],
                    dipole + ":" + field]

    def _psnames(self):
        ma_class = _mutil.magnet_class(self._maname)
        if 'dipole' == ma_class:
            if 'SI' == self._maname.sec:
                return ['SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2']
            elif 'BO' == self._maname.sec:
                return ['BO-Fam:PS-B-1', 'BO-Fam:PS-B-2']
        elif 'pulsed' == ma_class:
            return [self._maname.replace(':PM', ':PU')]

        return [self._maname.replace(':MA', ':PS')]


class UDCController(Controller):
    """UDC Controller."""

    pass


class _BaseControllerSim(Controller):
    """Base class that implements a controller interface.

        This class contains a number of pure virtual methods that should be
    implemented in sub classes. It also contains methods that implement
    most of the controller logic.
    """

    def __init__(self, callback=None, psname=None, cycgen=None):
        self._psname = psname
        self._init_cycgen(cycgen)
        self._set_cycling_state(False)
        self._set_timestamp_cycling(None)
        self._trigger_timeout = _trigger_timeout_default
        self._trigger_interval = _trigger_interval_default
        self._callbacks = {} if callback is None else {_uuid.uuid4(): callback}
        self.update_state(init=True)

        self._meth_dict_read = {
            'CtrlMode-Mon': 'ctrlmode',
            'PwrState-Sel': 'pwrstate',
            'PwrState-Sts': 'pwrstate',
            'OpMode-Sel': 'opmode',
            'OpMode-Sts': 'opmode',
            'Abort-Cmd': 'abort_counter',
            'Reset-Cmd': 'reset_counter',
            'Intlk-Mon': 'intlk',
            'IntlkLabels-Cte': 'intlklabels',
            'Current-SP': 'current_sp',
            'Current-RB': 'current_sp',
            'CurrentRef-Mon': 'current_ref',
            'Current-Mon': 'current_load',
            'WfmIndex-SP': 'wfmindex',
            'WfmIndex-RB': 'wfmindex',
            'WfmIndex-Mon': 'wfmindex',
            'WfmLabel-SP': 'wfmlabel',
            'WfmLabel-RB': 'wfmlabel',
            'WfmLabels-Mon': 'wfmlabels',
            'WfmData-SP': 'wfmdata',
            'WfmData-RB': 'wfmdata',
            'WfmLoad-Sel': 'wfmload',
            'WfmLoad-Sts': 'wfmload',
            'WfmSave-Cmd': 'wfmsave',
        }

        self._meth_dict_write = {
            'PwrState-Sel': 'pwrstate',
            'OpMode-Sel': 'opmode',
            'Current-SP': 'current_sp',
            'Abort-Cmd': 'abort',
            'Reset-Cmd': 'reset',
            'WfmLabel-SP': 'wfmlabel',
            'WfmLoad-SP': 'wfmload',
            'WfmData-SP': 'wfmdata',
            'WfmSave-SP': 'wfmsave',
        }

    # --- class interface - properties ---

    def read(self, field):
        """Return field value."""
        if field in self._meth_dict_read:
            return getattr(self, self._meth_dict_read[field])
        else:
            raise ValueError('Invalid field name "'+field+'"')

    def write(self, field, value):
        """Set field value."""
        if field in self._meth_dict_write:
            setattr(self, self._meth_dict_write[field], value)
        else:
            raise ValueError('Invalid field name "'+field+'"')

    @property
    def psname(self):
        return self._psname

    @property
    def connected(self):
        return True

    @property
    def trigger_timeout(self):
        return self._trigger_timeout

    @trigger_timeout.setter
    def trigger_timeout(self, value):
        value = float(value) if value > 0.0 else 0.0
        if value != self._trigger_timeout:
            self._trigger_timeout = value
            self.update_state(trigger_timeout=True)

    @property
    def trigger_interval(self):
        return self._trigger_interval

    @trigger_interval.setter
    def trigger_interval(self, value):
        self._trigger_interval = float(value) if value > 0.0 else 0.0

    @property
    def ctrlmode(self):
        return self._get_ctrlmode()

    @property
    def pwrstate(self):
        return self._get_pwrstate()

    @pwrstate.setter
    def pwrstate(self, value):
        if value not in _et.indices('OffOnTyp'):
            return
        # if value != self.pwrstate:
        #     self._set_pwrstate(value)
        #     self.update_state(pwrstate=True)
        self._set_pwrstate(value)
        self.update_state(pwrstate=True)

    @property
    def opmode(self):
        return self._get_opmode()

    @opmode.setter
    def opmode(self, value):
        if value not in _et.indices('PSOpModeTyp'):
            return
        # if value != self.opmode:
        #     self._set_cycling_state(False)
        #     self._set_timestamp_trigger(None)
        #     self._set_timestamp_cycling(None)
        #     self._set_wfmindex(0)
        #     self._set_cmd_abort_issued(False)
        #     if value in (_et.idx.SlowRef,_et.idx.SlowRefSync):
        #         self.current_sp = self.current_ref
        #     self._set_opmode(value)
        #     self.update_state(opmode=True)
        self._set_cycling_state(False)
        self._set_timestamp_trigger(None)
        self._set_timestamp_cycling(None)
        self._set_wfmindex(0)
        self._set_cmd_abort_issued(False)
        if value in (_et.idx.SlowRef, _et.idx.SlowRefSync):
            self.current_sp = self.current_ref
        self._set_opmode(value)
        self.update_state(opmode=True)

    @property
    def reset_counter(self):
        return self._get_reset_counter()

    def reset(self):
        self._inc_reset_counter()
        self.current_sp = 0.0
        self._set_current_ref(0.0)
        self.opmode = _et.idx.SlowRef
        self._intlk_reset()  # Try to reset interlock
        self.update_state(reset=True)

    @property
    def abort_counter(self):
        return self._get_abort_counter()

    def abort(self):
        self._inc_abort_counter()
        if self.opmode in (_et.idx.SlowRefSync, _et.idx.FastRef,
                           _et.idx.MigWfm, _et.idx.Cycle):
            self.opmode = _et.idx.SlowRef
        elif self.opmode == _et.idx.RmpWfm:
            self._set_cmd_abort_issued(True)
        self.update_state(abort=True)

    @property
    def timestamp_trigger(self):
        self._process_trigger_timed_out()
        return self._get_timestamp_trigger()

    @property
    def trigger_timed_out(self):
        self._process_trigger_timed_out()
        return self._get_trigger_timed_out()

    @property
    def intlk(self):
        return self._get_intlk()

    @property
    def intlklabels(self):
        return self._get_intlklabels()

    @property
    def current_min(self):
        return self._get_current_min()

    @property
    def current_max(self):
        return self._get_current_max()

    @current_min.setter
    def current_min(self, value):
        if value is None or self.current_max is None or \
           value <= self.current_max:
            self._set_current_min(value)
        else:
            raise ValueError('Attribution of current_min > current_max!')

    @current_max.setter
    def current_max(self, value):
        if value is None or self.current_min is None or \
           value >= self.current_min:
            self._set_current_max(value)
        else:
            raise ValueError('Attribution of current_max < current_min!')

    @property
    def current_sp(self):
        return self._get_current_sp()

    @current_sp.setter
    def current_sp(self, value):
        self._set_current_sp(float(value))
        self.update_state(current_sp=True)

    @property
    def current_ref(self):
        return self._get_current_ref()

    @property
    def current_load(self):
        return self._get_current_load()

    @property
    def wfmindex(self):
        return self._get_wfmindex()

    @property
    def wfmlabels(self):
        return self._get_wfmlabels()

    @property
    def wfmlabel(self):
        return self._get_wfmlabel()

    @wfmlabel.setter
    def wfmlabel(self, value):
        # if value != self.wfmlabel:
        #     self._set_wfmlabel(value)
        #     self.update_state(wfmlabel=True)
        self._set_wfmlabel(value)
        self.update_state(wfmlabel=True)

    @property
    def wfmload(self):
        return self._get_wfmload()

    @wfmload.setter
    def wfmload(self, value):
        if value < len(_default_wfmlabels):
            self._set_wfmload(value)
            self.update_state(wfmload=True)

    @property
    def _wfmload_changed(self):
        return self._get_wfmload_changed()

    @_wfmload_changed.setter
    def _wfmload_changed(self, value):
        self._set_wfmload_changed(value)

    @property
    def wfmdata(self):
        return self._get_wfmdata()

    @wfmdata.setter
    def wfmdata(self, value):
        # if (value != self.wfmdata).any():
        #     self._set_wfmdata_changed(True)
        #     self._set_wfmdata(value)
        #     self.update_state(wfmdata=True)
        self._set_wfmdata_changed(True)
        self._set_wfmdata(value)
        self.update_state(wfmdata=True)

    @property
    def _wfmdata_changed(self):
        return self._get_wfmdata_changed()

    @_wfmdata_changed.setter
    def _wfmdata_changed(self, value):
        self._set_wfmdata_changed(value)

    @property
    def wfmsave(self):
        return self._get_wfmsave()

    @wfmsave.setter
    def wfmsave(self, value):
        self._set_wfmsave(value)
        self.update_state(wfmsave=True)

    @property
    def time(self):
        return self._get_time()

    def add_callback(self, callback, index=None):
        index = _uuid.uuid4() if index is None else index
        self._callbacks[index] = callback
        return index

    def remove_callback(self, index):
        if index in self._callbacks:
            del self._callbacks[index]

    def clear_callbacks(self):
        self._callbacks.clear()

    # --- class interface - methods ---

    def trigger_signal(self, delay=0, nrpts=1):
        if delay != 0:
            _time.sleep(delay)
        self._process_trigger_timed_out()
        self._process_trigger_signal(nrpts)

    def update_state(self, **kwargs):
        self._process_trigger_timed_out()
        self._process_pending_waveform_update()
        if self.opmode == _et.idx.SlowRef:
            self._update_SlowRef(**kwargs)
        elif self.opmode == _et.idx.SlowRefSync:
            self._update_SlowRefSync(**kwargs)
        elif self.opmode == _et.idx.FastRef:
            self._update_FastRef(**kwargs)
        elif self.opmode == _et.idx.RmpWfm:
            self._update_RmpWfm(**kwargs)
        elif self.opmode == _et.idx.MigWfm:
            self._update_MigWfm(**kwargs)
        elif self.opmode == _et.idx.Cycle:
            self._update_Cycle(**kwargs)
        else:
            pass

    def fofb_signal(self, current):
        if self.opmode == _et.idx.FastRef:
            self._set_current_ref(float(current))
            self.update_state(fofb_signal=True)

    def _init_cycgen(self, cycgen):
        if cycgen is not None:
            self._cycgen = cycgen
        else:
            if self.current_min is None:
                self._cycgen = _PSCycGenerator(interval=5.0)
            elif self.current_min >= 0.0:
                self._cycgen = _PSCycGenerator(interval=30.0,
                                               cycgen_type='triangle',
                                               period=5.0,
                                               amplitude=abs(self.current_max))
            else:
                self._cycgen = _PSCycGenerator(interval=30.0,
                                               cycgen_type='exp_cos',
                                               period=2.0, tau=10,
                                               amplitude=abs(self.current_max))

    def _process_trigger_timed_out(self):
        if self.opmode != _et.idx.RmpWfm:
            return
        if self._get_trigger_timed_out():
            self._set_wfmindex(0)

    def _process_pending_waveform_update(self):
        if self.wfmindex == 0:
            if self._wfmdata_changed:
                self._wfmdata_changed = False
                self._wfmdata_in_use = [datum for datum in self._waveform.data]
            if self._wfmload_changed:
                self._wfmload_changed = False
                self._wfmdata_in_use = [datum for datum in self._waveform.data]

    def _update_current_ref(self, value):
        if self.pwrstate == _et.idx.Off:
            self._set_current_ref(0.0)
        else:
            value = self._check_current_ref_limits(value)
            self._set_current_ref(value)

    def _finilize_cycgen(self):
        self._update_current_ref(0.0)
        self.opmode = _et.idx.SlowRef

    def _update_SlowRef(self, **kwargs):
        self._update_current_ref(self.current_sp)

    def _update_SlowRefSync(self, **kwargs):
        if 'trigger_signal' in kwargs:
            self._update_current_ref(self.current_sp)
        else:
            self._update_current_ref(self.current_ref)

    def _update_FastRef(self, **kwargs):
        pass

    def _update_RmpWfm(self, **kwargs):
        if 'trigger_signal' in kwargs:
            scan_value = self._wfmdata_in_use[self._wfmindex]
            self._wfmindex = (self._wfmindex + 1) % len(self._wfmdata_in_use)
            if self._cmd_abort_issued and self._wfmindex == 0:
                self.opmode = _et.idx.SlowRef
        else:
            if self._cmd_abort_issued and self._wfmindex == 0:
                self.opmode = _et.idx.SlowRef
            scan_value = self.current_ref
        self._update_current_ref(scan_value)

    def _update_MigWfm(self, **kwargs):
        if 'trigger_signal' in kwargs:
            scan_value = self._wfmdata_in_use[self._wfmindex]
            if self._cmd_abort_issued:
                self.opmode = _et.idx.SlowRef
            else:
                self._wfmindex = (self._wfmindex + 1) % \
                    len(self._wfmdata_in_use)
            self._update_current_ref(scan_value)
            if self._wfmindex == 0:
                self.opmode = _et.idx.SlowRef
        else:
            self._update_current_ref(self.current_ref)

    def _update_Cycle(self, **kwargs):
        if 'trigger_signal' in kwargs:
            self._set_cycling_state(True)
        self._process_Cycle()

    def _check_current_ref_limits(self, value):
        value = value if self.current_min is None else \
            max(value, self.current_min)
        value = value if self.current_max is None else \
            min(value, self.current_max)
        return float(value)

    def __str__(self):
        self.update_state()
        st = '--- Controller ---\n'
        propty = 'opmode'
        st += '\n{0:<25s}: {1}'.format(propty, _et.conv_idx2key('PSOpModeTyp',
                                       self.opmode))
        propty = 'pwrstate'
        st += '\n{0:<25s}: {1}'.format(propty, _et.conv_idx2key('OffOnTyp',
                                       self.pwrstate))
        propty = 'intlk'
        st += '\n{0:<25s}: {1}'.format(propty, self.intlk)
        propty = 'intlklabels'
        st += '\n{0:<25s}: {1}'.format(propty, self.intlklabels)
        propty = 'reset_counter'
        st += '\n{0:<25s}: {1}'.format(propty, self.reset_counter)
        propty = 'abort_counter'
        st += '\n{0:<25s}: {1}'.format(propty, self.abort_counter)
        propty = 'current_min'
        st += '\n{0:<25s}: {1}'.format(propty, self.current_min)
        propty = 'current_max'
        st += '\n{0:<25s}: {1}'.format(propty, self.current_max)
        propty = 'current_sp'
        st += '\n{0:<25s}: {1}'.format(propty, self.current_sp)
        propty = 'current_ref'
        st += '\n{0:<25s}: {1}'.format(propty, self.current_ref)
        propty = 'current_load'
        st += '\n{0:<25s}: {1}'.format(propty, self.current_load)
        propty = 'wfmload'
        st += '\n{0:<25s}: {1}'.format(propty, self.wfmlabels[self.wfmload])
        propty = 'wfmdata'
        st += '\n{0:<25s}: {1}'.format(propty, '['+str(self.wfmdata[0]) +
                                       ' ... '+str(self.wfmdata[-1])+']')
        propty = 'wfmsave'
        st += '\n{0:<25s}: {1}'.format(propty, self.wfmsave)
        propty = 'wfmindex'
        st += '\n{0:<25s}: {1}'.format(propty, self.wfmindex)
        propty = 'trigger_timed_out'
        st += '\n{0:<25s}: {1}'.format(propty, self.trigger_timed_out)
        propty = 'cycling_state'
        st += '\n{0:<25s}: {1}'.format(propty, self._get_cycling_state())

        propty = '_timestamp_now'
        st += '\n{0:<25s}: {1}'.format(propty, _get_timestamp(self.time))
        try:
            propty = '_timestamp_opmode'
            st += '\n{0:<25s}: {1}'.format(
                propty, _get_timestamp(self._timestamp_opmode))
        except:
            pass
        try:
            propty = '_timestamp_pwrstate';  st += '\n{0:<25s}: {1}'.format(propty, _get_timestamp(self._timestamp_pwrstate))
        except:
            pass
        try:
            if self.timestamp_trigger is not None:
                propty = '_timestamp_trigger';   st += '\n{0:<25s}: {1}'.format(propty, _get_timestamp(self.timestamp_trigger))
            else:
                propty = '_timestamp_trigger';   st += '\n{0:<25s}: {1}'.format(propty, str(None))
        except:
            pass
        try:
            if self._get_timestamp_cycling() is not None:
                propty = '_timestamp_cycling';  st += '\n{0:<25s}: {1}'.format(propty, _get_timestamp(self._timestamp_cycling))
            else:
                propty = '_timestamp_cycling';   st += '\n{0:<25s}: {1}'.format(propty, str(None))
        except:
            pass

        return st

    # --- pure virtual methods ---

    def _get_ctrlmode(self):
        pass

    def _get_pwrstate(self):
        pass

    def _set_pwrstate(self, value):
        pass

    def _get_opmode(self):
        pass

    def _set_opmode(self, value):
        pass

    def _set_cmd_abort_issued(self, value):
        pass

    def _get_reset_counter(self):
        pass

    def _inc_reset_counter(self):
        pass

    def _get_abort_counter(self):
        pass

    def _inc_abort_counter(self):
        pass

    def _get_timestamp_trigger(self):
        pass

    def _set_timestamp_trigger(self, value):
        pass

    def _get_timestamp_opmode(self):
        pass

    def _set_timestamp_opmode(self, value):
        pass

    def _get_timestamp_cycling(self):
        pass

    def _set_timestamp_cycling(self, value):
        pass

    def _get_intlk(self):
        pass

    def _intlk_reset(self):
        pass

    def _get_intlklabels(self):
        pass

    def _get_trigger_timed_out(self, delay):
        pass

    def _set_trigger_timed_out(self):
        pass

    def _get_current_min(self):
        pass

    def _get_current_max(self):
        pass

    def _set_current_min(self, value):
        pass

    def _set_current_max(self, value):
        pass

    def _get_current_sp(self):
        pass

    def _set_current_sp(self, value):
        pass

    def _get_current_ref(self):
        pass

    def _get_current_load(self):
        pass

    def _get_wfmindex(self):
        pass

    def _get_wfmlabels(self):
        pass

    def _get_wfmlabel(self):
        pass

    def _set_wfmlabel(self, value):
        pass

    def _get_wfmload(self):
        pass

    def _set_wfmload(self, value):
        pass

    def _get_wfmload_changed(self):
        pass

    def _set_wfmload_changed(self, value):
        pass

    def _get_wfmdata(self):
        pass

    def _set_wfmdata(self, value):
        pass

    def _get_wfmdata_changed(self):
        pass

    def _set_wfmdata_changed(self, value):
        pass

    def _get_wfmsave(self):
        pass

    def _set_wfmsave(self, value):
        pass

    def _set_current_ref(self, value):
        pass

    def _set_wfmindex(self, value):
        pass

    def _get_time(self):
        pass

    def _process_trigger_signal(self, nrpts):
        pass

    def _get_cycling_state(self):
        pass

    def _set_cycling_state(self, value):
        pass

    def _process_Cycle(self):
        pass


class ControllerSim(_BaseControllerSim):
    """controllerSim class."""

    def __init__(self,
                 psname=None,
                 current_min=None,
                 current_max=None,
                 current_std=0.0,
                 random_seed=None,
                 **kwargs):
        """Init method."""
        self._time_simulated = None
        now = self.time
        if random_seed is not None:
            _random.seed(random_seed)
        self._psname = psname
        self._ctrlmode = _et.idx.Remote # CtrlMode state
        self._pwrstate = _et.idx.Off  # power state
        self._timestamp_pwrstate = now  # last time pwrstate was changed
        self._opmode = _et.idx.SlowRef  # operation mode state
        self._timestamp_opmode = now  # last time opmode was changed
        self._abort_counter = 0  # abort command counter
        self._cmd_abort_issued = False
        self._reset_counter = 0  # reset command counter
        self._cmd_reset_issued = False
        self._intlk = 0  # interlock signals
        self._intlklabels = _default_intlklabels
        self._timestamp_trigger = None  # last time trigger signal was received
        self.current_max = current_max
        self.current_min = current_min
        self._current_std = current_std  # std dev of error added to outp curr
        self._current_sp = 0.0  # init SP value
        self._current_ref = self._current_sp  # reference current of DSP
        self._current_load = self._current_ref  # current value supplied to mag
        self._init_waveforms()  # initialize waveform data

        super().__init__(psname=psname, **kwargs)

    def _get_ctrlmode(self):
        return self._ctrlmode

    def _get_pwrstate(self):
        return self._pwrstate

    def _set_pwrstate(self, value):
        self._timestamp_pwrstate = self.time
        self._pwrstate = value
        self._mycallback(pvname='pwrstate')

    def _get_opmode(self):
        return self._opmode

    def _set_opmode(self, value):
        self._timestamp_opmode = self.time
        self._opmode = value
        self._mycallback(pvname='opmode')

    def _set_cmd_abort_issued(self, value):
        self._cmd_abort_issued = value

    def _get_reset_counter(self):
        return self._reset_counter

    def _inc_reset_counter(self):
        self._reset_counter += 1
        self._mycallback(pvname='reset')

    def _get_abort_counter(self):
        return self._abort_counter

    def _inc_abort_counter(self):
        self._abort_counter += 1
        self._mycallback(pvname='abort')

    def _get_timestamp_trigger(self):
        return self._timestamp_trigger

    def _set_timestamp_trigger(self, value):
        self._timestamp_trigger = value

    def _get_timestamp_cycling(self):
        return self._timestamp_cycling

    def _set_timestamp_cycling(self, value):
        self._timestamp_cycling = value

    def _get_timestamp_opmode(self):
        return self._timestamp_opmode

    def _set_timestamp_opmode(self, value):
        self._timestamp_opmode = value

    def _get_intlk(self):
        return self._intlk

    def _intlk_reset(self):
        self._intlk = 0

    def _get_intlklabels(self):
        return self._intlklabels

    def _get_current_min(self):
        return None if not hasattr(self, '_current_min') else self._current_min

    def _get_current_max(self):
        return None if not hasattr(self, '_current_max') else self._current_max

    def _set_current_min(self, value):
        self._current_min = value

    def _set_current_max(self, value):
        self._current_max = value

    def _get_current_sp(self):
        return self._current_sp

    def _set_current_sp(self, value):
        self._current_sp = value
        self._mycallback(pvname='current_sp')

    def _get_current_ref(self):
        return self._current_ref

    def _get_current_load(self):
        return self._current_load

    def _get_wfmindex(self):
        return self._wfmindex

    def _set_wfmindex(self, value):
        self._wfmindex = value

    def _get_wfmlabels(self):
        return _np.array([label for label in self._wfmlabels])

    def _get_wfmlabel(self):
        return self._waveform.label

    def _set_wfmlabel(self, value):
        self._waveform.label = value
        self._wfmlabels[self._wfmslot] = value
        self._mycallback(pvname='wfmlabel')

    def _get_wfmload(self):
        return self._wfmslot

    def _set_wfmload(self, value):
        # load waveform stored in non-volatile memory
        self._wfmslot = value
        wfm = self._load_waveform_from_slot(self._wfmslot)
        if wfm != self._waveform:
            self._pending_wfmload = True
            self._waveform = wfm
            self._mycallback(pvname='wfmload')

    def _get_wfmload_changed(self):
        return self._wfmload_changed_state

    def _set_wfmload_changed(self, value):
        self._wfmload_changed_state = value

    def _get_wfmdata(self):
        return _np.array(self._waveform.data)

    def _set_wfmdata(self, value):
        self._waveform.data = _np.array(value)
        self._mycallback(pvname='wfmdata')

    def _get_wfmdata_changed(self):
        return self._wfmdata_changed_state

    def _set_wfmdata_changed(self, value):
        self._wfmdata_changed_state = value

    def _get_wfmsave(self):
        return self._wfmsave

    def _set_wfmsave(self, value):
        self._wfmsave += 1
        self._save_waveform_to_slot(self._wfmslot)
        self._mycallback(pvname='wfmsave')

    def _get_trigger_timed_out(self):
        if self._timestamp_trigger is not None and \
           self.time - self._timestamp_trigger > self._trigger_timeout:
            return True
        else:
            return False

    def _set_trigger_timed_out(self, value):
        self._trigger_timed_out = value

    def _get_time(self):
        if self._time_simulated is None:
            return _time.time()
        else:
            return self._time_simulated

    def _process_trigger_signal(self, nrpts):
        now = self.time
        if nrpts == 1:
            self._set_timestamp_trigger(now)
            self.update_state(trigger_signal=True)
        else:
            self._time_simulated = now
            for i in range(nrpts):
                self._time_simulated = now + i * self.trigger_interval
                self._set_timestamp_trigger(self._time_simulated)
                self.update_state(trigger_signal=True)
            self._time_simulated = None

    def _set_current_ref(self, value):
        if value != self._current_ref:
            self._current_ref = value
            self._mycallback(pvname='current_ref')
        value = _random.gauss(self._current_ref, self._current_std)
        if value != self._current_load:
            self._current_load = value
            self._mycallback(pvname='current_load')

    def _get_cycling_state(self):
        return self._cycling_state

    def _set_cycling_state(self, value):
        if value and not self._cycling_state:
            self._timestamp_cycle_start = self.time
        self._cycling_state = value

    def _process_Cycle(self):
        if self._get_cycling_state():
            dt = self.time - self._timestamp_cycle_start
            if self._cycgen.out_of_range(dt):
                self._finilize_cycgen()
            else:
                scan_value = self._cycgen.get_signal(dt)
                self._update_current_ref(scan_value)

    def _mycallback(self, pvname):
        # if self._callback is None:
        #     return
        if not self._callbacks:
            return
        elif pvname == 'pwrstate':
            for callback in self._callbacks.values():
                callback(pvname='pwrstate', value=self._pwrstate)
        elif pvname == 'opmode':
            for callback in self._callbacks.values():
                callback(pvname='opmode', value=self._opmode)
        elif pvname == 'current_sp':
            for callback in self._callbacks.values():
                callback(pvname='current_sp', value=self._current_sp)
        elif pvname == 'current_ref':
            for callback in self._callbacks.values():
                callback(pvname='current_ref', value=self._current_ref)
        elif pvname == 'current_load':
            for callback in self._callbacks.values():
                callback(pvname='current_load', value=self._current_load)
        elif pvname == 'wfmload':
            for callback in self._callbacks.values():
                callback(pvname='wfmload', value=self._wfmslot)
        elif pvname == 'wfmdata':
            for callback in self._callbacks.values():
                callback(pvname='wfmdata', value=self._waveform.data)
        elif pvname == 'wfmlabel':
            for callback in self._callbacks.values():
                callback(pvname='wfmlabel', value=self._waveform.label)
        elif pvname == 'wfmsave':
            for callback in self._callbacks.values():
                callback(pvname='wfmsave', value=self._wfmsave)
        elif pvname == 'reset':
            for callback in self._callbacks.values():
                callback(pvname='reset', value=self._reset_counter)
        elif pvname == 'abort':
            for callback in self._callbacks.values():
                callback(pvname='abort', value=self._abort_counter)
        else:
            raise NotImplementedError

    def _init_waveforms(self):
        # updated index selecting value of current in waveform in use
        self._wfmindex = 0
        self._wfmsave = 0   # waveform save command counter
        self._wfmslot = 0   # selected waveform slot index
        self._wfmlabels = []  # updated array with waveform labels
        self._wfmdata_changed_state = False
        self._wfmload_changed_state = False
        for i in range(len(_default_wfmlabels)):
            wfm = self._load_waveform_from_slot(i)
            self._wfmlabels.append(wfm.label)
            if i == self._wfmslot:
                self._waveform = wfm
                self._wfmdata_in_use = _np.array(wfm.data)

    def _load_waveform_from_slot(self, slot):
        if self._psname is not None:
            fname = self._psname + ':' + _default_wfmlabels[slot]
        else:
            fname = _default_wfmlabels[slot]
        try:
            pswfm = _PSWaveForm(
                label=_default_wfmlabels[slot],
                filename=fname + '.txt')
            if pswfm.nr_points != _default_wfmsize:
                raise ValueError
            return pswfm
        except (FileNotFoundError, ValueError):
            wfm = _PSWaveForm.wfm_constant(
                label=_default_wfmlabels[slot], filename=fname + '.txt')
            wfm.save_to_file(filename=fname+'.txt')
            return wfm

    def _load_waveform_from_label(self, label):
        if label in self._wfmlabels:
            slot = self._wfmlabels.index(label)
            return slot, self._load_waveform_from_slot(slot)
        else:
            return None

    def _save_waveform_to_slot(self, slot):
        if self._psname is not None:
            fname = self._psname + ':' + _default_wfmlabels[slot]
        else:
            fname = _default_wfmlabels[slot]
        try:
            self._waveform.save_to_file(filename=fname+'.txt')
        except PermissionError:
            raise Exception('Could not write file "' + fname+'.txt' + '"!')


class PUControllerSim(Controller):
    """Controller that simulates the behavior of pulsed power supply."""

    def __init__(self, psname):
        """Create object responsible for the simulatiion."""
        self._ps = PulsedPowerSupplySim(psname)

    def read(self, field):
        """Return field value."""
        if field == "Voltage-SP":
            return self._ps.voltage_sp
        elif field == "Voltage-RB":
            return self._ps.voltage_rb
        elif field == "Voltage-Mon":
            return self._ps.voltage_mon
        elif field == "PwrState-Sel":
            return self._ps.pwrstate_sel
        elif field == "PwrState-Sts":
            return self._ps.pwrstate_sts
        elif field == "Pulsed-Sel":
            return self._ps.pulsed_sel
        elif field == "Pulsed-Sts":
            return self._ps.pulsed_sts
        elif field == "CtrlMode-Mon":
            return self._ps.ctrlmode_mon
        elif field == "Intlk-Mon":
            return self._ps.intlk_mon
        elif field == "IntlkLabels-Cte":
            return self._ps.intlklabels_cte
        elif field == "Reset-Cmd":
            return self._ps.reset
        else:
            raise ValueError("Unknown field {}".format(field))

    def write(self, field, value):
        """Write value to field."""
        print("Writing {}".format(field, value))
        if field == "Voltage-SP":
            self._ps.voltage_sp = value
        elif field == "PwrState-Sel":
            self._ps.pwrstate_sel = value
        elif field == "Pulsed-Sel":
            self._ps.pulsed_sel = value
        elif field == "Reset-Cmd":
            self._ps.reset = value
        else:
            # Warn?
            pass

        return 1

    def add_callback(self, func):
        """Add callback."""
        self._ps.add_callback(func)
