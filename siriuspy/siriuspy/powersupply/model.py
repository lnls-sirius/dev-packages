"""Define a Pulsed Power Supply class to handle IOC connections."""

# PowerSupply
from siriuspy.pwrsupply.data import PSData as _PSData
# Magnet
from siriuspy.magnet.data import MAData as _MAData
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from . import controller as _controller


class PowerSupply:
    """Handles IOC request.

    This class is supposed to be used by an IOC to handle request and update
    PVs related to a specific Power Supply device(s) given by `psnames`.
    If no controller is passed a PSEpicsController will be used.
    """

    def __init__(self, psnames, controller=None, use_vaca=True, lock=True):
        """Create PV set."""
        self._psnames = psnames
        self._base_db = self._get_base_db()

        if use_vaca:
            self._vaca_prefix = _VACA_PREFIX
        else:
            self._vaca_prefix = ''

        if controller:
            self.controller = controller
        else:
            self._init_controller()

        # self._pvs = dict()
        # self._create_pvs()

    # Public API
    def read(self, field):
        """Read field value."""
        return self.controller.read(field)

    def write(self, field, value):
        """Write value to PV."""
        return self.controller.write(field, value)

    def add_callback(self, func):
        """Add callback to all PVs."""
        self.controller.add_callback(func)

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

    # Private methods
    def _get_base_db(self):
        return _PSData(self._psnames[0]).propty_database

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

    def _init_controller(self):
        dev_name = self._get_device_name()
        self.controller = _controller.PSEpicsController(
            self._psnames, self._get_fields(), self._vaca_prefix, dev_name)

    def _get_device_name(self):
        if "BO-Fam:PS-B" in self._psnames[0]:
            return "BO-Fam:PS-B"
        elif "SI-Fam:PS-B1B2" in self._psnames[0]:
            return "SI-Fam:PS-B1B2"
        else:
            return self._psnames[0]


class Magnet(PowerSupply):
    """Handles IOC request.

    This class is supposed to be used by an IOC to handle request and update
    PVs related to a specific Magnet device(s) given by `maname`.
    """

    def __init__(self, maname, **kwargs):
        """Class used to handle IOC connections for Magnets.

        If no controller is passed an MAEpicsController will be used.
        kwargs accepts:
            controller
            use_vaca
            lock
        """
        self._maname = _SiriusPVName(maname)
        self._madata = _MAData(maname)
        super().__init__(psnames=[], **kwargs)

    # Private
    def _get_base_db(self):
        return self._madata.get_database(self._madata.psnames[0])

    def _init_controller(self):
        self.controller = _controller.MAEpicsController(
            self._maname, fields=self._get_fields(), prefix=self._vaca_prefix)
