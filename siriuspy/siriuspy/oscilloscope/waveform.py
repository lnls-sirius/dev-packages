"""Waveform acquisition from oscilloscope."""

import logging as _log
import time as _time

import numpy as _np
from mathphys.functions import get_namedtuple as _get_namedtuple


class WaveformAcquisition:
    """."""

    _STAT_INDICES1 = ('CURR', 'STT', 'MIN', 'MAX', 'AVG', 'STD','COUNT')
    _STAT_INDICES2 = ('CURR', 'MIN', 'MAX', 'AVG', 'STD','COUNT')
    STATS = {
        'TB-ICT1': _STAT_INDICES1,
        'TB-ICT2': _STAT_INDICES1,
        'LI-ICT1': _STAT_INDICES1,
        'LI_ICT2':
    }
    STAT_INDICES1 = _get_namedtuple(
        'Indices1',
        ('NAME', 'CURR', 'STT', 'MIN', 'MAX', 'AVG', 'STD', 'COUNT')
    )
    # Some scopes does not return STT.
    STAT_INDICES2 = _get_namedtuple(
        'Indices2',
        ('NAME', 'CURR', 'MIN', 'MAX', 'AVG', 'STD', 'COUNT')
    )
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
        finally:
            self.close()

        if print_time:
            print('--------------------------')
            print(
                f'TOTAL: '
                f'{_time.perf_counter()-t0:.3f} s'
            )

        return status_ok, stat, wfms

    @staticmethod
    def process_stat(stat):
        """."""
        WfmAcqCls = WaveformAcquisition
        # Check if measurement for each ICT has the length we expect:
        if not len(stat) % len(WfmAcqCls.STAT_INDICES1):
            indcs = WfmAcqCls.STAT_INDICES1
        elif not len(stat) % len(WfmAcqCls.STAT_INDICES2):
            indcs = WfmAcqCls.STAT_INDICES2
        else:
            _log.warning(
                'Measurement list size does not match required length.')
            return

        name = acc + '-ICT1'
        idxict1 = [i for i, val in enumerate(meas) if name in val]
        if not idxict1:
            _log.warning(f'Could not find data for {name}.')
            return
        idxict1 = idxict1.pop()

        name = acc + '-ICT2'
        idxict2 = [i for i, val in enumerate(meas) if name in val]
        if not idxict2:
            _log.warning(f'Could not find data for {name}.')
            return
        idxict2 = idxict2.pop()

        try:
            chg1 = float(meas[idxict1 + indcs.CURR]) * 1e9
            ave1 = float(meas[idxict1 + indcs.AVG]) * 1e9
            min1 = float(meas[idxict1 + indcs.MIN]) * 1e9
            max1 = float(meas[idxict1 + indcs.MAX]) * 1e9
            std1 = float(meas[idxict1 + indcs.STD]) * 1e9
            cnt1 = int(float(meas[idxict1 + indcs.COUNT]))
            chg2 = float(meas[idxict2 + indcs.CURR]) * 1e9
            ave2 = float(meas[idxict2 + indcs.AVG]) * 1e9
            min2 = float(meas[idxict2 + indcs.MIN]) * 1e9
            max2 = float(meas[idxict2 + indcs.MAX]) * 1e9
            std2 = float(meas[idxict2 + indcs.STD]) * 1e9
            cnt2 = int(float(meas[idxict2 + indcs.COUNT]))
        except IndexError:
            _log.warning('Problem reading data.')
            return

    @staticmethod
    def _process_waveform_basic(waveform):
        """."""
        tim, val = waveform

        # get time of maximum voltage value
        peak_idx = _np.argmax(val)
        peak_tim = tim[peak_idx]

        return tim, val, peak_idx, peak_tim

    @staticmethod
    def process_waveform_scope(waveform, **kwargs):
        """."""
        params = WaveformAcquisition._process_waveform_basic(waveform)
        tim, val, peak_idx, peak_tim = params

        # calculate cummulative integral
        dtim = _np.diff(tim)
        aval = (val[:-1] + val[1:]) / 2.0
        areas = dtim * aval
        cumcurrint = _np.cumsum(areas)

        # scope take peak to peak value fo cummulative integral
        vpp = max(cumcurrint) - min(cumcurrint)

        # also return total integral
        currint = cumcurrint[-1]

        params = (
            vpp,  # Peak to peak range of cummulative integral
            peak_tim,  # time of peak
            currint,  # signal integral
            peak_idx,  # index of voltage peak
        )
        return params

    @staticmethod
    def process_waveform_baseline1(waveform, perc, order):
        """."""
        params = WaveformAcquisition._process_waveform_basic(waveform)
        tim, val, peak_idx, peak_tim = params

        # selection of waveform that
        # 1) below a percentage of "height" of signal &
        # 2) indices are less than peak_idx
        # create a selection of a baseline before the peak
        indcs = _np.arange(len(val))
        sel1 = (val - val[0]) < perc * (val[peak_idx] - val[0])
        sel2 = indcs < peak_idx
        sel = sel1 & sel2

        # fit a polynominal to the selected base line
        pcoeffs = _np.polynomial.polynomial.polyfit(tim[sel], val[sel], order)
        val_fit = _np.polynomial.polynomial.polyval(tim, pcoeffs)

        tim_fix = tim
        val_fix = val - val_fit

        currint = _np.trapz(val_fix, tim_fix)
        params = (
            currint,  # filtered signal integral
            peak_tim,  # time of peak
            sel,  # selection for filter baseline
            val_fit,  # poly fitted data using baseline
            val_fix,  # voltage of filtered signal
            pcoeffs,  # polynomial fit coeffs
            peak_idx,  # index of voltage peak
        )
        return params

    @staticmethod
    def process_waveform_baseline2(waveform, perc, order):
        """."""
        params = WaveformAcquisition._process_waveform_basic(waveform)
        tim, val, peak_idx, peak_tim = params

        # selection
        indcs = _np.arange(len(val))
        sel = (indcs < perc * len(val)) & ((indcs > (1-perc) * len(val)))

        # fit a polynominal to the selected base line
        pcoeffs = _np.polynomial.polynomial.polyfit(tim[sel], val[sel], order)
        val_fit = _np.polynomial.polynomial.polyval(tim, pcoeffs)

        tim_fix = tim
        val_fix = val - val_fit

        currint = _np.trapz(val_fix, tim_fix)
        params = (
            currint,  # filtered signal integral
            peak_tim,  # time of peak
            sel,  # selection for filter baseline
            val_fit,  # poly fitted data using baseline
            val_fix,  # voltage of filtered signal
            pcoeffs,  # polynomial fit coeffs
            peak_idx,  # index of voltage peak
        )
        return params

    @staticmethod
    def process_waveform(waveform, process_method, **kwargs):
        """."""
        WfmAcq = WaveformAcquisition
        if process_method == 'scope':
            return WfmAcq.process_waveform_scope(waveform)
        elif process_method == 'baseline1':
            perc = kwargs.pop('perc', 0.02)
            order = kwargs.pop('order', 1)
            return WfmAcq.process_waveform_baseline1(waveform, perc, order)
        elif process_method == 'baseline2':
            perc = kwargs.pop('perc', 0.02)
            order = kwargs.pop('order', 1)
            return WfmAcq.process_waveform_baseline2(waveform, perc, order)
