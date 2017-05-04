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

from siriuspy import servweb as _web
from siriuspy.namesys import SiriusPVName as _PVName

_timeout = 1.0

class Events:
    HL2LL_MAP = {'Linac':0,  'InjBO':1,  'InjSI':2,  'RmpBO':3,  'RmpSI':4,
                 'DigLI':5,  'DigTB':6,  'DigBO':7,  'DigTS':8,  'DigSI':9,
                 'Orbit':10, 'Coupl':11, 'Tunes':12, 'Study':13, }
    LL2HL_MAP = {  val:key for key,val in HL2LL_MAP.items()  }


    LL_CODES    = list(range(50)) + list(range(80,120)) + list(range(160,256))

    MODES       = ('Disabled','Continuous','Injection','Single')
    DELAY_TYPES = ('Incr','Fixed')

    LL_TMP   = 'Event{0:02x}'
    HL_TMP   = 'Event{0:s}'
    HL_PREF  = 'AS-Glob:TI-Event:'


class Clocks:
    LL_TMP   = 'Clock{0:d}'
    HL_TMP   = 'Clock{0:d}'
    HL_PREF = 'AS-Glob:TI-Clock:'

    NUM = 8


class Triggers:
    STATES      = ('Dsbl','Enbl')
    POLARITIES  = ('Normal','Inverse')
    CLOCKS      = tuple([Clocks.HL_TMP.format(i) for i in range(Clocks.NUM)])


class IOs:
    LL_RGX = _re.compile('([OPTMFLHVESR]{2,3})([IO]{1,2})([0-9]{0,2})',_re.IGNORECASE)

    # defines the relations between input and output of the timing devices that are possible taking
    # into consideration only the devices architecture
    I2O_MAP = {
        'EVR':{
            'MFIO':(
                'OPTO00','OPTO00','OPTO00','OPTO03','OPTO04','OPTO05',
                'OPTO06','OPTO07','OPTO08','OPTO09','OPTO10','OPTO11',
                'MFO0','MFO1','MFO2','MFO3','MFO4','MFO5','MFO6','MFO7',
                ),
            },
        'EVE':{
            'MFIO':(
                'LVEO00','LVEO01','LVEO02','LVEO03','LVEO04','LVEO05','LVEO06','LVEO07','LVEO08',
                ),
            },
        'AFC':{
            'MFIO':(
                'OPTO00','OPTO00','OPTO00','OPTO03','OPTO04',
                'OPTO05','OPTO06','OPTO07','OPTO08','OPTO09',
                'LVEIO0','LVEIO1','LVEIO2','LVEIO3','LVEIO4','LVEIO5','LVEIO6','LVEIO7','LVEIO8',
                ),
            },
        'STDMOE':{
            'MFI0':('HVEO0',),
            'MFI1':('HVEO1',),
            'MFI2':('HVEO2',),
            'MFI3':('HVEO3',),
            },
        'STDSOE':{
            'OPTI0':('HVEO0',),
            'OPTI1':('HVEO1',),
            'OPTI2':('HVEO2',),
            'OPTI3':('HVEO3',),
            },
        'SOE':{
            'OPTI':('HVEO',),
            },
        'FOUT':{
            'MFIO':(
                'MFIO0','MFIO1','MFIO2','MFIO3','MFIO4','MFIO5','MFIO6','MFIO7',
                ),
            },
        'BBB':{
            'OPTI':('RSIO'),
            },
        'Crate':{
            'LVEIO0':('LVEIO0',),
            'LVEIO1':('LVEIO1',),
            'LVEIO2':('LVEIO2',),
            'LVEIO3':('LVEIO3',),
            'LVEIO4':('LVEIO4',),
            'LVEIO5':('LVEIO5',),
            'LVEIO6':('LVEIO6',),
            'LVEIO7':('LVEIO7',),
            },
        }

    O2I_MAP = dict()
    for dev, conns_ in I2O_MAP.items():
        dic_ = dict()
        O2I_MAP[dev] = dic_
        for conn1,conns in conns_.items():
            for conn2 in conns:
                dic_[conn2] = conn1

    @staticmethod
    def ios_meaning(conn=None):
        print(  '{0:13s} {1:s}'.format('Connection', 'Meaning')  )
        print(  '{0:13s} {1:s}'.format('MFIO', 'Multi Fibre Input/Output')  )
        print(  '{0:13s} {1:s}'.format('OPTIO', 'Optical Fibre Input/Output')  )
        print(  '{0:13s} {1:s}'.format('SRIO', 'RS485 Serial Network')  )
        print(  '{0:13s} {1:s}'.format('LVEIO', 'Low Voltage Eletric Input/Output')  )
        print(  '{0:13s} {1:s}'.format('HVEIO', 'High Voltage Eletric Input/Output')  )


