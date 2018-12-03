"""Beam lifetime calculation."""

import os as _os
import numpy as _np
# import scipy.integrate as _integrate
from . import constants as _c
from . import units as _u
from . import beam_optics as _beam

# Constant factors
_ev_2_joule = 1 / _u.joule_2_eV
_mbar_2_pascal = 1.0e-3 / _u.pascal_2_bar

_elastic_factor = (
    (_c.light_speed * _c.elementary_charge**4) /
    (4 * _np.pi**2 * _c.vacuum_permitticity**2 * _c.boltzmann_constant))
_inelastic_factor = (
    (32 * _c.light_speed * _c.electron_radius**2) /
    (411 * _c.boltzmann_constant))
_touschek_factor = (_c.electron_radius**2 * _c.light_speed) / (8*_np.pi)

_d_touschek_file = \
    _os.path.join(_os.path.dirname(__file__), 'data', 'd_touschek.npz')
_ksi_table, _d_table = None, None


def _load_touschek_data():
    global _ksi_table, _d_table
    if _ksi_table is None or _d_table is None:
        data = _np.load(_d_touschek_file)
        _ksi_table = data['ksi']
        _d_table = data['d']


def get_touschek_data():
    """Return Touschek data."""
    _load_touschek_data()
    return _ksi_table, _d_table


def calc_touschek_loss_rate(
        energy_acceptance, twiss, coupling, n, natural_emittance,
        energy, energy_spread, bunch_length, **kwargs):
    """Calculate loss rate due to Touschek beam lifetime.

    arguments:

    natural_emittance = Natural emittance in m.rad
    energy            = Bunch energy in [GeV]
    n                 = Number of electrons ber bunch
    energy_spread     = relative energy spread,
    bunch_length      = bunch length in [m]
    coupling          = emittance coupling factor (emity = coupling*emitx)
    energy_acceptance =
        energy acceptance of the machine. May be a dictionary with keys:
        pos = positive acceptance for a selection of points in the ring
        neg = negative acceptance for a selection of points in the ring
              (remember: min(accep_din, accep_rf))
        s = Longitudinal position where pos and neg were calculated.
    twiss = pyaccel.TwissList object or similar object with fields:
            spos, betax, betay, etax, etay, alphax, alphay, etapx, etapy

    output:

    dictionary with fields:
       rate     = loss rate along the ring [1/s]
       ave_rate = average loss rate along the ring [1/s]
       pos      = longitudinal position where loss rate was calculated [m]
       volume   = volume of the beam along the ring [m^3]

    WARNING: if energy_acceptance is a dictionary the limits of the
    calculation will be defined by the initial and final points of the
    acceptance and not by the optical functions.
    """
    _load_touschek_data()
    _, _, _, gamma, _ = _beam.beam_rigidity(energy=energy)
    _, ind = _np.unique(twiss.spos, return_index=True)

    if isinstance(energy_acceptance, dict):
        s = energy_acceptance['s']
        accp = energy_acceptance['pos']
        accn = energy_acceptance['neg']
    elif isinstance(energy_acceptance, (list, tuple, _np.ndarray)):
        s = twiss.spos[ind]
        accp = s*0.0 + energy_acceptance[1]
        accn = s*0.0 + energy_acceptance[0]
    else:
        raise TypeError('energy_acceptance')

    # calcular o tempo de vida a cada 10 cm do anel:
    npoints = int((s[-1] - s[0])/0.1)
    s_calc = _np.linspace(s[0], s[-1], npoints)
    d_accp = _np.interp(s_calc, s, accp)
    d_accn = _np.interp(s_calc, s, -accn)

    # if momentum aperture is 0, set it to 1e-4:
    d_accp[d_accp == 0] = 1e-4
    d_accn[d_accn == 0] = 1e-4

    betax = _np.interp(s_calc, twiss.spos[ind], twiss.betax[ind])
    alphax = _np.interp(s_calc, twiss.spos[ind], twiss.alphax[ind])
    etax = _np.interp(s_calc, twiss.spos[ind], twiss.etax[ind])
    etaxl = _np.interp(s_calc, twiss.spos[ind], twiss.etapx[ind])
    betay = _np.interp(s_calc, twiss.spos[ind], twiss.betay[ind])
    etay = _np.interp(s_calc, twiss.spos[ind], twiss.etay[ind])

    # Volume do bunch
    sigX = _np.sqrt(
        betay*(coupling/(1+coupling))*natural_emittance +
        etay**2*energy_spread**2)
    sigY = _np.sqrt(
        betax*(1/(1+coupling))*natural_emittance +
        etax**2*energy_spread**2)
    V = bunch_length * sigX * sigY

    # Tamanho betatron horizontal do bunch
    Sx2 = 1 / (1+coupling) * natural_emittance * betax

    fator = betax*etaxl + alphax*etax
    A1 = 1 / (4*energy_spread**2) + (etax**2 + fator**2) / (4*Sx2)
    B1 = betax*fator / (2*Sx2)
    C1 = betax**2 / (4*Sx2) - B1**2 / (4*A1)

    # Limite de integração inferior
    ksip = (2*_np.sqrt(C1)/gamma * d_accp)**2
    ksin = (2*_np.sqrt(C1)/gamma * d_accn)**2

    # Interpola d_touschek
    Dp = _np.interp(ksip, _ksi_table, _d_table, left=0.0, right=0.0)
    Dn = _np.interp(ksin, _ksi_table, _d_table, left=0.0, right=0.0)

    # Tempo de vida touschek inverso
    Ratep = _touschek_factor*n/gamma**2 / d_accp**3 * Dp / V
    Raten = _touschek_factor*n/gamma**2 / d_accn**3 * Dn / V
    rate = (Ratep + Raten) / 2

    # Tempo de vida touschek inverso médio
    ave_rate = _np.trapz(rate, x=s_calc) / (s_calc[-1] - s_calc[0])
    resp = dict(rate=rate, ave_rate=ave_rate, volume=V, pos=s_calc)

    return resp


