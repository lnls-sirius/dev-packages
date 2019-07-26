"""Module with general utilities."""

import os as _os
from collections import Counter as _Counter
import logging as _log
import inspect as _inspect
import subprocess as _sp
import time as _time
import datetime as _datetime
import epics as _epics
import numpy as _np
import sys as _sys
from collections import namedtuple as _namedtuple

from mathphys import constants as _c
from mathphys import units as _u
from mathphys import beam_optics as _beam
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


# def save_ioc_pv_list(ioc_name, prefix, db, filename=None):
#     """Save a list of the IOC pvs.

#     Inputs:
#         ioc_name: name of the ioc;
#         prefix: str or 2-tuple. In case of a 2-tuple the first element is the
#                 sector prefix and the second element is the simulation prefix;
#         db: dictionary, set, tuple or list of pv names without the prefices.
#         filename (optional): the name of the file to save the PV names. In
#                 case no filename is given it will be built from the ioc_name.

#     """
#     if isinstance(prefix, (list, tuple)):
#         prefix_vaca = prefix[1]
#         prefix_sector = prefix[0]
#     else:
#         prefix_vaca = prefix
#         prefix_sector = ''

#     if filename is None:
#         home = _os.path.expanduser('~')
#         path = _os.path.join(home, 'iocs-log', 'pvs')
#         filename = ioc_name + ".txt"
#     else:
#         path = _os.path.join(home, 'iocs-log', 'pvs')

#     if not _os.path.exists(path):
#         _os.makedirs(path)
#     with open(path + "/" + filename, "w") as fd:
#         fd.write("{}\n".format(prefix_vaca))
#         for pv in db:
#             fd.write("{}\n".format(prefix_sector + pv))


def beam_rigidity(energy):
    """Return beam rigidity, beta amd game, given its energy [GeV]."""
    electron_rest_energy_eV = _c.electron_rest_energy * _u.joule_2_eV
    electron_rest_energy_GeV = electron_rest_energy_eV * _u.eV_2_GeV

    if isinstance(energy, (list, tuple)):
        energy = _np.array(energy)
    if isinstance(energy, _np.ndarray):
        if _np.any(energy < electron_rest_energy_GeV):
            raise ValueError('Electron energy less than rest energy!')
        brho, _, beta, gamma, _ = \
            _beam.beam_rigidity(energy=energy)
    else:
        brho, _, beta, gamma, _ = \
            _beam.beam_rigidity(energy=energy)
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


def get_strength_units(magfunc, pulsed=False):
    """Return strength units."""
    if magfunc == 'dipole':
        return 'GeV'
    elif magfunc in ('quadrupole', 'quadrupole-skew'):
        return '1/m'
    elif magfunc in ('sextupole',):
        return '1/m^2'
    elif magfunc in ('corrector-horizontal', 'corrector-vertical'):
        if not pulsed:
            return 'urad'
        else:
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


def mode(lst):
    """ Find statistical mode of iterable of hashable objects."""
    counter = _Counter(lst)
    return counter.most_common(1)[0]


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


def get_namedtuple(name, field_names, values=None):
    """Return an instance of a namedtuple Class.

    Inputs:
        - name:  Defines the name of the Class (str).
        - field_names:  Defines the field names of the Class (iterable).
        - values (optional): Defines field values . If not given, the value of
            each field will be its index in 'field_names' (iterable).

    Raises ValueError if at least one of the field names are invalid.
    Raises TypeError when len(values) != len(field_names)
    """
    if values is None:
        values = range(len(field_names))
    field_names = [f.replace(' ', '_') for f in field_names]
    return _namedtuple(name, field_names)(*values)
