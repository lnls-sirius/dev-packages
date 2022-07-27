"""Define properties of all timing devices and their connections."""

import re as _re
from copy import deepcopy as _dcopy
from threading import Lock as _Lock

from .. import clientweb as _web
from ..namesys import SiriusPVName as _PVName, Filter as _Filter

from .bpms_search import BPMSearch as _BPMSearch
from .ps_search import PSSearch as _PSSearch

_TIMEOUT = 1.0


class LLTimeSearch:
    """Get the timing devices connections."""

    LLRegExp = _re.compile('([A-Z]+)([0-9]{0,2})', _re.IGNORECASE)

    # defines the relations between input and output of the timing devices.
    In2OutMap = {
        'EVG': {
            'UPLINK': (
                'OUT0', 'OUT1', 'OUT2', 'OUT3',
                'OUT4', 'OUT5', 'OUT6', 'OUT7',
                ),
            },
        'EVR': {
            'UPLINK': (
                'OTP0', 'OTP1', 'OTP2', 'OTP3', 'OTP4', 'OTP5',
                'OTP6', 'OTP7', 'OTP8', 'OTP9', 'OTP10', 'OTP11',
                'OTP12', 'OTP13', 'OTP14', 'OTP15', 'OTP16', 'OTP17',
                'OTP18', 'OTP19', 'OTP20', 'OTP21', 'OTP22', 'OTP23',
                'OUT0', 'OUT1', 'OUT2', 'OUT3',
                'OUT4', 'OUT5', 'OUT6', 'OUT7',
                ),
            },
        'EVE': {
            'UPLINK': (
                'OTP0', 'OTP1', 'OTP2', 'OTP3', 'OTP4', 'OTP5',
                'OTP6', 'OTP7', 'OTP8', 'OTP9', 'OTP10', 'OTP11',
                'OTP12', 'OTP13', 'OTP14', 'OTP15', 'OTP16', 'OTP17',
                'OTP18', 'OTP19', 'OTP20', 'OTP21', 'OTP22', 'OTP23',
                'OUT0', 'OUT1', 'OUT2', 'OUT3',
                'OUT4', 'OUT5', 'OUT6', 'OUT7',
                'RFOUT',
                ),
            },
        'AMCFPGAEVR': {
            'SFP8': (
                'FMC1CH1', 'FMC1CH2', 'FMC1CH3', 'FMC1CH4', 'FMC1CH5',
                'FMC2CH1', 'FMC2CH2', 'FMC2CH3', 'FMC2CH4', 'FMC2CH5',
                'CRT0', 'CRT1', 'CRT2', 'CRT3', 'CRT4',
                'CRT5', 'CRT6', 'CRT7',
                ),
            },
        'OEMultSFP': {
            'OE1': ('OUT1', ),
            'OE2': ('OUT2', ),
            'OE3': ('OUT3', ),
            'OE4': ('OUT4', ),
            },
        'OEMultPOF': {
            'IN1': ('OUT1', ),
            'IN2': ('OUT2', ),
            'IN3': ('OUT3', ),
            'IN4': ('OUT4', ),
            },
        'OESglPOF': {
            'IN': ('OUT', ),
            },
        'OESglSFP': {
            'INRX': ('OUT', 'INTX'),
            },
        'Fout': {
            'UPLINK': (
                'OUT0', 'OUT1', 'OUT2', 'OUT3',
                'OUT4', 'OUT5', 'OUT6', 'OUT7',
                ),
            },
        'UDC': {
            'SYNCIN': ('BCKPLN', 'SYNCOUT'),
            },
        'Crate': {
            'CRT0': ('CRT0', ),
            'CRT1': ('CRT1', ),
            'CRT2': ('CRT2', ),
            'CRT3': ('CRT3', ),
            'CRT4': ('CRT4', ),
            'CRT5': ('CRT5', ),
            'CRT6': ('CRT6', ),
            'CRT7': ('CRT7', ),
            },
        'OERFRx': {'OPTICALACP': ('SIGNAL', )},
        'OERFTx': {'SIGNAL': ('OPTICALACP', )},
        }
    In2OutMap['DIO'] = {
        'P{0:03d}'.format(i): ('P{0:03d}'.format(i), ) for i in range(110)}
    In2OutMap['DIO'].update({
        'P{0:02d}'.format(i): ('P{0:02d}'.format(i), ) for i in range(1, 25)})
    In2OutMap['DIO']['P052B'] = ('P052B', )
    In2OutMap['DIO']['P027B'] = ('P027B', )

    Out2InMap = dict()
    for dev, conns_ in In2OutMap.items():
        dic_ = dict()
        Out2InMap[dev] = dic_
        for conn1, conns in conns_.items():
            for conn2 in conns:
                dic_[conn2] = conn1
    del dev, conns_, dic_, conn1, conns, conn2  # cleanning class namespace.

    _conn_from_evg = dict()
    _conn_twds_evg = dict()
    _top_chain_devs = set()
    _final_receiver_devs = set()
    _all_devices = set()
    _trig_src_devs = set()
    _fout_devs = set()
    _evg_devs = set()
    _lock = _Lock()

    @classmethod
    def get_channel_input(cls, channel):
        """Get channel input method."""
        if not isinstance(channel, _PVName):
            channel = _PVName(channel)
        o2i = cls.Out2InMap.get(channel.dev)
        if o2i is None:
            return []
        conn = o2i.get(channel.propty)
        if conn is None:
            conn = cls.In2OutMap[channel.dev].get(channel.propty)
        if conn is None:
            return []
        elif isinstance(conn, str):
            conn = [conn, ]
        return [_PVName(channel.device_name + ':' + co) for co in conn]

    @classmethod
    def get_channel_output_port_pvname(cls, channel):
        if not isinstance(channel, _PVName):
            channel = _PVName(channel)
        outprt = channel.propty
        if outprt.startswith('FMC'):
            outprt = 'FMC' + outprt[3] + 'Ch{0:d}'.format(int(outprt[6])-1)
        elif outprt.startswith('CRT'):
            outprt = 'AMC' + outprt[3]
        elif outprt.startswith('OTP'):
            outprt = 'OTP{0:02d}'.format(int(outprt[3:]))
        return channel.substitute(propty=outprt)

    @classmethod
    def get_channel_internal_trigger_pvname(cls, channel):
        if not isinstance(channel, _PVName):
            channel = _PVName(channel)
        inttrig = channel.propty
        if inttrig.startswith('OUT'):
            inttrig = 'OTP{0:02d}'.format(12 + int(inttrig[-1]))
        elif inttrig.startswith(('FMC', 'CRT', 'OTP')):
            return cls.get_channel_output_port_pvname(channel)
        return channel.substitute(propty=inttrig)

    @classmethod
    def get_device_names(cls, filters=None, sorting=None):
        """
        Return a set with all devices of type type_dev.

        if type_dev is None, return all devices.
        """
        cls._get_timedata()
        return _Filter.process_filters(
                sorted(cls._all_devices), filters=filters, sorting=sorting)

    @classmethod
    def get_evg_name(cls):
        return cls.get_device_names({'dev': 'EVG'})[0]

    @classmethod
    def get_evg2fout_mapping(cls):
        fouts = cls.get_device_names({'dev': 'Fout'})
        link = list(cls.In2OutMap['Fout'])[0]
        mapp = dict()
        for fout in fouts:
            out = cls.get_evg_channel(fout.substitute(propty=link))
            mapp[out.propty] = fout.device_name
        return mapp

    @classmethod
    def get_triggersource_devices(cls):
        cls._get_timedata()
        return _dcopy(cls._trig_src_devs)

    @classmethod
    def get_trigsrc2fout_mapping(cls):
        cls._get_timedata()
        mapp = dict()
        for dev in cls._trig_src_devs:
            inp = list(cls.In2OutMap[dev.dev])[0]
            dev = dev.substitute(propty=inp)
            mapp[dev.device_name] = cls.get_fout_channel(dev)
        return mapp

    @classmethod
    def get_fout2trigsrc_mapping(cls):
        mapp = cls.get_trigsrc2fout_mapping()
        mapp2 = dict()
        for k, v in mapp.items():
            if v.device_name in mapp2:
                mapp2[v.device_name][v.propty] = k
            else:
                mapp2[v.device_name] = {v.propty: k}
        return mapp2

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
            lst_chan = cls.get_channel_input(up_chan)
            if not lst_chan:
                raise Exception('Channel ', up_chan, ' not in dictionary.')
            up_chan = list(twds_evg[lst_chan[0]])[0]
            up_channels.append(up_chan)
        return up_channels

    @classmethod
    def reset(cls):
        """Reset data to initial value."""
        cls._conn_from_evg = dict()
        cls._conn_twds_evg = dict()
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
        return _dcopy(cls._top_chain_devs)

    @classmethod
    def get_final_receivers(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        cls._get_timedata()
        return _dcopy(cls._final_receiver_devs)

    @classmethod
    def get_relations_from_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        cls._get_timedata()
        return _dcopy(cls._devs_from_evg)

    @classmethod
    def get_relations_twds_evg(cls):
        """Return a dictionary with the beaglebone to power supply mapping."""
        cls._get_timedata()
        return _dcopy(cls._devs_twds_evg)

    @classmethod
    def has_clock(cls, ll_trigger):
        name = _PVName(ll_trigger)
        if name.dev == 'AMCFPGAEVR':
            return True
        elif name.dev in {'EVR', 'EVE'}:
            return name.propty.startswith('OUT')
        else:
            raise Exception('Error: ' + name)

    @classmethod
    def has_delay_type(cls, ll_trigger):
        name = _PVName(ll_trigger)
        return name.dev in {'EVR', 'EVE'} and name.propty.startswith('OUT')

    @classmethod
    def get_trigger_name(cls, channel):
        chan_tree = cls.get_device_tree(channel)
        for up_chan in chan_tree:
            if up_chan.device_name in cls._trig_src_devs:
                return up_chan

    @classmethod
    def get_fout_channel(cls, channel):
        chan_tree = cls.get_device_tree(channel)
        for up_chan in chan_tree:
            if up_chan.device_name in cls._fout_devs:
                return up_chan

    @classmethod
    def get_evg_channel(cls, channel):
        chan_tree = cls.get_device_tree(channel)
        for up_chan in chan_tree:
            if up_chan.device_name in cls._evg_devs:
                return up_chan

    # --- private methods ---

    @classmethod
    def _add_entry_to_map(cls, which_map, conn, ele1, ele2):
        if which_map.lower().startswith('from'):
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
        with cls._lock:
            if cls._conn_from_evg:
                return
            if not _web.server_online():
                raise Exception('Could not connect with Consts Server!!')
            text = _web.timing_devices_mapping(timeout=_TIMEOUT)
            cls._parse_text_and_build_connection_mappings(text)
            cls._update_related_maps()

    # --- methods auxiliar to _get_timedata ---

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
            if out in from_evg.keys():
                from_evg[out] |= {inn}
            else:
                from_evg[out] = {inn}

            if inn in twds_evg.keys():
                print(
                    'Duplicate device input connection in line ' +
                    '{0:d}:\n\t {1:s}'.format(n, line))
                return
            else:
                twds_evg[inn] = {out}
        cls._conn_from_evg = from_evg
        cls._conn_twds_evg = twds_evg
        cls._add_udc_info()
        cls._add_crates_info()

    @classmethod
    def _add_crates_info(cls):
        """Add the information of Crate to BPMs to timing map."""
        conns = tuple(cls.In2OutMap['AMCFPGAEVR'].values())[0]
        conns = [v for v in conns if not v.startswith('FMC')]

        conn_dict = _BPMSearch.get_timing_mapping()
        used = set()
        twds_evg = _dcopy(cls._conn_twds_evg)
        for chan in twds_evg.keys():
            bpms = conn_dict.get(chan.device_name)
            if bpms is None:
                continue
            used.add(chan.device_name)
            for bpm in bpms:
                for conn in conns:
                    cls._add_entry_to_map(
                        which_map='from', conn=conn,
                        ele1=chan.device_name, ele2=bpm)
                    cls._add_entry_to_map(
                        which_map='twds', conn=conn,
                        ele1=bpm, ele2=chan.device_name)
        # print(conn_dict.keys() - used)

    @classmethod
    def _add_udc_info(cls):
        """Add the information of bbb to PS to timing map."""
        data = _PSSearch.get_udc_dict()
        conn_dict = {udc: [x[0] for x in bsmps] for udc, bsmps in data.items()}
        conn = list(cls.In2OutMap['UDC'].values())[0][0]
        used = set()
        twds_evg = _dcopy(cls._conn_twds_evg)
        for chan in twds_evg.keys():
            pss = conn_dict.get(chan.device_name)
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
        # print(conn_dict.keys() - used)

    @classmethod
    def _update_related_maps(cls):
        def _get_device_names(filters=None, sorting=None):
            return _Filter.process_filters(
                    sorted(cls._all_devices), filters=filters, sorting=sorting)

        cls._build_devices_relations()
        cls._top_chain_devs = (
            cls._devs_from_evg.keys() - cls._devs_twds_evg.keys())
        cls._final_receiver_devs = (
            cls._devs_twds_evg.keys() - cls._devs_from_evg.keys())
        cls._all_devices = (
            cls._devs_from_evg.keys() | cls._devs_twds_evg.keys())
        cls._trig_src_devs = set(
                _get_device_names({'dev': 'EVR'}) +
                _get_device_names({'dev': 'EVE'}) +
                _get_device_names({'dev': 'AMCFPGAEVR'}))
        cls._fout_devs = set(_get_device_names({'dev': 'Fout'}))
        cls._evg_devs = set(_get_device_names({'dev': 'EVG'}))

    @classmethod
    def _build_devices_relations(cls):
        simple_map = dict()
        for k, vs in cls._conn_from_evg.items():
            devs = {_PVName(v.device_name) for v in vs}
            devs |= simple_map.get(k.device_name, set())
            simple_map[_PVName(k.device_name)] = devs

        inv_map = dict()
        for k, vs in simple_map.items():
            for v in vs:
                devs = {k}
                devs |= inv_map.get(v, set())
                inv_map[v] = devs

        cls._devs_from_evg = simple_map
        cls._devs_twds_evg = inv_map
