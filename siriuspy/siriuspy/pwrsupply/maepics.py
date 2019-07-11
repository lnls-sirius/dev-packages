"""Define Power Supply classes."""

import re as _re
import time as _time
from epics import PV as _PV

from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriuspy.factory import NormalizerFactory as _NormalizerFactory
from siriuspy.thread import QueueThread as _QueueThread
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.epics import connection_timeout as _connection_timeout
from siriuspy.epics.computed_pv import ComputedPV as _ComputedPV
from siriuspy.search.ma_search import MASearch as _MASearch
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply import sync as _sync
from siriuspy.pwrsupply.bsmp import ConstFBP as _c
from siriuspy.magnet.data import MAData as _MAData
from siriuspy.magnet import util as _mutil
from .status import PSCStatus as _PSCStatus


class PSCommInterface:
    """Communication interface class for power supplies."""

    # TODO: should this class have its own python module?
    # TODO: this class is not specific to PS! its name should be updated to
    # something line CommInterface or IOCConnInterface. In this case the class
    # should be moved to siriuspy.util or another python module.

    # --- public interface ---

    def __init__(self):
        """Init method."""
        self._callbacks = {}

    @property
    def connected(self):
        """Return connection status."""
        return self._connected()

    def read(self, field):
        """Return field value."""
        raise NotImplementedError

    def write(self, field, value):
        """Write value to a field.

        Return write value if command suceeds or None if it fails.
        """
        raise NotImplementedError

    def add_callback(self, func, index=None):
        """Add callback function."""
        if not callable(func):
            raise ValueError("Tried to set non callable as a callback")
        if index is None:
            index = 0 if len(self._callbacks) == 0 \
                else max(self._callbacks.keys()) + 1
        self._callbacks[index] = func

    # --- virtual private methods ---

    def _connected(self):
        raise NotImplementedError


class PSEpics(PSCommInterface):
    """Power supply with Epics communication."""

    # TODO: should we merge this base class into MAEpics?

    def __init__(self, psname, fields=None, use_vaca=True):
        """Create epics PVs and expose them through public controller API."""
        PSCommInterface.__init__(self)
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

    # NOTE: check if usage of QueueThread class is not degrading
    # performance. This class implemented in siriuspy.thread is
    # under suspicion...

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
            # an intermediate computed_pv is created in order for the
            # strength to be calculated from currents.
            pvname = self._prefix + self._maname + ":" + field
            str_obj = self._get_normalizer(self._maname)
            pvs = self._get_str_pv(field)
            return _ComputedPV(pvname, str_obj,
                               self._computed_pvs_queue, pvs)
        else:
            psnames = _MASearch.conv_psmaname_2_psnames(self._maname)
            if len(psnames) > 1:  # SyncPV
                # 2) SYNCPV fields
                # this is used basically for SI and BO dipoles
                sync = self._get_sync_obj(field)
                pvs = [self._prefix + device_name + ":" + field
                       for device_name in psnames]
                pvname = self._psname + ":" + field
                return _ComputedPV(pvname, sync,
                                   self._computed_pvs_queue, pvs)
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
                    n = _NormalizerFactory.create(maname=self._maname)
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
        return _NormalizerFactory.create(device_name)

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
            dipole_pv = dipole + ':' + field.replace('Kick', 'Energy')
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
