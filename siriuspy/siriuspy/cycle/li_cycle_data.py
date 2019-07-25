"""Linac cycle data."""

import numpy as _np


parms = {
    # psname             dt[s], max_amp[A], period[s], nrcycles, tau[s], sin**2
    'LI-01:PS-Spect':    [0.5, 6.0, 24, 8, 48, False],

    'LI-01:PS-QD1':      [0.5, 5, 24, 8, 48, False],
    'LI-01:PS-QD2':      [0.5, 5, 24, 8, 48, False],
    'LI-Fam:PS-QF1':     [0.5, 5, 24, 8, 48, False],
    'LI-Fam:PS-QF2':     [0.5, 5, 24, 8, 48, False],
    'LI-01:PS-QF3':      [0.5, 5, 24, 8, 48, False],

    'LI-01:PS-CV-3':     [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CH-3':     [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CV-4':     [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CH-4':     [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CV-5':     [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CH-5':     [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CV-6':     [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CH-6':     [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CV-7':     [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CH-7':     [0.5, 1.5, 24, 8, 48, False],

    'LI-01:PS-Lens-1':   [0.5, 5, 24, 8, 48, False],
    'LI-01:PS-Lens-2':   [0.5, 5, 24, 8, 48, False],
    'LI-01:PS-Lens-3':   [0.5, 5, 24, 8, 48, False],
    'LI-01:PS-Lens-4':   [0.5, 5, 24, 8, 48, False],

    'LI-01:PS-LensRev':  [0.5, 5, 24, 8, 48, False],

    'LI-01:PS-CV-1':     [0.5, 0.25, 24, 8, 48, False],
    'LI-01:PS-CH-1':     [0.5, 0.25, 24, 8, 48, False],
    'LI-01:PS-CV-2':     [0.5, 0.25, 24, 8, 48, False],
    'LI-01:PS-CH-2':     [0.5, 0.25, 24, 8, 48, False],

    'LI-01:PS-Slnd-1':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-2':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-3':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-4':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-5':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-6':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-7':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-8':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-9':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-10':  [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-11':  [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-12':  [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-13':  [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-14': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-15': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-16': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-17': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-18': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-19': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-20': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-21': [0.5, 35, 38, 5, 57, True],
}


def li_get_default_waveform(psname):
    """Return cycle waveform."""
    [dt, ampl, period, nr_periods, tau, square] = parms[psname]
    w = 2*_np.pi/period
    nrpts = nr_periods * int(period / dt)
    v = list(range(0, nrpts))
    t = dt * _np.array(v)
    n = 2 if square else 1
    t0 = _np.arctan(2*_np.pi*tau*n)/w
    sin = _np.sin(2*_np.pi*t/period)
    exp = _np.exp(-(t-t0)/tau)
    amp = ampl/(_np.sin(w*t0))**n
    f = amp * exp * sin**n
    t = _np.append(t, t[-1] + dt)
    f = _np.append(f, 0.0)
    f *= ampl/max(f)  # makes sure max point is 'ampl'
    return t, f
