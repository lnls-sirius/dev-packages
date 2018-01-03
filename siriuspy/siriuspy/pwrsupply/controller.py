"""Controller defitions."""
from epics import PV as _PV
import re as _re

from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.magnet import util as _mutil
from siriuspy.epics.computed_pv import ComputedPV as _ComputedPV
from siriuspy.pwrsupply import sync as _sync
from siriuspy.factory import NormalizerFactory as _NormalizerFactory


class PSEpicsController:
    """Create real PVs to control PS attributes."""

    def __init__(self, psnames, fields, prefix='', device_name=''):
        """Create epics PVs and expose them through public controller API."""
        # Attributes use build a full PV address
        self._psnames = psnames
        self.fields = fields
        self.prefix = prefix
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

        for field in self.fields:
            self._pvs[field] = self._create_pv(field)

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
            pvs = [self.prefix + device_name + ":" + field
                   for device_name in self._psnames]
            # Name of the ComputedPV
            pvname = self.device_name + ":" + field
            # Create a virtual PV (ComputedPV)
            x = _ComputedPV(pvname, sync, *pvs)
            return x
        else:
            return _PV(self.prefix + self.device_name + ":" + field)


class MAEpicsController(PSEpicsController):
    """Create real PVs to control PS attributes."""

    _is_strength = _re.compile('(Energy|KL|SL|Kick).+$')

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
            pvname = self.prefix + self._maname + ":" + field
            str_obj = self._get_str_obj(self._maname)
            pvs = self._get_str_pv(field)
            return _ComputedPV(pvname, str_obj, *pvs)
        else:
            return super()._create_pv(field)

    def _get_str_obj(self, device_name):
        # Return Normalizer object
        return _NormalizerFactory.factory(device_name)

    def _get_str_pv(self, field):
        ma_class = _mutil.magnet_class(self._maname)
        if 'dipole' == ma_class:
            return [self._pvs[field.replace('Energy', 'Current')], ]
        elif 'pulsed' == ma_class:
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self.prefix + dipole_name
            return [self._pvs[field.replace('Kick', 'Voltage')],
                    dipole + ":" + field.replace('Kick', 'Current')]
        elif 'trim' == ma_class:
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self.prefix + dipole_name
            fam_name = _mutil.get_magnet_family_name(self._maname)
            fam = self.prefix + fam_name
            field = field.replace('KL', 'Current')
            return [self._pvs[field],
                    dipole + ':' + field,
                    fam + ':' + field]
        else:
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self.prefix + dipole_name
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
