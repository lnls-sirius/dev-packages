"""Define properties of all timing devices and their connections."""

from siriuspy import servweb as _web
from siriuspy.namesys import SiriusPVName as _PVName
import copy as _copy
import re as _re
import sys as _sys
import math as _math
import numpy as _np
import importlib as _importlib
if _importlib.find_loader('matplotlib') is not None:
    import matplotlib.pyplot as _plt
    import matplotlib.gridspec as _gridspec
    import matplotlib.cm as _cmap

_timeout = 1.0
_LOCAL = False

AC_FREQUENCY = 60
RF_DIVISION = 4
RF_FREQUENCY = 299792458/518.396*864
BASE_FREQUENCY = RF_FREQUENCY / RF_DIVISION
RF_PERIOD = 1/RF_FREQUENCY
BASE_DELAY = 1 / BASE_FREQUENCY
RF_DELAY = BASE_DELAY / 20
FINE_DELAY = 5e-12                  # five picoseconds


class Events:
    """Contain properties of the Events."""

    HL2LL_MAP = {'Linac': 'Event00', 'InjBO': 'Event01',
                 'InjSI': 'Event02', 'RmpBO': 'Event03',
                 'MigSI': 'Event04', 'DigLI': 'Event05',
                 'DigTB': 'Event06', 'DigBO': 'Event07',
                 'DigTS': 'Event08', 'DigSI': 'Event09',
                 'Orbit': 'Event0A', 'Coupl': 'Event0B',
                 'Tunes': 'Event0C', 'Study': 'Event0D'}
    LL2HL_MAP = {val: key for key, val in HL2LL_MAP.items()}

    LL_TMP = 'Event{0:02X}'
    LL_RGX = _re.compile('Event([0-9A-E]{2})([a-z-\.]*)', _re.IGNORECASE)
    HL_RGX = _re.compile('('+'|'.join(list(HL2LL_MAP.keys())) +
                         ')([a-z-\.]*)', _re.IGNORECASE)
    HL_PREF = 'AS-Glob:TI-EVG:'

    LL_CODES = list(range(50)) + list(range(80, 120)) + list(range(160, 256))
    LL_EVENTS = []
    for i in LL_CODES:
        LL_EVENTS.append(LL_TMP.format(i))

    MODES = ('Disabled', 'Continuous', 'Injection', 'External')
    DELAY_TYPES = ('Fixed', 'Incr')


class Clocks:
    """Contain properties of the Clocks."""

    STATES = ('Dsbl', 'Enbl')

    LL_TMP = 'Clock{0:d}'
    HL_TMP = 'Clock{0:d}'
    HL_PREF = 'AS-Glob:TI-EVG:'

    HL2LL_MAP = dict()
    for i in range(8):
        HL2LL_MAP[HL_TMP.format(i)] = LL_TMP.format(i)
    LL2HL_MAP = {val: key for key, val in HL2LL_MAP.items()}


class Triggers:
    """Contain properties of the triggers."""

    STATES = ('Dsbl', 'Enbl')
    POLARITIES = ('Normal', 'Inverse')
    DELAY_TYPES = ('Fixed', 'Incr')

    def __init__(self):
        """Initialize the Instance."""
        text = ''
        if _LOCAL:
            with open('/home/fac_files/lnls-sirius/' +
                      'control-system-constants/' +
                      'timesys/high-level-triggers.txt', 'r') as f:
                text = f.read()
        else:
            if _web.server_online():
                text = _web.high_level_triggers(timeout=_timeout)
        # the execution of text will create the HL_TRIGGS variable.
        exec(text)
        self._hl_triggers = locals()['HL_TRIGGS']
        self.check_triggers_consistency()

    @property
    def hl_triggers(self):
        """Dictionary with high level trigger properties."""
        return _copy.deepcopy(self._hl_triggers)

    def check_triggers_consistency(self):
        """Check consitency of Triggers definition.

        Check if High Level definition of Triggers is consistent with
        Low Level connections of the timing devices.
        """
        Connections.add_bbb_info()
        Connections.add_crates_info()
        from_evg = Connections.get_connections_from_evg()
        twds_evg = Connections.get_connections_twds_evg()
        for trig, val in self.hl_triggers.items():
            chans = {_PVName(chan) for chan in val['channels']}
            for chan in chans:
                tmp = twds_evg.get(chan)
                if tmp is None:
                    raise Exception(
                        'Device ' + chan +
                        ' defined in the high level trigger ' +
                        trig + ' not specified in timing connections data.')
                if not tmp:
                    raise Exception('Device ' + chan +
                                    ' defined in the high level trigger ' +
                                    trig + ' maybe were already used.')
                up_dev = tmp.pop()
                diff_devs = from_evg[up_dev] - chans
                if diff_devs and not chan.dev_type.endswith('BPM'):
                    raise Exception(
                        'Devices: ' + ' '.join(diff_devs) +
                        ' are connected to the same output of ' +
                        up_dev + ' as ' + chan +
                        ' but are not related to the sam trigger (' +
                        trig + ').')


