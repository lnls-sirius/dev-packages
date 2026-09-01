"""Oscilloscopes and scope signals."""


import socket as _socket

import numpy as _np


class ScopeSignals:
    """Mapping of physical signals to scope channels."""

    SI_FILL_PATTERN = ('SI_FILL_PATTERN', 'AS_DI_FPMDIG', 'channel1')
    BO_FILL_PATTERN = ('BO_FILL_PATTERN', 'AS_DI_FPMDIG', 'channel4')

    TS_EJESEPTG_PULSE = ('TS_EJESEPTG_PULSE', 'TS_PU_OSC_EJEBO', 'channel1')
    TS_EJESEPTF_PULSE = ('TS_EJESEPTF_PULSE', 'TS_PU_OSC_EJEBO', 'channel2')
    BO_EJEKCKR_PULSE = ('BO_EJEKCKR_PULSE', 'TS_PU_OSC_EJEBO', 'channel3')
    SI_PINGV_PULSE = ('SI_PINGV_PULSE', 'TS_PU_OSC_EJEBO', 'channel4')

    LI_ICT1 = ('LI_ICT1', 'LI_DI_ICTOSC', 'channel1')
    LI_ICT2 = ('LI_ICT2', 'LI_DI_ICTOSC', 'channel2')
    TB_ICT1 = ('TB_ICT1', 'LI_DI_ICTOSC', 'channel3')
    TB_ICT2 = ('TB_ICT2', 'LI_DI_ICTOSC', 'channel4')

    TB_FCT = ('TB_FCT', 'AS_DI_FCTDIG', 'channel1')
    TS_FCT = ('TS_FCT', 'AS_DI_FCTDIG', 'channel2')
    TS_ICT1 = ('TS_ICT1', 'AS_DI_FCTDIG', 'channel3')
    TS_ICT2 = ('TS_ICT2', 'AS_DI_FCTDIG', 'channel4')

    MODLTR1_PULSE = ('MODLTR1_PULSE', 'LI_PU_OSC_MODLTR', 'channel1')
    MODLTR2_PULSE = ('MODLTR2_PULSE', 'LI_PU_OSC_MODLTR', 'channel3')

    @staticmethod
    def get_scopesignal(scopesignal):
        """."""
        if isinstance(scopesignal, str):
            scopesignal = getattr(ScopeSignals, scopesignal, None)
        return scopesignal

    @staticmethod
    def get_scopesignal_string(scopesignal):
        """."""
        scopesignal = ScopeSignals.get_scopesignal(scopesignal)
        return scopesignal[0] if scopesignal else None

    @staticmethod
    def get_scopename(scopesignal):
        """."""
        scopesignal = ScopeSignals.get_scopesignal(scopesignal)
        return scopesignal[1] if scopesignal else None

    @staticmethod
    def get_channel(scopesignal):
        """."""
        scopesignal = ScopeSignals.get_scopesignal(scopesignal)
        return scopesignal[2] if scopesignal else None


class Scope:
    """Configuration for an oscilloscope.

    Stores the connection parameters and channel signal mapping for
    an oscilloscope, along with the measurement statistics settings
    to be used.
    """

    def __init__(
        self,
        ipaddr,
        hostname,
        port,
        scopename=None,
        channel1=None,
        channel2=None,
        channel3=None,
        channel4=None,
        stats_fields=None,
    ):
        """Initialize the Scope instance.

        If scopename is provided, channel1..4 are first automatically
        mapped from ScopeSignals. Any of channel1..4 passed explicitly
        overrides the corresponding automatic mapping.

        Args:
            ipaddr (str): IP address used to connect to the oscilloscope.
            hostname (str): Hostname of the oscilloscope.
            port (int): Port used to connect to the oscilloscope.
            scopename (str, optional): Name of the scope, used to
                automatically map channel1..4 from ScopeSignals.
                Defaults to None.
            channel1 (str, optional): Name of the signal connected to
                channel 1. Overrides the automatic mapping, if
                provided. Defaults to None.
            channel2 (str, optional): Name of the signal connected to
                channel 2. Overrides the automatic mapping, if
                provided. Defaults to None.
            channel3 (str, optional): Name of the signal connected to
                channel 3. Overrides the automatic mapping, if
                provided. Defaults to None.
            channel4 (str, optional): Name of the signal connected to
                channel 4. Overrides the automatic mapping, if
                provided. Defaults to None.
            stats_fields (tuple, optional): Measurement statistics to
                be collected. Defaults to None.
        """
        self.ipaddr = ipaddr
        self.hostname = hostname
        self.port = port
        self.scopename = scopename
        (
            self.channel1,
            self.channel2,
            self.channel3,
            self.channel4,
        ) = self._configure_channels(channel1, channel2, channel3, channel4)
        r = self._get_valid_channels()
        self.valid_channels = r
        self.stats_fields = stats_fields

    def __str__(self):
        """."""
        strs = ''
        strs += f'{"scopename":<10s}: {self.scopename}'
        strs += f'\n{"ipaddr":<10s}: {self.ipaddr}'
        strs += f'\n{"hostname":<10s}: {self.hostname}'
        strs += f'\n{"port":<10s}: {self.port}'
        strs += f'\n{"channel1":<10s}: {self.channel1}'
        strs += f'\n{"channel2":<10s}: {self.channel2}'
        strs += f'\n{"channel3":<10s}: {self.channel3}'
        strs += f'\n{"channel4":<10s}: {self.channel4}'
        strs += f'\n{"stats":<10s}: {self.stats_fields}'
        return strs

    def _configure_channels(self, channel1, channel2, channel3, channel4):
        """."""
        signals = (
            v
            for k, v in vars(ScopeSignals).items()
            if not k.startswith('_') and isinstance(v, tuple)
        )
        mapping = {
            channel: scopesignal
            for scopesignal, scopename, channel in signals
            if scopename == self.scopename
        }
        channel1 = channel1 or mapping.get('channel1')
        channel2 = channel2 or mapping.get('channel2')
        channel3 = channel3 or mapping.get('channel3')
        channel4 = channel4 or mapping.get('channel4')
        return channel1, channel2, channel3, channel4

    def _get_valid_channels(self):
        all_channels = (f'channel{idx}' for idx in range(1, 5))
        valid_channels = list(
            channel
            for channel in all_channels
            if getattr(self, channel) is not None
        )
        return valid_channels

    def _process_meas(self, meas):
        """."""
        meas = meas.split(',')
        stat_dict = dict()

        # Check if measurement for each ICT has the length we expect:
        flds = self.stats_fields
        if not flds:
            errmsg = 'Stats field not defined. Unable to proccess measurement.'
            raise ValueError(errmsg)
        if len(meas) % (1 + len(flds)):
            errmsg = 'Measurement list size does not match required length.'
            raise ValueError(errmsg)

        nr_stats = len(meas) // (1 + len(flds))
        stat_splits = _np.array_split(meas, nr_stats)
        for stat_split in stat_splits:
            stats = list(float(val) for val in stat_split[1:])
            dct = dict(zip(flds, stats))  # ruff: ignore[zip-without-explicit-strict]
            stat_dict[stat_split[0]] = dct
        return stat_dict


