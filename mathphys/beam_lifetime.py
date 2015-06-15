"""Beam lifetime calculation"""

import os as _os
import numpy as _np
import scipy.integrate as _integrate
import mathphys as _mp
import mathphys.constants as _c
import mathphys.beam_optics as _beam_optics


_data_dir = 'data'

# Constant factors
_ev_2_joule = 1/_c._joule_2_eV
_mbar_2_pascal = 1.0e-3/_c.pascal_2_bar
_elastic_factor = ((_c.light_speed * _c.elementary_charge**4) /
    (4 * _np.pi**2 * _c.vacuum_permitticity**2 * _c.boltzmann_constant))
_inelastic_factor = ((32 * _c.light_speed * _c.electron_radius**2) /
    (411 * _c.boltzmann_constant))
_touschek_factor = (_c.electron_radius**2 * _c.light_speed) / (8*_np.pi)

_d_touschek_file = _os.path.join(_mp.__path__[0], _data_dir, 'd_touschek.npz')
_data = _np.load(_d_touschek_file)
_ksi_table = _data['ksi']
_d_table = _data['d']


def calc_touschek_loss_rate(energy, energy_spread, natural_emittance, n,
        bunch_length, coupling, energy_acceptances, betas, alphas, etas,
        eta_ps):
    """Calculate loss rate due to Touschek beam lifetime

    Acceptances and optical functions can be supplied as numbers or numpy
    arrays. In case arrays are supplied, lengths must be equal; the loss rate
    returned will be an array of same length.

    Keyword arguments:
    energy -- beam energy [eV]
    energy_spread -- relative energy spread
    natural_emittance -- natural emittance [m·rad]
    n -- number of electrons per bunch
    bunch_length -- [m]
    coupling -- coupling between vertical and horizontal planes
    energy_acceptances -- relative energy acceptances [positive, negative]
    betas -- betatron function [horizontal, vertical] [m]
    alphas -- betatron function derivative [horizontal, vertical]
    etas -- dispersion function [horizontal, vertical] [m]
    eta_ps -- dispersion function derivative [horizontal, vertical] [m]

    Returns loss rate [1/s].
    """
    power = _np.power
    sqrt = _np.sqrt
    interp = _np.interp

    se = energy_spread
    emit = natural_emittance
    k = coupling
    acc_p = energy_acceptances[0]
    acc_n = -energy_acceptances[1]
    beta_x, beta_y = betas
    alpha_x, alpha_y = alphas
    eta_x, eta_y = etas
    eta_p_x, eta_p_y = eta_ps

    _, _, _, gamma, _ = _beam_optics.beam_rigidity(energy=energy)

    size_x = sqrt(beta_x * 1/(1+k)*emit + power(eta_x, 2)*se**2)
    size_y = sqrt(beta_y * k/(1+k)*emit + power(eta_y, 2)*se**2)

    sbx2 = 1/(1+k)*emit*beta_x
    volume = bunch_length * size_x * size_y

    f = beta_x*eta_p_x + alpha_x*eta_x
    a_1 = 1/(4*se**2) + (power(eta_x, 2) + power(f, 2))/(4*sbx2)
    b_1 = beta_x*f/(2*sbx2)
    c_1 = power(beta_x, 2)/(4*sbx2) - power(b_1, 2)/(4*a_1)

    ksi_p = power(2*sqrt(c_1)*acc_p/gamma, 2)
    ksi_n = power(2*sqrt(c_1)*acc_n/gamma, 2)

    d_p = interp(ksi_p, _ksi_table, _d_table)
    d_n = interp(ksi_n, _ksi_table, _d_table)

    loss_rate_p = (_touschek_factor*n*d_p) / (gamma**2*power(acc_p, 3)*volume)
    loss_rate_n = (_touschek_factor*n*d_n) / (gamma**2*power(acc_n, 3)*volume)

    import matplotlib.pyplot as plt
    plt.plot(loss_rate_p)

    loss_rate = 0.5*(loss_rate_p + loss_rate_n)

    return loss_rate


def calc_elastic_loss_rate(energy, aperture_ratio, acceptances, pressure,
        betas, z=7, temperature=300):
    """Calculate beam loss rate due to elastic scattering from residual gas

    Pressure and betas can be supplied as numbers or numpy arrays. In case
    arrays are supplied, lengths must be equal; the loss rate returned will
    be an array of same length.

    Keyword arguments:
    energy -- beam energy [eV]
    aperture_ratio -- ratio of vertical to horizontal apertures
    acceptances -- [horizontal, vertical] [m·rad]
    pressure -- residual gas pressure [mbar]
    betas -- betatron function [horizontal, vertical] [m]
    z -- residual gas atomic number (default: 7)
    temperature -- [K] (default: 300)

    Returns loss rate [1/s].
    """
    _, _, beta, *_ = _beam_optics.beam_rigidity(energy=energy)
    energy_joule = energy*_ev_2_joule;

    beta_x, beta_y = betas
    r = aperture_ratio
    a_x, a_y = acceptances
    p = pressure

    f_x = ((2*_np.arctan(r) + _np.sin(2*_np.arctan(r))) *
        p*_mbar_2_pascal * beta_x / a_x)
    f_y = ((_np.pi - 2*_np.arctan(r) + _np.sin(2*_np.arctan(r))) *
        p*_mbar_2_pascal * beta_y / a_y)

    loss_rate = (_elastic_factor * z**2 * (f_x + f_y) /
        (beta * energy_joule**2 * temperature))

    return loss_rate


