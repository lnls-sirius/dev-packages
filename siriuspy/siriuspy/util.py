"""Util module.

    Implementation of general-purpose classes and functions used in IOCs, HLAS
and siriuspy subpackages and modules.
"""

import os as _os
import logging as _log
import inspect as _inspect
import subprocess as _sp
import time as _time
import math as _math
import datetime as _datetime
import epics as _epics
import numpy as _np
import sys as _sys

from siriuspy import envars as _envars


def conv_splims_labels(label):
    """Convert setpoint limit labels from pcaspy to epics and vice-versa."""
    # Limits description:
    # -------------------
    # DRVH     driver high level limit
    # HIHI     high-high level limit (ALARM)
    # HIGH     IOC high level limit (ALARM)
    # DRVL     driver low level limit
    # LOLO     IOC low-low level limit (ALARM)
    # LOW      IOC low level limit (ALARM)
    # LOPR     Low operating range
    # HOPR     High operating range
    #
    # Rules
    # -----
    # LOLO <= LO <= HI <= HIHI
    # DRVL <= LOPR <= HOPR <= DRVH.
    #
    labels_dict = {
        # Epics-DB  pcaspy    PyEpics
        # ===========================
        'DRVH':     'DRVH',   # ???
        'HIHI':     'hihi',   # upper_alarm_limit
        'HIGH':     'high',   # upper_warning_limit
        'HOPR':     'hilim',  # upper_disp_limit & upper_ctrl_limit
        'LOPR':     'lolim',  # lower_disp_limit & lower_ctrl_limit
        'LOW':      'low',    # lower_warning_limit
        'LOLO':     'lolo',   # lower_alarm_limit
        'DRVL':     'DRVL',   # ???
        'TSTV':     'TSTV',   # SIRIUS specific (Test value)
        'TSTR':     'TSTR',   # SIRIUS specific (Test acceptable range)
    }
    if label in labels_dict:
        # epics -> pcaspy
        return labels_dict[label]
    else:
        for k, v in labels_dict.items():
            if v == label:
                # pcaspy -> epics
                return k
        raise KeyError('Invalid splims label "' + label + '"!')


def get_last_commit_hash():
    """Get commit Hash of the repository of the calling file."""
    fname = _os.path.realpath(_inspect.stack()[1][1])
    path = fname.rpartition(_os.path.sep)[0]
    pwd = _os.path.abspath('.')
    return _sp.getoutput('cd ' + path +
                         '; git log --format=%h -1; cd ' + pwd)


def get_timestamp(now=None):
    """Get formatted timestamp ."""
    if now is None:
        now = _time.time()
    st = _datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d-%H:%M:%S')
    st = st + '.{0:03d}'.format(int(1000*(now-int(now))))
    return st


def read_text_data(text):
    """Parse text data from sirius-consts web server."""
    lines = text.splitlines()
    parameters = {}
    data = []
    for line in lines:
        line = line.strip()
        if not line:
            continue  # empty line
        if line[0] == '#':
            if len(line[1:].strip()) > 0:
                token, *words = line[1:].split()
                if token[0] == '[':
                    # it is a parameter.
                    parm = token[1:-1].strip()
                    parameters[parm] = words
        else:
            # it is a data line
            data.append(line.split())
    return data, parameters


def print_ioc_banner(ioc_name, db, description, version, prefix):
    """IOC banner."""
    ld = '==================================='
    nw = (len(ld)-len(ioc_name))//2
    line = ' '*nw + ioc_name + ' '*nw
    _log.info(ld)
    _log.info(line)
    _log.info(ld)
    _log.info(description)
    _log.info('LNLS, Sirius Project.')
    _log.info('Version   : ' + version)
    _log.info('Timestamp : ' + get_timestamp())
    _log.info('Prefix    : ' + prefix)
    _log.info('')
    pvs = sorted(tuple(db.keys()))
    for i, pv in enumerate(pvs, 1):
        _log.info('{0:04d} {1:<}'.format(i, pv))
    _log.info('')


def configure_log_file(stream=None, filename=None, debug=False):
    """Configure logging messages for the IOCs."""
    if stream is not None:
        dic_ = {'stream': stream}
    elif filename is not None:
        dic_ = {'filename': filename, 'filemode': 'w'}
    else:
        dic_ = {'stream': _sys.stdout}

    level = _log.DEBUG if debug else _log.INFO
    fmt = ('%(levelname)7s | %(asctime)s | ' +
           '%(module)15s.%(funcName)-20s[%(lineno)4d] ::: %(message)s')
    _log.basicConfig(format=fmt, datefmt='%F %T', level=level, **dic_)


def save_ioc_pv_list(ioc_name, prefix, db, filename=None):
    """Save a list of the IOC pvs."""
    if filename is None:
        home = _os.path.expanduser('~')
        path = _os.path.join(home, 'sirius-iocs', 'pvs')
        filename = ioc_name + ".txt"
    else:
        path = _os.path.join(home, 'sirius-iocs', 'pvs')

    if not _os.path.exists(path):
        _os.makedirs(path)
    with open(path + "/" + filename, "w") as fd:
        fd.write("{}\n".format(prefix[1]))
        for pv in db:
            fd.write("{}\n".format(prefix[0] + pv))


