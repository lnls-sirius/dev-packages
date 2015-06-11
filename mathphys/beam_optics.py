import math as _math
import mathphys as _mp


def calc_U0(beam_energy, I2):
    """Calculate U0 [keV] from beam energy [GeV] and I2 [1/m]"""
    U0 = _mp.constants.rad_cgamma/(2*_math.pi)*(beam_energy)**4*I2*1e+6
    return U0

def calc_overvoltage(Vrf, U0):
    """Calculate cavity overvoltage factor from
       U0:  energy loss per turn [keV]
       Vrf: rf total voltage  [MV] """
    q = Vrf*1e3/U0
    return q

def calc_rf_acceptance(U0, mcf, h, q, energy):
    """Calculate RF energy acceptance from:
       U0:     energy loss per turn [keV]
       mcf:    momentum compaction factor
       h:      harmonic_number
       q:      overvoltage
       energy: beam energy [GeV] """
    eRF = _math.sqrt(2*U0/(_math.pi*mcf*h*(energy*1e6))*(_math.sqrt(q**2-1)-_math.acos(1/q)))
    return eRF

def calc_number_of_electrons(energy, current, circumference):
    """Calculate numbe of electrons from
       energy:        beam energy [GeV]
       current:       beam current [mA]
       circumference: ring circumference [m]"""
    brho, velocity, beta, gamma = Beam.calc_brho(energy)
    mA = 1e-3 / _mp.constants.elementary_charge * circumference / velocity
    Np = current * mA
    return Np

def calc_natural_energy_spread(energy, I2, I3, I4):
    """Calculate energy dispersion from
       energy: beam energy [GeV]
       I2:     second radiation integral [1/m]
       I3:     third radiation integral [1/m²]
       I4:     fouth radiation integral [1/m]"""

    brho, velocity, beta, gamma = Beam.calc_brho(energy)
    sigmae = _math.sqrt(_mp.constants.Cq * gamma**2 * I3/(2*I2+I4))
    return sigmae

def calc_natural_bunch_length(energy, circumference, sigmae, U0, mcf, h, Vrf, hcavity = False):
    """Calculate natural bunch length [m] from
       energy:        beam energy [GeV]
       circumference: ring circumference [m]
       sigmae:        natural energy spread
       U0:            energy loss per turn [keV]
       mcf:           momentum compaction factor
       h:             harmonic number
       Vrf:           total rf voltage [MV]
       hcavity:       flag indicating that a 3rd order harmonic cavity is present"""
    if hcavity:
        Qs = _math.sqrt(mcf*h*_math.sqrt((Vrf/1e6)**2-(U0/1e3)**2)/(2*_math.pi*(energy/1e9)))
        sigmal = 0.432343807*(mcf*h*_math.pi*sigmae/Qs)**0.5 * circumference/(2*_math.pi*h)
    else:
        Qs = 0.0
        sigmal = sigmae * circumference * _math.sqrt(mcf*(energy*1e9)/(2*_math.pi*h*((Vrf*1e6)**2-(U0*1e3)**2)**0.5))
    return sigmal, Qs

def beam_rigidity(**kwargs):

    electron_rest_energy_eV = _mp.units.joule_2_eV * _mp.constants.electron_rest_energy

    if len(kwargs) != 1:
        raise Exception('beam rigidity accepts only one argument')

    if 'brho' in kwargs:
        k = kwargs['brho'] / (electron_rest_energy_eV/_mp.constants.light_speed)
        kwargs['gamma'] = _math.sqrt(1.0+k**2)
    if 'velocity' in kwargs:
        kwargs['beta'] = kwargs['velocity'] / _mp.constants.light_speed
    if 'beta' in kwargs:
        kwargs['gamma'] = 1.0/_math.sqrt((1.0 + kwargs['beta'])*(1.0 - kwargs['beta']))
    if 'gamma' in kwargs:
        kwargs['energy'] = kwargs['gamma'] * electron_rest_energy_eV

    energy = kwargs['energy']
    gamma = kwargs['gamma'] if 'gamma' in kwargs else energy/electron_rest_energy_eV
    beta = kwargs['beta'] if 'beta' in kwargs else _math.sqrt(((gamma-1.0)/gamma)*((gamma+1.0)/gamma))
    velocity = kwargs['velocity'] if 'velocity' in kwargs else _mp.constants.light_speed * beta
    brho = kwargs['brho'] if 'brho' in kwargs else beta * (energy) / _mp.constants.light_speed

    return brho, velocity, beta, gamma, energy
