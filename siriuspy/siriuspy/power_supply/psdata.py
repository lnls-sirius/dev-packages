import siriuspy.macapp_web as _web

_timeout = 1.0

class _PSData:
    """Class with names and excitation polarities of all power supplies.

    Data on power supplies are read from the Sirius web server.
    """

    def __init__(self, timeout=_timeout):

        self._pstype_name_list = None
        self._pstype_polarity_list = None
        self._pstype_sp_limits_dict = None
        self._setpoint_unit = None
        self._setpoint_limit_names = None
        self._ps_name_list = None
        self._pstype2ps_dict = None
        self._ps2pstype_dict = None

        if _web.server_online():
            pstypes_text = _web.power_supplies_pstypes_names_read(timeout=_timeout)
            self._build_pstype_data(pstypes_text)
            self._build_ps_data()
            self._build_pstype_sp_limits()

    @property
    def pstype_name_list(self):
        """Return a list of names of all power supply types."""
        return self._pstype_name_list

    @property
    def ps_name_list(self):
        """Return a list of names of all power supplies."""
        return self._ps_name_list

    @property
    def nr_pstypes(self):
        """Return the number of power supply types."""
        return len(self._pstype_name_list)

    @property
    def nr_ps(self):
        """Return the number of power supplies."""
        return len(self._ps_name_list)

    @property
    def setpoint_unit(self):
        return self._setpoint_unit

    @property
    def setpoint_limit_names(self):
        return self._setpoint_limit_names

    def get_polarity(self, psname):
        """Return the polarity of a given power supply or power supply type."""
        if psname in self._pstype_name_list:
            idx = self._pstype_name_list.index(psname)
            return self._pstype_polarity_list[idx]
        elif psname in self._ps_name_list:
            polatity = {}
            pstype_name = self._ps2pstype_dict[psname]
            idx = self._pstype_name_list.index(pstype_name)
            return self._pstype_polarity_list[idx]
        else:
            return None

    def get_setpoint_limits(self, psname, *limit_names):
        """Return setpoint limits of given power supply of power suppy type.

        Arguments:

        psname -- name of power supply of power supply type
        limit_names -- limit names of interest
                       a) it can be a sequence of strings, each for a limit name of interest
                       b) if not passed, all defined limits are returned
                       c) if a single string, the single value of the the corresponding limit is returned

        returns:

        A dictionary with name and value pair of the requested limits.
        In case of a string argument for single limit name, a single value is
        returned.
        """

        if self._pstype_name_list is None: return None

        if psname in self._pstype_name_list:
            values = self._pstype_sp_limits_dict[psname]
        elif psname in self._ps_name_list:
            pstype_name  = self._ps2pstype_dict[psname]
            values = self._pstype_sp_limits_dict[pstype_name]
        else:
            return None

        if len(limit_names) == 0:
            limit_names = self._setpoint_limit_names
        if len(limit_names) == 1 and isinstance(limit_names[0], str):
            idx = self._setpoint_limit_names.index(limit_names[0])
            return values[idx]

        limits_dict = {}
        for limit_name in limit_names:
            idx = self._setpoint_limit_names.index(limit_name)
            limits_dict[limit_name] = values[idx]
        return limits_dict

    def get_pstype2ps(self, pstype):
        """Return a list of power supplies of a given type."""
        if isinstance(pstype, str):
            return self._pstype2ps_dict[pstype]
        elif isinstance(pstype, int):
            return self._pstype2ps_dict[self._pstype_name_list[pstype]]

    def get_ps2pstype(self, ps):
        """Return a list of power supply typesies of a given type."""
        if isinstance(ps, str):
            return self._ps2pstype_dict[ps]
        elif isinstance(ps, int):
            return self._ps2pstype_dict[self._ps_name_list[ps]]

    def _build_pstype_data(self, text):
        data, _ = _PSData._read_text(text)
        names, polarities = [], []
        for datum in data:
            name, polarity = datum[0], datum[1]
            names.append(name), polarities.append(polarity)
        self._pstype_name_list = tuple(names)
        self._pstype_polarity_list = tuple(polarities)

    def _build_ps_data(self):

        # read data from files in the web server and build pstype2ps dict
        self._pstype2ps_dict = {}
        for name in self.pstype_name_list:
            text = _web.power_supplies_pstype_data_read(name + '.txt', timeout=_timeout)
            self._pstype2ps_dict[name] = tuple(self._read_text_pstype(text))

        # build ps2pstype dict
        self._ps2pstype_dict = {}
        for pstype_name in self._pstype_name_list:
            for ps_name in self._pstype2ps_dict[pstype_name]:
                if ps_name in self._ps2pstype_dict:
                    raise Exception('power supply "' + ps_name + '" is listed in more than one power supply type files!')
                else:
                    self._ps2pstype_dict[ps_name] = pstype_name

        self._ps_name_list = sorted(self._ps2pstype_dict.keys())

    def _build_pstype_sp_limits(self):
        text = _web.power_supplies_pstype_setpoint_limits(timeout=_timeout)
        data, param_dict = _PSData._read_text(text)
        self._setpoint_unit = tuple(param_dict['unit'])
        self._setpoint_limit_names = tuple(param_dict['power_supply_type'])
        self._pstype_sp_limits_dict = {pstype_name:[None,]*len(data[0]) for pstype_name in self._pstype_name_list}
        for line in data:
            pstype_name, *limits = line
            self._pstype_sp_limits_dict[pstype_name] = [float(limit) for limit in limits]
        for pstype_name in self._pstype_name_list:
            self._pstype_sp_limits_dict[pstype_name] = tuple(self._pstype_sp_limits_dict[pstype_name])

    def _read_text_pstype(self, text):
        data, _ = _PSData._read_text(text)
        psnames = []
        for datum in data:
            psnames.append(datum[0])
        return psnames

    @staticmethod
    def _read_text(text):
        lines = text.splitlines()
        parameters = {}
        data = []
        for line in lines:
            line = line.strip()
            if not line: continue # empty line
            if line[0] == '#':
                if len(line[1:].strip())>0:
                    token, *words = line[1:].split()
                    if token[0] == '[':
                        # it is a parameter.
                        parm = token[1:-1].strip()
                        parameters[parm] = words
            else:
                # it is a data line
                data.append(line.split())
        return data, parameters



# API
# ===

def server_online():
    """Return True/False if Sirius web server is online."""
    return _web.server_online()

_psdata = None
def get_psdata():
    """Return an object with static information of power supplies."""

    # encapsulating _psdata within a function avoid creating the global object
    # (which is time consuming) at module load time.
    global _psdata
    if _psdata is None:
        _psdata = _PSData()
    return _psdata
