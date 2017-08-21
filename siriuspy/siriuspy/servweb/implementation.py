"""Impletentation of webserver data retrievement functions."""
import urllib.request as _urllib_request
import siriuspy.envars as _envars
import siriuspy.util as _util

_timeout = 1.0  # [seconds]
_excdat_folder = '/magnet/excitation-data/'
_magnet_folder = '/magnet/'
_ps_folder = '/pwrsupply/'
_pstypes_data_folder = '/pwrsupply/pstypes-data/'
_diag_folder = '/diagnostics/'
_timesys_folder = '/timesys/'
_respm_folder = '/respm/'


def read_url(url, timeout=_timeout):
    """Read URL from server."""
    try:
        url = _envars.server_url_consts + url
        response = _urllib_request.urlopen(url, timeout=timeout)
        data = response.read()
        text = data.decode('utf-8')
    except Exception:
        errtxt = 'Error reading url "' + url + '"!'
        raise Exception(errtxt)

    return text


def server_online():
    """Verify if the server is online."""
    url = _envars.server_url_consts
    try:
        read_url(url, timeout=_timeout)
        return True
    except Exception:
        return False


def magnets_excitation_data_get_filenames_list(timeout=_timeout):
    """Get list of filenames in magnet excitation data folder at web server."""
    text = read_url(_excdat_folder, timeout=timeout)
    words = text.split('"[TXT]"></td><td><a href="')
    fname_list = []
    for word in words[1:]:
        fname = word.split('.txt">')[1].split('</a></td><td')
        fname_list.append(fname[0])
    return fname_list


def magnets_excitation_data_read(filename, timeout=_timeout):
    """Return the text of the retrieved magnet excitation data."""
    return read_url(_excdat_folder + filename, timeout=timeout)


def magnets_setpoint_limits(timeout=_timeout):
    """Get the magnet setpoint limits."""
    url = _magnet_folder + 'magnet-setpoint-limits.txt'
    return read_url(url, timeout=timeout)


def pulsed_magnets_setpoint_limits(timeout=_timeout):
    """Get the magnet setpoint limits."""
    url = _magnet_folder + 'pulsed-magnet-setpoint-limits.txt'
    return read_url(url, timeout=timeout)


def magnets_excitation_ps_read(timeout=_timeout):
    """Return the power supply excitation data."""
    url = _magnet_folder + 'magnet-excitation-ps.txt'
    return read_url(url, timeout=timeout)


def power_supplies_pstypes_names_read(timeout=_timeout):
    """Return the text of the power supplies type."""
    url = _ps_folder + 'pstypes-names.txt'
    return read_url(url, timeout=timeout)


def power_supplies_pstype_data_read(filename, timeout=_timeout):
    """Return the power supply data."""
    url = _pstypes_data_folder + filename
    return read_url(url, timeout=timeout)


def power_supplies_pstype_setpoint_limits(timeout=_timeout):
    """Return the power supply setpoint limits data."""
    url = _ps_folder + 'pstypes-setpoint-limits.txt'
    return read_url(url, timeout=timeout)


def pulsed_power_supplies_pstype_setpoint_limits(timeout=_timeout):
    """Return the power supply setpoint limits data."""
    url = _ps_folder + 'putypes-setpoint-limits.txt'
    return read_url(url, timeout=timeout)


def beaglebone_power_supplies_mapping(timeout=_timeout):
    """Return the beaglebone Black connections list."""
    url = _ps_folder + 'beaglebone-mapping.txt'
    return read_url(url, timeout=timeout)


def crate_to_bpm_mapping(timeout=_timeout):
    """Return the crate to bpm mapping."""
    url = _diag_folder + 'crates-connection.txt'
    return read_url(url, timeout=timeout)


def bpms_data(timeout=_timeout):
    """Return the BPMs data."""
    url = _diag_folder + 'bpms-data.txt'
    return read_url(url, timeout=timeout)


def timing_devices_mapping(timeout=_timeout):
    """Return the timing devices connections mapping."""
    url = _timesys_folder + 'timing-devices-connection.txt'
    return read_url(url, timeout=timeout)


def high_level_triggers(timeout=_timeout):
    """Return the data defining the high level triggers."""
    url = _timesys_folder + 'high-level-triggers.txt'
    return read_url(url, timeout=timeout)


def response_matrix_read(filename, timeout=_timeout):
    """Return response matrices."""
    url = _respm_folder + filename
    text = read_url(url, timeout=timeout)
    data, parameters = _util.read_text_data(text)
    return data, parameters
