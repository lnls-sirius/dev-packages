"""Oscilloscopes and scope signals."""


import base64 as _base64
import functools as _functools
import lzma as _lzma
import socket as _socket


import numpy as _np


class ScopeSignals:
    """Mapping of physical signals to scope channels."""

    TB_FCT = ('TB_FCT', 'AS_DI_FCT', 'channel1')
    TS_FCT = ('TS_FCT', 'AS_DI_FCT', 'channel2')
    TS_ICT1 = ('TS_ICT1', 'AS_DI_FCT', 'channel3')
    TS_ICT2 = ('TS_ICT2', 'AS_DI_FCT', 'channel4')

    SI_FILL = ('SI_FILL', 'AS_DI_FPM', 'channel1')
    BO_FILL = ('BO_FILL', 'AS_DI_FPM', 'channel4')

    LI_ICT1 = ('LI_ICT1', 'LI_DI_ICT', 'channel1')
    LI_ICT2 = ('LI_ICT2', 'LI_DI_ICT', 'channel2')
    TB_ICT1 = ('TB_ICT1', 'LI_DI_ICT', 'channel3')
    TB_ICT2 = ('TB_ICT2', 'LI_DI_ICT', 'channel4')

    LI_MODLTR1 = ('LI_MODLTR1', 'LI_PU_MODLTR', 'channel1')
    LI_MODLTR2 = ('LI_MODLTR2', 'LI_PU_MODLTR', 'channel3')

    TB_INJSEPT = ('TB_INJSEPT', 'TB_PU_INJBO', 'channel1')
    BO_INJKCKR = ('BO_INJKCKR', 'TB_PU_INJBO', 'channel3')

    TS_EJESEPTG = ('TS_EJESEPTG', 'TS_PU_EJEBO', 'channel1')
    TS_EJESEPTF = ('TS_EJESEPTF', 'TS_PU_EJEBO', 'channel2')
    BO_EJEKCKR = ('BO_EJEKCKR', 'TS_PU_EJEBO', 'channel3')
    SI_PINGERV = ('SI_PINGERV', 'TS_PU_EJEBO', 'channel4')

    SI_INJSEPG2 = ('SI_INJSEPG2', 'SI_PU_INJBO', 'channel1')
    SI_INJSEPG1 = ('SI_INJSEPG1', 'SI_PU_INJBO', 'channel2')
    SI_INJSEPF = ('SI_INJSEPF', 'SI_PU_INJBO', 'channel3')

    @staticmethod
    def get_scopesignal(scopesignal):
        """Resolve a scope signal to its definition tuple.

        Args:
            scopesignal (str or tuple): Name of a class attribute
                defined in ScopeSignals (e.g. 'LI_ICT1'), or an
                already-resolved signal tuple.

        Returns:
            tuple or None: The signal tuple in the form
            (signal_name, scopename, channel), or None if
            scopesignal is a string that does not match any
            attribute.
        """
        if isinstance(scopesignal, str):
            scopesignal = getattr(ScopeSignals, scopesignal, None)
        return scopesignal

    @staticmethod
    def get_scopesignal_string(scopesignal):
        """Return the signal name string from a scope signal.

        Args:
            scopesignal (str or tuple): Signal name or signal tuple,
                as accepted by get_scopesignal.

        Returns:
            str or None: The signal name (first element of the
            tuple), or None if the signal could not be resolved.
        """
        scopesignal = ScopeSignals.get_scopesignal(scopesignal)
        return scopesignal[0] if scopesignal else None

    @staticmethod
    def get_scopename(scopesignal):
        """Return the scope name associated with a scope signal.

        Args:
            scopesignal (str or tuple): Signal name or signal tuple,
                as accepted by get_scopesignal.

        Returns:
            str or None: The scope name (second element of the
            tuple, e.g. 'LI_DI_ICT'), or None if the signal could
            not be resolved.
        """
        scopesignal = ScopeSignals.get_scopesignal(scopesignal)
        return scopesignal[1] if scopesignal else None

    @staticmethod
    def get_channel(scopesignal):
        """Return the channel associated with a scope signal.

        Args:
            scopesignal (str or tuple): Signal name or signal tuple,
                as accepted by get_scopesignal.

        Returns:
            str or None: The channel name (third element of the
            tuple, e.g. 'channel1'), or None if the signal could not
            be resolved.
        """
        scopesignal = ScopeSignals.get_scopesignal(scopesignal)
        return scopesignal[2] if scopesignal else None


