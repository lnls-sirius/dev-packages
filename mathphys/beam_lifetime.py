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

def lnls_tau_touschek_inverso(Accep,twispos,twiss,emit0,E,N,sigE,sigS,K):
    """ calcula o inverso do tempo de vida Touschek.

      Saídas:
          Resp = estrutura com campos:
              Rate = taxa de perda de elétrons ao longo do anel [1/s]
              AveRate = Taxa média de perda de elétrons [1/s]
              Pos  = Posição do anel onde foi calculada a taxa [m]
              Volume = Volume do feixe ao longo do anel [m^3]

      Entradas:
          emit0 = emitância natural [m rad]
          E     = energia das partículas [eV]
          N     = número de elétrons por bunch
          sigE  = dispersão de energia relativa sigE,
          sigS  = comprimento do bunch [m]
          K     = fator de acoplamento (emity = K*emitx)
          Accep = dicionário com chaves:
              pos = aceitância positiva para uma seleção de pontos do anel;
              neg = aceitância negativa para uma seleção de pontos do anel;
                       (lembrar: min(accep_din, accep_rf))
              s   = posição longitudinal dos pontos para os quais a
                       aceitância foi calculada.

          twiss = estrutura com as funções óticas ao longo do trecho
                  para o qual setá calculado o tempo de vida:
                       pos,   betax,    betay,  etax,   etay,
                              alphax,   alphay, etapx,  etapy

      CUIDADO: os limites de cálculo são definidos pelos pontos
         inicial e final da Aceitância e não das funções ópticas.
    """

    _, _, _, gamma, _ = _beam_optics.beam_rigidity(energy=E)

    s    = Accep['s']
    accp = Accep['pos']
    accn = Accep['neg']
    # calcular o tempo de vida a cada 10 cm do anel:
    npoints = int((s[-1] - s[0])/0.1)
    s_calc = _np.linspace(s[0], s[-1], npoints)

    d_accp  = _np.interp(s_calc,s, accp)
    d_accn  = _np.interp(s_calc,s,-accn)
    # if momentum aperture is 0, set it to 1e-4:
    d_accp[d_accp==0] = 1e-4
    d_accn[d_accn==0] = 1e-4

    _, ind = _np.unique(twispos,return_index=True)

    betax  = _np.interp(s_calc, twispos[ind], twiss.betax[ind])
    alphax = _np.interp(s_calc, twispos[ind], twiss.alphax[ind])
    etax   = _np.interp(s_calc, twispos[ind], twiss.etax[ind])
    etaxl  = _np.interp(s_calc, twispos[ind], twiss.etapx[ind])
    betay  = _np.interp(s_calc, twispos[ind], twiss.betay[ind])
    etay   = _np.interp(s_calc, twispos[ind], twiss.etay[ind])

    # Volume do bunch
    sigX = _np.sqrt(betay*(K/(1+K))*emit0 + etay**2*sigE**2)
    sigY = _np.sqrt(betax*(1/(1+K))*emit0 + etax**2*sigE**2)
    V = sigS * sigX * sigY


    # Tamanho betatron horizontal do bunch
    Sx2 = 1/(1+K) * emit0 * betax

    fator = betax*etaxl + alphax*etax
    A1 = 1/(4*sigE**2) + (etax**2 + fator**2)/(4*Sx2)
    B1 = betax*fator/(2*Sx2)
    C1 = betax**2/(4*Sx2) - B1**2/(4*A1)

    # Limite de integração inferior
    ksip = (2*_np.sqrt(C1)/gamma * d_accp)**2
    ksin = (2*_np.sqrt(C1)/gamma * d_accn)**2

    # Interpola d_touschek
    Dp = _np.interp(ksip,_ksi_table,_d_table,left=0.0,right=0.0)
    Dn = _np.interp(ksin,_ksi_table,_d_table,left=0.0,right=0.0)

    # Tempo de vida touschek inverso
    Ratep = _touschek_factor*N/gamma**2 / d_accp**3 * Dp / V
    Raten = _touschek_factor*N/gamma**2 / d_accn**3 * Dn / V
    rate = (Ratep + Raten) / 2

    # Tempo de vida touschek inverso médio
    ave_rate = _np.trapz(rate,x=s_calc) / ( s_calc[-1] - s_calc[0] )
    resp = dict(rate=rate,ave_rate=ave_rate,volume=V,pos=s_calc)

    return resp


