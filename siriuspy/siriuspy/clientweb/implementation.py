"""Impletentation of webserver data retrievement functions."""
import re as _re
import urllib.request as _urllib_request
import siriuspy.envars as _envars

_timeout = 1.0  # [seconds]
_excdat_folder = '/magnet/excitation-data/'
_magnet_folder = '/magnet/'
_ps_folder = '/pwrsupply/'
_bbb_folder = '/beaglebone/'
_pstypes_data_folder = '/pwrsupply/pstypes-data/'
_diag_folder = '/diagnostics/'
_timesys_folder = '/timesys/'
_respm_folder = '/respm/'

# TODO: we should adopt a naming standard for functions.
# maybe to use a name prefix that indicates what top folder contains the data
# to be accessed?


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
    try:
        read_url('', timeout=_timeout)
        return True
    except Exception:
        return False


def magnets_model_data(timeout=_timeout):
    """Return the text of the retrieved magnet model data."""
    url = _magnet_folder + 'magnets-model-data.txt'
    return read_url(url, timeout=timeout)


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


def ps_pstypes_names_read(timeout=_timeout):
    """Return the text of the power supplies type."""
    url = _ps_folder + 'pstypes-names.txt'
    return read_url(url, timeout=timeout)


def ps_pstype_data_read(filename, timeout=_timeout):
    """Return the power supply data."""
    url = _pstypes_data_folder + filename
    return read_url(url, timeout=timeout)


def ps_pstype_setpoint_limits(timeout=_timeout):
    """Return the power supply setpoint limits data."""
    url = _ps_folder + 'pstypes-setpoint-limits.txt'
    return read_url(url, timeout=timeout)


def pu_pstype_setpoint_limits(timeout=_timeout):
    """Return the power supply setpoint limits data."""
    url = _ps_folder + 'putypes-setpoint-limits.txt'
    return read_url(url, timeout=timeout)


def ps_psmodels_read(timeout=_timeout):
    """Return the psmodels file."""
    url = _ps_folder + 'psmodels.txt'
    return read_url(url, timeout=timeout)


def ps_siggen_configuration_read(timeout=_timeout):
    """Return power supplies signal default generation configuration."""
    url = _ps_folder + 'siggen-configuration.txt'
    return read_url(url, timeout=timeout)


def pu_psmodels_read(timeout=_timeout):
    """Return the pumodels file."""
    url = _ps_folder + 'pumodels.txt'
    return read_url(url, timeout=timeout)


def beaglebone_freqs_mapping(timeout=_timeout):
    """Return the beaglebone Black BSMP PRU sync off and on freqs."""
    url = _bbb_folder + 'beaglebone-freq.txt'
    return read_url(url, timeout=timeout)


def beaglebone_ip_list(timeout=_timeout):
    """Return the beaglebone Black IP list."""
    url = _bbb_folder + 'ip-list.txt'
    return read_url(url, timeout=timeout)


def bbb_udc_mapping(timeout=_timeout):
    """Read beaglebone-udc mapping."""
    url = _bbb_folder + 'beaglebone-udc.txt'
    return read_url(url, timeout=timeout)


def udc_ps_mapping(timeout=_timeout):
    """Read beaglebone-udc mapping."""
    url = _bbb_folder + 'udc-bsmp.txt'
    return read_url(url, timeout=timeout)


def crates_mapping(timeout=_timeout):
    """Return the crates mapping."""
    url = _diag_folder + 'microTCA-vs-BPMs-mapping/'
    text = read_url(url, timeout=timeout)
    pat = _re.compile('>(names.crate[a-zA-Z_0-9]*.cfg)<')
    files = pat.findall(text)
    txt = ''
    for fi in files:
        for t in read_url(url + fi, timeout=timeout).splitlines():
            txt += '{0:20s}'.format(fi[6:13]) + t + '\n'
        txt += '\n\n'
    return txt


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
    url = _timesys_folder + 'high-level-triggers.py'
    return read_url(url, timeout=timeout)


def high_level_events(timeout=_timeout):
    """Return the data defining the high level events."""
    url = _timesys_folder + 'high-level-events.py'
    return read_url(url, timeout=timeout)


def bsmp_dclink_mapping(timeout=_timeout):
    """Read bsmp dclink mapping."""
    url = _ps_folder + 'bsmp-dclink.txt'
    return read_url(url, timeout=timeout)
