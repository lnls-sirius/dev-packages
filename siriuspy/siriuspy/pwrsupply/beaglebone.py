"""Beagle Bone implementation module."""

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import get_ps_propty_database as \
    _get_ps_propty_database
from siriuspy.pwrsupply.pru import SerialComm as _SerialComm
from siriuspy.pwrsupply.pru import PRU as _PRU
from siriuspy.pwrsupply.pru import PRUSim as _PRUSim
from siriuspy.pwrsupply.bsmp import BSMPResponse as _BSMPResponse
from siriuspy.pwrsupply.bsmp import BSMPResponseSim as _BSMPResponseSim
from siriuspy.pwrsupply.controller import Controller as _Controller
from siriuspy.pwrsupply.model import PowerSupply as _PowerSupply


_I_LOAD_FLUCTUATION_RMS = 0.01  # [A]
# _I_LOAD_FLUCTUATION_RMS = 0.0000  # [A]


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
        self._power_supplies = self._create_power_supplies()

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

    @property
    def power_supplies(self):
        """Return list of power supplies."""
        return self._power_supplies.values()

    def _create_power_supplies(self):
        # Return dict of power supply objects
        power_supplies = dict()
        for i, psname in enumerate(self._psnames):
            ID_device = i + 1  # This will have to change !!!
            if self._simulate:
                ps = _BSMPResponseSim(
                    ID_device=ID_device,
                    i_load_fluctuation_rms=_I_LOAD_FLUCTUATION_RMS)
            else:
                ps = _BSMPResponse(ID_device=ID_device, PRU=self._pru)
            self._serial_comm.add_slave(ps)
            ps_database = _get_ps_propty_database(
                pstype=_PSSearch.conv_psname_2_pstype(psname))
            c = _Controller(serial_comm=self._serial_comm,
                            ID_device=ID_device,
                            ps_database=ps_database)
            power_supplies[psname] = _PowerSupply(controller=c, psname=psname)
        return power_supplies

    def __getitem__(self, psname):
        """Return corresponding power supply object."""
        return self._power_supplies[psname]

    def __contains__(self, psname):
        """Test is psname is in psname list."""
        return psname in self._psnames


class BeagleBoneTest(BeagleBone):
    """Test class for ps-test-bench."""

    def __init__(self, pair=1):
        """Retrieve power supplies."""
        self._bbbname = 'teste'
        self._simulate = False
        self._pair = pair
        if self._pair == 1:
            self._psnames = ['BO-01U:PS-CH', 'BO-01U:PS-CV']
        else:
            self._psnames = ['BO-03U:PS-CH', 'BO-03U:PS-CV']

        # create PRU and serial_comm
        self._pru = _PRUSim() if self._simulate else _PRU()
        self._serial_comm = _SerialComm(PRU=self._pru)
        # create power supplies dictionary
        self._power_supplies = self._get_power_supplies()

    def _get_power_supplies(self):
        # Return dict of power supply objects
        power_supplies = dict()
        if self._pair == 1:
            IDs_device = (1, 2)
        else:
            IDs_device = (5, 6)
        for i, psname in enumerate(self._psnames):
            ID_device = IDs_device[i]
            ps = _BSMPResponse(ID_device=ID_device, PRU=self._pru)
            self._serial_comm.add_slave(ps)
            ps_database = _get_ps_propty_database(
                pstype=_PSSearch.conv_psname_2_pstype(psname))
            c = _Controller(serial_comm=self._serial_comm,
                            ID_device=ID_device,
                            ps_database=ps_database)
            power_supplies[psname] = _PowerSupply(controller=c, psname=psname)
        return power_supplies
