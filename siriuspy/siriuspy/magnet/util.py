def get_magfunc_2_multipole_dict():

    _magfuncs = {
        'dipole' : {'type':'normal', 'harmonic':0},
        'corrector-horizontal' : {'type':'normal', 'harmonic':0},
        'corrector-vertical' : {'type':'skew', 'harmonic':0},
        'quadrupole' : {'type':'normal', 'harmonic':1},
        'quadrupole-skew' : {'type':'skew', 'harmonic':1},
        'sextupole' : {'type':'normal', 'harmonic':2},
    }
    return _magfuncs

def get_multipole_name(harmonic, suffix='pole'):

    names = {0: 'dipole',
             1: 'quadrupole',
             2: 'sextupole',
             3: 'octupole',
             4: 'decapole',
             5: 'dodecapole',}

    if harmonic <= max(names.keys()):
        return names[harmonic].replace('pole',suffix)
    else:
        return '{0:d}-pole'.format((harmonic+1)*2).replace('pole',suffix)


def get_multipole_si_units(harmonic, power='^', product='.'):

    if harmonic == 0:
        return 'T{0:s}m'.format(product)
    elif harmonic == 1:
        return 'T'
    elif harmonic == 2:
        return 'T/m'
    else:
        return 'T/m{0:s}{1:d}'.format(power,harmonic-1)


def linear_extrapolation(x,x1,x2,y1,y2):

    if x2 == x1:
        return min(y1,y2,key=abs)
    else:
        return y1 + (y2-y1)*(x-x1)/(x2-x1)

def sum_magnetic_multipoles(*multipoles_list):
    """Sum an iterable composed of multipoles dictionaries."""
    res = {}
    for multipoles in multipoles_list:
        m = multipoles.get('normal',{})
        s = res.get('normal', {})
        for h,m in m.items():
            s[h] = s.get(h,0.0) + m
        if s: res['normal'] = s
        m = multipoles.get('skew',{})
        s = res.get('skew', {})
        for h,m in m.items():
            s[h] = s.get(h,0.0) + m
        if s: res['skew'] = s
    return res