def calc_elastic_loss_rate(
        transverse_acceptances, pressure, z=7, temperature=300, **kwargs):
    """Calculate beam loss rate due to elastic scattering from residual gas.

    Pressure and betas can be supplied as numbers or numpy arrays. In case
    arrays are supplied, lengths must be equal; the loss rate returned will
    be an array of same length.

    Positional arguments:
    transverse_acceptances -- [horizontal, vertical] [m·rad]
    pressure -- Residual gas pressure [mbar]

    Keyword arguments:
    z -- Residual gas atomic number (default: 7)
    temperature -- [K] (default: 300)
    energy -- Beam energy [GeV]
    betax  -- Horizontal betatron function [m]
    betay  -- Vertical betatron function [m]

    Returns loss rate [1/s].
    """
    energy = kwargs['energy']
    betax, betay = kwargs['betax'], kwargs['betay']

    _, _, beta, *_ = _beam.beam_rigidity(energy=energy)
    energy_joule = energy*1e9 * _ev_2_joule

    horizontal_acceptance, vertical_acceptance = transverse_acceptances

    thetax = _np.sqrt(horizontal_acceptance/betax)
    thetay = _np.sqrt(vertical_acceptance/betay)
    r = thetay / thetax
    p = pressure

    f_x = (
        (2*_np.arctan(r) + _np.sin(2*_np.arctan(r))) *
        p*_mbar_2_pascal * betax / horizontal_acceptance)
    f_y = (
        (_np.pi - 2*_np.arctan(r) + _np.sin(2*_np.arctan(r))) *
        p*_mbar_2_pascal * betay / vertical_acceptance)

    loss_rate = (
        _elastic_factor * z**2 * (f_x + f_y) /
        (beta * energy_joule**2 * temperature))

    return loss_rate


def calc_inelastic_loss_rate(
        energy_acceptance, pressure, z=7, temperature=300):
    """Calculate loss rate due to inelastic scattering beam lifetime.

    Pressure can be supplied as a number or numpy array. In case an array is
    supplied, the loss rate returned will be an array of same length.

    Positional arguments:
    energy_acceptance -- Relative energy acceptance
    pressure -- Residual gas pressure [mbar]

    Keyword arguments:
    z -- Residual gas atomic number (default: 7)
    temperature -- [K] (default: 300)

    Returns loss rate [1/s].
    """
    acc = energy_acceptance
    p = pressure
    loss_rate = (
        z**2 * _inelastic_factor * _np.log(183/z**(1/3)) *
        (acc - _np.log(acc) - 5/8) * p*_mbar_2_pascal / temperature)
    return loss_rate


