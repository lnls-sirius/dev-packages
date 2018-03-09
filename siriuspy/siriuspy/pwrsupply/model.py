"""Define Power Supply classes."""

import re as _re
from threading import Thread as _Thread
import time as _time
import numpy as _np

from epics import PV as _PV

from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriuspy.factory import NormalizerFactory as _NormalizerFactory
from siriuspy.epics import connection_timeout as _connection_timeout
from siriuspy.epics.computed_pv import QueueThread as _QueueThread
from siriuspy.epics.computed_pv import ComputedPV as _ComputedPV
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply.controller import PSCommInterface as _PSCommInterface
from siriuspy.magnet.data import MAData as _MAData
from siriuspy.magnet import util as _mutil
from siriuspy.pwrsupply import sync as _sync


class PowerSupply(_PSCommInterface):
    """Abstract control-system power supply class.

        Objects of this are used to interact with power supplies in the
    control-system using the implemented PSCommInterface.
    """

    _SCAN_FREQUENCY = 10.0  # [Hz]
    _is_setpoint = _re.compile('.*-(SP|Sel|Cmd)$')

    # power supply objet, not controller's, is responsible to provide state
    # of the following fields:
    _db_const_fields = ('IntlkSoftLabels-Cte',
                        'IntlkHardLabels-Cte')

    def __init__(self, psname, controller):
        """Init method."""
        _PSCommInterface.__init__(self)
        self._field_values = {}  # dict with last read field values
        self._psdata = _PSData(psname=psname)
        self._controller = controller
        self._updating = True
        self._base_db = self._get_base_db()
        self._setpoints = self._build_setpoints()
        self._callbacks = {}
        self._thread_scan = _Thread(target=self._scan_fields)
        self._thread_scan.setDaemon(True)
        self._thread_scan.start()

    @property
    def psdata(self):
        """Return PSData object."""
        return self._psdata

    @property
    def updating(self):
        """Return updating state."""
        return self._updating

    @updating.setter
    def updating(self, value):
        """Set updating state."""
        self._updating = value

    # --- PSCommInterface implementation ---

    def read(self, field):
        """Read field value."""
        # Check CtrlMode?
        if PowerSupply._is_setpoint.match(field):
            # why not use _base_db to store setpoints?
            return self._setpoints[field]['value']
        if field in PowerSupply._db_const_fields:
                return self._base_db[field]['value']
        else:
            return self._controller.read(field)

    def write(self, field, value):
        """Write value to field."""
        if field in self._setpoints:
            func = self._setpoints[field]['func']
            return func(value)

    def _connected(self):
        return self._controller.connected

    def add_callback(self, func, index=None):
        """Add callback function."""
        _PSCommInterface.add_callback(self, func=func, index=index)
        # send all data initially to registered callback function
        for field in self._base_db:
            if field in PowerSupply._db_const_fields:
                continue
            value = self.read(field)
            self._run_callbacks(field, value)

    # --- public methods ---

    def get_database(self, prefix=""):
        """Fill base DB with values and limits read from PVs.

        Optionally add a prefix to the dict keys.
        """
        db = self._fill_database()

        if prefix:
            prefixed_db = {}
            for key, value in db.items():
                prefixed_db[prefix + ":" + key] = value
            return prefixed_db
        else:
            return db

    # --- private methods ---

    def _build_setpoints(self):
        sp = dict()
        for field in self._get_fields():
            if not PowerSupply._is_setpoint.match(field):
                continue
            sp[field] = dict()
            self._set_field_setpoint(sp[field], field)
        return sp

    def _set_field_setpoint(self, keyvalue, field):
        # should we use database as setpoint state?!
        db = self._base_db
        if field == 'PwrState-Sel':
            keyvalue['func'] = self._set_pwrstate
            # keyvalue['value'] = db['PwrState-Sel']['value']
            keyvalue['value'] = self._controller.read('PwrState-Sts')
        elif field == 'OpMode-Sel':
            keyvalue['func'] = self._set_opmode
            # keyvalue['value'] = db['OpMode-Sel']['value']
            keyvalue['value'] = self._controller.read('OpMode-Sts')
        elif field == 'Current-SP':
            keyvalue['func'] = self._set_current
            # keyvalue['value'] = db['Current-SP']['value']
            keyvalue['value'] = self._controller.read('Current-RB')
        elif field == 'WfmLoad-Sel':
            keyvalue['func'] = self._set_wfmload
            # keyvalue['value'] = db['WfmLoad-Sel']['value']
            keyvalue['value'] = self._controller.read('Current-RB')
        elif field == 'WfmLabel-SP':
            keyvalue['func'] = self._set_wfmlabel
            keyvalue['value'] = db['WfmLabel-SP']['value']
        elif field == 'WfmData-SP':
            keyvalue['func'] = self._set_wfmdata
            keyvalue['value'] = [v for v in db['WfmData-SP']['value']]
        elif field == 'Abort-Cmd':
            keyvalue['func'] = self._abort
            keyvalue['value'] = db['Abort-Cmd']['value']
        elif field == 'Reset-Cmd':
            keyvalue['func'] = self._reset
            keyvalue['value'] = db['Reset-Cmd']['value']

    def _set_pwrstate(self, value):
        self._setpoints['PwrState-Sel']['value'] = value
        if value >= 0 and value < len(self._base_db['PwrState-Sel']['enums']):
            ret = self._controller.write('PwrState-Sel', value)
            # zero PS current
            # self._setpoints['Current-SP']['value'] = 0.0
            # self._controller.write('Current-SP', 0.0)
            return ret

    def _set_opmode(self, value):
        self._setpoints['OpMode-Sel']['value'] = value
        if value >= 0 and value < len(self._base_db['OpMode-Sel']['enums']):
            return self._controller.write('OpMode-Sel', value)

    def _set_current(self, value):
        self._setpoints['Current-SP']['value'] = value
        return self._controller.write('Current-SP', value)

    def _set_wfmload(self, value):
        self._wfmload_sel = value
        self._setpoints['WfmLoad-Sel']['value'] = value
        return self._controller.write('WfmLoad-Sel', value)

    def _set_wfmlabel(self, value):
        self._wfmlabel_sp = value
        self._setpoints['WfmLabel-SP']['value'] = value
        return self._controller.write('WfmLabel-SP', value)

    def _set_wfmdata(self, value):
        self._wfmdata_sp = value
        self._setpoints['WfmData-SP']['value'] = value
        return self._controller.write('WfmData-SP', value)

    def _abort(self, value):
        # op_mode = self.read('OpMode-Sts')
        self._setpoints['Abort-Cmd']['value'] += 1
        self.write('OpMode-Sel', 0)  # Set to SlowRef
        self.write('Current-SP', 0.0)
        return self._setpoints['Abort-Cmd']['value']

    def _reset(self, value):
        self._setpoints['Reset-Cmd']['value'] += 1
        self.write('Current-SP', 0.0)
        self.write('OpMode-Sel', 0)
        # Reset interlocks
        self._controller.write('Reset-Cmd', 1)
        return self._setpoints['Reset-Cmd']['value']

    def _get_base_db(self):
        return self._psdata.propty_database

    def _get_fields(self):
        return self._base_db.keys()

    def _fill_database(self):
        db = dict()
        db.update(self._base_db)
        for field in db:
            value = self.read(field)
            if value is not None:
                db[field]["value"] = value

        return db

    def _scan_fields(self):
        """Scan fields."""
        interval = 1.0/PowerSupply._SCAN_FREQUENCY
        while True:
            time_start = _time.time()
            if self._updating:
                for field in self._base_db:
                    if field in PowerSupply._db_const_fields:
                        continue
                    value = self.read(field)
                    # if _base_db is a updated copy of ps state, users (IOC)
                    # of powersupply could access it directly, without the
                    # the need of callback registration!

                    # if value just read is not new, skipp.
                    if field in self._field_values:
                        prev_value = self._field_values[field]
                        if isinstance(value, _np.ndarray):
                            if _np.all(value == prev_value):
                                continue
                        else:
                            if value == prev_value:
                                continue

                    # run callback function since field has a new value
                    self._run_callbacks(field, value)

                    # register read value of field
                    self._field_values[field] = value
            time_end = _time.time()
            sleep_time = max(0, interval - (time_end - time_start))
            _time.sleep(sleep_time)
            # _time.sleep(PowerSupply._SCAN_INTERVAL)

    def _run_callbacks(self, field, value):
        for index, callback in self._callbacks.items():
            callback(
                pvname=self._psdata.psname + ':' + field,
                value=value)


