"""Waveform acquisition from oscilloscope."""

import logging as _log
import time as _time

import numpy as _np


class WaveformAcquisition:
    """."""

    CHANNELS = ('CHAN1', 'CHAN2', 'CHAN3', 'CHAN4')

    def __init__(self, keysight):
        """Initialize the waveform acquisition."""
        self.keysight = keysight
        self.idn = None
        self.scales = {}

    def connect(self):
        """Connect to the oscilloscope."""
        self.keysight.connect()

    def close(self):
        """Close the oscilloscope connection."""
        self.keysight.close()

    def configure_waveforms(self):
        """Configure the oscilloscope for waveform acquisition."""
        self.idn = self.keysight.send_command(b'*IDN?\r\n')
        self.keysight.send_command(b":WAVeform:FORMat WORD\n", get_res=False)
        self.keysight.send_command(b":WAVeform:BYTeorder MSBF\n", get_res=False)
        return self.idn

    def select_channel(self, channel):
        """Select the channel for waveform acquisition."""
        self.keysight.send_command(
            b":WAVeform:SOURce "
            + channel.encode('ascii')
            + b"\n",
            get_res=False)

    def read_scales(self, channel):
        """Read the scales for the selected channel."""
        self.select_channel(channel)
        xinc = float(
            self.keysight.send_command(
                b":WAVeform:XINCrement?\n"))
        yinc = float(
            self.keysight.send_command(
                b":WAVeform:YINCrement?\n"))
        yor = float(
            self.keysight.send_command(
                b":WAVeform:YORigin?\n"))
        return xinc, yinc, yor

    def read_all_scales(self):
        """Read the scales for all channels."""
        self.scales = {}
        for ch in self.CHANNELS:
            self.scales[ch] = self.read_scales(ch)
        return self.scales

    def read_header(self):
        """Read the header of the waveform data."""
        marker = self.keysight._socket.recv(1)
        if marker != b'#':
            raise RuntimeError(
                f'Esperava "#", recebi {repr(marker)}')
        num = int(
            self.keysight._socket.recv(1).decode('ascii'))
        datanum = int(
            self.keysight._socket.recv(num).decode('ascii'))
        return datanum

    def read_waveform_raw(self):
        """Read the raw waveform data from the oscilloscope."""
        self.keysight.send_command(
            b":WAVeform:STReaming OFF\n",
            get_res=False)
        self.keysight.send_command(
            b":WAVeform:DATA?\n",
            get_res=False)
        datanum = self.read_header()
        dataraw = b''
        while len(dataraw) < datanum:
            dataraw += self.keysight._socket.recv(
                datanum - len(dataraw))
        # consome '\n' final
        self.keysight._socket.recv(1)
        return dataraw

    def process_data(self, dataraw, yinc, yor, xinc):
        """Process the raw waveform data into x and y arrays."""
        dataraw = dataraw[0:-1]
        va1 = _np.array(list(dataraw)[0::2])
        va0 = _np.array(list(dataraw)[1::2])
        va1 = va1[:va0.size]
        datay = ((va1 << 8) + va0 - 2**16*(va1 >> 7)) * yinc + yor
        datax = _np.arange(datay.size) * xinc
        return datax, datay

    def acquire_channel(self, channel):
        """Acquire waveform data from a specific channel."""
        self.select_channel(channel)
        dataraw = self.read_waveform_raw()
        xinc, yinc, yor = self.scales[channel]
        datax, datay = self.process_data(dataraw, yinc, yor, xinc)
        return datax, datay

    def acquire_all_channels(self, print_time=False):
        """Acquire waveform data from all channels."""
        waveforms = {}
        for ch in self.CHANNELS:
            t0 = _time.perf_counter()
            datax, datay = self.acquire_channel(ch)
            waveforms[ch] = (datax, datay)
            if print_time:
                print(
                    f'{ch}: '
                    f'{_time.perf_counter()-t0:.3f} s'
                )
        return waveforms

    def initialize_waveforms(self):
        """Initialize the oscilloscope for waveform acquisition."""
        self.configure_waveforms()
        if not self.scales:
            self.read_all_scales()

    def get_measurements(self):
        """Get the measurements from the oscilloscope."""
        stat = self.keysight.send_command(b":MEASure:RESults?\n")
        stat = stat.split(',')
        return stat

    def acquire(self, acq_meas=True, acq_wfms=True, print_time=False):
        """Acquire waveform data from all channels."""
        t0 = _time.perf_counter()

        stat = list()
        wfms = dict()
        status_ok = False
        try:
            self.connect()
            if acq_meas:
                stat = self.get_measurements()
            if acq_wfms:
                self.initialize_waveforms()
                wfms = self.acquire_all_channels(print_time=print_time)
            status_ok = True
        except Exception as err:
            _log.error(str(err))
            raise
        finally:
            self.close()

        if print_time:
            print('--------------------------')
            print(
                f'TOTAL: '
                f'{_time.perf_counter()-t0:.3f} s'
            )

        return status_ok, stat, wfms
