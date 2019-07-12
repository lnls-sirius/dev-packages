"""Define MA Epics Class."""

import re as _re

# TODO: test using siriuspy.epics.pv.PV instead
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
from siriuspy.magnet.data import MAData as _MAData
from siriuspy.magnet import util as _mutil


class PSCommInterface:
    """Communication interface class for power supplies."""

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

    def __init__(self, psname, fields=None):
        """Create epics PVs and expose them through public controller API."""
        PSCommInterface.__init__(self)

        # attributes used to build a full PV address
        self._psname = psname
        self._prefix = _VACA_PREFIX

        # get pv db
        self._base_db = self._get_base_db()

        # get fields, if none is passed they'll will be retrieved from the db
        if fields is None:
            self._fields = self._get_fields()
        else:
            self._fields = fields

        # dictionary with PV objects
        self._create_pvs()

    # --- PSCommInterface implementation ---

    def read(self, field):
        """Read a field value."""
        if self._pvs[field].connected:
            return self._pvs[field].get()
        else:
            return None

    def write(self, field, value):
        """Write a value to a field."""
        # Check wether value is valid and return 0
        if self._pvs[field].connected:
            return self._pvs[field].put(value)
        else:
            # print("Not connected")
            return None

    def add_callback(self, func, index=None):
        """Add callback to field."""
        if not callable(func):
            raise ValueError("Tried to set non callable as a callback")
        else:
            for pv in self._pvs.values():
                pv.add_callback(func, index)

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
        self._pvs = dict()
        for field in self._fields:
            pv = self._create_pv(field)
            if pv:
                self._pvs[field] = pv

    def _create_pv(self, field):
        pvname = self._prefix + self._psname + ":" + field
        pv = _PV(pvname)
        return pv

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
        pass


class MAEpics(PSEpics):
    """Magnet power supply with Epics communication."""

    # NOTE: check if usage of QueueThread class is not degrading
    # performance. This class implemented in siriuspy.thread is
    # under suspicion...

    _is_strength = _re.compile('(Energy|KL|SL|Kick).+$')
    _is_multi_ps = _re.compile('(SI|BO)-\w{2,4}:MA-B.*$')

    def __init__(self, maname, lock=False, **kwargs):
        """Create epics PVs and expose them through public controller API."""
        # Attributes used to build a full PV address
        self._maname = _SiriusPVName(maname)
        self._maclass = _mutil.magnet_class(self._maname)
        self._madata = _MAData(maname)

        self._lock = lock
        self._computed_pvs_queue = _QueueThread()
        psname = self._maname.replace("MA", "PS").replace("PM", "PU")
        super().__init__(psname, **kwargs)

    @property
    def maname(self):
        """Return maname."""
        return self._maname

    def read(self, field):
        """Read a field value."""
        if 'PSConnStatus' in field:
            return self.connected
        else:
            return super().read(field)

    # --- virtual methods ---

    # def _create_pvs(self):
    #     self._sort_fields()
    #     super()._create_pvs()

    def _create_pv(self, field):
        # Build either a base or computed PV
        if 'PSConnStatus' in field:
            # PSConnStatus is not a PV, it is a MAEpics object field
            return None
        if MAEpics._is_strength.match(field):
            # 1) STRENGTH fields
            # an intermediate computed_pv is created in order for the
            # strength to be calculated from currents.
            pvname = self._prefix + self._maname + ":" + field
            str_obj = self._get_normalizer(self._maname)
            str_pvs = self._get_str_pv(field)
            # print('ComputedPV:       ', pvname)
            # print(' strength_object: ', str_obj)
            # print(' sytength pvs:    ', str_pvs)
            # print()
            return _ComputedPV(pvname, str_obj,
                               self._computed_pvs_queue, str_pvs)
        else:
            psnames = _MASearch.conv_psmaname_2_psnames(self._maname)
            if len(psnames) > 1:  # SyncPV
                # 2) SYNCPV fields
                # this is used basically for SI and BO dipoles
                sync = self._get_sync_obj(field)
                pvnames = [self._prefix + device_name + ":" + field
                           for device_name in psnames]
                pvname = self._psname + ":" + field
                computer_pv = _ComputedPV(
                    pvname, sync, self._computed_pvs_queue, pvnames)
                return computer_pv
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
        if self._maclass == 'dipole':
            # field pv
            field = field.replace('Energy', 'Current')
            field_pv = self._pvs[field]
            # return list
            return [field_pv, ]
        elif self._maclass == 'pulsed':
            # field pv
            field_pv = self._pvs[field.replace('Kick', 'Voltage')]
            # dipole pvname
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self._prefix + dipole_name
            dipole_pvname = dipole + ':' + field.replace('Kick', 'Energy')
            # return list
            return [field_pv, dipole_pvname]
        elif self._maclass == 'trim':
            # field pv
            field = field.replace('KL', 'Current')
            field_pv = self._pvs[field]
            # dipole pvname
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self._prefix + dipole_name
            dipole_pvname = dipole + ':' + field.replace('Current', 'Energy')
            # family pvname
            fam_name = _mutil.get_magnet_family_name(self._maname)
            fam = self._prefix + fam_name
            family_pvname = fam + ':' + field.replace('Current', 'KL')
            # NOTE: optimization
            # use Ref-Mon, instead of -Mon
            # (this is not necessary anymore for efficiency standpoint, since
            # now only the main current pv is being used to trigger
            # conversion. The line below may be commented out or deleted. )
            dipole_pvname = dipole_pvname.replace('Energy-Mon', 'EnergyRef-Mon')
            family_pvname = family_pvname.replace('KL-Mon', 'KLRef-Mon')
            # return list
            return [field_pv, dipole_pvname, family_pvname]
        else:
            # field pv
            field = field.replace('KL', 'Current')
            field = field.replace('SL', 'Current')
            field = field.replace('Kick', 'Current')
            field_pv = self._pvs[field]
            # dipole pvname
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self._prefix + dipole_name
            dipole_pvname = dipole + ':' + field.replace('Current', 'Energy')
            # NOTE: optimization
            # use Ref-Mon, instead of -Mon
            # (this is not necessary anymore for efficiency standpoint, since
            # now only the main current pv is being used to trigger
            # conversion. The line below may be commented out or deleted. )
            dipole_pvname = dipole_pvname.replace('Energy-Mon', 'EnergyRef-Mon')
            # return list
            return [field_pv, dipole_pvname]

    def _sort_fields(self):
        # send all strength fields to end of list
        fields = []
        for field in self._fields:
            if not self._is_strength.match(field):
                fields.insert(0, field)
            else:
                fields.append(field)
        self._fields = fields