class PSEpics(_PSCommInterface):
    """Power supply with Epics communication."""

    # Should we merge this base class into MAEpics?

    # valid_fields = ('Current-SP', 'Current-RB', 'CurrentRef-Mon',
    #                 'Current-Mon', 'PwrState-Sel', 'PwrState-Sts',
    #                 'OpMode-Sel', 'OpMode-Sts',
    #                 'Energy-SP', 'Energy-RB', 'EnergyRef-Mon', 'Energy-Mon',
    #                 'KL-SP', 'KL-RB', 'KLRef-Mon', 'KL-Mon',
    #                 'SL-SP', 'SL-RB', 'SLRef-Mon', 'SL-Mon',
    #                 'Kick-SP', 'Kick-RB', 'KickRef-Mon', 'Kick-Mon',
    #                 'Reset-Cmd', 'Abort-Cmd')

    def __init__(self, psname, fields=None, use_vaca=True):
        """Create epics PVs and expose them through public controller API."""
        _PSCommInterface.__init__(self)
        # Attributes use build a full PV address
        self._psname = psname
        # self._sort_fields()
        if use_vaca:
            self._prefix = _VACA_PREFIX
        else:
            self._prefix = ''
        # Get pv db
        self._base_db = self._get_base_db()
        # Get fields, if none is passed they'll will be retrieved from the db
        if fields is None:
            self._fields = self._get_fields()
        else:
            self._fields = fields
        # Holds PVs objects
        self._pvs = dict()
        self._create_pvs()

    # --- PSCommInterface implementation ---

    def read(self, field):
        """Read a field value."""
        # if field not in self.valid_fields:
        #     return None
        if self._pvs[field].connected:
            return self._pvs[field].get()
        else:
            # print("Not connected")
            return None

    def write(self, field, value):
        """Write a value to a field."""
        # Check wether value is valid and return 0
        # if field not in self.valid_fields:
        #     return None
        if self._pvs[field].connected:
            return self._pvs[field].put(value)
        else:
            # print("Not connected")
            return None

    def add_callback(self, func):
        """Add callback to field."""
        if not callable(func):
            raise ValueError("Tried to set non callable as a callback")
        else:
            for pvname, pv in self._pvs.items():
                # field = pvname.split(':')[-1]
                # if field in self.valid_fields:
                pv.add_callback(func)

    def _connected(self):
        for pv in self._pvs.values():
            if not pv.connected:
                return False
        return True

    # --- public methods ---

    def get_database(self, prefix=""):
        """Fill base DB with values and limits read from PVs.

        Optionally add a prefix to the dict keys.
        """
        db = self._fill_database()

        if prefix:
            prefixed_db = {}
            for key, value in db.items():
                prefixed_db[prefix + ":" + key] = value
            return prefixed_db
        else:
            return db

    # --- private methods ---

    def _create_pvs(self):
        # No/rmally create normal PV objects
        # In case more than one source is supplied creates a SyncPV
        # In case the device is a Magnet with a normalized force being supplied
        # as one of the fields, a NormalizedPV is created
        self._sort_fields()
        for field in self._fields:
            # if field in self.valid_fields:
            self._pvs[field] = self._create_pv(field)

    def _create_pv(self, field):
        return _PV(self._prefix + self._psname + ":" + field,
                   connection_timeout=_connection_timeout)

    def _get_base_db(self):
        return _PSData(self._psname).propty_database

    def _get_fields(self):
        return self._base_db.keys()

    def _fill_database(self):
        db = dict()
        db.update(self._base_db)
        for field in db:
            value = self.read(field)
            if value is not None:
                db[field]['value'] = value

                # calc pv limits
                if 'KL' in field or 'Energy' in field or \
                   'SL' in field or 'Kick' in field:
                    cpv = self._pvs[field]
                    lims = cpv.computer.compute_limits(cpv)
                    # cpv.upper_alarm_limit = lims[0]
                    # cpv.upper_warning_limit = lims[1]
                    # cpv.upper_disp_limit = lims[2]
                    # cpv.lower_disp_limit = lims[3]
                    # cpv.lower_warning_limit = lims[4]
                    # cpv.lower_alarm_limit = lims[5]
                    db[field]['hihi'] = lims[0]
                    db[field]['high'] = lims[1]
                    db[field]['hilim'] = lims[2]
                    db[field]['lolim'] = lims[3]
                    db[field]['low'] = lims[4]
                    db[field]['lolo'] = lims[5]

        return db

    def _sort_fields(self):
        fields = []
        for field in self._fields:
            if not self._is_strength.match(field):
                fields.insert(0, field)
            else:
                fields.append(field)

        self._fields = fields


