"""Util module.

    Implementation of general-purpose classes and functions used in IOCs, HLAS
and siriuspy subpackages and modules.
"""

import os as _os
import inspect as _inspect
import subprocess as _sp
import time as _time
import math as _math
import datetime as _datetime
import siriuspy.envars as _envars
import epics as _epics
import numpy as _np
import sys as _sys


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
        return None


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


# def get_prop_types():
#     """Get attribute dictionary if PV properties."""
#     prop_types = {
#         'RB':  {'read': True,  'write': False, 'enum': False},
#         'SP':  {'read': True,  'write': True,  'enum': False},
#         'Sel': {'read': True,  'write': True,  'enum': True},
#         'Sts': {'read': True,  'write': False, 'enum': True},
#         'Cmd': {'read': False, 'write': True,  'enum': False},
#     }
#     return prop_types


# def get_prop_suffix(prop):
#     """Get property suffix."""
#     if prop[-3:] == '-RB':
#         return 'RB'
#     if prop[-3:] == '-SP':
#         return 'SP'
#     if prop[-4:] == '-Sel':
#         return 'Sel'
#     if prop[-4:] == '-Sts':
#         return 'Sts'
#     if prop[-4:] == '-Mon':
#         return 'Mon'
#     if prop[-4:] == '-Cmd':
#         return 'Cmd'
#     return None


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


def print_ioc_banner(ioc_name, db, description, version, prefix, file=None):
    """IOC banner."""
    file = _sys.stdout if file is None else file
    ld = '==================================='
    nw = (len(ld)-len(ioc_name))//2
    line = ' '*nw + ioc_name + ' '*nw
    print(ld, file=file)
    print(line, file=file)
    print(ld, file=file)
    print(description, file=file)
    print('FAC@LNLS,   Sirius Project.', file=file)
    print('Version   : ' + version, file=file)
    print('Timestamp : ' + get_timestamp(), file=file)
    print('Prefix    : ' + prefix, file=file)
    print()
    pvs = sorted(tuple(db.keys()))
    max_len = 0
    for pv in pvs:
        if len(pv) > max_len:
            max_len = len(pv)
    i = 1
    new_line = False
    for pv in pvs:
        print(('{0:04d} {1:<'+str(max_len+2)+'}  ').format(i, pv),
              end='', file=file)
        new_line = True
        i += 1
        if not (i-1) % 5:
            print('', file=file)
            new_line = False
    if new_line:
        print('', file=file)


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


def beam_rigidity(energy):
    """Return beam rigidity, beta amd game, given its energy [GeV]."""
    if isinstance(energy, (list, tuple)):
        energy = _np.array(energy)
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
    electron_rest_energy_eV = joule_2_eV * electron_rest_energy
    gamma = energy*1e9/electron_rest_energy_eV
    if isinstance(gamma, _np.ndarray):
        if _np.any(energy*1e9 < electron_rest_energy_eV):
            raise ValueError('Electron energy less than its rest energy!')
        beta = _np.sqrt(((gamma-1.0)/gamma)*((gamma+1.0)/gamma))
        # beta[gamma < 1.0] = 0.0
    else:
        if energy*1e9 < electron_rest_energy_eV:
            raise ValueError('Electron energy less than its rest energy!')
            # beta = 0.0
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


def update_integer_bit(integer, number_of_bits, value, bit):
    """Update a specific integer bit.

    Parameters
    ----------
    integer: int
        Integer whose bit will be updated.
    number_of_bits: (>=1)
        Number of bits of the integer whose bit will be updated.
    value: 0 | 1
        Value to put on the bit.
    bit: (0 <= bit < number_of_bits)
        The number of the bit.
    """
    if not isinstance(integer, int):
        raise TypeError

    if value > 1 or value < 0:
        raise ValueError

    if bit >= number_of_bits:
        raise ValueError

    allset = 1
    for i in range(number_of_bits-1):
        allset = 2*allset + 1

    if value == 1:
        mask = 1 << bit
        integer = integer | mask
    elif value == 0:
        mask = (1 << bit) ^ allset
        integer = integer & mask

    return integer
