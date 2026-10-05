"""ASCII-encoded waveform normalization and conversion utilities."""

import base64 as _base64

try:
    import lzma as _lzma
except ModuleNotFoundError:
    _lzma = None

import numpy as _np
from scipy.signal import (
    butter as _butter,
    filtfilt as _filttilt
)
from scipy.signal.windows import tukey as _tukey


class Waveform:
    """Discrete temporal waveform representation and processing class."""

    DEFAULT_CALIBRATION_FACTOR = 5.0

    def __init__(self, tim, wfm):
        """Initialize waveform object with time and amplitude vectors.

        Args:
            tim (array_like): Time grid array [s].
            wfm (array_like): Amplitude signal array [V].

        Raises:
            ValueError: If time and waveform vectors have different shapes.
        """
        self._tim = _np.array(tim, dtype=_np.float64)
        self._wfm = _np.array(wfm, dtype=_np.float64)

        if self._tim.shape != self._wfm.shape:
            raise ValueError(
                "Time and waveform vectors must have the same shape. "
                f"Got tim={self._tim.shape} and wfm={self._wfm.shape}."
            )

        self._wfm_maxmin, self._domain_tim, self._domain_idx = (
            self._calc_basic_params(self._tim, self._wfm)
        )

    @property
    def tim(self):
        """Time vector array in seconds [s]."""
        return self._tim

    @property
    def wfm(self):
        """Amplitude signal vector array [V]."""
        return self._wfm

    @property
    def wfm_maxmin(self):
        """Peak maximum and minimum signal amplitudes."""
        return self._wfm_maxmin

    @property
    def wfm_idx_max(self):
        """Array index corresponding to maximum amplitude peak."""
        return self._domain_idx[0]

    @property
    def wfm_idx_fwhm(self):
        """Full width at half maximum (FWHM) in sample point count."""
        return self._domain_idx[1]

    @property
    def wfm_tim_max(self):
        """Time value [s] corresponding to maximum amplitude peak."""
        return self._domain_tim[0]

    @property
    def wfm_tim_fwhm(self):
        """Full width at half maximum (FWHM) in time domain [s]."""
        return self._domain_tim[1]

    def fit_linear_coeffs(self, wfm_basis):
        """Fit signal as a linear combination of basis vectors using LLSQ.

        Args:
            wfm_basis (list[Waveform | numpy.ndarray]): List of basis
                vector objects or raw arrays.

        Returns:
            tuple: Tuple containing:
                - coeffs (numpy.ndarray): Fitted linear coefficients.
                - residues (numpy.ndarray): Sum of squared residuals.
                - wfm_fit (Waveform): Fitted waveform object.
                - rank_s (tuple[int, numpy.ndarray]): Matrix rank and singular
                  values from least-squares solver.
        """
        nvecs = [
            vec.wfm if isinstance(vec, Waveform) else vec
            for vec in wfm_basis
        ]
        mat_a = _np.column_stack(nvecs)
        coeffs, residues, rank, s = _np.linalg.lstsq(
            mat_a, self._wfm, rcond=None
        )
        wfm_fit = Waveform(self._tim, mat_a @ coeffs)
        return coeffs, residues, wfm_fit, (rank, s)

    def calc_integral(self, calibration_factor=None):
        """Calculate area under curve integrated using trapezoidal rule.

        Args:
            calibration_factor (float, optional): Scaling divisor factor.
                Defaults to 5.0.

        Returns:
            Calibrated integral value.
        """
        trapz_func = getattr(_np, "trapezoid", getattr(_np, "trapz"))
        cal_factor = (Waveform.DEFAULT_CALIBRATION_FACTOR
            if calibration_factor is None
            else calibration_factor
        )
        integral = trapz_func(self._wfm, self._tim)
        return float(integral / cal_factor)

    def gen_shifted(self, shift=None, wfm_ref=None):
        """Shift signal vector by N sample points or align it with a ref wfm.

        A positive shift moves the signal to the right (padded with wfm[0]).
        A negative shift moves the signal to the left (padded with wfm[-1]).
        If 'wfm_ref' is provided, the shift is automatically computed to align
        the peak index of this waveform with the peak index of 'wfm_ref'.

        Args:
            shift (int, optional): Number of sample points to shift
                (positive=right, negative=left). Defaults to None.
            wfm_ref (Waveform, optional): Reference waveform object to align
                peaks with. Defaults to None.

        Returns:
            Waveform: New Waveform instance with the shifted signal.

        Raises:
            ValueError: If neither 'shift' nor 'wfm_ref' is provided.
        """
        if shift is None and wfm_ref is None:
            raise ValueError(
                "Either 'shift' or 'wfm_ref' must be provided for shifting."
            )

        if wfm_ref is not None:
            shift = int(wfm_ref.wfm_idx_max - self.wfm_idx_max)

        if shift == 0:
            return Waveform(self._tim, self._wfm)

        n = len(self._wfm)

        if shift > 0:
            nwfm = _np.full_like(self._wfm, self._wfm[0])
            if shift < n:
                nwfm[shift:] = self._wfm[:-shift]
        else:
            abs_shift = abs(shift)
            nwfm = _np.full_like(self._wfm, self._wfm[-1])
            if abs_shift < n:
                nwfm[:-abs_shift] = self._wfm[abs_shift:]

        return Waveform(self._tim, nwfm)

    def gen_filtered_and_zeroed_edges(
        self,
        cutoff_ratio=0.01,
        threshold_ratio=0.02,
        margin_pts=10,
        taper_ratio=0.1,
    ):
        """Filter high frequencies and smooth edge noise to zero.

        Args:
            wfm (Waveform): Input Waveform object to be filtered.
            cutoff_ratio (float, optional): Normalized cutoff frequency
                relative to Nyquist limit [0.0 to 1.0]. Lower values filter
                more high frequencies. Defaults to 0.2.
            threshold_ratio (float, optional): Fraction of peak amplitude used
                to detect pulse start/end (e.g., 0.02 = 2% of peak).
                Defaults to 0.02.
            margin_pts (int, optional): Extra sample points to keep around the
                detected pulse region before tapering to zero. Defaults to 10.
            taper_ratio (float, optional): Fraction of the pulse boundary used
                for smooth transition to zero [0.0 to 1.0]. Defaults to 0.1.

        Returns:
            Waveform: New Waveform instance with filtered signal and
                zeroed edges.
        """
        # 1. Extract background gradient
        n = len(self._tim)
        indcs = _np.arange(n)
        sel = (indcs < int(0.15 * n)) | (indcs > int(0.90 * n))
        pval = _np.polyfit(self._tim[sel], self._wfm[sel], 1)
        wfm_fit = _np.polyval(pval, self.tim)
        wfm = self.wfm - wfm_fit

        # 2. Low-Pass Filter with Relative Cutoff Frequency
        # (no sampling frequency needed)
        b, a = _butter(N=4, Wn=cutoff_ratio, btype="low", analog=False)
        wfm_filtered = _filttilt(b, a, wfm)

        # 3. Automatic Detection of the Pulse Region
        abs_wfm = _np.abs(wfm_filtered)
        peak_val = _np.max(abs_wfm)
        if peak_val == 0:
            return Waveform(self._tim, _np.zeros_like(wfm))

        threshold = peak_val * threshold_ratio
        pulse_indices = _np.where(abs_wfm >= threshold)[0]

        if len(pulse_indices) == 0:
            return Waveform(self._tim, _np.zeros_like(wfm))

        # 4. Define pulse boundaries with safety margin
        idx_start = max(0, pulse_indices[0] - margin_pts)
        idx_end = min(len(wfm), pulse_indices[-1] + margin_pts)
        pulse_len = idx_end - idx_start

        # 5. Smooth Mask Generation (Tukey Window)
        mask = _np.zeros_like(wfm)
        pulse_window = _tukey(pulse_len, alpha=taper_ratio)
        mask[idx_start:idx_end] = pulse_window

        # 6. Return new Waveform object with recalculated derived parameters
        return Waveform(self._tim, wfm_filtered * mask)

    def normalize_integral(self, calibration_factor=None):
        """Normalize waveform integral to 1 nC using trapezoidal rule.

        Args:
            calibration_factor (float, optional): Scaling divisor factor.
                Defaults to 5.0.

        Returns:
            Waveform: New Waveform instance with normalized signal.
        """
        cal_factor = (Waveform.DEFAULT_CALIBRATION_FACTOR
            if calibration_factor is None
            else calibration_factor
        )
        integral = self.calc_integral(cal_factor)
        if integral == 0:
            return Waveform(self._tim, self._wfm)
        normalized_wfm = 1e-9 * self._wfm / integral
        return Waveform(self._tim, normalized_wfm)

    @staticmethod
    def _calc_basic_params(tim, wfm):
        """Calculate peak amplitude, time bounds, and FWHM values.

        Args:
            tim (numpy.ndarray): Time vector array.
            wfm (numpy.ndarray): Signal amplitude array.

        Returns:
            tuple: Tuple containing amplitude limits, time bounds, and indices.
        """
        if len(wfm) == 0:
            return (0.0, 0.0), (0.0, 0.0), (0, 0)

        min_wfm = float(_np.min(wfm))
        max_wfm = float(_np.max(wfm))
        max_idx = int(_np.argmax(wfm))
        max_tim = float(tim[max_idx])

        wfm_maxmin = (max_wfm, min_wfm)
        half_max = max_wfm / 2.0

        try:
            left_side = wfm[: max_idx + 1]
            right_side = wfm[max_idx:]

            left_idx = int(_np.abs(left_side - half_max).argmin())
            right_idx = int(_np.abs(right_side - half_max).argmin() + max_idx)

            fwhm_idx = right_idx - left_idx
            fwhm_tim = float(tim[right_idx] - tim[left_idx])
        except (IndexError, ValueError):
            fwhm_idx = 0
            fwhm_tim = 0.0

        return wfm_maxmin, (max_tim, fwhm_tim), (max_idx, fwhm_idx)

    def _extract_operand(self, other):
        """Extract array or scalar operand for arithmetic operations.

        Args:
            other (Waveform | numpy.ndarray | float | int): Other operand.

        Returns:
            Processed array, scalar, or NotImplemented flag.

        Raises:
            ValueError: If other Waveform instance has a different time grid.
        """
        if isinstance(other, Waveform):
            if not _np.array_equal(self._tim, other.tim):
                raise ValueError(
                    "Waveform instances must share the same time grid."
                )
            return other.wfm
        if isinstance(other, (float, int, _np.ndarray)):
            return other
        return NotImplemented

    def __add__(self, other):
        """Add another waveform, array, or scalar to current signal.

        Args:
            other (Waveform | numpy.ndarray | float | int): Operand to add.

        Returns:
            New Waveform instance with sum result.
        """
        operand = self._extract_operand(other)
        if operand is NotImplemented:
            return NotImplemented
        return Waveform(self._tim, self._wfm + operand)

    def __radd__(self, other):
        """Reverse addition operator.

        Args:
            other (Waveform | numpy.ndarray | float | int): Operand to add.

        Returns:
            New Waveform instance with sum result.
        """
        return self.__add__(other)

    def __sub__(self, other):
        """Subtract another waveform, array, or scalar from current signal.

        Args:
            other (Waveform | numpy.ndarray | float | int): Operand to subtract.

        Returns:
            New Waveform instance with difference result.
        """
        operand = self._extract_operand(other)
        if operand is NotImplemented:
            return NotImplemented
        return Waveform(self._tim, self._wfm - operand)

    def __rsub__(self, other):
        """Reverse subtraction operator.

        Args:
            other (Waveform | numpy.ndarray | float | int): Value to subtract
                current signal from.

        Returns:
            New Waveform instance with difference result.
        """
        operand = self._extract_operand(other)
        if operand is NotImplemented:
            return NotImplemented
        return Waveform(self._tim, operand - self._wfm)

    def __mul__(self, other):
        """Multiply waveform by another waveform, array, or scalar.

        Args:
            other (Waveform | numpy.ndarray | float | int): Multiplier operand.

        Returns:
            New Waveform instance with product result.
        """
        operand = self._extract_operand(other)
        if operand is NotImplemented:
            return NotImplemented
        return Waveform(self._tim, self._wfm * operand)

    def __rmul__(self, other):
        """Reverse multiplication operator.

        Args:
            other (Waveform | numpy.ndarray | float | int): Multiplier operand.

        Returns:
            New Waveform instance with product result.
        """
        return self.__mul__(other)

    def __truediv__(self, other):
        """Divide waveform by another waveform, array, or scalar.

        Args:
            other (Waveform | numpy.ndarray | float | int): Divisor operand.

        Returns:
            New Waveform instance with quotient result.
        """
        operand = self._extract_operand(other)
        if operand is NotImplemented:
            return NotImplemented
        return Waveform(self._tim, self._wfm / operand)

    def __len__(self):
        """Return number of sample points in signal.

        Returns:
            Number of elements in signal array.
        """
        return len(self._wfm)

    def __repr__(self):
        """Return string representation of Waveform instance.

        Returns:
            Formal string representation with points, time range, and peak.
        """
        return (
            f"Waveform(points={len(self)}, "
            f"t_range=[{self._tim[0]:.3e}, {self._tim[-1]:.3e}], "
            f"peak_val={self._wfm_maxmin[0]:.3f})"
        )