class MAEpics(PSEpics):
    """Magnet power supply with Epics communication."""

    _is_strength = _re.compile('(Energy|KL|SL|Kick).+$')
    _is_multi_ps = _re.compile('(SI|BO)-\w{2,4}:MA-B.*$')

    def __init__(self, maname, lock=False, **kwargs):
        """Create epics PVs and expose them through public controller API."""
        # Attributes use build a full PV address
        self._maname = _SiriusPVName(maname)
        self._madata = _MAData(maname)
        self._lock = lock
        self._computed_pvs_queue = _QueueThread()
        super().__init__(
            self._maname.replace("MA", "PS").replace("PM", "PU"),
            **kwargs)

    # --- virtual methods ---

    def _create_pvs(self):
        self._sort_fields()
        super()._create_pvs()

    def _create_pv(self, field):
        # Build either a real or computed PV
        if MAEpics._is_strength.match(field):
            # 1) STRENGTH magnet fields
            # an intermediary computed_pv is created in order for the
            # strength to be calculated from currents.
            pvname = self._prefix + self._maname + ":" + field
            str_obj = self._get_normalizer(self._maname)
            pvs = self._get_str_pv(field)
            return _ComputedPV(pvname, str_obj,
                               self._computed_pvs_queue, *pvs)
        else:
            if len(self._psnames()) > 1:  # SyncPV
                # 2) SYNCPV fields
                # this is used basically for SI and BO dipoles
                sync = self._get_sync_obj(field)
                pvs = [self._prefix + device_name + ":" + field
                       for device_name in self._psnames()]
                pvname = self._psname + ":" + field
                return _ComputedPV(pvname, sync,
                                   self._computed_pvs_queue, *pvs)
            else:
                # 3) PV
                # a normal pv mirroring the power supply pv.
                # no computed_pv is needed.
                return super()._create_pv(field)

    def _get_base_db(self):
        # set dipole energy limits
        n, db = None, self._madata.get_database(self._madata.psnames[0])
        for pvname in db:
            if 'Energy' in pvname:
                pvname_ps = pvname.replace('Energy', 'Current')
                if n is None:
                    n = _NormalizerFactory.factory(maname=self._maname)
                currents = []
                currents.append(db[pvname_ps]['hihi'])
                currents.append(db[pvname_ps]['high'])
                currents.append(db[pvname_ps]['hilim'])
                currents.append(db[pvname_ps]['lolim'])
                currents.append(db[pvname_ps]['low'])
                currents.append(db[pvname_ps]['lolo'])
                lims = sorted(n.conv_current_2_strength(currents=currents))
                db[pvname]['hihi'] = lims[0]
                db[pvname]['high'] = lims[1]
                db[pvname]['hilim'] = lims[2]
                db[pvname]['lolim'] = lims[3]
                db[pvname]['low'] = lims[4]
                db[pvname]['lolo'] = lims[5]
        return db

    # --- class methods ---

    def _get_normalizer(self, device_name):
        # Return Normalizer object
        return _NormalizerFactory.factory(device_name)

    def _get_sync_obj(self, field):
        # Return SyncWrite or SyncRead object
        if "SP" in field or "Sel" in field or "Cmd" in field:
            return _sync.SyncWrite(lock=self._lock)
        else:
            return _sync.SyncRead()

    def _get_str_pv(self, field):
        ma_class = _mutil.magnet_class(self._maname)
        if 'dipole' == ma_class:
            field = field.replace('Energy', 'Current')
            return [self._pvs[field], ]
        elif 'pulsed' == ma_class:
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self._prefix + dipole_name
            dipole_pv = dipole + ':' + field.replace('Kick', 'Current')
            return [self._pvs[field.replace('Kick', 'Voltage')],
                    dipole_pv]
        elif 'trim' == ma_class:
            field = field.replace('KL', 'Current')
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self._prefix + dipole_name
            dipole_pv = dipole + ':' + field.replace('Current', 'Energy')
            fam_name = _mutil.get_magnet_family_name(self._maname)
            fam = self._prefix + fam_name
            family_pv = fam + ':' + field.replace('Current', 'KL')

            # use Ref-Mon, instead of -Mon
            # (this is not necessary anymore for efficiency standpoint, since
            #  now only the main current pv is being used to trigger
            #  conversion. The line below may be commented out or deleted. )
            dipole_pv = dipole_pv.replace('Energy-Mon', 'EnergyRef-Mon')

            family_pv = family_pv.replace('KL-Mon', 'KLRef-Mon')
            return [self._pvs[field], dipole_pv, family_pv]
        else:
            field = field.replace('KL', 'Current')
            field = field.replace('SL', 'Current')
            field = field.replace('Kick', 'Current')
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self._prefix + dipole_name
            dipole_pv = dipole + ':' + field.replace('Current', 'Energy')

            # use Ref-Mon, instead of -Mon
            # (this is not necessary anymore for efficiency standpoint, since
            #  now only the main current pv is being used to trigger
            #  conversion. The line below may be commented out or deleted. )
            dipole_pv = dipole_pv.replace('Energy-Mon', 'EnergyRef-Mon')

            return [self._pvs[field], dipole_pv]

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