def calc_inelastic_loss_rate(energy_acceptance, pressure, z=7,
        temperature=300):
    """Calculate loss rate due to inelastic scattering beam lifetime

    Pressure can be supplied as a number or numpy array. In case an array is
    supplied, the loss rate returned will be an array of same length.

    Keyword arguments:
    energy_acceptance -- relative energy acceptance
    pressure -- residual gas pressure [mbar]
    z -- residual gas atomic number (default: 7)
    temperature -- [K] (default: 300)

    Returns loss rate [1/s].
    """
    acc = energy_acceptance
    p = pressure
    loss_rate = (z**2 * _inelastic_factor * _np.log(183/z**(1/3)) *
        (acc - _np.log(acc) - 5/8) * p*_mbar_2_pascal / temperature)
    return loss_rate


def calc_quantum_loss_rates(natural_emittance, coupling, energy_spread,
        transverse_acceptances, energy_acceptance, radiation_damping_times):
    """Calculate beam loss rates due to quantum excitation and radiation damping

    Acceptances can be supplied as numbers or numpy arrays. In case arrays are
    supplied, the corresponding loss rates returned will also be arrays.

    Keyword arguments:
    natural_emittance -- natural emittance [m·rad]
    coupling -- coupling between vertical and horizontal planes
    energy_spread -- relative energy spread
    transverse_acceptances -- [horizontal, vertical] [m·rad]
    energy_acceptance -- relative energy acceptance
    radiation_damping_times -- [horizontal, vertical, longitudinal] [s]

    Returns loss rates (horizontal, vertical, longitudinal) [1/s].
    """
    loss_rate_x, loss_rate_y = calc_quantum_loss_rates_transverse(
        natural_emittance, coupling, transverse_acceptances,
        radiation_damping_times[:-1])

    loss_rate_s = calc_quantum_loss_rate_longitudinal(energy_spread,
        energy_acceptance, radiation_damping_times[-1])

    return loss_rate_x, loss_rate_y, loss_rate_s


def calc_quantum_loss_rates_transverse(natural_emittance, coupling,
        acceptances, radiation_damping_times):
    """Calculate beam loss rate due to quantum excitation and radiation damping in transverse directions

    Acceptances can be supplied as numbers or numpy arrays. In case arrays are
    supplied, the corresponding loss rates returned will also be arrays.

    Keyword arguments:
    natural_emittance -- natural emittance [m·rad]
    coupling -- coupling between vertical and horizontal planes
    acceptances -- [horizontal, vertical] [m·rad]
    radiation_damping_times -- [horizontal, vertical] [s]

    Returns loss rates (horizontal, vertical) [1/s].
    """
    tau_x, tau_y = radiation_damping_times
    acceptance_x, acceptance_y = acceptances

    ksi_x = (1+coupling)*acceptance_x/(2*natural_emittance);
    loss_rate_x = _calc_quantum_loss_rate(ksi_x, tau_x)

    ksi_y = (1+coupling)*acceptance_y/(2*coupling*natural_emittance);
    loss_rate_y = _calc_quantum_loss_rate(ksi_y, tau_y)

    return loss_rate_x, loss_rate_y


def calc_quantum_loss_rate_longitudinal(energy_spread, energy_acceptance,
        radiation_damping_time):
    """Calculate beam loss rate due to quantum excitation and radiation damping in longitudinal direction

    Acceptances can be supplied as numbers or numpy arrays. In case arrays are
    supplied, the corresponding loss rates returned will also be arrays.

    Keyword arguments:
    energy_spread -- relative energy spread
    energy_acceptance -- relative energy acceptance
    radiation_damping_time -- longitudinal radiation damping time [s]

    Returns loss rate [1/s].
    """
    ksi_s = (energy_acceptance/energy_spread)**2/2
    return _calc_quantum_loss_rate(ksi_s, radiation_damping_time)


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
    limit = 1000

    sqrt = _np.sqrt
    exp = _np.exp
    log = _np.log
    inf = _np.inf

    f1 = lambda x: exp(-x)/x
    f2 = lambda x: exp(-x)*log(x)/x

    i1, _ = _integrate.quad(f1, ksi, inf, limit=limit)
    i2, _ = _integrate.quad(f2, ksi, inf, limit=limit)

    d = sqrt(ksi)*(-1.5*exp(-ksi) + 0.5*(3*ksi-ksi*log(ksi)+2)*i1 + 0.5*ksi*i2)

    return d


def _calc_quantum_loss_rate(ksi, tau):
    return 2*ksi*_np.exp(-ksi)/tau
