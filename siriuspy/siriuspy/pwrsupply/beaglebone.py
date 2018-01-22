"""Beagle Bone implementation module."""

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.pwrsupply.controller import Controller as _Controller
from siriuspy.pwrsupply.controller import SerialComm as _SerialComm
from siriuspy.pwrsupply.controller import DevSlave as _DevSlave
from siriuspy.pwrsupply.controller import DevSlaveSim as _DevSlaveSim
from siriuspy.pwrsupply.controller import PRU as _PRU
from siriuspy.pwrsupply.controller import PRUSim as _PRUSim
# from siriuspy.pwrsupply.controller import PUControllerSim as _PUControllerSim
from siriuspy.pwrsupply.model import PowerSupply as _PowerSupply


class _BeagleBone:
    """BeagleBone class."""

    def __init__(self, bbb_name):
        """Init method."""
        self._bbb_name = bbb_name
        self._serial_comm = None
        self._pwrsupplies = None

    @property
    def psnames(self):
        """Return power supply names."""
        raise NotImplementedError

    @property
    def read(self, psname, field):
        """Return power supply field."""
        return self._pwrsupplies[psname].read(field)

    @property
    def write(self, psname, field, value):
        """Write value to field of power supply."""
        return self._pwrsupplies[psname].write(field, value)


class BeagleBoneSim(_BeagleBone):

    def __init__(self, bbb_name):
        """Init method."""
        self._bbb_name = bbb_name
        self._create_pwrsupply_dict()

    def _create_pwrsupply_dict(self):
        pass


class BeagleBone:
    """Responsible for handling BBB objects."""

    def __init__(self, bbbname, simulate=True):
        """Retrieve power supplies."""
        self._bbbname = bbbname
        self._simulate = True
        self._psnames = _PSSearch.conv_bbbname_2_psnames(bbbname)

        if self._simulate:
            self._pru = _PRUSim()
        else:
            self._pru = _PRU()

        self._serial_comm = _SerialComm(PRU=self._pru)
        self._power_supplies = self._get_power_supplies()

    @property
    def serial_comm(self):
        """Return serial_comm object."""
        return self._serial_comm

    @property
    def power_supplies(self):
        """Return dict with all power supplies objects."""
        return self._power_supplies

    def _get_power_supplies(self):
        """Build power supply objects."""
        power_supplies = dict()
        for i, psname in enumerate(self._psnames):
            id_device = i + 1

            if self._simulate:
                self._serial_comm.add_slave(_DevSlaveSim(ID_device=id_device))
            else:
                self._serial_comm.add_slave(
                    _DevSlave(ID_device=id_device, PRU=self._pru))

            c = _Controller(serial_comm=self._serial_comm, ID_device=id_device)
            power_supplies[psname] = _PowerSupply(controller=c, psname=psname)

        return power_supplies
