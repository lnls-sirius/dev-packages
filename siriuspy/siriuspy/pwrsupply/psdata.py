import re as _re
import siriuspy.servweb as _web
import siriuspy.util as _util
import types as _types

_timeout = 1.0

class _PSData:
    """Class with names and excitation polarities of all power supplies.

    Data on power supplies are read from the Sirius web server.
    """

    def __init__(self, timeout=_timeout):

        self._filter = list()

        self._pstype_name_list = None
        self._pstype_polarity_list = None
        self._pstype_sp_limits_dict = None
        self._setpoint_unit = None
        self._setpoint_limit_labels = None
        self._ps_name_list = None
        self._pstype2ps_dict = None
        self._ps2pstype_dict = None

        if _web.server_online():
            pstypes_text = _web.power_supplies_pstypes_names_read(timeout=_timeout)
            self._build_pstype_data(pstypes_text)
            self._build_ps_data()
            self._build_pstype_sp_limits()

    @property
    def pwrsupply_types(self):
        """Return a list of names of all power supply types."""
        return self._pstype_name_list

    @property
    def pwrsupply_names(self):
        """Return a list of names of all power supplies."""
        if len(self._filter) > 0 and self._ps_name_list is not None:
            filtered_ps_name_list = list()
            for ps in self._ps_name_list:
                for pattern in self._filter:
                    if pattern.match(ps):
                        filtered_ps_name_list.append(ps)
                        break
            return filtered_ps_name_list

        return self._ps_name_list

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, regexp):
        self._filter.append(regexp)

    def clear_filter(self):
        self._filter.clear()

    def conv_pstype_2_psname(self, pstype):
        """Return a list of power supplies of a given type."""
        if isinstance(pstype, str):
            return self._pstype2ps_dict[pstype]
        elif isinstance(pstype, int):
            return self._pstype2ps_dict[self._pstype_name_list[pstype]]

    def conv_psname_2_pstype(self, ps):
        """Return the type of a given power supply."""
        if isinstance(ps, str):
            return self._ps2pstype_dict[ps]
        elif isinstance(ps, int):
            return self._ps2pstype_dict[self._ps_name_list[ps]]

    def get_setpoint_unit(self):
        return self._setpoint_unit

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

    def get_setpoint_limits(self, psname, *limit_labels):
        """Return setpoint limits of given power supply of power suppy type.

        Arguments:

        psname -- name of power supply of power supply type
        limit_labels -- limit labels of interest
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

        if len(limit_labels) == 0:
            limit_labels = self._setpoint_limit_labels
        if len(limit_labels) == 1 and isinstance(limit_labels[0], str):
            idx = self._setpoint_limit_labels.index(limit_labels[0])
            return values[idx]

        limits_dict = {}
        for limit_name in limit_labels:
            idx = self._setpoint_limit_labels.index(limit_name)
            limits_dict[limit_name] = values[idx]
        return limits_dict

    def _build_pstype_data(self, text):
        data, _ = _util.read_text_data(text)
        names, polarities = [], []
        for datum in data:
            name, polarity = datum[0], datum[1]
            names.append(name), polarities.append(polarity)
        self._pstype_name_list = tuple(names)
        self._pstype_polarity_list = tuple(polarities)

    def _build_ps_data(self):

        # read data from files in the web server and build pstype2ps dict
        self._pstype2ps_dict = {}
        for name in self._pstype_name_list:
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
        data, param_dict = _util.read_text_data(text)
        self._setpoint_unit = tuple(param_dict['unit'])
        self._setpoint_limit_labels = tuple(param_dict['power_supply_type'])
        self._pstype_sp_limits_dict = {pstype_name:[None,]*len(data[0]) for pstype_name in self._pstype_name_list}
        for line in data:
            pstype_name, *limits = line
            self._pstype_sp_limits_dict[pstype_name] = [float(limit) for limit in limits]
        for pstype_name in self._pstype_name_list:
            self._pstype_sp_limits_dict[pstype_name] = tuple(self._pstype_sp_limits_dict[pstype_name])

    def _read_text_pstype(self, text):
        data, _ = _util.read_text_data(text)
        psnames = []
        for datum in data:
            psnames.append(datum[0])
        return psnames


filters = _types.SimpleNamespace()

#SubSections
filters.FAM = 'Fam'
filters.TRIM = '\d{2}\w{0,2}'
#Devices
filters.DIPO = 'B.*'
filters.QUAD = '(?:QD|QF|Q[0-9]).*'
filters.DEFO_QUAD = 'QD.*'
filters.FOCU_QUAD = 'QF.*'
filters.SEXT = 'S(?:D|F)*'
filters.DEFO_SEXT = 'SD.*'
filters.FOCU_SECT = 'SF.*'
filters.CORR = '(?:C|FC).*'
filters.SLOW_CORR = 'C(?:H|V).*'
filters.H_SLOW_CORR = 'CH.*'
filters.V_SLOW_CORR = 'CV.*'
filters.FAST_CORR = 'FC.*'
filters.H_FAST_CORR = 'FCH.*'
filters.V_FAST_CORR = 'FCV.*'
filters.QUAD_SKEW = 'QS'

_psdata = None
def _get_psdata():
    # encapsulating _psdata within a function avoid creating the global object
    # (which is time consuming) at module load time.
    global _psdata
    if _psdata is None:
        _psdata = _PSData()
    return _psdata


# PSDATA API
# ==========
def server_online():
    """Return True/False if Sirius web server is online."""
    return _web.server_online()

def get_types():
    """Return a name list of power supply types."""
    psdata = _get_psdata()
    return psdata.pwrsupply_types

def get_names():
    """Return a name list of power supplies."""
    psdata = _get_psdata()
    psdata.clear_filter()
    return psdata.pwrsupply_names

def add_filter(section, sub_section, discipline, device):
    psdata = _get_psdata()

    if section is None:
        section = '[A-Z]{2}'
    if sub_section is None:
        sub_section = '\w{2,4}'
    if discipline is None:
        discipline = '[A-Z]{2,6}'
    if device is None:
        device = '.+'

    pattern = section + '-' + sub_section + ':' + discipline + '-' + device
    regexp = _re.compile(pattern)
    #Append new filter to psdata
    psdata.filter = regexp

def clear_filter():
    psdata = _get_psdata()
    psdata.clear_filter()

def get_filtered_names():
    psdata = _get_psdata()
    return psdata.pwrsupply_names

def get_polarity(psname):
    """Return the polarity type of a given power supply or power supply type."""
    psdata = _get_psdata()
    return psdata.get_polarity(psname)

def get_unit():
    """Return the power supplies' unit for the currents."""
    psdata = _get_psdata()
    return psdata._setpoint_unit()

def conv_pstype_2_psname(pstype):
    """Return a list of power supply of a given type."""
    psdata = _get_psdata()
    return psdata.conv_pstype_2_psname(pstype)

def conv_psname_2_pstype(psname):
    """Return the type name of a given power suppply."""
    psdata = _get_psdata()
    return psdata.conv_psname_2_pstype(psname)

def get_setpoint_limits(ps, *limit_labels):
    """Return a dictionary with setpoint limits of a given power supply name of
    type."""
    psdata = _get_psdata()
    return psdata.get_setpoint_limits(ps, *limit_labels)