def calc_quantum_loss_rates(
        transverse_acceptances, energy_acceptance, coupling, **kwargs):
    """Beam loss rates due to quantum excitation and radiation damping.

    Acceptances can be supplied as numbers or numpy arrays. In case arrays are
    supplied, the corresponding loss rates returned will also be arrays.

    Positional arguments:
    transverse_acceptances -- [horizontal, vertical] [m·rad]
    energy_acceptance -- Relative energy acceptance
    coupling -- coupling between vertical and horizontal planes

    Keyword arguments:
    natural_emittance -- natural emittance [m·rad]
    energy_spread -- relative energy spread
    damping_times -- [horizontal, vertical, longitudinal] [s]

    Returns loss rates (horizontal, vertical, longitudinal) [1/s].
    """
    energy_spread = kwargs['energy_spread']
    natural_emittance = kwargs['natural_emittance']
    damping_times = kwargs['damping_times']

    loss_rate_x, loss_rate_y = \
        calc_quantum_loss_rates_transverse(
            transverse_acceptances, coupling,
            natural_emittance=natural_emittance, damping_times=damping_times)

    loss_rate_s = \
        calc_quantum_loss_rate_longitudinal(
            energy_acceptance,
            energy_spread=energy_spread, damping_times=damping_times)

    return loss_rate_x, loss_rate_y, loss_rate_s


def calc_quantum_loss_rates_transverse(
        transverse_acceptances, coupling, **kwargs):
    """Beam loss rate due to quantum exc. and rad. damping in transverse dir.

    Acceptances can be supplied as numbers or numpy arrays. In case arrays are
    supplied, the corresponding loss rates returned will also be arrays.

    Positional arguments:
    transverse_acceptances -- [horizontal, vertical] [m·rad]
    coupling -- coupling between vertical and horizontal planes

    Keyword arguments:
    natural_emittance -- natural emittance [m·rad]
    damping_times -- [horizontal, vertical, longitudinal] [s]

    Returns loss rates (horizontal, vertical) [1/s].
    """
    natural_emittance = kwargs['natural_emittance']
    damping_times = kwargs['damping_times']

    tau_x, tau_y, *_ = damping_times
    horizontal_acceptance, vertical_acceptance = transverse_acceptances

    ksi_x = (1+coupling)*horizontal_acceptance / (2*natural_emittance)
    loss_rate_x = _calc_quantum_loss_rate(ksi_x, tau_x)

    ksi_y = (1+coupling)*vertical_acceptance / (2*coupling*natural_emittance)
    loss_rate_y = _calc_quantum_loss_rate(ksi_y, tau_y)

    return loss_rate_x, loss_rate_y


def calc_quantum_loss_rate_longitudinal(energy_acceptance, **kwargs):
    """Beam loss rate due to quantum exc. and rad. damping in long. dir.

    Acceptances can be supplied as numbers or numpy arrays. In case arrays are
    supplied, the corresponding loss rates returned will also be arrays.

    Positional arguments:
    energy_acceptance -- relative energy acceptance

    Keyword arguments:
    energy_spread -- relative energy spread
    damping_time -- [horizontal, vertical, longitudinal] [s]

    Returns loss rate [1/s].
    """
    energy_spread = kwargs['energy_spread']
    damping_times = kwargs['damping_times']

    _, _, tau_s = damping_times
    ksi_s = (energy_acceptance/energy_spread)**2/2
    return _calc_quantum_loss_rate(ksi_s, tau_s)


def _calc_d_touschek_table(a, b, n):
    ksi = _np.logspace(a, b, n)
    d = _calc_d_touschek_array(ksi)
    return ksi, d


def _calc_d_touschek_array(ksi):
    d = _np.zeros(len(ksi))
    for i in range(len(ksi)):
        d[i] = _calc_d_touschek(ksi[i])
    return d


def _calc_d_touschek(ksi):
    # limit = 1000
    # sqrt = _np.sqrt
    # exp = _np.exp
    # log = _np.log
    # inf = _np.inf
    # f1 = lambda x: exp(-x)/x
    # f2 = lambda x: exp(-x)*log(x)/x
    # i1, _ = _integrate.quad(f1, ksi, inf, limit=limit)
    # i2, _ = _integrate.quad(f2, ksi, inf, limit=limit)
    # d = \
    #     sqrt(ksi)*(
    #         -1.5*exp(-ksi) +
    #         0.5*(3*ksi-ksi*log(ksi)+2)*i1 + 0.5*ksi*i2)
    # return d
    raise NotImplementedError('Touschek calc commented out!')


def _calc_quantum_loss_rate(ksi, tau):
    return 2*ksi*_np.exp(-ksi)/tau