class Keysight(Scope):
    """"."""

    SOCKET_TIMEOUT = 10  # [s]

    STATS_FIELDS1 = ('CURR', 'STT', 'MIN', 'MAX', 'AVG', 'STD', 'COUNT')
    STATS_FIELDS2 = ('CURR', 'MIN', 'MAX', 'AVG', 'STD', 'COUNT')

    def __init__(self, *args, **kwargs):
        """."""
        Scope.__init__(self, *args, **kwargs)
        self._socket = None
        self.channels_scales = {}

    def connect(self):
        """Connect to the oscilloscope."""
        self._socket = _socket.socket(
            _socket.AF_INET,  # Internet
            _socket.SOCK_STREAM,  # TCP
        )
        self._socket.settimeout(Keysight.SOCKET_TIMEOUT)
        self._socket.connect((self.ipaddr, self.port))

    def disconnect(self):
        """."""
        if self._socket:
            self._socket.close()
            self._socket = None

    def read_meas(self):
        """Get the measurements from the oscilloscope."""
        meas = self._send_cmd(b":MEASure:RESults?\n")
        if meas:
            meas = self._process_meas(meas)
            return meas
        else:
            return None

    def select_channel(self, channel):
        """Select the channel for waveform acquisition."""
        if channel not in self.valid_channels:
            raise ValueError('Invalid channel name "{}"'.format(channel))
        chan = channel.replace('channel', 'CHAN')
        self._send_cmd(
            b':WAVeform:SOURce ' + chan.encode('ascii') + b'\n',
            get_res=False,
        )

    def read_channel_scales(self, channel):
        """Read the scales for the selected channel."""
        self.select_channel(channel)
        xinc = self._send_cmd(b":WAVeform:XINCrement?\n")
        yinc = self._send_cmd(b":WAVeform:YINCrement?\n")
        yor = self._send_cmd(b":WAVeform:YORigin?\n")
        xinc = float(xinc) if xinc else None
        yinc = float(yinc) if yinc else None
        yor = float(yor) if yor else None
        scales = (xinc, yinc, yor)
        if None in scales:
            raise ValueError('None returned in read_all_channel_scales')
        return scales

    def update_channel_scales(self, channel):
        """Update the scales for the selected channel."""
        scales = self.read_channel_scales(channel)
        self.channels_scales[channel] = scales

    def update_all_channels_scales(self):
        """Read the scales for all channels."""
        self.channels_scales = {}
        for channel in self.valid_channels:
            self.update_channel_scales(channel)

    def config_acq_wfm(self):
        """Configure the oscilloscope for waveform acquisition."""
        idn = self._send_cmd(b'*IDN?\r\n')  # needed ?
        self._send_cmd(b":WAVeform:FORMat WORD\n", get_res=False)
        self._send_cmd(b":WAVeform:BYTeorder MSBF\n", get_res=False)
        return idn

    def init_wfm(self):
        """Initialize the oscilloscope for waveform acquisition."""
        self.config_acq_wfm()
        if not self.channels_scales:
            self.update_all_channels_scales()

    def read_header_wfm(self):
        """Read the header of the waveform data."""
        if not self._socket:
            raise ValueError('socket is None')
        marker = self._recv_cmd(1)
        if marker != b'#':
            raise RuntimeError(
                f'Esperava "#", recebi {repr(marker)}')
        num = int(self._recv_cmd(1).decode('ascii'))
        datanum = int(self._recv_cmd(num).decode('ascii'))
        return datanum

    def read_raw_wfm(self):
        """Read the raw waveform data from the oscilloscope."""
        self._send_cmd(b":WAVeform:STReaming OFF\n", get_res=False)
        self._send_cmd(b":WAVeform:DATA?\n", get_res=False)
        datanum = self.read_header_wfm()
        dataraw = b''
        while len(dataraw) < datanum:
            datasize = datanum - len(dataraw)
            dataraw += self._recv_cmd(datasize)
        # consome '\n' final
        self._recv_cmd(1)
        return dataraw

    def read_channel_wfm(self, channel):
        """Read waveform data from a specific channel."""
        self.select_channel(channel)
        dataraw = self.read_raw_wfm()
        xinc, yinc, yor = self.channels_scales[channel]
        datax, datay = self._process_scales_wfm(dataraw, yinc, yor, xinc)
        return datax, datay

    def read_wfm(self, channels=None):
        """Read waveform data from channels."""
        channels = channels or self.valid_channels
        waveforms = {}
        for channel in channels:
            datax, datay = self.read_channel_wfm(channel)
            signal = getattr(self, channel)
            waveforms[signal] = (datax, datay)
        return waveforms

    def acquire(self, acq_meas=False, acq_wfms=False):
        """Acquire waveform data from all channels."""
        meas = list()
        wfms = dict()
        try:
            self.connect()
            if acq_meas:
                meas = self.read_meas()
            if acq_wfms:
                self.init_wfm()
                wfms = self.read_wfm()
        finally:
            self.disconnect()

        return meas, wfms

    @staticmethod
    def _process_scales_wfm(dataraw, yinc, yor, xinc):
        """Process the raw waveform data into x and y arrays."""
        dataraw = dataraw[0:-1]
        va1 = _np.array(list(dataraw)[0::2])
        va0 = _np.array(list(dataraw)[1::2])
        va1 = va1[:va0.size]
        datay = ((va1 << 8) + va0 - 2**16*(va1 >> 7)) * yinc + yor
        datax = _np.arange(datay.size) * xinc
        return datax, datay

    def _send_cmd(self, cmd, get_res=True):
        """."""
        if self._socket:
            self._socket.sendall(cmd)
            if get_res:
                return self._recv_cmd(1024).decode('ascii')
        return None

    def _recv_cmd(self, nrbytes):
        """."""
        if self._socket:
            return self._socket.recv(nrbytes)
        else:
            raise ValueError('Communication socket is None!')