def _ensure_connection(func):
    """Ensure the socket is connected before executing the method."""
    @_functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        was_connected = self._socket is not None
        if not was_connected:
            self.connect()
        try:
            return func(self, *args, **kwargs)
        finally:
            if not was_connected:
                self.disconnect()
    return wrapper


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
        model=None,
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
            model (str, optional): Model name of the oscilloscope.
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
        self.model = model
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
        """Return a human-readable summary of the scope configuration.

        Returns:
            str: Multi-line string listing scopename, ipaddr,
            hostname, port, channel1..4 and stats_fields.
        """
        strs = ''
        strs += f'{"scopename":<15s}: {self.scopename}'
        strs += f'\n{"ipaddr":<15s}: {self.ipaddr}'
        strs += f'\n{"hostname":<15s}: {self.hostname}'
        strs += f'\n{"port":<15s}: {self.port}'
        strs += f'\n{"channel1":<15s}: {self.channel1}'
        strs += f'\n{"channel2":<15s}: {self.channel2}'
        strs += f'\n{"channel3":<15s}: {self.channel3}'
        strs += f'\n{"channel4":<15s}: {self.channel4}'
        strs += f'\n{"stats_fields":<15s}: {self.stats_fields}'
        return strs

    @staticmethod
    def setup_compress(dataraw):
        """Compress a raw setup block for storage or transmission."""
        if isinstance(dataraw, str):
            dataraw = dataraw.encode()
        dataraw_compressed = _base64.b64encode(
            _lzma.compress(dataraw, preset=9)
        ).decode()
        return dataraw_compressed

    @staticmethod
    def setup_decompress(dataraw_compressed):
        """Decompress a compressed setup block."""
        return _lzma.decompress(_base64.b64decode(dataraw_compressed))

    def _configure_channels(self, channel1, channel2, channel3, channel4):
        """Resolve channel1..4, combining explicit values with ScopeSignals.

        For each channel not explicitly provided, looks up
        ScopeSignals for a signal tuple whose scope name matches
        self.scopename and whose channel matches, using its signal
        name as the value.

        Args:
            channel1 (str, optional): Explicit value for channel 1.
            channel2 (str, optional): Explicit value for channel 2.
            channel3 (str, optional): Explicit value for channel 3.
            channel4 (str, optional): Explicit value for channel 4.

        Returns:
            tuple: (channel1, channel2, channel3, channel4), with
            explicit values taking precedence over the automatic
            mapping.
        """
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
        """List the channels that have a signal assigned.

        Returns:
            list of str: Names of channel1..4 attributes (e.g.
            'channel1') whose value is not None.
        """
        all_channels = (f'channel{idx}' for idx in range(1, 5))
        valid_channels = list(
            channel
            for channel in all_channels
            if getattr(self, channel) is not None
        )
        return valid_channels

    def _process_meas(self, meas):
        """Parse a raw measurement string returned by the oscilloscope.

        Expects meas as a comma-separated string formed by one or
        more repeated groups, each with a label followed by one
        value per entry in self.stats_fields, e.g.
        'LABEL1,v1,v2,...,LABEL2,v1,v2,...'.

        Args:
            meas (str): Raw comma-separated measurement string as
                returned by the oscilloscope.

        Returns:
            dict: Mapping of each label to a dict of
            {stats_field: value}, with values converted to float.

        Raises:
            ValueError: If self.stats_fields is not defined, or if
                the number of comma-separated values in meas is not
                a multiple of (1 + len(self.stats_fields)).
        """
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
    """Oscilloscope driver for Keysight instruments.

    Extends Scope with socket-based SCPI communication to connect,
    read measurement statistics, and acquire raw waveform data.
    """

    SOCKET_TIMEOUT = 10  # [s]

    STATS_FIELDS1 = ('CURR', 'MEAN', 'MIN', 'MAX', 'RANGE', 'STD', 'COUNT')

    def __init__(self, *args, **kwargs):
        """Initialize the Keysight instance.

        Args:
            *args: Positional arguments forwarded to Scope.__init__.
            **kwargs: Keyword arguments forwarded to Scope.__init__.
        """
        Scope.__init__(self, *args, **kwargs)
        self._socket = None
        self.channels_scales = {}

    def connect(self):
        """Open a TCP socket connection to the oscilloscope."""
        self._socket = _socket.socket(
            _socket.AF_INET,  # Internet
            _socket.SOCK_STREAM,  # TCP
        )
        self._socket.settimeout(Keysight.SOCKET_TIMEOUT)
        self._socket.connect((self.ipaddr, self.port))

    def disconnect(self):
        """Close the TCP socket connection to the oscilloscope, if open."""
        if self._socket:
            self._socket.close()
            self._socket = None

    @_ensure_connection
    def get_identification(self):
        """Query and return the identification string (*IDN?) from the scope.

        Returns:
            str or None: Instrument identification response (e.g.
            'KEYSIGHT TECHNOLOGIES,DSOS104A,MY12345678,06.74.01101'),
            or None if no response was received.
        """
        return self._cmd_send(b"*IDN?\n")

    @_ensure_connection
    def channel_select(self, channel):
        """Select the channel to be used for waveform acquisition.

        Assumes a connection is already open (see connect()).

        Args:
            channel (str): Channel name, e.g. 'channel1'. Must be
                one of self.valid_channels.

        Raises:
            ValueError: If channel is not in self.valid_channels.
        """
        if channel not in self.valid_channels:
            raise ValueError('Invalid channel name "{}"'.format(channel))
        chan = channel.replace('channel', 'CHAN').encode('ascii')
        self._cmd_send(b':WAVeform:SOURce ' + chan + b'\n', get_res=False)

    @_ensure_connection
    def scales_read(self, channel):
        """Read the x/y scaling factors for the given channel.

        Selects the channel and queries the oscilloscope for the
        waveform increment and origin values needed to convert raw
        samples into physical units. Assumes a connection is
        already open (see connect()).

        Args:
            channel (str): Channel name, e.g. 'channel1'.
            force_update_scale (bool, optional): If True, re-reads the
                scaling factors for this channel even if already cached.

        Returns:
            tuple: (xinc, yinc, yor), the x increment, y increment
            and y origin reported by the oscilloscope.

        Raises:
            ValueError: If any of xinc, yinc or yor could not be
                read.
        """
        self.channel_select(channel)
        xinc = self._cmd_send(b":WAVeform:XINCrement?\n")
        yinc = self._cmd_send(b":WAVeform:YINCrement?\n")
        yor = self._cmd_send(b":WAVeform:YORigin?\n")
        xinc = float(xinc) if xinc else None
        yinc = float(yinc) if yinc else None
        yor = float(yor) if yor else None
        scales = (xinc, yinc, yor)
        if None in scales:
            raise ValueError('None returned in read_all_channel_scales')
        self.channels_scales[channel] = scales
        return scales

    @_ensure_connection
    def scales_update_all(self):
        """Read and store the x/y scales for all valid channels.

        Assumes a connection is already open (see connect()).
        """
        self.channels_scales = {}
        for channel in self.valid_channels:
            self.scales_read(channel)

    @_ensure_connection
    def wfm_config(self):
        """Configure the oscilloscope for waveform data acquisition.

        Sets the waveform data format to 16-bit words with
        most-significant-byte-first ordering. Assumes a connection
        is already open (see connect()).

        Returns:
            str: The instrument identification string (*IDN?)
            response.
        """
        self._cmd_send(b":WAVeform:FORMat WORD\n", get_res=False)
        self._cmd_send(b":WAVeform:BYTeorder MSBF\n", get_res=False)

    @_ensure_connection
    def wfm_read_raw(self):
        """Read the raw waveform data block from the oscilloscope.

        Assumes a connection is already open (see connect()).

        Returns:
            bytes: Raw waveform data, as returned by the
            oscilloscope (16-bit words, MSB-first).
        """
        self._cmd_send(b":WAVeform:STReaming OFF\n", get_res=False)
        self._cmd_send(b":WAVeform:DATA?\n", get_res=False)
        datanum = self._read_block_header()
        dataraw = b''
        while len(dataraw) < datanum:
            datasize = datanum - len(dataraw)
            dataraw += self._cmd_recv(datasize)
        self._cmd_recv(1)
        return dataraw

    @_ensure_connection
    def wfm_read_channel(self, channel, force_update_scale=False):
        """Read and scale waveform data for a specific channel.

        Assumes a connection is already open (see connect()).

        Args:
            channel (str): Channel name, e.g. 'channel1'.
            force_update_scale (bool, optional): If True, re-reads the
                scaling factors for this channel even if already cached.

        Returns:
            tuple: (datax, datay), the time and amplitude arrays for
            the channel, scaled to physical units.
        """
        self.channel_select(channel)

        if channel not in self.channels_scales or force_update_scale:
            self.scales_read(channel)

        dataraw = self.wfm_read_raw()
        xinc, yinc, yor = self.channels_scales[channel]
        datax, datay = self._wfm_process_scales(dataraw, yinc, yor, xinc)
        return datax, datay

    @_ensure_connection
    def wfm_read(self, channels=None):
        """Read waveform data from one or more channels.

        Assumes a connection is already open (see connect()).

        Args:
            channels (list of str, optional): Channel names to
                read. Defaults to self.valid_channels.

        Returns:
            dict: Mapping of signal name (as configured for each
            channel) to a (datax, datay) tuple.
        """
        channels = channels or self.valid_channels
        waveforms = {}
        for channel in channels:
            datax, datay = self.wfm_read_channel(channel)
            signal = getattr(self, channel)
            waveforms[signal] = (datax, datay)
        return waveforms

    @_ensure_connection
    def meas_read(self):
        """Query and parse the measurement statistics from the oscilloscope.

        Assumes a connection is already open (see connect()).

        Returns:
            dict or None: Parsed measurement statistics (see
            Scope._process_meas), or None if the oscilloscope
            returned no data.
        """
        meas = self._cmd_send(b":MEASure:RESults?\n")
        if meas:
            meas = self._process_meas(meas)
            return meas
        else:
            return None

    @_ensure_connection
    def acquire(self, acq_meas=False, acq_wfms=False):
        """Connect, acquire data, and disconnect from the oscilloscope.

        Args:
            acq_meas (bool, optional): If True, read measurement
                statistics. Defaults to False.
            acq_wfms (bool, optional): If True, read waveform data
                from all valid channels. Defaults to False.

        Returns:
            tuple: (meas, wfms), where meas is the result of
            meas_read (or an empty list if acq_meas is False) and
            wfms is the result of wfm_read (or an empty dict if
            acq_wfms is False).
        """
        meas = list()
        wfms = dict()
        if acq_meas:
            meas = self.meas_read()
        if acq_wfms:
            self.wfm_config()
            wfms = self.wfm_read()
        return meas, wfms

    @_ensure_connection
    def setup_fetch(self):
        """Connect, read the current setup, and disconnect.

        Queries ':SYSTem:SETup?' and reads back the resulting
        definite-length binary block, which encodes the
        oscilloscope's entire current configuration. Opens and
        closes the connection itself.

        On Infiniium oscilloscopes, the returned block is an XML
        document; use setup_to_text to inspect it.

        Returns:
            bytes: Raw setup data. Can be passed to setup_apply
            later to restore this configuration.
        """
        self._cmd_send(b':SYSTem:SETup?\n', get_res=False)
        datanum = self._read_block_header()
        dataraw = b''
        while len(dataraw) < datanum:
            datasize = datanum - len(dataraw)
            dataraw += self._cmd_recv(datasize)
        self._cmd_recv(1)  # consome '\n' final
        return dataraw

    @_ensure_connection
    def setup_apply(self, dataraw):
        """Connect, apply a previously fetched setup, and disconnect.

        Sends dataraw back to the oscilloscope via ':SYSTem:SETup',
        restoring the configuration it was read from. Opens and
        closes the connection itself.

        Args:
            dataraw (bytes): Setup data, as returned by
                setup_fetch.
        """
        header = f'#{len(str(len(dataraw)))}{len(dataraw)}'.encode('ascii')
        self._cmd_send(
            b':SYSTem:SETup ' + header + dataraw + b'\n',
            get_res=False,
        )

    # --- private methods ---

    def _read_block_header(self):
        """Read and parse an SCPI definite-length binary block header.

        The header follows the IEEE 488.2 definite-length block
        format '#<n><len>', where n is the number of digits of len,
        and len is the number of bytes of the block data that
        follow. Used for both waveform and setup data blocks.
        Assumes a connection is already open (see connect()).

        Returns:
            int: Number of bytes of block data that follow the
            header.

        Raises:
            ValueError: If the socket is not connected.
            RuntimeError: If the expected '#' marker is not
                received.
        """
        if not self._socket:
            raise ValueError('socket is None')
        marker = self._cmd_recv(1)
        if marker != b'#':
            raise RuntimeError(
                f'Esperava "#", recebi {repr(marker)}')
        num = int(self._cmd_recv(1).decode('ascii'))
        datanum = int(self._cmd_recv(num).decode('ascii'))
        return datanum

    def _cmd_recv_until(self, terminator=b'\n'):
        """Read from socket until terminator is reached."""
        buf = bytearray()
        while True:
            chunk = self._socket.recv(1)
            if not chunk:
                break
            buf.extend(chunk)
            if buf.endswith(terminator):
                break
        return bytes(buf)

    def _cmd_send(self, cmd, get_res=True):
        if self._socket:
            self._socket.sendall(cmd)
            if get_res:
                res = self._cmd_recv_until(b'\n')
                return res.decode('ascii').strip()
        return None

    def _cmd_recv(self, nrbytes):
        """Receive raw bytes from the oscilloscope socket.

        Args:
            nrbytes (int): Number of bytes to read.

        Returns:
            bytes: The bytes received.

        Raises:
            ValueError: If the socket is not connected.
        """
        if self._socket:
            return self._socket.recv(nrbytes)
        else:
            raise ValueError('Communication socket is None!')

    @staticmethod
    def _wfm_process_scales(dataraw, yinc, yor, xinc):
        """Convert raw 16-bit waveform samples into physical x/y arrays.

        Args:
            dataraw (bytes): Raw waveform bytes, as returned by
                wfm_read_raw (16-bit samples, MSB-first).
            yinc (float): Y-axis (amplitude) increment per ADC
                count.
            yor (float): Y-axis (amplitude) origin/offset.
            xinc (float): X-axis (time) increment per sample.

        Returns:
            tuple: (datax, datay), the time and amplitude arrays.
        """
        if len(dataraw) % 2 != 0:
            dataraw = dataraw[:-1]

        # >i2: Big-endian (MSBF), 16-bit signed integer
        data = _np.frombuffer(dataraw, dtype='>i2')

        datay = data * yinc + yor
        datax = _np.arange(datay.size, dtype=float) * xinc
        return datax, datay


