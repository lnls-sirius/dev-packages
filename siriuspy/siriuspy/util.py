"""Util module."""

import os as _os
import inspect as _inspect
import subprocess as _sp
import time as _time
import math as _math
import datetime as _datetime
import siriuspy.envars as _envars
import epics as _epics


def conv_splims_labels(label):
    """Convert setpoint limit labels from pcaspy to epics and vice-versa."""
    # Limits description:
    # -------------------
    # DRVH      driver high level limit
    # HIHI      high-high level limit (ALARM)
    # HIGH      IOC high level limit (ALARM)
    #  DRVL     driver low level limit
    #  LOLO     IOC low-low level limit (ALARM)
    #  LOW      IOC low level limit (ALARM)
    #  LOPR     Low operating range
    #  HOPR     High operating range
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
        'TSTV':     'TSTV',   # ---
        'TSTR':     'TSTR',   # ---
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


def get_signal_names():
    """Get signal names."""
    signal_names = {
        1: 'SIGHUP',		# Hangup (POSIX)
        2: 'SIGINT',		# Terminal interrupt (ANSI)
        3: 'SIGQUIT',		# Terminal quit (POSIX)
        4: 'SIGILL',		# Illegal instruction (ANSI)
        5: 'SIGTRAP',		# Trace trap (POSIX)
        6: 'SIGIOT',		# IOT Trap (4.2 BSD)
        7: 'SIGBUS',		# BUS error (4.2 BSD)
        8: 'SIGFPE',		# Floating point exception (ANSI)
        9: 'SIGKILL',		# Kill(can't be caught or ignored) (POSIX)
        10: 'SIGUSR1',		# User defined SIGnal 1 (POSIX)
        11: 'SIGSEGV',		# Invalid memory segment access (ANSI)
        12: 'SIGUSR2',		# User defined SIGnal 2 (POSIX)
        13: 'SIGPIPE',		# Write on a pipe with no reader, Broken pipe (POSIX)
        14: 'SIGALRM',		# Alarm clock (POSIX)
        15: 'SIGTERM',		# Termination (ANSI)
        16: 'SIGSTKFLT',    # Stack fault
        17: 'SIGCHLD',		# Child process has stopped or exited, changed (POSIX)
        18: 'SIGCONT',		# Continue executing, if stopped (POSIX)
        19: 'SIGSTOP',		# Stop executing(can't be caught or ignored) (POSIX)
        20: 'SIGTSTP',		# Terminal stop SIGnal (POSIX)
        21: 'SIGTTIN',		# Background process trying to read, from TTY (POSIX)
        22: 'SIGTTOU',		# Background process trying to write, to TTY (POSIX)
        23: 'SIGURG',		# Urgent condition on socket (4.2 BSD)
        34: 'SIGXCPU',		# CPU limit exceeded (4.2 BSD)
        25: 'SIGXFSZ',		# File size limit exceeded (4.2 BSD)
        26: 'SIGVTALRM',    # Virtual alarm clock (4.2 BSD)
        27: 'SIGPROF',		# Profiling alarm clock (4.2 BSD)
        28: 'SIGWINCH',		# Window size change (4.3 BSD, Sun)
        29: 'SIGIO',	    # I/O now possible (4.2 BSD)
        30: 'SIGPWR',	    # Power failure restart (System V)
    }
    return signal_names


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


def get_prop_types():
    """Get attribute dictionary if PV properties."""
    prop_types = {
        'RB':  {'read': True,  'write': False, 'enum': False},
        'SP':  {'read': True,  'write': True,  'enum': False},
        'Sel': {'read': True,  'write': True,  'enum': True},
        'Sts': {'read': True,  'write': False, 'enum': True},
        'Cmd': {'read': False, 'write': True,  'enum': False},
    }
    return prop_types


def get_prop_suffix(prop):
    """Get property suffix."""
    if prop[-3:] == '-RB':
        return 'RB'
    if prop[-3:] == '-SP':
        return 'SP'
    if prop[-4:] == '-Sel':
        return 'Sel'
    if prop[-4:] == '-Sts':
        return 'Sts'
    if prop[-4:] == '-Mon':
        return 'Mon'
    if prop[-4:] == '-Cmd':
        return 'Cmd'
    return None


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


def print_ioc_banner(ioc_name, db, description, version, prefix, ):
    """IOC banner."""
    ld = '==================================='
    nw = (len(ld)-len(ioc_name))//2
    line = ' '*nw + ioc_name + ' '*nw
    print(ld)
    print(line)
    print(ld)
    print(description)
    print('FAC@LNLS,   Sirius Project.')
    print('Version   : ' + version)
    print('Timestamp : ' + get_timestamp())
    print('Prefix    : ' + prefix)
    print()
    pvs = sorted(tuple(db.keys()))
    max_len = 0
    for pv in pvs:
        if len(pv) > max_len:
            max_len = len(pv)
    i = 1
    for pv in pvs:
        print(('{0:04d} {1:<'+str(max_len+2)+'}  ').format(i, pv), end='')
        new_line = True
        i += 1
        if not (i-1) % 5:
            print('')
            new_line = False
    if new_line:
        print('')


def save_ioc_pv_list(ioc_name, prefix, db):
    """Save a list of the IOC pvs."""
    home = _os.path.expanduser('~')
    path = _os.path.join(home, 'sirius-iocs', 'pvs')
    filename = ioc_name + ".txt"

    if not _os.path.exists(path):
        _os.makedirs(path)
    with open(path + "/" + filename, "w") as fd:
        fd.write("{}\n".format(prefix[1]))
        for pv in db:
            fd.write("{}\n".format(prefix[0] + pv))


def beam_rigidity(energy):
    """Return beam rigidity give its energy [GeV]."""
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
    try:
        beta = _math.sqrt(((gamma-1.0)/gamma)*((gamma+1.0)/gamma))
    except Exception:
        return 0
    brho = beta * (energy*1e9) / light_speed
    return brho


def check_running_ioc(pvname, timeout=1.0, use_prefix=True):
    """Return whether a PV is online."""
    if use_prefix:
        pvname = _envars.vaca_prefix + pvname
    pv = _epics.PV(pvname=pvname, connection_timeout=timeout)
    status = pv.wait_for_connection(timeout=timeout)
    return status