_LOCAL = True
class _TimeDevData:
    """Class with mapping of Connection among timing devices and triggers receivers.

    Data are read from the Sirius web server.
    """
    _spacing_for_plot = 10

    def __init__(self, timeout=_timeout):
        self._conn_from_evg       = dict()
        self._conn_twrds_evg      = dict()
        self._devices_relations   = dict()
        self._top_chain_devs      = set()
        self._final_receiver_devs = set()
        self._all_devices         = set()
        self._hierarchy_map       = list()
        self._positions           = dict()
        self._colors              = dict()
        self._arrow_colors        = dict()
        if _web.server_online():
            if _LOCAL:
                with open('/home/fac_files/lnls-sirius/control-system-constants/'+
                          'timesys/timing-devices-connection.txt','r') as f:
                    text = f.read()
            else:
                text = _web.timing_devices_mapping(timeout=_timeout)
            self._parse_text_and_build_connection_mappings(text)
            self._update_related_maps()

    def _update_related_maps(self):
        self._top_chain_devs      = self._conn_from_evg.keys()  - self._conn_twrds_evg.keys()
        self._final_receiver_devs = self._conn_twrds_evg.keys() - self._conn_from_evg.keys()
        self._all_devices         = self._conn_from_evg.keys()  | self._conn_twrds_evg.keys()
        self._build_devices_relations()
        self._build_hierarchy_map()
        self._build_positions()
        self._build_colors()
        self._build_arrow_colors()

    def _get_dev_and_channel(self,txt):
        type_chan = num_chan = None
        txt = _PVName(txt)
        dev = txt.dev_name
        chan  = txt.propty.lower()
        reg_match = IOs.LL_RGX.findall(chan)
        if reg_match:
            type_chan, io_chan, num_chan = reg_match[0]
            return dev, chan, type_chan, num_chan

    def _parse_text_and_build_connection_mappings(self,text):
        from_evg = dict()
        twrds_evg = dict()
        lines = text.splitlines()
        for n,line in enumerate(lines,1):
            line = line.strip()
            if not line or line[0] == '#': continue # empty line
            out,inn,*_ = line.split()
            send, ochn, octyp, ocn = self._get_dev_and_channel(out)
            recv, ichn, ictyp, icn = self._get_dev_and_channel(inn)
            if not ochn or not ichn:
                print('No {0:s} channel defined in line {1:d}:\n\t {2:s}'.format(
                       'output' if not ochn else 'input', n,        line))
                return
            elif not octyp or not ictyp:
                print('Sintaxe error in definition of {0:s} channel in line {1:d}:\n\t {2:s}'.format(
                                        'output' if not octyp else 'input',   n,       line))
                return
            elif octyp != ictyp:
                print('Channel types do not match in line {0:d}:\n\t {1:s}'.format(n,line))
                return
            else:
                if send in from_evg.keys():
                    this_sen = from_evg[send]
                    if ochn in this_sen.keys():  this_sen[ochn] += (recv,ichn)
                    else:                        this_sen.update({ ochn : ((recv, ichn), ) }  )
                else:
                    from_evg[send] = { ochn : ((recv, ichn), ) }

                if recv in twrds_evg.keys():
                    this_recv = twrds_evg[recv]
                    if ichn in this_recv.keys():
                        print('Duplicate device input connection in line {0:d}:\n\t {1:s}'.format(n,line))
                        return
                    else:
                        this_recv.update(  { ichn : (send, ochn) }  )
                else:
                    twrds_evg[recv] =   { ichn : (send, ochn) }
        self._conn_from_evg   = from_evg
        self._conn_twrds_evg = twrds_evg

    def _build_devices_relations(self):
        simple_map = dict()
        for k,vs in self._conn_from_evg.items():
            devs = set()
            for v in vs.values(): devs.update([i[0] for i in v])
            simple_map[k] = devs
        self._devices_relations =  simple_map

    def _build_hierarchy_map(self):
        hierarchy = [self._top_chain_devs.copy(),]
        while True:
            vals = set()
            for k in hierarchy[-1]:
                vals |= self._devices_relations.get(k,set())
            if vals: hierarchy.append(vals)
            else:    break
        self._hierarchy_map = hierarchy

    def plot_network(self):
        if 'matplotlib' not in _sys.modules:
            print('Cannot draw network:matplotlib is not installed')
            return

        def on_motion(event):
            if event.inaxes is None: return
            ind = _np.argmin(  ( xs - event.xdata )**2  +  ( ys - event.ydata )**2  )
            pos = (xs[ind],ys[ind])
            txt.xy = pos
            txt.set_position(pos)
            txt.set_text(self._inv_positions[pos])
            f.canvas.draw()


        f  = _plt.figure(figsize=(20,20))
        f.canvas.mpl_connect('motion_notify_event',on_motion)
        gs = _gridspec.GridSpec(1, 1)
        gs.update(left=0.1,top=0.97,bottom=0.12,right=0.95,hspace=0.00,wspace=0.2)
        ax = _plt.subplot(gs[0,0])
        xs = _np.zeros(len(self._all_devices))
        ys = _np.zeros(len(self._all_devices))
        for i,dev in enumerate(sorted(self._all_devices)):
            xs[i], ys[i] = self._positions[dev]
            ax.plot(*self._positions[dev],color=self._colors[dev],marker='.',markersize = 8)

        txt = ax.annotate(s='',xy=(0.0,0.0),xycoords='data')

        kwargs = dict()
        for dev in sorted(self._devices_relations.keys()):
            conns = sorted(self._devices_relations[dev])
            for conn in conns:
                x  = self._positions[dev][0]
                y  = self._positions[dev][1]
                dx = self._positions[conn][0] - x
                dy = self._positions[conn][1] - y
                cor = self._arrow_colors[(dev,conn)]
                ax.arrow(x,y,dx,dy, fc=cor, ec=cor, length_includes_head=True)#,**kwargs)

    def _build_positions(self):
        pi2 = _math.pi*2
        dist = lambda x: self._spacing_for_plot/_math.sqrt(  2*( 1-_math.cos(x) )  )
        pol2cart = lambda x,y:(  x*_math.cos( (y[0]+y[1])/2 ),  x*_math.sin( (y[0]+y[1])/2 )   )

        nevgs = len(self._hierarchy_map[0])
        radia = [0]* len(self._hierarchy_map)
        radia[0] = 0 if nevgs == 1 else dist(pi2/nevgs)
        angles = dict()
        positions = dict()
        for i,dev in enumerate(self._hierarchy_map[0]):
            angles[dev] = ( i*pi2/nevgs, (i+1)*pi2/nevgs )
            positions[dev] = pol2cart(radia[0],angles[dev])

        #find angles and radia
        for n, devs in enumerate(self._hierarchy_map):
            min_ang = pi2
            for dev in devs:
                angi, angf = angles[dev]
                dang = angf-angi
                devs2 = self._devices_relations.get(dev,set())
                nr = len(devs2)
                min_ang = min(min_ang,dang,dang/nr if nr else min_ang)
                for i,dev2 in enumerate(devs2):
                    angles[dev2] = ( i*dang/nr + angi, (i+1)*dang/nr + angi)
            r = dist(min_ang)
            if n>0 and r <= radia[n-1]:
                radia[n] = 2*radia[n-1]
            else:
                radia[n] = r

        # get positions
        for n,devs in enumerate(self._hierarchy_map):
            for dev in devs:
                devs2 = self._devices_relations.get(dev,set())
                for i,dev2 in enumerate(devs2):
                    positions[dev2] = pol2cart(radia[n],angles[dev2])

        self._positions =  positions
        self._inv_positions = {xy:dev for dev,xy in positions.items()}

    def _build_colors(self):
        dev_types = set()
        for dev in self._all_devices:
            dev_types.add(_PVName(dev).dev_type)

        nr = len(dev_types)+2
        color_types = dict()
        for i, dev_type in  enumerate(sorted(dev_types),1):
            color_types[dev_type] = _cmap.spectral(i/nr)

        colors = dict()
        for dev in self._all_devices:
            colors[dev] = color_types[_PVName(dev).dev_type]

        self._colors = colors

    def _build_arrow_colors(self):
        chan_types = set()
        for conns in self._conn_from_evg.values():
            for chan in conns.keys():
                chan_type = IOs.LL_RGX.findall(chan)[0][0]
                chan_types.add(chan_type)

        nr = len(chan_types)+2
        color_types = dict()
        for i, chan_type in  enumerate(sorted(chan_types),1):
            color_types[chan_type] = _cmap.spectral(i/nr)

        colors = dict()
        for dev1,conns in self._conn_from_evg.items():
            for chan,devs in conns.items():
                chan_type = IOs.LL_RGX.findall(chan)[0][0]
                for dev2 in devs:
                    colors[(dev1,dev2[0])] = color_types[chan_type]

        self._arrow_colors = colors

    def add_crates_info(self,connections_dict):
        not_used = set()
        for crate, bpms in connections_dict.items():
            my_conns = self._conn_twrds_evg.get(crate)
            if my_conns is None:
                not_used.add(crate)
                continue
            for conn in my_conns.keys():
                for bpm in bpms:
                    self._add_entry_to_map(which_map='from', conn=conn, ele1=crate, ele2=bpm)
                    self._add_entry_to_map(which_map='twrds', conn=conn, ele1=bpm, ele2=crate)
        self._update_related_maps()
        return not_used

    def add_bbb_info(self,connections_dict):
        conn = 'SRIO'
        not_used = set()
        for bbb, pss in connections_dict.items():
            my_conns = self._conn_twrds_evg.get(bbb)
            if my_conns is None:
                not_used.add(bbb)
                continue
            for ps in pss:
                self._add_entry_to_map(which_map='from', conn=conn, ele1=bbb, ele2=ps)
                self._add_entry_to_map(which_map='twrds', conn=conn, ele1=ps, ele2=bbb)
        self._update_related_maps()
        return not_used

    def _add_entry_to_map(self, which_map, conn, ele1, ele2):
        mapp = self._conn_from_evg if which_map=='from' else self._conn_twrds_evg
        ele1_entry = mapp.get(ele1)
        if not ele1_entry:
            mapp[ele1] = {  conn:( (ele2,conn), )  }
        else:
            conn_entry = ele1_entry.get(conn)
            if not conn_entry:
                ele1_entry[conn]  = ((ele2,conn),)
            else:
                ele1_entry[conn] += ((ele2,conn),)

    def get_devices_by_type(self,type_dev):
        _pv_fun = lambda x,y: _PVName(x).dev_type.lower() == y.lower()
        return {  dev for dev in self._all_devices if _pv_fun(dev,type_dev) }

    @property
    def conn_from_evg(self): return _copy.deepcopy(self._conn_from_evg)

    @property
    def conn_twrds_evg(self): return _copy.deepcopy(self._conn_twrds_evg)

    @property
    def final_receivers(self): return _copy.deepcopy(self._final_receiver_devs)

    @property
    def top_chain_senders(self): return _copy.deepcopy(self._top_chain_devs)

    @property
    def relations_from_evg(self): return _copy.deepcopy(self._devices_relations)

    @property
    def hierarchy_list(self): return _copy.deepcopy(self._hierarchy_map)

    @property
    def all_devices(self): return _copy.deepcopy(self._all_devices)


