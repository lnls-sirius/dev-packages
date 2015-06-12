
import numpy as _np


def calc_quantum_loss_rates(natural_emittance, coupling, energy_spread,
        transverse_acceptances, energy_acceptance, radiation_damping_times):
    """Calculate loss rates due to quantum beam lifetime

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
    alpha_x, alpha_y = calc_quantum_loss_rates_transverse(natural_emittance,
        coupling, transverse_acceptances, radiation_damping_times[:-1])

    alpha_s = calc_quantum_loss_rate_longitudinal(energy_spread,
        energy_acceptance, radiation_damping_times[-1])

    return alpha_x, alpha_y, alpha_s


def calc_quantum_loss_rates_transverse(natural_emittance, coupling,
        acceptances, radiation_damping_times):
    """Calculate loss rate due to transverse quantum beam lifetime

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
    alpha_x = _calc_quantum_loss_rate(ksi_x, tau_x)

    ksi_y = (1+coupling)*acceptance_y/(2*coupling*natural_emittance);
    alpha_y = _calc_quantum_loss_rate(ksi_y, tau_y)

    return alpha_x, alpha_y


def calc_quantum_loss_rate_longitudinal(energy_spread, energy_acceptance,
        radiation_damping_time):
    """Calculate loss rate due to longitudinal quantum beam lifetime

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


def _calc_quantum_loss_rate(ksi, tau):
    return 2*ksi*_np.exp(-ksi)/tau