class Scopes:
    """Oscilloscopes names and IPs."""

    AS_DI_FCT = Keysight(
        ipaddr='10.128.150.22',
        hostname='AS-DI-FCTDig.lnls-sirius.com.br',
        port=5025,
        scopename='AS_DI_FCT',
        stats_fields=Keysight.STATS_FIELDS1,
    )
    AS_DI_FPM = Keysight(
        ipaddr='10.128.150.21',
        hostname='AS-DI-FPMDig.lnls-sirius.com.br',
        port=5025,
        scopename='AS_DI_FPM',
        stats_fields=None,
    )
    LI_DI_ICT = Keysight(
        ipaddr='10.128.1.150',
        hostname='li-di-ictosc.lnls-sirius.com.br',
        port=5025,
        scopename='LI_DI_ICT',
        stats_fields=Keysight.STATS_FIELDS1,
    )
    LI_PU_MODLTR = Keysight(
        ipaddr='10.128.150.20',
        hostname='KEYSIGH-QQI8MNR.abtlus.org.br',
        port=5025,
        scopename='LI_PU_MODLTR',
        stats_fields=Keysight.STATS_FIELDS1,
    )
    TB_PU_INJBO = Keysight(
        ipaddr='10.128.101.70',
        hostname='TB-PU-Osc-InjBO.abtlus.org.br',
        port=5025,
        scopename='TB_PU_INJBO',
        stats_fields=None,
    )
    TS_PU_EJEBO = Keysight(
        ipaddr='10.128.120.70',
        hostname='TS-PU-Osc-EjeBO.abtlus.org.br',
        port=5025,
        scopename='TS_PU_EJEBO',
        stats_fields=Keysight.STATS_FIELDS1,
    )
    TS_PU_INJSI = Keysight(
        ipaddr='10.128.101.72',
        hostname='TS-PU-Osc-InjSI.abtlus.org.br',
        port=5025,
        scopename='TS_PU_INJSI',
        stats_fields=Keysight.STATS_FIELDS1,
    )
    SI_PU_INJSI = Keysight(
        ipaddr='10.128.101.71',
        hostname='SI-PU-Osc-InjSI.abtlus.org.br',
        port=5025,
        scopename='SI_PU_INJSI',
        stats_fields=Keysight.STATS_FIELDS1,
    )

    @staticmethod
    def get_scope(scopesignal):
        """Return the Keysight instance associated with a scope signal.

        Args:
            scopesignal (str or tuple): Signal name (as defined in
                ScopeSignals) or an already-resolved signal tuple.

        Returns:
            Keysight: The Keysight instance whose scopename
            matches the signal.
        """
        if isinstance(scopesignal, str):
            scopesignal = getattr(ScopeSignals, scopesignal)
        scopename = scopesignal[1]
        return getattr(Scopes, scopename)
