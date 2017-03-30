
import siriuspy.servweb as _web
import siriuspy.util as _util

_timeout = 1.0


class _MagData:

    def __init__(self, timeout=_timeout):

        self.mag_excitation_dict = None
        self.magps_sp_limits_dict = None

        if _web.server_online():
            self._build_mag_sp_limits(timeout)
            self._build_mag_excitation_dict()

    def _build_mag_sp_limits(self, timeout=_timeout):
        text = _web.magnets_setpoint_limits(timeout=timeout)
        data, param_dict = _util.read_text_data(text)
        self.setpoint_unit = tuple(param_dict['unit'])
        setpoint_limit_labels = tuple(param_dict['power_supply_type'])
        self.magps_sp_limits_dict = {}
        for line in data:
            magps_name, *limits = line
            db = {setpoint_limit_labels[i]:limits[i] for i in range(len(setpoint_limit_labels))}
            self.magps_sp_limits_dict[magps_name] = db

    def _build_mag_excitation_dict(self):
        pass


_magdata = None
def _get_magdata():
    # encapsulating _psdata within a function avoid creating the global object
    # (which is time consuming) at module load time.
    global _magdata
    if _magdata is None:
        _magdata = _MagData()
    return _magdata


# PSDATA API
# ==========

def server_online():
    """Return True/False if Sirius web server is online."""
    return _web.server_online()

def get_magnet_names():
    """Return a name list of magnets"""
    magdata = _get_magdata()
    return tuple(magdata.mag_excitation_dict.keys())

def get_magps_names():
    """Return a name list of magnets"""
    magdata = _get_magdata()
    return tuple(magdata.magps_sp_limits_dict.keys())


def get_magps_unit():
    """Return the power supplies' unit for the currents."""
    magdata = _get_magdata()
    return magdata.setpoint_unit

def get_magps_setpoint_limits(magps=None):
    """Return a dictionary with setpoint limits of a given power supply name of
    type."""
    magdata = _get_magdata()
    return magdata.magps_sp_limits_dict[magps]