class Connections:
    _timedata = None

    @classmethod
    def  _get_timedata(cls):
        # encapsulating _bbbdata within a function avoid creating the global object
        # (which is time consuming) at module load time.
        if cls._timedata is None:
            cls._timedata = _TimeDevData()
        return cls._timedata

    @classmethod
    def reset(cls):
        _timedata = _TimeDevData()

    @staticmethod
    def server_online():
        """Return True/False if Sirius web server is online."""
        return _web.server_online()

    @classmethod
    def get_connections_from_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata =  cls._get_timedata()
        return timedata.conn_from_evg

    @classmethod
    def get_connections_twrds_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata =  cls._get_timedata()
        return timedata.conn_twrds_evg

    @classmethod
    def get_top_chain_senders(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata =  cls._get_timedata()
        return timedata.top_chain_senders

    @classmethod
    def get_final_receivers(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata =  cls._get_timedata()
        return timedata.final_receivers

    @classmethod
    def get_relations_from_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata =  cls._get_timedata()
        return timedata.relations_from_evg

    @classmethod
    def get_hierarchy_list(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata =  cls._get_timedata()
        return timedata.hierarchy_list

    @classmethod
    def get_devices(cls, type_dev = None):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata =  cls._get_timedata()
        if not type_dev:
            return timedata.all_devices
        else:
            return timedata.get_devices_by_type(type_dev)

    @classmethod
    def add_bbb_info(cls, connections_dict = None):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata =  cls._get_timedata()
        if connections_dict is None:
            from siriuspy import pwrsupply
            connections_dict = pwrsupply.bbbdata.get_mapping()
        return timedata.add_bbb_info(connections_dict)

    @classmethod
    def add_crates_info(cls, connections_dict = None):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata =  cls._get_timedata()
        if connections_dict is None:
            from siriuspy import diagnostics
            connections_dict = diagnostics.cratesdata.get_mapping()
        return timedata.add_crates_info(connections_dict)

    @classmethod
    def plot_network(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        timedata =  cls._get_timedata()
        return timedata.plot_network()
