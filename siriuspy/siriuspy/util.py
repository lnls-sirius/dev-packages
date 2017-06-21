import os as _os
import time as _time
import math as _math
import datetime as _datetime
from . import envars as _envars

def get_timestamp(now = None):
    if now is None:
        now = _time.time()
    st = _datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d-%H:%M:%S')
    st = st + '.{0:03d}'.format(int(1000*(now-int(now))))
    return st

# this function can be substituted with fernando's implementation in VACA
def get_prop_types():
    prop_types = {
        'RB'  : {'read':True,  'write':False, 'enum':False},
        'SP'  : {'read':True,  'write':True,  'enum':False},
        'Sel' : {'read':True,  'write':True,  'enum':True},
        'Sts' : {'read':True,  'write':False, 'enum':True},
        'Cmd' : {'read':False, 'write':True,  'enum':False},
    }
    return prop_types

# this function can be substituted with fernando's implementation in VACA
def get_prop_suffix(prop):
    if prop[-3:] == '-RB': return 'RB'
    if prop[-3:] == '-SP': return 'SP'
    if prop[-4:] == '-Sel': return 'Sel'
    if prop[-4:] == '-Sts': return 'Sts'
    if prop[-4:] == '-Mon': return 'Mon'
    if prop[-4:] == '-Cmd': return 'Cmd'
    return None

def read_text_data(text):
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

def print_ioc_banner(ioc_name, db, description, version, prefix, ):
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
        if len(pv)>max_len: max_len=len(pv)
    i=1;
    for pv in pvs:
        print(('{0:04d} {1:<'+str(max_len+2)+'}  ').format(i, pv), end=''); new_line=True
        i += 1
        if not (i-1) % 5:
            print(''); new_line=False
    if new_line: print('')

def conv_splims_labels(label):
    """Convert setpoint limit labels from pcaspy to epics and vice-versa."""
    labels_dict = {
        'DRVH' : 'DRVH',   # ??? [pyepics]
        'HIHI' : 'hihi',   # upper_alarm_limit [pyepics]
        'HIGH' : 'high',   # upper_warning_limit [pyepics]
        'HOPR' : 'hilim',  # upper_disp_limit & upper_ctrl_limit [pyepics]
        'LOPR' : 'lolim',  # lower_disp_limit & lower_ctrl_limit [pyepics]
        'LOW'  : 'low',    # lower_warning_limit [pyepics]
        'LOLO' : 'lolo',   # lower_alarm_limit [pyepics]
        'DRVL' : 'DRVL',   # ??? [pyepics]
        'TSTV' : 'TSTV',   # ---
        'TSTR' : 'TSTR',   # ---
    }
    if label in labels_dict:
        # epics -> pcaspy
        return labels_dict[label]
    else:
        for k,v in labels_dict.items():
            if v == label:
                # pcaspy -> epics
                return k
        return None

def beam_rigidity(energy):
    """Return beam rigidity give its energy [GeV]."""
    second  = 1.0; meter    = 1.0; kilogram = 1.0; ampere   = 1.0
    newton  = kilogram * meter / second
    joule   = newton * meter
    watt    = joule / second
    coulomb = second * ampere
    volt    = watt / ampere
    light_speed    = 299792458 * (meter/second)    # [m/s]   - definition
    electron_mass  = 9.10938291e-31   * kilogram   # 2014-06-11 - http://physics.nist.gov/cgi-bin/cuu/Value?me
    elementary_charge = 1.602176565e-19  * coulomb                                    # 2014-06-11 - http://physics.nist.gov/cgi-bin/cuu/Value?e
    electron_volt  = elementary_charge * volt
    joule_2_eV = (joule / electron_volt)
    electron_rest_energy = electron_mass * _math.pow(light_speed,2) # [Kg̣*m^2/s^2] - derived

    electron_rest_energy_eV = joule_2_eV * electron_rest_energy
    gamma = energy*1e9/electron_rest_energy_eV
    beta = _math.sqrt(((gamma-1.0)/gamma)*((gamma+1.0)/gamma))
    brho = beta * (energy*1e9) / light_speed
    return brho

# # Is this being used ?!?!
# def set_ioc_ca_port_number(ioc_name):
#     envar, default_port = _envars.ioc_ca_ports_dict[ioc_name]
#     port = _os.environ.get(envar, default=default_port)
#     _os.environ['EPICS_CA_SERVER_PORT'] = port