def calc_touschek_loss_rate(energy_acceptance_interval, coupling, n, **kwargs):
    """Calculate loss rate due to Touschek beam lifetime

    Acceptances and optical functions can be supplied as numbers or numpy
    arrays. In case arrays are supplied, lengths must be equal; the loss rate
    returned will be an array of same length.

    Positional arguments:
    energy_acceptance_interval -- Relative energy acceptance interval [min, max]
    coupling -- Coupling between vertical and horizontal planes
    n -- Number of electrons per bunch

    Keyword arguments:
    energy            -- Beam energy [eV]
    energy_spread     -- Relative energy spread
    natural_emittance -- Natural emittance [m·rad]
    bunch_length      -- Bunch length [m]
    betax             -- Horizontal betatron function [m]
    betay             -- Vertical betatron function [m]
    etax              -- Horizontal dispersion function [m]
    etay              -- Vertical dispersion function [m]
    alphax            -- Horizontal betatron function derivative
    etalx             -- Horizontal dispersion function derivative

    Returns loss rate [1/s].
    """
    energy            = kwargs['energy']
    energy_spread     = kwargs['energy_spread']
    natural_emittance = kwargs['natural_emittance']
    bunch_length      = kwargs['bunch_length']
    betax, betay      = kwargs['betax'], kwargs['betay']
    etax, etay        = kwargs['etax'], kwargs['etay']
    alphax            = kwargs['alphax']
    etapx             = kwargs['etapx']

    power = _np.power
    sqrt = _np.sqrt
    interp = _np.interp

    se = energy_spread
    emit = natural_emittance
    k = coupling
    acc_n = -energy_acceptance_interval[0]
    acc_p = energy_acceptance_interval[1]

    _, _, _, gamma, _ = _beam_optics.beam_rigidity(energy=energy)

    emitx = emit / (1 + k)
    emity = emit * k / (1 + k)
    sizex = sqrt(betax*emitx + power(etax, 2)*se**2)
    sizey = sqrt(betay*emity + power(etay, 2)*se**2)
    volume = bunch_length*sizex*sizey

    sbx2 = emitx*betax

    f = betax*etapx + alphax*etax
    a_1 = 1/(4*se**2) + (power(etax, 2) + power(f, 2))/(4*sbx2)
    b_1 = betax*f/(2*sbx2)
    c_1 = power(betax, 2)/(4*sbx2) - power(b_1, 2)/(4*a_1)

    ksi_p = power(2*sqrt(c_1)*acc_p/gamma, 2)
    ksi_n = power(2*sqrt(c_1)*acc_n/gamma, 2)

    d_p = interp(ksi_p, _ksi_table, _d_table)
    d_n = interp(ksi_n, _ksi_table, _d_table)

    loss_rate_p = (_touschek_factor*n*d_p) / (gamma**2*power(acc_p, 3)*volume)
    loss_rate_n = (_touschek_factor*n*d_n) / (gamma**2*power(acc_n, 3)*volume)

    loss_rate = 0.5*(loss_rate_p + loss_rate_n)

    return loss_rate


def calc_elastic_loss_rate(transverse_acceptances, pressure, z=7, temperature=300, **kwargs):
    """Calculate beam loss rate due to elastic scattering from residual gas

    Pressure and betas can be supplied as numbers or numpy arrays. In case
    arrays are supplied, lengths must be equal; the loss rate returned will
    be an array of same length.

    Positional arguments:
    transverse_acceptances -- [horizontal, vertical] [m·rad]
    pressure -- Residual gas pressure [mbar]

    Keyword arguments:
    z -- Residual gas atomic number (default: 7)
    temperature -- [K] (default: 300)
    energy -- Beam energy [eV]
    betax  -- Horizontal betatron function [m]
    betay  -- Vertical betatron function [m]

    Returns loss rate [1/s].
    """
    energy            = kwargs['energy']
    betax, betay      = kwargs['betax'], kwargs['betay']

    _, _, beta, *_ = _beam_optics.beam_rigidity(energy=energy)
    energy_joule = energy*_ev_2_joule;

    horizontal_acceptance, vertical_acceptance = transverse_acceptances

    thetax = _np.sqrt(horizontal_acceptance/betax)
    thetay = _np.sqrt(vertical_acceptance/betay)
    r = thetay / thetax
    p = pressure

    f_x = ((2*_np.arctan(r) + _np.sin(2*_np.arctan(r))) *
        p*_mbar_2_pascal * betax / horizontal_acceptance)
    f_y = ((_np.pi - 2*_np.arctan(r) + _np.sin(2*_np.arctan(r))) *
        p*_mbar_2_pascal * betay / vertical_acceptance)

    loss_rate = (_elastic_factor * z**2 * (f_x + f_y) /
        (beta * energy_joule**2 * temperature))

    return loss_rate


