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
        self._socket.settimeout(10)
        self._socket.connect((self.host, self.port))

    def close(self):
        """."""
        self._socket.close()

    def wfm_enable(self):
        """Enable scope waveform acquisition."""
        self._socket.sendall(b'*IDN?\r\n')
        ans = self._socket.recv(1024).decode('ascii')
        return ans

    def wfm_config(self):
        """Set scope waveform format."""
        sock = self._socket
        sock.sendall(b":WAVeform:FORMat WORD\n")
        sock.sendall(b":WAVeform:FORMat?\n")
        dataformat = sock.recv(1024).decode('ascii')
        print('Data format:', dataformat)
        # Set bit order to MSB First
        sock.sendall(b":WAVeform:BYTeorder MSBF\n")
        # Acquire
        sock.sendall(b':DIG\n')

    def wfm_acquire(self, channel):
        """Acquire scope waveform."""
        if isinstance(channel, tuple):
            channel = channel[2]
        sock = self._socket

        # Get the number of waveform points
        sock.sendall(b":WAVeform:POINts?\n")
        points = int(sock.recv(1024).decode('ascii'))
        print('Points:', points)

        # Get sample rate
        sock.sendall(b":ACQuire:SRATe?\n")
        srate = float(sock.recv(1024).decode('ascii'))
        print('Sample rate:', srate)

        # Get bandwidth
        sock.sendall(b":ACQuire:BANDwidth:FRAMe?\n")
        bdw = float(sock.recv(1024).decode('ascii'))
        print('Bandwidth:', bdw)

        # Set the waveform channel source
        sock.sendall(b":WAVeform:SOURce " + channel.encode('ascii')+b"\n")
        sock.sendall(b":WAVeform:SOURce?\n")
        channel = sock.recv(1024).decode('ascii')

        # Get scales
        sock.sendall(b":WAVeform:XINCrement?\n")
        xinc = float(sock.recv(1024).decode('ascii'))
        print('Horizontal Scale:', xinc)
        sock.sendall(b":WAVeform:YINCrement?\n")
        yinc = float(sock.recv(1024).decode('ascii'))
        sock.sendall(b":WAVeform:YORigin?\n")
        yor = float(sock.recv(1024).decode('ascii'))
        print('Vertical Scale:', xinc, yor)

        # Data aquisition
        sock.sendall(b":WAVeform:STReaming OFF\n")
        sock.sendall(b":WAVeform:DATA?\n")
        _ = sock.recv(1)  # ignore marker '#'
        num = int(sock.recv(1).decode('ascii'))
        datanum = int(sock.recv(num).decode('ascii'))
        dataraw = b''

        # Return scope to RUN mode
        self._socket.sendall(b":RUN\n")

        while len(dataraw) < datanum:
            dataraw = dataraw + sock.recv(datanum)
        dataraw = dataraw[0:-1]  # remove EOF char

        va1 = _np.array(list(dataraw)[0::2])
        va0 = _np.array(list(dataraw)[1::2])
        datay = ((va1 << 8) + va0 - 2**16*(va1 >> 7)) * yinc + yor

        datax = _np.arange(datay.size)*xinc
        return datax, datay, srate, bdw

    def wfm_get_data(self, channel=None):
        """Enable and get sccope waveform data."""
        channel = channel or self.chan
        self.connect()
        wavet = None
        waved = None
        try:
            self.wfm_enable()
            self.wfm_config()
            tini = _time.time()
            print('Acquiring ' + self.chan)
            wavet, waved, srate1, bdw1 = self.wfm_acquire(channel)
            print('Total acquisition time:', _time.time() - tini)
            # self._socket.sendall(b":WAVeform:STReaming ON\n")
        except Exception:
            print("Unexpected error:", _sys.exc_info()[0])
            print('Close connetion by exception')
        finally:
            self.close()

        return wavet, waved

    def stats_enable(self):
        """Enable scope measurement statistics info."""
        sock = self._socket
        # Set bit order to MSB First
        sock.sendall(b":MEASure:STATistics ON\n")
        sock.sendall(b":MEASure:SENDvalid ON\n")

    def stats_acquire(self):
        """Return a dictionary of scope measurement statistics."""
        sock = self._socket
        sock.sendall(b":MEASure:RESults?\n")
        meas = sock.recv(1024).decode('ascii')
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

    def stats_get_data(self):
        """."""
        self.connect()
        try:
            self.stats_enable()
            tini = _time.time()
            print('Acquiring ' + self.chan)
            wavet, waved, srate1, bdw1 = self.stats_acquire()
            print('Total acquisition time:', _time.time() - tini)
        except Exception:
            print("Unexpected error:", _sys.exc_info()[0])
            print('Close connetion by exception')
        finally:
            self.close()
