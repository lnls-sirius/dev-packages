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
            tuple, e.g. 'LI_DI_ICTOSC'), or None if the signal could
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
        """Return a human-readable summary of the scope configuration.

        Returns:
            str: Multi-line string listing scopename, ipaddr,
            hostname, port, channel1..4 and stats_fields.
        """
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

    STATS_FIELDS1 = ('CURR', 'STT', 'MIN', 'MAX', 'AVG', 'STD', 'COUNT')
    STATS_FIELDS2 = ('CURR', 'MIN', 'MAX', 'AVG', 'STD', 'COUNT')

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
        chan = channel.replace('channel', 'CHAN')
        self._cmd_send(
            b':WAVeform:SOURce ' + chan.encode('ascii') + b'\n',
            get_res=False,
        )

    def scales_read(self, channel):
        """Read the x/y scaling factors for the given channel.

        Selects the channel and queries the oscilloscope for the
        waveform increment and origin values needed to convert raw
        samples into physical units. Assumes a connection is
        already open (see connect()).

        Args:
            channel (str): Channel name, e.g. 'channel1'.

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
        return scales

    def scales_update(self, channel):
        """Read and store the x/y scales for the given channel.

        Assumes a connection is already open (see connect()).

        Args:
            channel (str): Channel name, e.g. 'channel1'.
        """
        scales = self.scales_read(channel)
        self.channels_scales[channel] = scales

    def scales_update_all(self):
        """Read and store the x/y scales for all valid channels.

        Assumes a connection is already open (see connect()).
        """
        self.channels_scales = {}
        for channel in self.valid_channels:
            self.scales_update(channel)

    def wfm_config(self):
        """Configure the oscilloscope for waveform data acquisition.

        Sets the waveform data format to 16-bit words with
        most-significant-byte-first ordering. Assumes a connection
        is already open (see connect()).

        Returns:
            str: The instrument identification string (*IDN?)
            response.
        """
        idn = self._cmd_send(b'*IDN?\r\n')  # needed ?
        self._cmd_send(b":WAVeform:FORMat WORD\n", get_res=False)
        self._cmd_send(b":WAVeform:BYTeorder MSBF\n", get_res=False)
        return idn

    def wfm_init(self):
        """Prepare the oscilloscope for waveform acquisition.

        Configures the acquisition format and, if not already done,
        updates the x/y scales for all valid channels. Assumes a
        connection is already open (see connect()).
        """
        self.wfm_config()
        if not self.channels_scales:
            self.scales_update_all()

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
        # consome '\n' final
        self._cmd_recv(1)
        return dataraw

    def wfm_read_channel(self, channel):
        """Read and scale waveform data for a specific channel.

        Assumes a connection is already open (see connect()).

        Args:
            channel (str): Channel name, e.g. 'channel1'.

        Returns:
            tuple: (datax, datay), the time and amplitude arrays for
            the channel, scaled to physical units.
        """
        self.channel_select(channel)
        dataraw = self.wfm_read_raw()
        xinc, yinc, yor = self.channels_scales[channel]
        datax, datay = self._wfm_process_scales(dataraw, yinc, yor, xinc)
        return datax, datay

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

    def setup_fetch(self):
        """Connect, read the current setup, and disconnect.

        Queries ':SYSTem:SETup?' and reads back the resulting
        definite-length binary block, which encodes the
        oscilloscope's entire current configuration. Opens and
        closes the connection itself.

        Returns:
            bytes: Raw setup data. Can be passed to setup_apply
            later to restore this configuration.
        """
        try:
            self.connect()
            self._cmd_send(b':SYSTem:SETup?\n', get_res=False)
            datanum = self._read_block_header()
            dataraw = b''
            while len(dataraw) < datanum:
                datasize = datanum - len(dataraw)
                dataraw += self._cmd_recv(datasize)
            self._cmd_recv(1)  # consome '\n' final
        finally:
            self.disconnect()
        return dataraw

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
        try:
            self.connect()
            self._cmd_send(
                b':SYSTem:SETup ' + header + dataraw + b'\n',
                get_res=False,
            )
        finally:
            self.disconnect()

    def setup_save_to_file(self, filename):
        """Connect, save the current setup to a file, and disconnect.

        Saves to a file on the oscilloscope's own local storage.
        Opens and closes the connection itself.

        Args:
            filename (str): Name of the file to save the setup to.
                If an extension is given, it must be ".scp".

        Raises:
            ValueError: If filename contains a double quote.
        """
        if '"' in filename:
            raise ValueError('filename must not contain a double quote')
        cmd = f':SAVE:SETup "{filename}"\n'.encode('ascii')
        try:
            self.connect()
            self._cmd_send(cmd, get_res=False)
        finally:
            self.disconnect()

    def setup_load_from_file(self, filename):
        """Connect, load a setup from a file, and disconnect.

        Loads a file previously saved with setup_save_to_file, from
        the oscilloscope's own local storage. Opens and closes the
        connection itself.

        Args:
            filename (str): Name of the setup file to load.

        Raises:
            ValueError: If filename contains a double quote.
        """
        if '"' in filename:
            raise ValueError('filename must not contain a double quote')
        cmd = f':RECall:SETup "{filename}"\n'.encode('ascii')
        try:
            self.connect()
            self._cmd_send(cmd, get_res=False)
        finally:
            self.disconnect()

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
        try:
            self.connect()
            if acq_meas:
                meas = self.meas_read()
            if acq_wfms:
                self.wfm_init()
                wfms = self.wfm_read()
        finally:
            self.disconnect()

        return meas, wfms

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
        dataraw = dataraw[0:-1]
        va1 = _np.array(list(dataraw)[0::2])
        va0 = _np.array(list(dataraw)[1::2])
        va1 = va1[:va0.size]
        datay = ((va1 << 8) + va0 - 2**16*(va1 >> 7)) * yinc + yor
        datax = _np.arange(datay.size) * xinc
        return datax, datay

    def _cmd_send(self, cmd, get_res=True):
        """Send a SCPI command to the oscilloscope and optionally read the reply.

        Args:
            cmd (bytes): SCPI command to send.
            get_res (bool, optional): If True, read and return the
                response. Defaults to True.

        Returns:
            str or None: The decoded response, if get_res is True
            and the socket is connected; otherwise None.
        """
        if self._socket:
            self._socket.sendall(cmd)
            if get_res:
                return self._cmd_recv(1024).decode('ascii')
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
        """Return the Scope instance associated with a scope signal.

        Args:
            scopesignal (str or tuple): Signal name (as defined in
                ScopeSignals) or an already-resolved signal tuple.

        Returns:
            Scope: The Scope (or Keysight) instance whose scopename
            matches the signal.
        """
        if isinstance(scopesignal, str):
            scopesignal = getattr(ScopeSignals, scopesignal)
        scopename = scopesignal[1]
        return getattr(Scopes, scopename)
