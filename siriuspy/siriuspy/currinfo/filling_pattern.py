"""."""

import socket as _socket
import time as _time
import sys as _sys
import numpy as _np


class MeasFillingPattern:
    """Beam filling pattern from Keysight DSOS104A Oscilloscopes.
    
    For users' and programmers' guides, see
        https://www.keysight.com/us/en/support/DSOS104A/
        high-definition-oscilloscope-1-ghz-4-analog-channels.html"""

    class DEVICES:
        SI = ('10.128.150.77', 5025)
        ALL = (SI, )

    def __init__(self, device=None):
        """."""
        device = device or MeasFillingPattern.DEVICES.SI

        # check if device exists
        if device not in MeasFillingPattern.DEVICES.ALL:
            raise NotImplementedError(device)

        self.host = device[0]
        self.port = device[1]
        self._socket = None

    def connect(self):
        """."""
        self._socket = _socket.socket(
            _socket.AF_INET,  # Internet
            _socket.SOCK_STREAM)  # TCP
        self._socket.settimeout(10)
        self._socket.connect((self.host, self.port))

    def initialize(self):
        """."""
        self._socket.sendall(b'*IDN?\r\n')
        ans = self._socket.recv(1024).decode('ascii')
        return ans

    def acquire(self):
        """Set waveform format."""
        sock = self._socket
        sock.sendall(b":WAVeform:FORMat WORD\n")
        sock.sendall(b":WAVeform:FORMat?\n")
        dataformat = sock.recv(1024).decode('ascii')
        print('Data format:', dataformat)
        # Set bit order to MSB First
        sock.sendall(b":WAVeform:BYTeorder MSBF\n")
        # Acquire
        sock.sendall(b':DIG\n')

    def capture(self, source):
        """."""
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
        sock.sendall(b":WAVeform:SOURce " + source.encode('ascii')+b"\n")
        sock.sendall(b":WAVeform:SOURce?\n")
        source = sock.recv(1024).decode('ascii')

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

        # return oscilloscopy to
        self._socket.sendall(b":RUN\n")

        while len(dataraw) < datanum:
            dataraw = dataraw + sock.recv(datanum)
        dataraw = dataraw[0:-1]  # remove EOF char

        va1 = _np.array(list(dataraw)[0::2])
        va0 = _np.array(list(dataraw)[1::2])
        datay = ((va1 << 8) + va0 - 2**16*(va1 >> 7)) * yinc + yor

        datax = _np.arange(datay.size)*xinc
        return datax, datay, srate, bdw

    def get_data(self):
        """."""
        self.connect()
        wavet = None
        waved = None
        try:
            self.initialize()
            self.acquire()
            tini = _time.time()
            print('Acquiring CHAN1')
            wavet, waved, srate1, bdw1 = self.capture('CHAN1')
            print('Total acquisition time:', _time.time()-tini)
            # self._socket.sendall(b":WAVeform:STReaming ON\n")
        except Exception:
            print("Unexpected error:", _sys.exc_info()[0])
            print('Close connetion by exception')
        finally:
            self._socket.close()

        return wavet, waved
