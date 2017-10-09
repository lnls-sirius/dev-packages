"""Magnet utils."""

import math as _math
import numpy as _numpy
import re as _re
from siriuspy.namesys import SiriusPVName as _SiriusPVName


def get_nominal_dipole_angles():
    """Return nominal angles of all Sirius individual dipole types."""
    ref_angles = {
        'SI_BC': _math.radians(4.296600),
        'SI_B1': _math.radians(2.755300),
        'SI_B2': _math.radians(4.096400),
        'TS': _math.radians(5.011542),  # TS.V03.03
        'BO': _math.radians(7.200000),
        'TB': _math.radians(15.00000),
    }
    return ref_angles


def get_magfunc_2_multipole_dict():
    """Return multipole dict given the magnetic function."""
    _magfuncs = {
        'dipole': {'type': 'normal', 'harmonic': 0},
        'corrector-horizontal': {'type': 'normal', 'harmonic': 0},
        'corrector-vertical': {'type': 'skew', 'harmonic': 0},
        'quadrupole': {'type': 'normal', 'harmonic': 1},
        'quadrupole-skew': {'type': 'skew', 'harmonic': 1},
        'sextupole': {'type': 'normal', 'harmonic': 2},
    }
    return _magfuncs


def get_multipole_name(harmonic, suffix='pole'):
    """Return names of multipoles, given harmonic number."""
    names = {0: 'dipole',
             1: 'quadrupole',
             2: 'sextupole',
             3: 'octupole',
             4: 'decapole',
             5: 'dodecapole', }

    if harmonic <= max(names.keys()):
        return names[harmonic].replace('pole', suffix)
    else:
        return '{0:d}-pole'.format((harmonic+1)*2).replace('pole', suffix)


def get_multipole_si_units(harmonic, power='^', product='.'):
    """Return multipole units, given harmonic number."""
    if harmonic == 0:
        return 'T{0:s}m'.format(product)
    elif harmonic == 1:
        return 'T'
    elif harmonic == 2:
        return 'T/m'
    else:
        return 'T/m{0:s}{1:d}'.format(power, harmonic-1)


def linear_extrapolation(x, x1, x2, y1, y2):
    """Return linear extrapolation function value."""
    if x2 == x1:
        return min(y1, y2, key=abs)
    else:
        return y1 + (y2-y1)*(x-x1)/(x2-x1)


def sum_magnetic_multipoles(*multipoles_list):
    """Sum an iterable composed of multipoles dictionaries."""
    res = {}
    for multipoles in multipoles_list:
        m = multipoles.get('normal', {})
        s = res.get('normal', {})
        for h, m in m.items():
            s[h] = s.get(h, 0.0) + m
        if s:
            res['normal'] = s
        m = multipoles.get('skew', {})
        s = res.get('skew', {})
        for h, m in m.items():
            s[h] = s.get(h, 0.0) + m
        if s:
            res['skew'] = s
    return res


def generate_normalized_ramp(interval=500, nrpts=2000,
                             ti=None, fi=None, forms=None):
    """Generate normalized ramp."""
    t = interval * _numpy.linspace(0, 1.0, nrpts)
    if ti is None:
        ti = interval * _numpy.array([0, 13, 310,
                                      322, 330, 342, 480, 500])/500.0
    if fi is None:
        fi = _numpy.array([0.01, 0.02625, 1.0339285714,
                           1.05, 1.05, 1, 0.07, 0.01])
    if forms is None:
        forms = ['cube', 'injection', 'cube', 'line', 'cube', 'line', 'cube']

    # brho_3gev = 10.00692271077752  # [T.m]
    # brho_150mev = 0.5003432394479871  # [T.m]

    ramp = _numpy.zeros(len(t))
    a1 = _numpy.zeros(len(ti))
    dti = _numpy.zeros(len(forms))

    # findout the initial derivatives and delta ts from the straigth lines
    for i, fo in enumerate(forms):
        dti[i] = (ti[i+1]-ti[i])
        if fo.startswith(('l', 'i')) or fo == 0:
            equal_previous = False
            a1[i] = (fi[i+1]-fi[i])/dti[i]
            a1[i+1] = a1[i]
        else:
            equal_previous = True
        if equal_previous:
            a1[i] = a1[i-1]

    # calculate the ramp:
    for i, fo in enumerate(forms):
        ind = _numpy.bitwise_and(ti[i] <= t, t <= ti[i+1])
        dt = t[ind] - ti[i]
        a2, a3 = 0, 0
        if fo.startswith(('c', 'i')):
            a2 = (-3*(fi[i]-fi[i+1]) - dti[i] * (2*a1[i]+a1[i+1]))/dti[i]**2
            a3 = (2*(fi[i]-fi[i+1]) + dti[i] * (a1[i]+a1[i+1]))/dti[i]**3
        ramp[ind] = fi[i] + a1[i]*dt + a2*dt**2 + a3*dt**3

    return ramp


def get_strength_label(magfunc):
    """Return strength label, depending on magnet function."""
    if magfunc == 'dipole':
        return 'Energy'
    elif magfunc in ('quadrupole', 'quadrupole-skew'):
        return 'KL'
    elif magfunc in ('sextupole',):
        return 'SL'
    elif magfunc in ('corrector-horizontal', 'corrector-vertical'):
        return 'Kick'
    else:
        raise NotImplementedError("magfunc {}".format(magfunc))


def get_section_dipole_name(maname):
    """Return name of dipole in the same section of given magnet name."""
    maname = _SiriusPVName(maname)
    if _re.match("B.*", maname.dev_type):
        return None
    elif maname.section == "SI":
        return "SI-Fam:MA-B1B2"
    elif maname.section == "BO":
        return "BO-Fam:MA-B"
    elif maname.section == "TB":
        return "TB-Fam:MA-B"
    elif maname.section == "TS":
        return "TS-Fam:MA-B"
    else:
        raise NotImplementedError(
            "No section named {}".format(maname.section))


def get_magnet_fam_name(maname):
    """Return family name associated with a given magnet name."""
    maname = _SiriusPVName(maname)
    if maname.section == "SI" and \
       maname.subsection != "Fam" and \
       _re.match("(?:QD|QF|Q[0-9]).*", maname.dev_type):
            return _re.sub("SI-\d{2}\w{2}:", "SI-Fam:", maname)
    else:
        return None