class WaveformUtils:
    """ASCII-encoded waveform normalization and conversion utilities."""

    GAUSS = (
        '/Td6WFoAAATm1rRGAgAhARYAAAB0L+Wj4AfPA+ddAABv/frHxJZsZ4FTQ5mWJfkPoLLhem'
        'frqGGWgTv30h2fJ6n/PlHAOJ4LGbZlxVNGEycO2Dp1W/mjTtvg0rTCzgOok2L2eZbNJ0un'
        'CD6BaP/HYDuBnO2IwIAqOYH9adCfblcIF1zkOhXOLv6+7b0sIewjvU7KGAvu5ehZI0smF4'
        'bptJT3gCiWtqNlfN9G9MXBfq/Frazix8q7ga5Vl66QsCcnta/+GiR7TpY1qk8e8BXk/9VD'
        'jz/zuI56Xb/qfIuFjm8aCpb6VdXF/oncFgIyGMUEyjFAx0iZ0P/qlN8oX9fk2mS4Hm6lI9'
        'uHxUxFZbULhhtSqdMy8Wq3sgXPQ2MTUsSpdCN0xkLWldfoioOx6cBo6K6SH79ba7QWlG51'
        'ebA0cDULRavvfYXemBhfdqTzLss1pfZgqIxA/vnbKRqpBEJjiRn5opaRG/Yb7SjeKvZ8sx'
        'N46o3SJ0x+3ZE8cuQ4aHL31UY3PWQPQJ82oFfeVU/1FOeGY9W/4/R9w1LuhOCQj56EEk1V'
        'YszAeaN3RkRURqq3FJ5HCO6ra19H/EaYZ44NkyadIy7G49ahQGtqNTYkP6vcNzjBoq7RqP'
        '/xDZi3eR7hTSELCVpdlAdVxdh8jtmt/FaLyCpIvVSDvXmYQVfIGNFjMrEsA7D5YgNj+isy'
        'cQ8ahlb2+f5QX54nKn0dIY79JpWjiV13wW3EOs4yLeGqF6/v3Hv++EoysuHXoS8P+bB2f9'
        'm33YzcN5urtNJHOO5XYfCyuHVGPQ5u0AF9J7/PV7kZ4bj2LxIFSde1bixb8iD+n9Hwk4ub'
        '4gB6202yIyCufw9OXc5xqdB9ntax+JcCOdq59Hq1jaR+L/B24VJlFui4xXeJnz0V28zvFF'
        'auzPnIoW/ahnG+MnOgSkz7oXBMlemNFz9jkj0kp/ahxUpVbp+a7OwmU77+va/QliscP/Di'
        'xTDieDSZEaFo7ESHm1ttmj9zPAXH4VSQsUwZHfnvDD71fpvyOrX+zKARGb8DXm6xIVudHH'
        'ceLAQ6gfp8sLWYxP2X8Gyh5rb9TC48byIAFBYd2ahu1ZIOS1qxYlTK1KM/3fXJTWfovBHr'
        'f8NUM3MktVyOsQosdOAeIrcuMQLNkAZiVxW66KenKqJFiFz84km5ab2uaO8cWpmF5xsVJ1'
        'b1BQn91e5AACbnlya5tFBrY6oGSzl04+Q2M/OkSx+0EG53F0aQjHRxwRMqgV6Rs6xuyx34'
        'M3CMx22hvnzE5RimLUCpiJzSCbkLdniuA4Xu+kpZ1cs7vUQ363WH2Ek/m2LVw6q+f9euNt'
        'tNpPEkcA4VqENpApBftKkDU60PtXfp0zuEZc1A39mhAAAAKxXlZo+M7yYAAYMI0A8AAM4H'
        'CUaxxGf7AgAAAAAEWVo='
    )

    @staticmethod
    def curve_to_ascii(curve):
        """Compress and encode a normalized curve array into a Base64 string.

        Args:
            curve (numpy.ndarray): Input float array with values normalized in
                the range [0, 1].

        Returns:
            str: LZMA-compressed and Base64 ASCII-encoded string.

        Raises:
            RuntimeError: If the 'lzma' module is not available in system.
        """
        if _lzma is None:
            raise RuntimeError(
                "The 'lzma' module is required for curve conversion."
            )
        quantized = _np.clip(_np.round(curve * 65535), 0, 65535).astype(
            _np.uint16
        )
        compressed = _lzma.compress(quantized.tobytes())
        return _base64.b64encode(compressed).decode('ascii')

    @staticmethod
    def ascii_to_curve(ascii_str):
        """Decode and decompress an ASCII string back into a curve array.

        Args:
            ascii_str (str): LZMA-compressed and Base64 ASCII-encoded string.

        Returns:
            numpy.ndarray: Reconstructed float array normalized to range [0, 1].

        Raises:
            RuntimeError: If the 'lzma' module is not available in system.
        """
        if _lzma is None:
            raise RuntimeError(
                "The 'lzma' module is required for curve conversion."
            )
        compressed = _base64.b64decode(ascii_str.encode('ascii'))
        raw_bytes = _lzma.decompress(compressed)
        return _np.frombuffer(raw_bytes, dtype=_np.uint16) / 65535.0

    @staticmethod
    def conv_normalized(
        wfm_norm, nrpts, amplitude=1.0, offset=0.0, tim_init=0.0, tim_final=1.0
    ):
        """Resample a normalized waveform and scale it over a time grid.

        Args:
            wfm_norm (numpy.ndarray): Base normalized waveform array.
            nrpts (int): Number of desired sample points in output grid.
            amplitude (float, optional): Scaling factor for signal amplitude.
                Defaults to 1.0.
            offset (float, optional): Vertical offset added to signal.
                Defaults to 0.0.
            tim_init (float, optional): Initial time value [s].
                Defaults to 0.0.
            tim_final (float, optional): Final time value [s].
                Defaults to 1.0.

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: Tuple containing:
                - tim_interp (numpy.ndarray): Resampled time array [s].
                - wfm_interp (numpy.ndarray): Scaled signal amplitude array.
        """
        tim_origin = _np.linspace(tim_init, tim_final, len(wfm_norm))
        tim_interp = _np.linspace(tim_init, tim_final, nrpts)
        wfm_interp = _np.interp(
            tim_interp, tim_origin, wfm_norm, left=0.0, right=0.0
        )
        return tim_interp, amplitude * wfm_interp + offset

    @staticmethod
    def gen_uniform(
        wfm=None, nrpts=None, tim_beg=None, tim_end=None, amp=None
    ):
        """Generate a uniform constant signal array over a time grid.

        If an existing Waveform object is provided as a template, its point count,
        time boundaries, and average amplitude value are used as fallback defaults,
        unless explicitly overridden by the arguments. If no template waveform
        is provided, all individual parameters must be explicitly specified.

        Args:
            wfm (Waveform, optional): Reference Waveform object to use as a
                template for grid parameters and average amplitude.
                Defaults to None.
            nrpts (int, optional): Number of sample points.
                Defaults to len(wfm) if wfm is provided.
            tim_beg (float, optional): Initial time value [s].
                Defaults to wfm.tim[0] if wfm is provided.
            tim_end (float, optional): Final time value [s].
                Defaults to wfm.tim[-1] if wfm is provided.
            amp (float, optional): Constant signal amplitude value.
                Defaults to mean of wfm.wfm if wfm is provided.

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: Tuple containing:
                - tim (numpy.ndarray): Generated time array [s].
                - wfm (numpy.ndarray): Constant amplitude signal array.

        Raises:
            ValueError: If 'wfm' is None and any required parameter (nrpts,
                tim_beg, tim_end, or amp) is omitted.
        """
        if wfm is not None:
            nrpts = len(wfm) if nrpts is None else nrpts
            tim_beg = wfm.tim[0] if tim_beg is None else tim_beg
            tim_end = wfm.tim[-1] if tim_end is None else tim_end
            amp = float(_np.mean(wfm.wfm)) if amp is None else amp
        if None in (nrpts, tim_beg, tim_end, amp):
            raise ValueError(
                'All parameters must be specified if no reference '
                'waveform is provided.'
            )
        tim = _np.linspace(tim_beg, tim_end, nrpts)
        wfm_arr = _np.full(nrpts, amp, dtype=_np.float64)
        return Waveform(tim, wfm_arr)

    @staticmethod
    def gen_sine(
        wfm=None,
        nrpts=None,
        period=None,
        tim_init=None,
        tim_final=None,
        phase=0.0,
        amplitude=None,
        offset=None,
    ):
        """Generate a sinusoidal waveform over a specified time grid.

        If an existing Waveform object is provided as a template, its point count,
        time boundaries, peak amplitude scale, and vertical offset are used as
        fallback defaults, unless explicitly overridden by the arguments. If no
        template waveform is provided, all positional grid, period, and amplitude
        parameters must be explicitly specified.

        Args:
            wfm (Waveform, optional): Reference Waveform object to use as a
                template for grid parameters and amplitude bounds.
                Defaults to None.
            nrpts (int, optional): Number of sample points.
                Defaults to len(wfm) if wfm is provided.
            period (float, optional): Signal period in time units [s].
                Defaults to time range span (wfm.tim[-1] - wfm.tim[0]) if wfm
                is provided.
            tim_init (float, optional): Initial time value [s].
                Defaults to wfm.tim[0] if wfm is provided.
            tim_final (float, optional): Final time value [s].
                Defaults to wfm.tim[-1] if wfm is provided.
            phase (float, optional): Phase shift in radians [rad].
                Defaults to 0.0.
            amplitude (float, optional): Peak amplitude scaling factor.
                Defaults to half peak-to-peak amplitude of wfm if wfm is provided.
            offset (float, optional): Vertical signal offset.
                Defaults to mean of wfm.wfm if wfm is provided.

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: Tuple containing:
                - tim (numpy.ndarray): Time array [s].
                - wfm (numpy.ndarray): Sinusoidal amplitude array.

        Raises:
            ValueError: If 'wfm' is None and any required parameter (nrpts,
                period, tim_init, tim_final, amplitude, or offset) is omitted.
        """
        if wfm is not None:
            nrpts = len(wfm) if nrpts is None else nrpts
            tim_init = wfm.tim[0] if tim_init is None else tim_init
            tim_final = wfm.tim[-1] if tim_final is None else tim_final
            period = float(tim_final - tim_init) if period is None else period
            if amplitude is None:
                p2p = wfm.wfm_maxmin[0] - wfm.wfm_maxmin[1]
                amplitude = float(p2p / 2.0)
            offset = float(_np.mean(wfm.wfm)) if offset is None else offset

        if None in (nrpts, period, tim_init, tim_final, amplitude, offset):
            raise ValueError(
                'All parameters must be specified if no reference '
                'waveform is provided.'
            )

        tim = _np.linspace(tim_init, tim_final, nrpts)
        sinf = _np.sin(2 * _np.pi * tim / period + phase)
        wfm_arr = amplitude * sinf + offset
        return Waveform(tim, wfm_arr)

    @staticmethod
    def gen_gauss(
        wfm=None,
        nrpts=None,
        sigma=None,
        avg=0.5,
        tim_init=None,
        tim_final=None,
        amplitude=None,
        offset=None,
    ):
        """Generate a Gaussian pulse waveform over a specified time grid.

        If an existing Waveform object is provided as a template, its point count,
        time boundaries, peak amplitude scale, and minimum baseline offset are
        used as fallback defaults, unless explicitly overridden by the arguments.
        If no template waveform is provided, all positional grid, sigma, and
        amplitude parameters must be explicitly specified.

        Args:
            wfm (Waveform, optional): Reference Waveform object to use as a
                template for grid parameters and amplitude bounds.
                Defaults to None.
            nrpts (int, optional): Number of sample points.
                Defaults to len(wfm) if wfm is provided.
            sigma (float, optional): Standard deviation relative to total time span.
                Defaults to 0.1 if wfm is provided.
            avg (float, optional): Fractional peak center position in range
                [0, 1]. Defaults to 0.5 (middle of interval).
            tim_init (float, optional): Initial time value [s].
                Defaults to wfm.tim[0] if wfm is provided.
            tim_final (float, optional): Final time value [s].
                Defaults to wfm.tim[-1] if wfm is provided.
            amplitude (float, optional): Peak amplitude scaling factor.
                Defaults to peak-to-peak amplitude (max - min) of wfm if wfm is provided.
            offset (float, optional): Vertical signal offset.
                Defaults to minimum amplitude value of wfm if wfm is provided.

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: Tuple containing:
                - tim (numpy.ndarray): Time array [s].
                - wfm (numpy.ndarray): Gaussian pulse amplitude array.

        Raises:
            ValueError: If 'wfm' is None and any required parameter (nrpts,
                sigma, tim_init, tim_final, amplitude, or offset) is omitted.
        """
        if wfm is not None:
            nrpts = len(wfm) if nrpts is None else nrpts
            tim_init = wfm.tim[0] if tim_init is None else tim_init
            tim_final = wfm.tim[-1] if tim_final is None else tim_final
            sigma = 0.1 if sigma is None else sigma

            if amplitude is None:
                amplitude = float(wfm.wfm_maxmin[0] - wfm.wfm_maxmin[1])
            if offset is None:
                offset = float(wfm.wfm_maxmin[1])

        if None in (nrpts, sigma, tim_init, tim_final, amplitude, offset):
            raise ValueError(
                'All parameters must be specified if no reference '
                'waveform is provided.'
            )

        tim = _np.linspace(tim_init, tim_final, nrpts)
        time_span = tim_final - tim_init
        avg_val = tim_init + avg * time_span
        sigma_val = sigma * time_span
        gaussf = _np.exp(-0.5 * ((tim - avg_val) / sigma_val) ** 2)
        wfm_arr = amplitude * gaussf + offset
        return Waveform(tim, wfm_arr)