class IOs:
    """Contain the properties of the connections."""

    LL_RGX = _re.compile('([A-Z]+)([0-9]{0,2})', _re.IGNORECASE)

    # defines the relations between input and output of the timing devices
    # that are possible taking into consideration only the devices architecture
    I2O_MAP = {
        'EVR': {
            'UPLINK': (
                'OTP00', 'OTP00', 'OTP00', 'OTP03', 'OTP04', 'OTP05',
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
                'FMC0', 'FMC1', 'FMC2', 'FMC3', 'FMC4',
                'FMC5', 'FMC6', 'FMC7', 'FMC8', 'FMC9',
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

    O2I_MAP = dict()
    for dev, conns_ in I2O_MAP.items():
        dic_ = dict()
        O2I_MAP[dev] = dic_
        for conn1, conns in conns_.items():
            for conn2 in conns:
                dic_[conn2] = conn1


class _TimeDevData:
    """Class with mapping of timing devices and triggers receivers connections.

    Data are read from the Sirius web server.
    """

    _spacing_for_plot = 10

    def __init__(self, timeout=_timeout):
        self._conn_from_evg = dict()
        self._conn_twrds_evg = dict()
        self._devices_relations = dict()
        self._top_chain_devs = set()
        self._final_receiver_devs = set()
        self._all_devices = set()
        self._hierarchy_map = list()
        self._positions = dict()
        self._colors = dict()
        self._arrow_colors = dict()
        if _LOCAL:
            with open('/home/fac_files/lnls-sirius/' +
                      'control-system-constants/' +
                      'timesys/timing-devices-connection.txt', 'r') as f:
                text = f.read()
        else:
            if _web.server_online():
                text = _web.timing_devices_mapping(timeout=_timeout)
        self._parse_text_and_build_connection_mappings(text)
        self._update_related_maps()

    def _update_related_maps(self):
        self._build_devices_relations()
        self._top_chain_devs = (self._dev_from_evg.keys() -
                                self._dev_twds_evg.keys())
        self._final_receiver_devs = (self._dev_twds_evg.keys() -
                                     self._dev_from_evg.keys())
        self._all_devices = (self._dev_from_evg.keys() |
                             self._dev_twds_evg.keys())
        self._build_hierarchy_map()
        self._isGraphUpToDate = False

    def _get_dev_and_channel(self, txt):
        type_chan = num_chan = None
        dev = txt.dev_name
        chan = txt.propty
        reg_match = IOs.LL_RGX.findall(chan)
        if reg_match:
            type_chan, num_chan = reg_match[0]
            return dev, chan, type_chan, num_chan

    def _parse_text_and_build_connection_mappings(self, text):
        from_evg = dict()
        twds_evg = dict()
        lines = text.splitlines()
        for n, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line[0] == '#':
                continue  # empty line
            out, inn = line.split()[:2]
            out, inn = _PVName(out), _PVName(inn)
            send, ochn, octyp, ocn = self._get_dev_and_channel(out)
            recv, ichn, ictyp, icn = self._get_dev_and_channel(inn)
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
        self._conn_from_evg = from_evg
        self._conn_twds_evg = twds_evg

    def _build_devices_relations(self):
        simple_map = dict()
        for k, vs in self._conn_from_evg.items():
            devs = {v.dev_name for v in vs}
            devs |= simple_map.get(k.dev_name, set())
            simple_map[k.dev_name] = devs

        inv_map = dict()
        for k, vs in simple_map.items():
            for v in vs:
                devs = {k}
                devs |= inv_map.get(v, set())
                inv_map[v] = devs

        self._dev_from_evg = simple_map
        self._dev_twds_evg = inv_map

    def _build_hierarchy_map(self):
        hierarchy = [self._top_chain_devs.copy(), ]
        while True:
            vals = set()
            for k in hierarchy[-1]:
                vals |= self._dev_from_evg.get(k, set())
            if vals:
                hierarchy.append(vals)
            else:
                break
        self._hierarchy_map = hierarchy

    def plot_network(self):
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
            txt.set_text(self._inv_positions[pos])
            f.canvas.draw()

        if not self._isGraphUpToDate:
            self._build_positions()
            self._build_colors()
            self._build_arrow_colors()
            self._isGraphUpToDate = True

        f = _plt.figure(figsize=(20, 20))
        f.canvas.mpl_connect('motion_notify_event', on_motion)
        gs = _gridspec.GridSpec(1, 1)
        gs.update(left=0.1, right=0.95,
                  top=0.97, bottom=0.12,
                  hspace=0.00, wspace=0.2)
        ax = _plt.subplot(gs[0, 0])
        xs = _np.zeros(len(self._all_devices))
        ys = _np.zeros(len(self._all_devices))
        for i, dev in enumerate(sorted(self._all_devices)):
            xs[i], ys[i] = self._positions[dev]
            ax.plot(*self._positions[dev],
                    color=self._colors[dev],
                    marker='.', markersize=8)

        txt = ax.annotate(s='', xy=(0.0, 0.0), xycoords='data')

        for dev in sorted(self._dev_from_evg.keys()):
            conns = sorted(self._dev_from_evg[dev])
            for conn in conns:
                x = self._positions[dev][0]
                y = self._positions[dev][1]
                dx = self._positions[conn][0] - x
                dy = self._positions[conn][1] - y
                cor = self._arrow_colors[(dev, conn)]
                ax.arrow(x, y, dx, dy,
                         fc=cor, ec=cor, length_includes_head=True)

    @classmethod
    def _dist(cls, x):
        return cls._spacing_for_plot/_math.sqrt(2*(1-_math.cos(x)))

    @staticmethod
    def _pol2cart(x, y):
        return (x*_math.cos((y[0]+y[1])/2), x*_math.sin((y[0]+y[1])/2))

    def _build_positions(self):

        pi2 = _math.pi*2
        nevgs = len(self._hierarchy_map[0])
        radia = [0] * len(self._hierarchy_map)
        radia[0] = 0 if nevgs == 1 else self._dist(pi2/nevgs)
        angles = dict()
        positions = dict()
        for i, dev in enumerate(self._hierarchy_map[0]):
            angles[dev] = (i*pi2/nevgs, (i+1)*pi2/nevgs)
            positions[dev] = self._pol2cart(radia[0], angles[dev])

        # find angles and radia
        for n, devs in enumerate(self._hierarchy_map):
            min_ang = pi2
            for dev in devs:
                angi, angf = angles[dev]
                dang = angf-angi
                devs2 = self._dev_from_evg.get(dev, set())
                nr = len(devs2)
                min_ang = min(min_ang, dang, dang/nr if nr else min_ang)
                for i, dev2 in enumerate(devs2):
                    angles[dev2] = (i*dang/nr + angi, (i+1)*dang/nr + angi)
            r = self._dist(min_ang)
            if n > 0 and r <= radia[n-1]:
                radia[n] = 2*radia[n-1]
            else:
                radia[n] = r

        # get positions
        for n, devs in enumerate(self._hierarchy_map):
            for dev in devs:
                devs2 = self._dev_from_evg.get(dev, set())
                for i, dev2 in enumerate(devs2):
                    positions[dev2] = self._pol2cart(radia[n], angles[dev2])

        self._positions = positions
        self._inv_positions = {xy: dev for dev, xy in positions.items()}

    def _build_colors(self):
        if 'matplotlib' not in _sys.modules:
            print('Cannot draw network: matplotlib is not installed')
            return
        dev_types = set()
        for dev in self._all_devices:
            dev_types.add(_PVName(dev).dev_type)

        nr = len(dev_types)+2
        color_types = dict()
        for i, dev_type in enumerate(sorted(dev_types), 1):
            color_types[dev_type] = _cmap.spectral(i/nr)

        colors = dict()
        for dev in self._all_devices:
            colors[dev] = color_types[_PVName(dev).dev_type]

        self._colors = colors

    def _build_arrow_colors(self):
        if 'matplotlib' not in _sys.modules:
            print('Cannot draw network:matplotlib is not installed')
            return
        chan_types = set()
        for chan in self._conn_from_evg.keys():
            chan_type = IOs.LL_RGX.findall(chan.propty)[0][0]
            chan_types.add(chan_type)

        nr = len(chan_types)+2
        color_types = dict()
        for i, chan_type in enumerate(sorted(chan_types), 1):
            color_types[chan_type] = _cmap.spectral(i/nr)

        colors = dict()
        for chan1, conns in self._conn_from_evg.items():
                chan_type = IOs.LL_RGX.findall(chan1.propty)[0][0]
                for chan2 in conns:
                    colors[(chan1.dev_name,
                            chan2.dev_name)] = color_types[chan_type]

        self._arrow_colors = colors

    def add_crates_info(self, connections_dict):
        used = set()
        twds_evg = self.conn_twds_evg
        for chan in twds_evg.keys():
            bpms = connections_dict.get(chan.dev_name)
            if bpms is None:
                continue
            used.add(chan.dev_name)
            for bpm in bpms:
                self._add_entry_to_map(which_map='from', conn=chan.propty,
                                       ele1=chan.dev_name, ele2=bpm)
                self._add_entry_to_map(which_map='twds', conn=chan.propty,
                                       ele1=bpm, ele2=chan.dev_name)
        self._update_related_maps()
        return (connections_dict.keys() - used)

    def add_bbb_info(self, connections_dict):
        conn = 'RSIO'
        used = set()
        twds_evg = self.conn_twds_evg
        for chan in twds_evg.keys():
            pss = connections_dict.get(chan.dev_name)
            if pss is None:
                continue
            used.add(chan.dev_name)
            for ps in pss:
                self._add_entry_to_map(which_map='from', conn=conn,
                                       ele1=chan.dev_name, ele2=ps)
                self._add_entry_to_map(which_map='twds', conn=conn,
                                       ele1=ps, ele2=chan.dev_name)
        self._update_related_maps()
        return (connections_dict.keys() - used)

    def _add_entry_to_map(self, which_map, conn, ele1, ele2):
        if which_map == 'from':
            mapp = self._conn_from_evg
        else:
            mapp = self._conn_twds_evg
        ele1 = _PVName(ele1+':'+conn)
        ele2 = _PVName(ele2+':'+conn)
        ele1_entry = mapp.get(ele1)
        if not ele1_entry:
            mapp[ele1] = {ele2}
        else:
            ele1_entry |= {ele2}

    def get_devices_by_type(self, type_dev):
        def _pv_fun(x, y):
            return _PVName(x).dev_type == y

        return {dev for dev in self._all_devices if _pv_fun(dev, type_dev)}

    @property
    def conn_from_evg(self): return _copy.deepcopy(self._conn_from_evg)

    @property
    def conn_twds_evg(self): return _copy.deepcopy(self._conn_twds_evg)

    @property
    def final_receivers(self): return _copy.deepcopy(self._final_receiver_devs)

    @property
    def top_chain_senders(self): return _copy.deepcopy(self._top_chain_devs)

    @property
    def relations_from_evg(self): return _copy.deepcopy(self._dev_from_evg)

    @property
    def relations_twds_evg(self): return _copy.deepcopy(self._dev_twds_evg)

    @property
    def hierarchy_list(self): return _copy.deepcopy(self._hierarchy_map)

    @property
    def all_devices(self): return _copy.deepcopy(self._all_devices)


class Connections:
    """Get the timing devices connections."""

    _timedata = None

    @classmethod
    def _get_timedata(cls):
        # encapsulating _bbbdata within a function avoid creating the global
        # object (which is time consuming) at module load time.
        if cls._timedata is None:
            cls._timedata = _TimeDevData()
        return cls._timedata

    @classmethod
    def reset(cls):
        """Reset data to initial value."""
        cls._timedata = _TimeDevData()

    @staticmethod
    def server_online():
        """Return True/False if Sirius web server is online."""
        return _web.server_online()

    @classmethod
    def get_connections_from_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata = cls._get_timedata()
        return timedata.conn_from_evg

    @classmethod
    def get_connections_twds_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata = cls._get_timedata()
        return timedata.conn_twds_evg

    @classmethod
    def get_top_chain_senders(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata = cls._get_timedata()
        return timedata.top_chain_senders

    @classmethod
    def get_final_receivers(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata = cls._get_timedata()
        return timedata.final_receivers

    @classmethod
    def get_relations_from_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata = cls._get_timedata()
        return timedata.relations_from_evg

    @classmethod
    def get_relations_twds_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata = cls._get_timedata()
        return timedata.relations_twds_evg

    @classmethod
    def get_hierarchy_list(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata = cls._get_timedata()
        return timedata.hierarchy_list

    @classmethod
    def get_devices(cls, type_dev=None):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata = cls._get_timedata()
        if not type_dev:
            return timedata.all_devices
        else:
            return timedata.get_devices_by_type(type_dev)

    @classmethod
    def add_bbb_info(cls, connections_dict=None):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata = cls._get_timedata()
        if connections_dict is None:
            from siriuspy import pwrsupply
            pwrsupply.bbbdata._LOCAL = _LOCAL
            connections_dict = pwrsupply.bbbdata.get_mapping()
        return timedata.add_bbb_info(connections_dict)

    @classmethod
    def add_crates_info(cls, connections_dict=None):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata = cls._get_timedata()
        if connections_dict is None:
            from siriuspy import diagnostics
            diagnostics.cratesdata._LOCAL = _LOCAL
            connections_dict = diagnostics.cratesdata.get_mapping()
        return timedata.add_crates_info(connections_dict)

    @classmethod
    def plot_network(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata = cls._get_timedata()
        return timedata.plot_network()
