"""Beagle Bone implementation module."""

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.pwrsupply.controller import Controller as _Controller
from siriuspy.pwrsupply.controller import SerialComm as _SerialComm
from siriuspy.pwrsupply.controller import BSMPResponse as _BSMPResponse
from siriuspy.pwrsupply.controller import BSMPResponseSim as _BSMPResponseSim
from siriuspy.pwrsupply.controller import PRU as _PRU
from siriuspy.pwrsupply.controller import PRUSim as _PRUSim
# from siriuspy.pwrsupply.controller import PUControllerSim as _PUControllerSim
from siriuspy.pwrsupply.model import PowerSupply as _PowerSupply


class BeagleBone():
    """Responsible for handling BBB objects."""

    def __init__(self, bbbname, simulate=True):
        """Retrieve power supplies."""
        self._bbbname = bbbname
        self._simulate = simulate
        self._psnames = _PSSearch.conv_bbbname_2_psnames(bbbname)

        # create PRU and serial_comm
        self._pru = _PRUSim() if self._simulate else _PRU()
        self._serial_comm = _SerialComm(PRU=self._pru)
        # create power supplies dictionary
        self._power_supplies = self._get_power_supplies()

    @property
    def psnames(self):
        """Return list of power supply names."""
        return self._psnames.copy()

    @property
    def scanning(self):
        """Return ps variable scanning state."""
        return self._serial_comm.scanning

    @scanning.setter
    def scanning(self, value):
        """Set ps variable scanning state."""
        self._serial_comm.scanning = value

    def _get_power_supplies(self):
        # Return dict of power supply objects
        power_supplies = dict()
        for i, psname in enumerate(self._psnames):
            ID_device = i + 1
            ps = _BSMPResponseSim(ID_device=ID_device) if self._simulate else \
                _BSMPResponse(ID_device=ID_device, PRU=self._pru)
            self._serial_comm.add_slave(ps)
            c = _Controller(serial_comm=self._serial_comm, ID_device=ID_device)
            power_supplies[psname] = _PowerSupply(controller=c, psname=psname)
        return power_supplies

    def __getitem__(self, psname):
        """Return corresponding power supply object."""
        return self._power_supplies[psname]

    def __contains__(self, psname):
        """Test is psname is in psname list."""
        return psname in self._psnames
