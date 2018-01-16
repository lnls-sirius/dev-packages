"""Module implementing BSMP protocol."""

__version__ = '2.20'




class BSMPDeviceMaster:
    """BSMP class."""

    def __init__(self, variables, functions, slaves=None):
        """Init method."""
        self._variables = {ID: value for ID, value in variables.items()}
        self._functions = {ID: value for ID, value in functions.items()}
        self._groups = {}
        self._slaves = {}
        if slaves is not None:
            if isinstance(slaves, (list, tuple)):
                for i in range(len(slaves)):
                    self._slaves[i] = slaves[i]
            elif isinstance(slaves, dict):
                for k, v in slaves.items():
                    self._slaves[k] = v

    @property
    def slaves(self):
        """Return slave devices."""
        return self._slaves

    @slaves.setter
    def slaves(self, value):
        """Set slaves devices."""
        self._slaves = value
        self._broadcast_master()

    def add_slave(self, slave):
        """Add slave."""
        self._slaves[slave.ID_device] = slave

    @property
    def variables(self):
        """Return variables dictionary."""
        return self._variables

    # --- master commands ---

    def cmd_0x00(self):
        """Return BSMP protocol version."""
        return __version__

    def cmd_0x10(self, ID_slave, ID_variable):
        """Read variable identified by its ID."""
        slave = self._slaves[ID_slave]
        return slave.ack_0x10(ID_variable)

    def cmd_0x12(self, ID_slave, ID_group):
        """Read group variables identified by its ID."""
        slave = self._slaves[ID_slave]
        return slave.ack_0x12(ID_group)

    def cmd_0x30(self, IDs_variable):
        """Create group of variables."""
        ID_group = len(self._groups)
        self._groups[ID_group] = IDs_variable[:]
        # broadcast command to slaves
        if self.slaves:
            for slave in self.slaves:
                self.slave.cmd_0x30(IDs_variable)

    def cmd_0x32(self):
        """Remove all groups of variables."""
        self._groups = []
        # broadcast command to slaves
        if self.slaves:
            for slave in self.slaves:
                self.slave.cmd_0x32()

    def cmd_0x50(self, ID_slave, ID_function, **kwargs):
        """Execute function identified by its ID."""
        slave = self._slaves[ID_slave]
        return slave.ack_0x50(ID_function, **kwargs)

    # --- private methods ---

    # def _broadcast_master(self):
    #     if self._slaves:
    #         for slave in self._slaves:
    #             slave.master = self


class BSMPDeviceSlave:
    """BSMP class."""

    def __init__(self, variables, functions,
                 ID_device=None):
        """Init method."""
        self._ID_device = ID_device
        self._variables = {ID: value for ID, value in variables.items()}
        self._functions = {ID: value for ID, value in functions.items()}
        self._groups = {}

    @property
    def ID_device(self):
        """Return the BSMP ID for the device."""
        return self._ID_device

    @property
    def master(self):
        """Return master device."""
        return self._master

    @master.setter
    def master(self, value):
        """Set master device."""
        self._master = value

    @property
    def variables(self):
        """Return variables dictionary."""
        return self._variables

    def ack_0x10(self, ID_variable):
        """Read variable identified by its ID."""
        raise NotImplementedError

    def ack_0x12(self, ID_group):
        """Read group variables identified by its ID (slave)."""
        raise NotImplementedError

    def ack_0x50(self, ID_function, **kwargs):
        """Slave response to function execution."""
        raise NotImplementedError

    # --- private methods ---

    # def _broadcast_master(self):
    #     if self._slaves:
    #         for slave in self._slaves:
    #             slave.master = self



class BSMPDevice:
    """BSMP class."""

    def __init__(self, variables, functions,
                 ID_device=None, master=None, slaves=None):
        """Init method."""
        self._ID_device = ID_device
        self._variables = {ID: value for ID, value in variables.items()}
        self._functions = {ID: value for ID, value in functions.items()}
        self._groups = {}
        self.master = master
        self._slaves = {}
        if slaves is not None:
            if isinstance(slaves, (list, tuple)):
                for i in range(len(slaves)):
                    self._slaves[i] = slaves[i]
            elif isinstance(slaves, dict):
                for k, v in slaves.items():
                    self._slaves[k] = v

    @property
    def ID_device(self):
        """Return the BSMP ID for the device."""
        return self._ID_device

    @property
    def master(self):
        """Return master device."""
        return self._master

    @master.setter
    def master(self, value):
        """Set master device."""
        self._master = value

    @property
    def slaves(self):
        """Return slave devices."""
        return self._slaves

    @slaves.setter
    def slaves(self, value):
        """Set slaves devices."""
        self._slaves = value
        self._broadcast_master()

    def add_slave(self, slave):
        """Add slave."""
        self._slaves[slave.ID_device] = slave

    @property
    def variables(self):
        """Return variables dictionary."""
        return self._variables

    # --- master commands ---

    def cmd_0x00(self):
        """Return BSMP protocol version."""
        return __version__

    def cmd_0x10(self, ID_slave, ID_variable):
        """Read variable identified by its ID."""
        slave = self._slaves[ID_slave]
        return slave.ack_0x10(ID_variable)

    def cmd_0x12(self, ID_slave, ID_group):
        """Read group variables identified by its ID."""
        slave = self._slaves[ID_slave]
        return slave.ack_0x12(ID_group)

    def cmd_0x30(self, IDs_variable):
        """Create group of variables."""
        ID_group = len(self._groups)
        self._groups[ID_group] = IDs_variable[:]
        # broadcast command to slaves
        if self.slaves:
            for slave in self.slaves:
                self.slave.cmd_0x30(IDs_variable)

    def cmd_0x32(self):
        """Remove all groups of variables."""
        self._groups = []
        # broadcast command to slaves
        if self.slaves:
            for slave in self.slaves:
                self.slave.cmd_0x32()

    def cmd_0x50(self, ID_slave, ID_function, **kwargs):
        """Execute function identified by its ID."""
        slave = self._slaves[ID_slave]
        return slave.ack_0x50(ID_function, **kwargs)

    # --- slave acknowledgments ---

    def ack_0x10(self, ID_variable):
        """Read variable identified by its ID."""
        raise NotImplementedError

    def ack_0x12(self, ID_group):
        """Read group variables identified by its ID (slave)."""
        raise NotImplementedError

    def ack_0x50(self, ID_function, **kwargs):
        """Slave response to function execution."""
        raise NotImplementedError

    # --- private methods ---

    def _broadcast_master(self):
        if self._slaves:
            for slave in self._slaves:
                slave.master = self