def calc_inelastic_loss_rate(energy_acceptance, pressure, z=7, temperature=300):
    """Calculate loss rate due to inelastic scattering beam lifetime

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
    loss_rate = (z**2 * _inelastic_factor * _np.log(183/z**(1/3)) *
        (acc - _np.log(acc) - 5/8) * p*_mbar_2_pascal / temperature)
    return loss_rate


def calc_quantum_loss_rates(transverse_acceptances, energy_acceptance, coupling, **kwargs):
    """Calculate beam loss rates due to quantum excitation and radiation
    damping

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
    energy_spread     = kwargs['energy_spread']
    natural_emittance = kwargs['natural_emittance']
    damping_times     = kwargs['damping_times']

    loss_rate_x, loss_rate_y = calc_quantum_loss_rates_transverse(transverse_acceptances,
        coupling, natural_emittance=natural_emittance, damping_times=damping_times)

    loss_rate_s = calc_quantum_loss_rate_longitudinal(energy_acceptance,
        energy_spread=energy_spread, damping_times=damping_times)

    return loss_rate_x, loss_rate_y, loss_rate_s


def calc_quantum_loss_rates_transverse(transverse_acceptances, coupling, **kwargs):
    """Calculate beam loss rate due to quantum excitation and radiation damping
    in transverse directions

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
    damping_times     = kwargs['damping_times']

    tau_x, tau_y, *_ = damping_times
    horizontal_acceptance, vertical_acceptance = transverse_acceptances

    ksi_x = (1+coupling)*horizontal_acceptance/(2*natural_emittance);
    loss_rate_x = _calc_quantum_loss_rate(ksi_x, tau_x)

    ksi_y = (1+coupling)*vertical_acceptance/(2*coupling*natural_emittance);
    loss_rate_y = _calc_quantum_loss_rate(ksi_y, tau_y)

    return loss_rate_x, loss_rate_y


def calc_quantum_loss_rate_longitudinal(energy_acceptance, **kwargs):
    """Calculate beam loss rate due to quantum excitation and radiation damping
    in longitudinal direction

    Acceptances can be supplied as numbers or numpy arrays. In case arrays are
    supplied, the corresponding loss rates returned will also be arrays.

    Positional arguments:
    energy_acceptance -- relative energy acceptance

    Keyword arguments:
    energy_spread -- relative energy spread
    damping_time -- [horizontal, vertical, longitudinal] [s]

    Returns loss rate [1/s].
    """
    energy_spread     = kwargs['energy_spread']
    damping_times     = kwargs['damping_times']

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

#
# """Beam lifetime calculation"""
#
# import os as _os
# import numpy as _np
# import scipy.integrate as _integrate
# import mathphys as _mp
# import mathphys.constants as _c
# import mathphys.beam_optics as _beam_optics
#
#
# _data_dir = 'data'
#
# # Constant factors
# _ev_2_joule = 1/_c._joule_2_eV
# _mbar_2_pascal = 1.0e-3/_c.pascal_2_bar
# _elastic_factor = ((_c.light_speed * _c.elementary_charge**4) /
#     (4 * _np.pi**2 * _c.vacuum_permitticity**2 * _c.boltzmann_constant))
# _inelastic_factor = ((32 * _c.light_speed * _c.electron_radius**2) /
#     (411 * _c.boltzmann_constant))
# _touschek_factor = (_c.electron_radius**2 * _c.light_speed) / (8*_np.pi)
#
# _d_touschek_file = _os.path.join(_mp.__path__[0], _data_dir, 'd_touschek.npz')
# _data = _np.load(_d_touschek_file)
# _ksi_table = _data['ksi']
# _d_table = _data['d']
#
#
# def calc_touschek_loss_rate(energy, energy_spread, natural_emittance, n,
#         bunch_length, coupling, energy_acceptance_interval, betas, etas, alphax,
#         etapx):
#     """Calculate loss rate due to Touschek beam lifetime
#
#     Acceptances and optical functions can be supplied as numbers or numpy
#     arrays. In case arrays are supplied, lengths must be equal; the loss rate
#     returned will be an array of same length.
#
#     Keyword arguments:
#     energy -- beam energy [eV]
#     energy_spread -- relative energy spread
#     natural_emittance -- natural emittance [m·rad]
#     n -- number of electrons per bunch
#     bunch_length -- [m]
#     coupling -- coupling between vertical and horizontal planes
#     energy_acceptance_interval -- relative energy acceptance interval [min, max]
#     betas -- betatron function [horizontal, vertical] [m]
#     etas -- dispersion function [horizontal, vertical] [m]
#     alphax -- horizontal betatron function derivative
#     etalx -- horizontal dispersion function derivative
#
#     Returns loss rate [1/s].
#     """
#
#     power = _np.power
#     sqrt = _np.sqrt
#     interp = _np.interp
#
#     se = energy_spread
#     emit = natural_emittance
#     k = coupling
#     acc_n = -energy_acceptance_interval[0]
#     acc_p = energy_acceptance_interval[1]
#     betax, betay = betas
#     etax, etay = etas
#
#     _, _, _, gamma, _ = _beam_optics.beam_rigidity(energy=energy)
#
#     emitx = emit / (1 + k)
#     emity = emit * k / (1 + k)
#     sizex = sqrt(betax*emitx + power(etax, 2)*se**2)
#     sizey = sqrt(betay*emity + power(etay, 2)*se**2)
#     volume = bunch_length*sizex*sizey
#
#     sbx2 = emitx*betax
#
#     f = betax*etapx + alphax*etax
#     a_1 = 1/(4*se**2) + (power(etax, 2) + power(f, 2))/(4*sbx2)
#     b_1 = betax*f/(2*sbx2)
#     c_1 = power(betax, 2)/(4*sbx2) - power(b_1, 2)/(4*a_1)
#
#     ksi_p = power(2*sqrt(c_1)*acc_p/gamma, 2)
#     ksi_n = power(2*sqrt(c_1)*acc_n/gamma, 2)
#
#     d_p = interp(ksi_p, _ksi_table, _d_table)
#     d_n = interp(ksi_n, _ksi_table, _d_table)
#
#     loss_rate_p = (_touschek_factor*n*d_p) / (gamma**2*power(acc_p, 3)*volume)
#     loss_rate_n = (_touschek_factor*n*d_n) / (gamma**2*power(acc_n, 3)*volume)
#
#     loss_rate = 0.5*(loss_rate_p + loss_rate_n)
#
#     return loss_rate
#
#
# def calc_elastic_loss_rate(energy, aperture_ratio, acceptances, pressure,
#         betas, z=7, temperature=300):
#     """Calculate beam loss rate due to elastic scattering from residual gas
#
#     Pressure and betas can be supplied as numbers or numpy arrays. In case
#     arrays are supplied, lengths must be equal; the loss rate returned will
#     be an array of same length.
#
#     Keyword arguments:
#     energy -- beam energy [eV]
#     aperture_ratio -- ratio of vertical to horizontal apertures
#     acceptances -- [horizontal, vertical] [m·rad]
#     pressure -- residual gas pressure [mbar]
#     betas -- betatron function [horizontal, vertical] [m]
#     z -- residual gas atomic number (default: 7)
#     temperature -- [K] (default: 300)
#
#     Returns loss rate [1/s].
#     """
#     _, _, beta, *_ = _beam_optics.beam_rigidity(energy=energy)
#     energy_joule = energy*_ev_2_joule;
#
#     beta_x, beta_y = betas
#     r = aperture_ratio
#     a_x, a_y = acceptances
#     p = pressure
#
#     f_x = ((2*_np.arctan(r) + _np.sin(2*_np.arctan(r))) *
#         p*_mbar_2_pascal * beta_x / a_x)
#     f_y = ((_np.pi - 2*_np.arctan(r) + _np.sin(2*_np.arctan(r))) *
#         p*_mbar_2_pascal * beta_y / a_y)
#
#     loss_rate = (_elastic_factor * z**2 * (f_x + f_y) /
#         (beta * energy_joule**2 * temperature))
#
#     return loss_rate
#
#
# def calc_inelastic_loss_rate(energy_acceptance, pressure, z=7,
#         temperature=300):
#     """Calculate loss rate due to inelastic scattering beam lifetime
#
#     Pressure can be supplied as a number or numpy array. In case an array is
#     supplied, the loss rate returned will be an array of same length.
#
#     Keyword arguments:
#     energy_acceptance -- relative energy acceptance
#     pressure -- residual gas pressure [mbar]
#     z -- residual gas atomic number (default: 7)
#     temperature -- [K] (default: 300)
#
#     Returns loss rate [1/s].
#     """
#     acc = energy_acceptance
#     p = pressure
#     loss_rate = (z**2 * _inelastic_factor * _np.log(183/z**(1/3)) *
#         (acc - _np.log(acc) - 5/8) * p*_mbar_2_pascal / temperature)
#     return loss_rate
#
#
# def calc_quantum_loss_rates(natural_emittance, coupling, energy_spread,
#         transverse_acceptances, energy_acceptance, radiation_damping_times):
#     """Calculate beam loss rates due to quantum excitation and radiation
#     damping
#
#     Acceptances can be supplied as numbers or numpy arrays. In case arrays are
#     supplied, the corresponding loss rates returned will also be arrays.
#
#     Keyword arguments:
#     natural_emittance -- natural emittance [m·rad]
#     coupling -- coupling between vertical and horizontal planes
#     energy_spread -- relative energy spread
#     transverse_acceptances -- [horizontal, vertical] [m·rad]
#     energy_acceptance -- relative energy acceptance
#     radiation_damping_times -- [horizontal, vertical, longitudinal] [s]
#
#     Returns loss rates (horizontal, vertical, longitudinal) [1/s].
#     """
#     loss_rate_x, loss_rate_y = calc_quantum_loss_rates_transverse(
#         natural_emittance, coupling, transverse_acceptances,
#         radiation_damping_times[:-1])
#
#     loss_rate_s = calc_quantum_loss_rate_longitudinal(energy_spread,
#         energy_acceptance, radiation_damping_times[-1])
#
#     return loss_rate_x, loss_rate_y, loss_rate_s
#
#
# def calc_quantum_loss_rates_transverse(natural_emittance, coupling,
#         acceptances, radiation_damping_times):
#     """Calculate beam loss rate due to quantum excitation and radiation damping
#     in transverse directions
#
#     Acceptances can be supplied as numbers or numpy arrays. In case arrays are
#     supplied, the corresponding loss rates returned will also be arrays.
#
#     Keyword arguments:
#     natural_emittance -- natural emittance [m·rad]
#     coupling -- coupling between vertical and horizontal planes
#     acceptances -- [horizontal, vertical] [m·rad]
#     radiation_damping_times -- [horizontal, vertical] [s]
#
#     Returns loss rates (horizontal, vertical) [1/s].
#     """
#     tau_x, tau_y = radiation_damping_times
#     acceptance_x, acceptance_y = acceptances
#
#     ksi_x = (1+coupling)*acceptance_x/(2*natural_emittance);
#     loss_rate_x = _calc_quantum_loss_rate(ksi_x, tau_x)
#
#     ksi_y = (1+coupling)*acceptance_y/(2*coupling*natural_emittance);
#     loss_rate_y = _calc_quantum_loss_rate(ksi_y, tau_y)
#
#     return loss_rate_x, loss_rate_y
#
#
# def calc_quantum_loss_rate_longitudinal(energy_spread, energy_acceptance,
#         radiation_damping_time):
#     """Calculate beam loss rate due to quantum excitation and radiation damping
#     in longitudinal direction
#
#     Acceptances can be supplied as numbers or numpy arrays. In case arrays are
#     supplied, the corresponding loss rates returned will also be arrays.
#
#     Keyword arguments:
#     energy_spread -- relative energy spread
#     energy_acceptance -- relative energy acceptance
#     radiation_damping_time -- longitudinal radiation damping time [s]
#
#     Returns loss rate [1/s].
#     """
#     ksi_s = (energy_acceptance/energy_spread)**2/2
#     return _calc_quantum_loss_rate(ksi_s, radiation_damping_time)
#
#
# def _calc_d_touschek_table(a, b, n):
#     ksi = _np.logspace(a, b, n)
#     d = _calc_d_touschek_array(ksi)
#
#     return ksi, d
#
#
# def _calc_d_touschek_array(ksi):
#     d = _np.zeros(len(ksi))
#     for i in range(len(ksi)):
#         d[i] = _calc_d_touschek(ksi[i])
#
#     return d
#
#
# def _calc_d_touschek(ksi):
#     limit = 1000
#
#     sqrt = _np.sqrt
#     exp = _np.exp
#     log = _np.log
#     inf = _np.inf
#
#     f1 = lambda x: exp(-x)/x
#     f2 = lambda x: exp(-x)*log(x)/x
#
#     i1, _ = _integrate.quad(f1, ksi, inf, limit=limit)
#     i2, _ = _integrate.quad(f2, ksi, inf, limit=limit)
#
#     d = sqrt(ksi)*(-1.5*exp(-ksi) + 0.5*(3*ksi-ksi*log(ksi)+2)*i1 + 0.5*ksi*i2)
#
#     return d
#
#
# def _calc_quantum_loss_rate(ksi, tau):
#     return 2*ksi*_np.exp(-ksi)/tau
