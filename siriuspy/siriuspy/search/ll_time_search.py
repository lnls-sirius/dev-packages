"""Define properties of all timing devices and their connections."""

import re as _re
import sys as _sys
from copy import deepcopy as _dcopy
import math as _math
import numpy as _np
import importlib as _importlib
from siriuspy import servweb as _web
from siriuspy import diagnostics as _diag
from .ps_search import PSSearch as _PSSearch
from siriuspy.namesys import SiriusPVName as _PVName

# TODO: temporarily moved import matplolib
# this is necessary until it be imported correctly in the BBB
# the problem has to do with Qt...

# if _importlib.find_loader('matplotlib') is not None:
#     import matplotlib.pyplot as _plt
#     import matplotlib.gridspec as _gridspec
#     import matplotlib.cm as _cmap

_timeout = 1.0


class LLTimeSearch:
    """Get the timing devices connections."""

    ll_rgx = _re.compile('([A-Z]+)([0-9]{0,2})', _re.IGNORECASE)

    # defines the relations between input and output of the timing devices
    # that are possible taking into consideration only the devices architecture
    i2o_map = {
        'EVR': {
            'UPLINK': (
                'OTP00', 'OTP01', 'OTP02', 'OTP03', 'OTP04', 'OTP05',
                'OTP06', 'OTP07', 'OTP08', 'OTP09', 'OTP10', 'OTP11',
                'OUT0', 'OUT1', 'OUT2', 'OUT3',
                'OUT4', 'OUT5', 'OUT6', 'OUT7',
                ),
            },
        'EVE': {
            'UPLINK': (
                'OUT0', 'OUT1', 'OUT2', 'OUT3',
                'OUT4', 'OUT5', 'OUT6', 'OUT7',
                'RFOUT',
                ),
            },
        'AFC': {
            'SFP': (
                'FMC1CH1', 'FMC1CH2', 'FMC1CH3', 'FMC1CH4', 'FMC1CH5',
                'FMC2CH1', 'FMC2CH2', 'FMC2CH3', 'FMC2CH4', 'FMC2CH5',
                'CRT0', 'CRT1', 'CRT2', 'CRT3', 'CRT4',
                'CRT5', 'CRT6', 'CRT7',
                ),
            },
        'STDMOE': {
            'OE1': ('OUT1',),
            'OE2': ('OUT2',),
            'OE3': ('OUT3',),
            'OE4': ('OUT4',),
            },
        'STDSOE': {
            'IN1': ('OUT1',),
            'IN2': ('OUT2',),
            'IN3': ('OUT3',),
            'IN4': ('OUT4',),
            },
        'SOE': {
            'IN': ('OUT',),
            },
        'MOE': {
            'INRX': ('OUT', 'INTX'),
            },
        'FOUT': {
            'UPLINK': (
                'OUT0', 'OUT1', 'OUT2', 'OUT3',
                'OUT4', 'OUT5', 'OUT6', 'OUT7',
                ),
            },
        'BBB': {
            'IN': ('RSIO',),
            },
        'Crate': {
            'CRT0': ('CRT0',),
            'CRT1': ('CRT1',),
            'CRT2': ('CRT2',),
            'CRT3': ('CRT3',),
            'CRT4': ('CRT4',),
            'CRT5': ('CRT5',),
            'CRT6': ('CRT6',),
            'CRT7': ('CRT7',),
            },
        }

    o2i_map = dict()
    for dev, conns_ in i2o_map.items():
        dic_ = dict()
        o2i_map[dev] = dic_
        for conn1, conns in conns_.items():
            for conn2 in conns:
                dic_[conn2] = conn1
    del(dev, conns_, dic_, conn1, conns, conn2)  # cleanning class namespace.

    _spacing_for_plot = 10

    _conn_from_evg = None
    _conn_twds_evg = None
    _top_chain_devs = None
    _final_receiver_devs = None
    _all_devices = None
    _hierarchy_map = None
    _positions = None
    _colors = None
    _arrow_colors = None

    @classmethod
    def get_channel_input(cls, channel):
        """Get channel input method."""
        if not isinstance(channel, _PVName):
            channel = _PVName(channel)
        conn_up = cls.o2i_map[channel.dev][channel.propty]
        return _PVName(channel.device_name + ':' + conn_up)

    @classmethod
    def plot_network(cls):
        """Plot the map of connections between all devices."""
        # TODO: temporarily moved import matplolib
        if _importlib.find_loader('matplotlib') is not None:
            import matplotlib.pyplot as _plt
            import matplotlib.gridspec as _gridspec

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

    @classmethod
    def add_crates_info(cls, connections_dict=None):
        """Add the information of Crate to BPMs to timing map."""
        cls._get_timedata()
        if connections_dict is None:
            connections_dict = _diag.cratesdata.get_mapping()
        used = set()
        twds_evg = _dcopy(cls._conn_twds_evg)
        for chan in twds_evg.keys():
            bpms = connections_dict.get(chan.device_name)
            if bpms is None:
                continue
            used.add(chan.device_name)
            for bpm in bpms:
                cls._add_entry_to_map(
                    which_map='from', conn=chan.propty,
                    ele1=chan.device_name, ele2=bpm)
                cls._add_entry_to_map(
                    which_map='twds', conn=chan.propty,
                    ele1=bpm, ele2=chan.device_name)
        cls._update_related_maps()
        return (connections_dict.keys() - used)

    @classmethod
    def add_bbb_info(cls, connections_dict=None):
        """Add the information of bbb to PS to timing map."""
        cls._get_timedata()
        if connections_dict is None:
            connections_dict = _PSSearch.get_bbbname_dict()
        conn = 'RSIO'
        used = set()
        twds_evg = _dcopy(cls._conn_twds_evg)
        for chan in twds_evg.keys():
            pss = connections_dict.get(chan.device_name)
            if pss is None:
                continue
            used.add(chan.device_name)
            for ps in pss:
                cls._add_entry_to_map(
                    which_map='from', conn=conn,
                    ele1=chan.device_name, ele2=ps)
                cls._add_entry_to_map(
                    which_map='twds', conn=conn,
                    ele1=ps, ele2=chan.device_name)
        cls._update_related_maps()
        return (connections_dict.keys() - used)

    @classmethod
    def get_devices_by_type(cls, type_dev=None):
        """
        Return a set with all devices of type type_dev.

        if type_dev is None, return all devices.
        """
        def _pv_fun(x, y):
            return _PVName(x).dev == y

        cls._get_timedata()
        if not type_dev:
            return _dcopy(cls._all_devices)
        return {dev for dev in cls._all_devices if _pv_fun(dev, type_dev)}

    @classmethod
    def get_device_tree(cls, channel):
        """Return a dictionary with the beaglebone to power supply mapping."""
        cls._get_timedata()
        twds_evg = cls._conn_twds_evg
        up_chan = _PVName(channel)
        if up_chan in twds_evg.keys():
            up_chan = list(twds_evg[up_chan])[0]
        up_channels = [up_chan]
        while up_chan.device_name not in cls._top_chain_devs:
            up_chan = cls.get_channel_input(up_chan)
            up_chan = list(twds_evg[up_chan])[0]
            up_channels.append(up_chan)
        return up_channels

    @classmethod
    def reset(cls):
        """Reset data to initial value."""
        cls._conn_from_evg = None
        cls._conn_twds_evg = None
        cls._get_timedata()

    @staticmethod
    def server_online():
        """Return True/False if Sirius web server is online."""
        return _web.server_online()

    @classmethod
    def get_connections_from_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        cls._get_timedata()
        return _dcopy(cls._conn_from_evg)

    @classmethod
    def get_connections_twds_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        cls._get_timedata()
        return _dcopy(cls._conn_twds_evg)

    @classmethod
    def get_top_chain_senders(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        cls._get_timedata()
        return _dcopy(cls._top_chain_senders)

    @classmethod
    def get_final_receivers(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        cls._get_timedata()
        return _dcopy(cls._final_receivers)

    @classmethod
    def get_relations_from_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        cls._get_timedata()
        return _dcopy(cls._relations_from_evg)

    @classmethod
    def get_relations_twds_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        cls._get_timedata()
        return _dcopy(cls._relations_twds_evg)

    @classmethod
    def get_hierarchy_list(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        cls._get_timedata()
        return _dcopy(cls._hierarchy_list)

    # ############ Auxiliar methods ###########
    @classmethod
    def _add_entry_to_map(cls, which_map, conn, ele1, ele2):
        if which_map == 'from':
            mapp = cls._conn_from_evg
        else:
            mapp = cls._conn_twds_evg
        ele1 = _PVName(ele1+':'+conn)
        ele2 = _PVName(ele2+':'+conn)
        ele1_entry = mapp.get(ele1)
        if not ele1_entry:
            mapp[ele1] = {ele2}
        else:
            ele1_entry |= {ele2}

    @classmethod
    def _get_timedata(cls):
        if cls._conn_from_evg:
            return
        if _web.server_online():
            text = _web.timing_devices_mapping(timeout=_timeout)
        cls._parse_text_and_build_connection_mappings(text)
        cls._update_related_maps()

    # Methods auxiliar to _get_timedata
    @classmethod
    def _parse_text_and_build_connection_mappings(cls, text):
        from_evg = dict()
        twds_evg = dict()
        lines = text.splitlines()
        for n, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line[0] == '#':
                continue  # empty line
            out, inn = line.split()[:2]
            out, inn = _PVName(out), _PVName(inn)
            send, ochn, octyp, ocn = cls._get_dev_and_channel(out)
            recv, ichn, ictyp, icn = cls._get_dev_and_channel(inn)
            if not ochn or not ichn:
                print('No {0:s} channel defined in line {1:d}:\n\t {2:s}'
                      .format('output' if not ochn else 'input', n, line))
                return
            elif not octyp or not ictyp:
                print('Sintaxe error in definition of ' +
                      '{0:s} channel in line {1:d}:\n\t {2:s}'
                      .format('output' if not octyp else 'input', n, line))
                return
            else:
                if out in from_evg.keys():
                    from_evg[out] |= {inn}
                else:
                    from_evg[out] = {inn}

                if inn in twds_evg.keys():
                    print('Duplicate device input connection in line ' +
                          '{0:d}:\n\t {1:s}'.format(n, line))
                    return
                else:
                    twds_evg[inn] = {out}
        cls._conn_from_evg = from_evg
        cls._conn_twds_evg = twds_evg

    @classmethod
    def _get_dev_and_channel(cls, txt):
        type_chan = num_chan = None
        dev = txt.device_name
        chan = txt.propty
        reg_match = cls.ll_rgx.findall(chan)
        if reg_match:
            type_chan, num_chan = reg_match[0]
            return dev, chan, type_chan, num_chan
        else:
            print(chan)

    @classmethod
    def _update_related_maps(cls):
        cls._build_devices_relations()
        cls._top_chain_devs = (
            cls._dev_from_evg.keys() - cls._dev_twds_evg.keys()
            )
        cls._final_receiver_devs = (
            cls._dev_twds_evg.keys() - cls._dev_from_evg.keys()
            )
        cls._all_devices = (
            cls._dev_from_evg.keys() | cls._dev_twds_evg.keys()
            )
        cls._build_hierarchy_map()
        cls._isGraphUpToDate = False

    @classmethod
    def _build_devices_relations(cls):
        simple_map = dict()
        for k, vs in cls._conn_from_evg.items():
            devs = {v.device_name for v in vs}
            devs |= simple_map.get(k.device_name, set())
            simple_map[k.device_name] = devs

        inv_map = dict()
        for k, vs in simple_map.items():
            for v in vs:
                devs = {k}
                devs |= inv_map.get(v, set())
                inv_map[v] = devs

        cls._dev_from_evg = simple_map
        cls._dev_twds_evg = inv_map

    @classmethod
    def _build_hierarchy_map(cls):
        hierarchy = [cls._top_chain_devs.copy(), ]
        while True:
            vals = set()
            for k in hierarchy[-1]:
                vals |= cls._dev_from_evg.get(k, set())
            if vals:
                hierarchy.append(vals)
            else:
                break
        cls._hierarchy_map = hierarchy

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
        # TODO: temporarily moved import matplolib
        if _importlib.find_loader('matplotlib') is not None:
            import matplotlib.cm as _cmap

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
        # TODO: temporarily moved import matplolib
        if _importlib.find_loader('matplotlib') is not None:
            import matplotlib.cm as _cmap

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
