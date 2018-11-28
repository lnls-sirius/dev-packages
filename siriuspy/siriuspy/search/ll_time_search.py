"""Define properties of all timing devices and their connections."""

import re as _re
from copy import deepcopy as _dcopy

from siriuspy import servweb as _web
from siriuspy.namesys import Filter as _Filter
from siriuspy.namesys import SiriusPVName as _PVName

from siriuspy.search.bpms_search import BPMSearch as _BPMSearch
from siriuspy.search.ps_search import PSSearch as _PSSearch

_timeout = 1.0


class LLTimeSearch:
    """Get the timing devices connections."""

    ll_rgx = _re.compile('([A-Z]+)([0-9]{0,2})', _re.IGNORECASE)

    # defines the relations between input and output of the timing devices
    # that are possible taking into consideration only the devices architecture
    i2o_map = {
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
                'OUT0', 'OUT1', 'OUT2', 'OUT3',
                'OUT4', 'OUT5', 'OUT6', 'OUT7',
                ),
            },
        'EVE': {
            'UPLINK': (
                'OTP0', 'OTP1', 'OTP2', 'OTP3', 'OTP4', 'OTP5',
                'OTP6', 'OTP7', 'OTP8', 'OTP9', 'OTP10', 'OTP11',
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
        'PSCtrl': {
            'TIMIN': ('RS485',),
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
    i2o_map['FibPatch'] = {
        'P{0:03d}'.format(i): ('P{0:03d}'.format(i), ) for i in range(100)}
    i2o_map['FibPatch']['P052B'] = ('P052B', )

    o2i_map = dict()
    for dev, conns_ in i2o_map.items():
        dic_ = dict()
        o2i_map[dev] = dic_
        for conn1, conns in conns_.items():
            for conn2 in conns:
                dic_[conn2] = conn1
    del(dev, conns_, dic_, conn1, conns, conn2)  # cleanning class namespace.

    _conn_from_evg = dict()
    _conn_twds_evg = dict()
    _top_chain_devs = set()
    _final_receiver_devs = set()
    _all_devices = set()

    @classmethod
    def get_channel_input(cls, channel):
        """Get channel input method."""
        if not isinstance(channel, _PVName):
            channel = _PVName(channel)
        o2i = cls.o2i_map.get(channel.dev)
        if o2i is None:
            return []
        conn = o2i.get(channel.propty)
        if conn is None:
            conn = cls.i2o_map[channel.dev].get(channel.propty)
        if conn is None:
            return []
        elif isinstance(conn, str):
            conn = [conn, ]
        return [_PVName(channel.device_name + ':' + co) for co in conn]

    @classmethod
    def get_device_names(cls, filters=None, sorting=None):
        """
        Return a set with all devices of type type_dev.

        if type_dev is None, return all devices.
        """
        cls._get_timedata()
        return _Filter.process_filters(
                            cls._all_devices, filters=filters, sorting=sorting)

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
            up_chan = cls.get_channel_input(up_chan)[0]
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

    # ############ Auxiliar methods ###########
    @classmethod
    def _add_entry_to_map(cls, which_map, conn, ele1, ele2):
        cls._get_timedata()
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
            _, ochn, octyp, _ = cls._get_dev_and_channel(out)
            _, ichn, ictyp, _ = cls._get_dev_and_channel(inn)
            if not ochn or not ichn:
                print('No {0:s} channel defined in line {1:d}:\n\t {2:s}'
                      .format('output' if not ochn else 'input', n, line))
                return
            elif not octyp or not ictyp:
                print('Sintax error in definition of ' +
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
        cls._add_bbb_info()
        cls._add_crates_info()

    @classmethod
    def _add_crates_info(cls):
        """Add the information of Crate to BPMs to timing map."""
        conns = tuple(cls.i2o_map['AMCFPGAEVR'].values())[0]
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
        print(conn_dict.keys() - used)

    @classmethod
    def _add_bbb_info(cls):
        """Add the information of bbb to PS to timing map."""
        data = _PSSearch.get_bbbname_dict()
        conn_dict = {bbb: [x[0] for x in bsmps] for bbb, bsmps in data.items()}
        conn = list(cls.i2o_map['PSCtrl'].values())[0][0]
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
        print(conn_dict.keys() - used)

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
            cls._devs_from_evg.keys() - cls._devs_twds_evg.keys())
        cls._final_receiver_devs = (
            cls._devs_twds_evg.keys() - cls._devs_from_evg.keys())
        cls._all_devices = (
            cls._devs_from_evg.keys() | cls._devs_twds_evg.keys())

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

        cls._devs_from_evg = simple_map
        cls._devs_twds_evg = inv_map