def get_electron_rest_energy():
    """Return electron rest energy [GeV]."""
    second = 1.0
    meter = 1.0
    kilogram = 1.0
    ampere = 1.0
    newton = kilogram * meter / second
    joule = newton * meter
    watt = joule / second
    coulomb = second * ampere
    volt = watt / ampere
    light_speed = 299792458 * (meter/second)    # [m/s]   - definition
    electron_mass = 9.10938291e-31 * kilogram
    #  2014-06-11 - http://physics.nist.gov/cgi-bin/cuu/Value?me
    elementary_charge = 1.602176565e-19 * coulomb
    #  2014-06-11 - http://physics.nist.gov/cgi-bin/cuu/Value?e
    electron_volt = elementary_charge * volt
    joule_2_eV = (joule / electron_volt)
    electron_rest_energy = electron_mass * _math.pow(light_speed, 2)
    # [Kg̣*m^2/s^2] - derived
    electron_rest_energy = joule_2_eV * electron_rest_energy / 1e9
    return electron_rest_energy


def beam_rigidity(energy):
    """Return beam rigidity, beta amd game, given its energy [GeV]."""
    if isinstance(energy, (list, tuple)):
        energy = _np.array(energy)
    second = 1.0
    meter = 1.0
    light_speed = 299792458 * (meter/second)    # [m/s]   - definition
    electron_rest_energy = get_electron_rest_energy()
    gamma = energy/electron_rest_energy
    if isinstance(gamma, _np.ndarray):
        if _np.any(energy < electron_rest_energy):
            raise ValueError('Electron energy less than rest energy!')
        beta = _np.sqrt(((gamma-1.0)/gamma)*((gamma+1.0)/gamma))
        # beta[gamma < 1.0] = 0.0
    else:
        if energy < electron_rest_energy:
            # raise ValueError('Electron energy less than rest energy!')
            beta = 0.0
        else:
            beta = _math.sqrt(((gamma-1.0)/gamma)*((gamma+1.0)/gamma))
    brho = beta * (energy*1e9) / light_speed
    return brho, beta, gamma


def check_pv_online(pvname, timeout=1.0, use_prefix=True):
    """Return whether a PV is online."""
    if use_prefix:
        pvname = _envars.vaca_prefix + pvname
    pv = _epics.PV(pvname=pvname, connection_timeout=timeout)
    status = pv.wait_for_connection(timeout=timeout)
    return status


def get_strength_label(magfunc):
    """Return magnetic function strength label."""
    if magfunc == 'dipole':
        return 'Energy'
    elif magfunc in ('quadrupole', 'quadrupole-skew'):
        return 'KL'
    elif magfunc in ('sextupole',):
        return 'SL'
    elif magfunc in ('corrector-horizontal', 'corrector-vertical'):
        return 'Kick'
    else:
        raise ValueError('magfunc "{}" not defined!'.format(magfunc))


def get_strength_units(magfunc, section=None):
    """Return strength units."""
    if magfunc == 'dipole':
        return 'GeV'
    elif magfunc in ('quadrupole', 'quadrupole-skew'):
        return '1/m'
    elif magfunc in ('sextupole',):
        return '1/m^2'
    elif magfunc in ('corrector-horizontal', 'corrector-vertical'):
        if section in ('SI', 'BO'):
            return 'urad'
        elif section in ('TB', 'TS', 'LI'):
            return 'mrad'
    else:
        raise ValueError('magfunc "{}" not defined!'.format(magfunc))


def update_bit(v, bit_pos, bit_val):
    """Update a specific integer bit.

    Parameters
    ----------
    v: non-negative int
        Integer whose bit will be updated.
    bit_pos: non-negative int
        The position of the bit to update.
    bit_val: Any python object that evaluates to True or False
        Value to put on the bit.

    """
    if not isinstance(v, int) or not isinstance(bit_pos, int):
        raise TypeError("v and bit_pos must be integers.")

    if v < 0 or bit_pos < 0:
        raise ValueError("v and bit_pos must be non-negative.")

    return v | (1 << bit_pos) if bit_val else v & ~(1 << bit_pos)


def get_bit(v, bit_pos):
    """Update a specific integer bit.

    Parameters
    ----------
    v: non-negative int
        Integer whose bit will be get.
    bit_pos: int
        The position of the bit to get.

    """
    if not isinstance(v, int) or not isinstance(bit_pos, int):
        raise TypeError("v and bit_pos must be integers")

    if v < 0 or bit_pos < 0:
        raise ValueError("v and bit_pos must be non-negative.")

    return (v >> bit_pos) & 1


def check_public_interface_namespace(namespace, valid_interface,
                                     checkdoc_flag=True,
                                     print_flag=True):
    """Check function used in unittests to test module's public interface.

    This function checks only static public interface symbols. It does not
    check those symbols that are created within class methods.
    """
    for name in namespace.__dict__:
        if checkdoc_flag:
            doc = getattr(name, '__doc__')
            if doc is None or len(doc) < 5:
                if print_flag:
                    print('"' + name + '" has an invalid docstring!')
                return False
        if not name.startswith('_') and name not in valid_interface:
            if print_flag:
                print('Invalid symbol: ', name)
            return False
    for name in valid_interface:
        if name not in namespace.__dict__:
            if print_flag:
                print('Missing symbol: ', name)
            return False
    return True
