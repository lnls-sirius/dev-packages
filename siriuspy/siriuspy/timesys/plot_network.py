"""Make plots of all timing devices and their connections."""

import sys as _sys
import math as _math
import importlib as _importlib

import numpy as _np

from ..namesys import SiriusPVName as _PVName
from ..search import LLTimeSearch as _LLTimeSearch
if _importlib.util.find_spec('matplotlib') is not None:
    import matplotlib.pyplot as _plt
    import matplotlib.gridspec as _gridspec
    import matplotlib.cm as _cmap

_timeout = 1.0


class PlotNetwork(_LLTimeSearch):
    """Plot the timing devices connections."""

    _spacing_for_plot = 10
    _positions = None
    _colors = None
    _arrow_colors = None

    @classmethod
    def plot(cls):
        """Plot the map of connections between all devices."""
        cls._get_timedata()
        if 'matplotlib' not in _sys.modules:
            print('Cannot draw network:matplotlib is not installed')
            return

        def on_motion(event):
            if event.inaxes is None:
                return
            ind = _np.argmin((xs - event.xdata)**2 +
                             (ys - event.ydata)**2)
            pos = (xs[ind], ys[ind])
            txt.xy = pos
            txt.set_position(pos)
            txt.set_text(cls._inv_positions[pos])
            f.canvas.draw()

        if not cls._isGraphUpToDate:
            cls._build_positions()
            cls._build_colors()
            cls._build_arrow_colors()
            cls._isGraphUpToDate = True

        f = _plt.figure(figsize=(20, 20))
        f.canvas.mpl_connect('motion_notify_event', on_motion)
        gs = _gridspec.GridSpec(1, 1)
        gs.update(left=0.1, right=0.95,
                  top=0.97, bottom=0.12,
                  hspace=0.00, wspace=0.2)
        ax = _plt.subplot(gs[0, 0])
        xs = _np.zeros(len(cls._all_devices))
        ys = _np.zeros(len(cls._all_devices))
        for i, dev in enumerate(sorted(cls._all_devices)):
            xs[i], ys[i] = cls._positions[dev]
            ax.plot(*cls._positions[dev],
                    color=cls._colors[dev],
                    marker='.', markersize=8)

        txt = ax.annotate(s='', xy=(0.0, 0.0), xycoords='data')

        for dev in sorted(cls._dev_from_evg.keys()):
            conns = sorted(cls._dev_from_evg[dev])
            for conn in conns:
                x = cls._positions[dev][0]
                y = cls._positions[dev][1]
                dx = cls._positions[conn][0] - x
                dy = cls._positions[conn][1] - y
                cor = cls._arrow_colors[(dev, conn)]
                ax.arrow(x, y, dx, dy,
                         fc=cor, ec=cor, length_includes_head=True)

    # Methods auxiliar to plot_network
    @classmethod
    def _dist(cls, x):
        return cls._spacing_for_plot/_math.sqrt(2*(1-_math.cos(x)))

    @staticmethod
    def _pol2cart(x, y):
        return (x*_math.cos((y[0]+y[1])/2), x*_math.sin((y[0]+y[1])/2))

    @classmethod
    def _build_positions(cls):
        pi2 = _math.pi*2
        nevgs = len(cls._hierarchy_map[0])
        radia = [0] * len(cls._hierarchy_map)
        radia[0] = 0 if nevgs == 1 else cls._dist(pi2/nevgs)
        angles = dict()
        positions = dict()
        for i, dev in enumerate(cls._hierarchy_map[0]):
            angles[dev] = (i*pi2/nevgs, (i+1)*pi2/nevgs)
            positions[dev] = cls._pol2cart(radia[0], angles[dev])

        # find angles and radia
        for n, devs in enumerate(cls._hierarchy_map):
            min_ang = pi2
            for dev in devs:
                angi, angf = angles[dev]
                dang = angf-angi
                devs2 = cls._dev_from_evg.get(dev, set())
                nr = len(devs2)
                min_ang = min(min_ang, dang, dang/nr if nr else min_ang)
                for i, dev2 in enumerate(devs2):
                    angles[dev2] = (i*dang/nr + angi, (i+1)*dang/nr + angi)
            r = cls._dist(min_ang)
            if n > 0 and r <= radia[n-1]:
                radia[n] = 2*radia[n-1]
            else:
                radia[n] = r

        # get positions
        for n, devs in enumerate(cls._hierarchy_map):
            for dev in devs:
                devs2 = cls._dev_from_evg.get(dev, set())
                for i, dev2 in enumerate(devs2):
                    positions[dev2] = cls._pol2cart(radia[n], angles[dev2])

        cls._positions = positions
        cls._inv_positions = {xy: dev for dev, xy in positions.items()}

    @classmethod
    def _build_colors(cls):
        if 'matplotlib' not in _sys.modules:
            print('Cannot draw network: matplotlib is not installed')
            return
        dev_types = set()
        for dev in cls._all_devices:
            dev_types.add(_PVName(dev).dev)

        nr = len(dev_types)+2
        color_types = dict()
        for i, dev_type in enumerate(sorted(dev_types), 1):
            color_types[dev_type] = _cmap.spectral(i/nr)

        colors = dict()
        for dev in cls._all_devices:
            colors[dev] = color_types[_PVName(dev).dev]

        cls._colors = colors

    @classmethod
    def _build_arrow_colors(cls):
        if 'matplotlib' not in _sys.modules:
            print('Cannot draw network:matplotlib is not installed')
            return
        chan_types = set()
        for chan in cls._conn_from_evg.keys():
            chan_type = cls.ll_rgx.findall(chan.propty)[0][0]
            chan_types.add(chan_type)

        nr = len(chan_types)+2
        color_types = dict()
        for i, chan_type in enumerate(sorted(chan_types), 1):
            color_types[chan_type] = _cmap.spectral(i/nr)

        colors = dict()
        for chan1, conns in cls._conn_from_evg.items():
                chan_type = cls.ll_rgx.findall(chan1.propty)[0][0]
                for chan2 in conns:
                    colors[(chan1.device_name,
                            chan2.device_name)] = color_types[chan_type]
        cls._arrow_colors = colors

    @classmethod
    def _update_related_maps(cls):
        super()._update_related_maps()
        cls._isGraphUpToDate = False