class Scopes:
    """Keysight oscilloscopes names and IPs."""

    AS_DI_FCTDIG = Scope(
        ipaddr='10.128.150.22',
        hostname='AS-DI-FCTDig.lnls-sirius.com.br',
        port=5025,
        scopename='AS_DI_FCTDIG',
        stats_fields=None,
    )
    AS_DI_FPMDIG = Scope(
            ipaddr='10.128.150.21',
            hostname='AS-DI-FPMDig.lnls-sirius.com.br',
            port=5025,
            scopename='AS_DI_FPMDIG',
            stats_fields=None,
    )
    LI_DI_ICTOSC = Keysight(
        ipaddr='10.128.1.150',
        hostname='li-di-ictosc.lnls-sirius.com.br',
        port=5025,
        scopename='LI_DI_ICTOSC',
        stats_fields=Keysight.STATS_FIELDS1,
    )
    LI_PU_OSC_MODLTR = Scope(
            ipaddr='10.128.150.20',
            hostname='KEYSIGH-QQI8MNR.abtlus.org.br',
            port=5025,
            scopename='LI_PU_OSC_MODLTR',
            stats_fields=None,
    )
    TB_PU_OSC_INJBO = Scope(
        ipaddr='10.128.101.70',
        hostname='TB-PU-Osc-InjBO.abtlus.org.br',
        port=5025,
        scopename='TB_PU_OSC_INJBO',
        stats_fields=None,
    )
    TS_PU_OSC_EJEBO = Scope(
        ipaddr='10.128.120.70',
        hostname='TS-PU-Osc-EjeBO.abtlus.org.br',
        port=5025,
        scopename='TS_PU_OSC_EJEBO',
        stats_fields=None,
    )
    SI_PU_OSC_INJSI = Scope(
            ipaddr='10.128.101.71',
            hostname='SI-PU-Osc-InjSI.abtlus.org.br',
            port=5025,
            scopename='SI_PU_OSC_INJSI',
            stats_fields=None,
    )

    @staticmethod
    def get_scope(scopesignal):
        """."""
        if isinstance(scopesignal, str):
            scopesignal = getattr(ScopeSignals, scopesignal)
        scopename = scopesignal[1]
        return getattr(Scopes, scopename)
