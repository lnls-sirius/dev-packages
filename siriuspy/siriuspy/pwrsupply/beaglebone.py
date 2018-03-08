"""Beagle Bone implementation module."""

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import get_ps_propty_database as \
    _get_ps_propty_database
from siriuspy.pwrsupply.pru import SerialComm as _SerialComm
from siriuspy.pwrsupply.pru import PRU as _PRU
from siriuspy.pwrsupply.pru import PRUSim as _PRUSim
from siriuspy.pwrsupply.bsmp import BSMPMasterSlave as _BSMPMasterSlave
from siriuspy.pwrsupply.bsmp import BSMPMasterSlaveSim as _BSMPMasterSlaveSim
from siriuspy.pwrsupply.controller import IOCController as _IOCController
from siriuspy.pwrsupply.controller import PSControllerSim as _PSControllerSim
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

    def _get_bsmp_slave_IDs(self):
        # This will have to be generalized!
        if self._bbbname == 'BO-Glob:CO-BBB-T1':
            # test-bench BBB # 1
            return (1, 2)
        elif self._bbbname == 'BO-Glob:CO-BBB-T2':
            # test-bench BBB # 2
            return (5, 6)
        else:
            return tuple(range(1, 1+len(self._psnames)))

    def _create_power_supplies(self):
        # Return dict of power supply objects
        slave_ids = self._get_bsmp_slave_IDs()
        power_supplies = dict()
        for i, psname in enumerate(self._psnames):
            ID_device = slave_ids[i]
            if self._simulate:
                ps_c = _PSControllerSim()
                slave = _BSMPMasterSlaveSim(ID_device=ID_device,
                                            pscontroller=ps_c)
            else:
                slave = _BSMPMasterSlave(ID_device=ID_device, PRU=self._pru)
            self._serial_comm.add_slave(slave)
            ps_database = _get_ps_propty_database(
                pstype=_PSSearch.conv_psname_2_pstype(psname))
            ioc_c = _IOCController(serial_comm=self._serial_comm,
                                   ID_device=ID_device,
                                   ps_database=ps_database)
            power_supplies[psname] = _PowerSupply(controller=ioc_c,
                                                  psname=psname)
        return power_supplies

    def __getitem__(self, psname):
        """Return corresponding power supply object."""
        return self._power_supplies[psname]

    def __contains__(self, psname):
        """Test is psname is in psname list."""
        return psname in self._psnames
