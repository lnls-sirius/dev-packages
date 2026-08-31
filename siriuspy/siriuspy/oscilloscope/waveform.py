"""Waveform acquisition from oscilloscope."""

import time as _time

import numpy as _np


def _time_method(method):
    """."""
    def wrapper(*args, **kwargs):
        if WaveformAcquisition.DEBUG_FLAG:
            t0 = _time.perf_counter()
        res = method(*args, **kwargs)
        if WaveformAcquisition.DEBUG_FLAG:
            print(
                f'{method.__name__:<25s}: '
                f'{_time.perf_counter()-t0:.3f} s'
            )
        return res
    wrapper.__wrapped__ = method
    return wrapper


class WaveformAcquisition:
    """."""

    DEBUG_FLAG = False

    _STAT_INDICES1 = ('CURR', 'STT', 'MIN', 'MAX', 'AVG', 'STD', 'COUNT')
    _STAT_INDICES2 = ('CURR', 'MIN', 'MAX', 'AVG', 'STD', 'COUNT')
    STATS = {
        'TB-ICT1': _STAT_INDICES1,
        'TB-ICT2': _STAT_INDICES1,
        'LI-ICT1': _STAT_INDICES1,
        'LI_ICT2': _STAT_INDICES1,
    }
    CHANNELS = ('CHAN1', 'CHAN2', 'CHAN3', 'CHAN4')

    def __init__(self, keysight):
        """Initialize the waveform acquisition."""
        self.keysight = keysight
        self.idn = None
        self.scales = {}

    @_time_method
    def connect(self):
        """Connect to the oscilloscope."""
        self.keysight.connect()

    @_time_method
    def close(self):
        """Close the oscilloscope connection."""
        self.keysight.close()

    def wfm_config_acq(self):
        """Configure the oscilloscope for waveform acquisition."""
        self.idn = self.keysight.send_command(b'*IDN?\r\n')
        self.keysight.send_command(b":WAVeform:FORMat WORD\n", get_res=False)
        self.keysight.send_command(b":WAVeform:BYTeorder MSBF\n", get_res=False)
        return self.idn

    def channel_select(self, channel):
        """Select the channel for waveform acquisition."""
        self.keysight.send_command(
            b':WAVeform:SOURce ' + channel.encode('ascii') + b'\n',
            get_res=False,
        )

    def channel_read_scales(self, channel):
        """Read the scales for the selected channel."""
        self.channel_select(channel)
        xinc = float(
            self.keysight.send_command(b":WAVeform:XINCrement?\n")
        )
        yinc = float(
            self.keysight.send_command(
                b":WAVeform:YINCrement?\n"))
        yor = float(
            self.keysight.send_command(
                b":WAVeform:YORigin?\n"))
        return xinc, yinc, yor

    @_time_method
    def channel_read_all_scales(self):
        """Read the scales for all channels."""
        self.scales = {}
        for ch in self.CHANNELS:
            self.scales[ch] = self.channel_read_scales(ch)
        return self.scales

    def wfm_initialize(self):
        """Initialize the oscilloscope for waveform acquisition."""
        self.wfm_config_acq()
        if not self.scales:
            self.channel_read_all_scales()

    def wfm_read_header(self):
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

    def wfm_read_raw(self):
        """Read the raw waveform data from the oscilloscope."""
        self.keysight.send_command(
            b":WAVeform:STReaming OFF\n",
            get_res=False)
        self.keysight.send_command(
            b":WAVeform:DATA?\n",
            get_res=False)
        datanum = self.wfm_read_header()
        dataraw = b''
        while len(dataraw) < datanum:
            dataraw += self.keysight._socket.recv(
                datanum - len(dataraw))
        # consome '\n' final
        self.keysight._socket.recv(1)
        return dataraw

    def wfm_process_scales(self, dataraw, yinc, yor, xinc):
        """Process the raw waveform data into x and y arrays."""
        dataraw = dataraw[0:-1]
        va1 = _np.array(list(dataraw)[0::2])
        va0 = _np.array(list(dataraw)[1::2])
        va1 = va1[:va0.size]
        datay = ((va1 << 8) + va0 - 2**16*(va1 >> 7)) * yinc + yor
        datax = _np.arange(datay.size) * xinc
        return datax, datay

    @_time_method
    def wfm_read_channel(self, channel):
        """Read waveform data from a specific channel."""
        self.channel_select(channel)
        dataraw = self.wfm_read_raw()
        xinc, yinc, yor = self.scales[channel]
        datax, datay = self.wfm_process_scales(dataraw, yinc, yor, xinc)
        return datax, datay

    @_time_method
    def meas_read(self):
        """Get the measurements from the oscilloscope."""
        meas = self.keysight.send_command(b":MEASure:RESults?\n")
        meas = meas.split(',')
        return meas

    def wfm_read(self, channels=None):
        """Read waveform data from channels."""
        channels = channels or self.CHANNELS
        waveforms = {}
        for ch in channels:
            datax, datay = self.wfm_read_channel(ch)
            waveforms[ch] = (datax, datay)
        return waveforms

    @_time_method
    def acquire(self, acq_meas=True, acq_wfms=True):
        """Acquire waveform data from all channels."""
        meas = list()
        wfms = dict()
        errormsg = ''
        try:
            self.connect()
            if acq_meas:
                meas = self.meas_read()
            if acq_wfms:
                self.wfm_initialize()
                wfms = self.wfm_read()
            errormsg = ''
        except Exception as err:
            errormsg = str(err)
        finally:
            self.close()

        return errormsg, meas, wfms

    @staticmethod
    def _process_waveform_basic(waveform):
        """."""
        tim, val = waveform

        # get time of maximum voltage value
        peak_idx = _np.argmax(val)
        peak_tim = tim[peak_idx]

        return tim, val, peak_idx, peak_tim

    @staticmethod
    def wfm_process_scope(waveform, **kwargs):
        """."""
        _ = kwargs
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
    def wfm_process_baseline1(waveform, perc, order):
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
    def wfm_process_baseline2(waveform, perc, order):
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
    def meas_process(meas):
        """."""
        statusmsg = ''
        stat_dict = dict()

        wfmacqcls = WaveformAcquisition
        # Check if measurement for each ICT has the length we expect:
        if not len(meas) % (1+len(wfmacqcls._STAT_INDICES1)):
            indcs = wfmacqcls._STAT_INDICES1
        elif not len(meas) % (1+len(wfmacqcls._STAT_INDICES2)):
            indcs = wfmacqcls._STAT_INDICES2
        else:
            statusmsg = 'Measurement list size does not match required length.'
            return statusmsg, stat_dict

        nr_stats = len(meas) // (1 + len(indcs))
        stat_splits = _np.array_split(meas, nr_stats)
        for stat_split in stat_splits:
            stat_dict[stat_split[0]] = list(
                float(val) for val in stat_split[1:]
            )
        return statusmsg, stat_dict

    @staticmethod
    def wfm_process(waveform, process_method, **kwargs):
        """."""
        wfmacqcls = WaveformAcquisition
        if process_method == 'scope':
            return wfmacqcls.wfm_process_scope(waveform)
        elif process_method == 'baseline1':
            perc = kwargs.pop('perc', 0.02)
            order = kwargs.pop('order', 1)
            return wfmacqcls.wfm_process_baseline1(waveform, perc, order)
        elif process_method == 'baseline2':
            perc = kwargs.pop('perc', 0.02)
            order = kwargs.pop('order', 1)
            return wfmacqcls.wfm_process_baseline2(waveform, perc, order)
