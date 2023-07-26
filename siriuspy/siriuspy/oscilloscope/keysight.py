"""Keysight oscilloscope classes."""

import socket as _socket
import time as _time
import sys as _sys
import numpy as _np

from . import scopes as _scopes


class Keysight:
    """Keysight Oscilloscopes.

    For users' and programmers' guides (model DSOS104A), see
    http://10.0.38.42/control-system-constants/documentation/keysight/
    for original source:
        https://www.keysight.com/us/en/support/DSOS104A/
        high-definition-oscilloscope-1-ghz-4-analog-channels.html.


    Example
    =======

    from siriuspy.oscilloscope import Keysight, ScopeSignals
    import matplotlib.pyplot as plt

    scope = Keysight(scopesignal=ScopeSignals.SI_FILL_PATTERN)
    print(scope.scope_name)
    wavet, waved = scope.wfm_get_data()
    plt.plot(wavet, waved)
    plt.show()

    """

    SOCKET_TIMEOUT = 10  # [s]

    def __init__(self, scope=None, scopesignal=None):
        """."""
        if scopesignal and isinstance(scopesignal, tuple):
            self.host = scopesignal[0]
            self.port = scopesignal[1]
            self.chan = scopesignal[2]
        elif scope and isinstance(scope, str):
            self.host = scope
            self.port = 5025  # keysight default?
            self.chan = 'CHAN1'
        else:
            raise NotImplementedError
        self._socket = None

    @property
    def scope_name(self):
        """."""
        return _scopes.ScopeSignals.get_scope_name(self.host)

    def connect(self):
        """."""
        self._socket = _socket.socket(
            _socket.AF_INET,  # Internet
            _socket.SOCK_STREAM)  # TCP
        self._socket.settimeout(Keysight.SOCKET_TIMEOUT)
        self._socket.connect((self.host, self.port))

    def close(self):
        """."""
        self._socket.close()

    def wfm_enable(self):
        """Enable scope waveform acquisition."""
        return self.send_command(b'*IDN?\r\n')

    def wfm_config(self, wait_trigger=False):
        """Set scope waveform format."""
        self.send_command(b":WAVeform:FORMat WORD\n", get_res=False)
        dataformat = self.send_command(b":WAVeform:FORMat?\n")
        print('Data format:', dataformat)
        # Set bit order to MSB First
        self.send_command(b":WAVeform:BYTeorder MSBF\n", get_res=False)
        # Acquire
        if wait_trigger:
            self.send_command(b':DIG\n', get_res=False)
        else:
            self.send_command(b':RUN\n', get_res=False)

    def wfm_acquire(self, channel):
        """Acquire scope waveform."""
        if isinstance(channel, tuple):
            channel = channel[2]

        # Get the number of waveform points
        points = self.send_command(b":WAVeform:POINts?\n")
        print('Points:', points)

        # Get sample rate
        srate = self.send_command(b":ACQuire:SRATe?\n")
        print('Sample rate:', srate)

        # Get bandwidth
        bdw = self.send_command(b":ACQuire:BANDwidth:FRAMe?\n")
        print('Bandwidth:', bdw)

        # Set the waveform channel source
        self.send_command(
            b":WAVeform:SOURce " + channel.encode('ascii')+b"\n",
            get_res=False)
        channel = self.send_command(b":WAVeform:SOURce?\n")

        # Get scales
        xinc = self.send_command(b":WAVeform:XINCrement?\n")
        xinc = float(xinc)
        print('Horizontal Scale:', xinc)
        yinc = self.send_command(b":WAVeform:YINCrement?\n")
        yor = self.send_command(b":WAVeform:YORigin?\n")
        yinc = float(yinc)
        yor = float(yor)
        print('Vertical Scale:', xinc, yor)

        # Data aquisition
        self.send_command(b":WAVeform:STReaming OFF\n", get_res=False)
        self.send_command(b":WAVeform:DATA?\n", get_res=False)
        _ = self._socket.recv(1)  # ignore marker '#'
        num = int(self._socket.recv(1).decode('ascii'))
        datanum = int(self._socket.recv(num).decode('ascii'))
        dataraw = b''

        # Return scope to RUN mode
        self.send_command(b":RUN\n", get_res=False)
        while len(dataraw) < datanum:
            dataraw = dataraw + self._socket.recv(datanum)
        dataraw = dataraw[0:-1]  # remove EOF char

        va1 = _np.array(list(dataraw)[0::2])
        va0 = _np.array(list(dataraw)[1::2])
        va1 = va1[:va0.size]

        datay = ((va1 << 8) + va0 - 2**16*(va1 >> 7)) * yinc + yor

        datax = _np.arange(datay.size)*xinc
        return datax, datay, srate, bdw

    def wfm_get_data(self, channel=None, wait_trigger=False):
        """Enable and get sccope waveform data."""
        channel = channel or self.chan
        self.connect()
        wavet = None
        waved = None
        try:
            self.wfm_enable()
            self.wfm_config(wait_trigger)
            tini = _time.time()
            print('Acquiring ' + self.chan)
            wavet, waved, srate1, bdw1 = self.wfm_acquire(channel)
            print('Total acquisition time:', _time.time() - tini)
            # self.send_command(b":WAVeform:STReaming ON\n", get_res=False)
        except Exception:
            print('Close connection by exception')
            raise

        finally:
            self.close()

        return wavet, waved

    def stats_enable(self):
        """Enable scope measurement statistics info."""
        # Set bit order to MSB First
        self.send_command(b":MEASure:STATistics ON\n", get_res=False)
        self.send_command(b":MEASure:SENDvalid ON\n", get_res=False)

    def stats_acquire(self):
        """Return a dictionary of scope measurement statistics."""
        meas = self.send_command(b":MEASure:RESults?\n")
        data = Keysight.process_stats_meas(meas)
        return data

    def stats_get_data(self):
        """."""
        self.connect()
        try:
            self.stats_enable()
            tini = _time.time()
            print('Acquiring ' + self.chan)
            data = self.stats_acquire()
            print('Total acquisition time:', _time.time() - tini)
        except Exception:
            print('Close connection by exception')
            raise
        finally:
            self.close()
        return data

    def send_command(self, cmd, get_res=True):
        """."""
        self._socket.sendall(cmd)
        if get_res:
            return self._socket.recv(1024).decode('ascii')
        return

    @staticmethod
    def process_stats_meas(meas):
        """Process stats measurents."""
        # TODO: generalize or instantiate for each scope type
        meas = meas.split(',')
        data = dict()
        for i in range(0, len(meas) - len(meas) % 8, 8):
            datum = dict()
            label = meas[i]
            datum['current'] = float(meas[i+1])
            datum['state'] = int(float(meas[i+2]))
            datum['min'] = float(meas[i+3])
            datum['max'] = float(meas[i+4])
            datum['mean'] = float(meas[i+5])
            datum['std_dev'] = float(meas[i+6])
            datum['num_of_meas'] = int(float(meas[i+7]))
            data[label] = datum
        return data
