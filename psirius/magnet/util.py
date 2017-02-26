
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
