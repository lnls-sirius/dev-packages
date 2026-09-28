"""ASCII-encoded waveform normalization and conversion utilities."""

import base64 as _base64

try:
    import lzma as _lzma
except ModuleNotFoundError:
    _lzma = None

import numpy as _np


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
    def gen_uniform(nrpts, tim_init=0.0, tim_final=1.0, amplitude=1.0):
        """Generate a uniform constant signal array over a time grid.

        Args:
            nrpts (int): Number of sample points.
            tim_init (float, optional): Initial time value [s].
                Defaults to 0.0.
            tim_final (float, optional): Final time value [s].
                Defaults to 1.0.
            amplitude (float, optional): Constant signal amplitude value.
                Defaults to 1.0.

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: Tuple containing:
                - tim (numpy.ndarray): Generated time array [s].
                - wfm (numpy.ndarray): Constant amplitude signal array.
        """
        tim = _np.linspace(tim_init, tim_final, nrpts)
        wfm = _np.full(nrpts, amplitude, dtype=_np.float64)
        return tim, wfm

    @staticmethod
    def gen_sine(
        nrpts,
        period,
        tim_init=0.0,
        tim_final=1.0,
        phase=0.0,
        amplitude=1.0,
        offset=0.0,
    ):
        """Generate a sinusoidal waveform over a specified time grid.

        Args:
            nrpts (int): Number of sample points.
            period (float): Signal period in time units [s].
            tim_init (float, optional): Initial time value [s].
                Defaults to 0.0.
            tim_final (float, optional): Final time value [s].
                Defaults to 1.0.
            phase (float, optional): Phase shift in radians [rad].
                Defaults to 0.0.
            amplitude (float, optional): Peak amplitude scaling factor.
                Defaults to 1.0.
            offset (float, optional): Vertical signal offset.
                Defaults to 0.0.

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: Tuple containing:
                - tim (numpy.ndarray): Time array [s].
                - wfm (numpy.ndarray): Sinusoidal amplitude array.
        """
        tim = _np.linspace(tim_init, tim_final, nrpts)
        sinf = _np.sin(2 * _np.pi * tim / period + phase)
        return tim, amplitude * sinf + offset

    @staticmethod
    def gen_gauss(
        nrpts,
        sigma,
        avg=None,
        tim_init=0.0,
        tim_final=1.0,
        amplitude=1.0,
        offset=0.0,
    ):
        """Generate a Gaussian pulse waveform over a specified time grid.

        Args:
            nrpts (int): Number of sample points.
            sigma (float): Standard deviation relative to total time span.
            avg (float, optional): Fractional peak center position in range
                [0, 1]. Defaults to 0.5 (middle of interval).
            tim_init (float, optional): Initial time value [s].
                Defaults to 0.0.
            tim_final (float, optional): Final time value [s].
                Defaults to 1.0.
            amplitude (float, optional): Peak amplitude scaling factor.
                Defaults to 1.0.
            offset (float, optional): Vertical signal offset.
                Defaults to 0.0.

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: Tuple containing:
                - tim (numpy.ndarray): Time array [s].
                - wfm (numpy.ndarray): Gaussian pulse amplitude array.
        """
        tim = _np.linspace(tim_init, tim_final, nrpts)
        avg = 0.5 if avg is None else avg
        time_span = tim_final - tim_init
        avg_val = tim_init + avg * time_span
        sigma_val = sigma * time_span
        gaussf = _np.exp(-0.5 * ((tim - avg_val) / sigma_val) ** 2)
        return tim, amplitude * gaussf + offset

    @staticmethod
    def shift_right(wfm, shift):
        """Shift a signal vector to the right by N sample points.

        Left side is padded with the first signal value (wfm[0]).

        Args:
            wfm (numpy.ndarray): Input signal array.
            shift (int): Number of discrete sample points to shift right.

        Returns:
            numpy.ndarray: Shifted signal array copy.
        """
        if shift <= 0:
            return wfm.copy()
        nwfm = _np.full_like(wfm, wfm[0])
        if shift >= len(wfm):
            return nwfm
        nwfm[shift:] = wfm[:-shift]
        return nwfm

    @staticmethod
    def shift_left(wfm, shift):
        """Shift a signal vector to the left by N sample points.

        Right side is padded with the last signal value (wfm[-1]).

        Args:
            wfm (numpy.ndarray): Input signal array.
            shift (int): Number of discrete sample points to shift left.

        Returns:
            numpy.ndarray: Shifted signal array copy.
        """
        if shift <= 0:
            return wfm.copy()
        nwfm = _np.full_like(wfm, wfm[-1])
        if shift >= len(wfm):
            return nwfm
        nwfm[:-shift] = wfm[shift:]
        return nwfm


class Waveform:
    """Discrete temporal waveform representation and processing class."""

    def __init__(self, tim, wfm):
        """Initialize waveform object with time and amplitude vectors.

        Args:
            tim (array_like): Time grid array [s].
            wfm (array_like): Amplitude signal array [V].

        Raises:
            ValueError: If time and waveform vectors have different shapes.
        """
        self._tim = _np.asarray(tim, dtype=_np.float64)
        self._wfm = _np.asarray(wfm, dtype=_np.float64)

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

    def fit_linear_coeffs(self, normalized_vectors):
        """Fit signal as a linear combination of basis vectors using LLSQ.

        Args:
            normalized_vectors (list[Waveform | numpy.ndarray]): List of basis
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
            for vec in normalized_vectors
        ]
        mat_a = _np.column_stack(nvecs)
        coeffs, residues, rank, s = _np.linalg.lstsq(
            mat_a, self._wfm, rcond=None
        )
        wfm_fit = Waveform(self._tim, mat_a @ coeffs)
        return coeffs, residues, wfm_fit, (rank, s)

    def calc_integral(self, calibration_factor=5.0):
        """Calculate area under curve integrated using trapezoidal rule.

        Args:
            calibration_factor (float, optional): Scaling divisor factor.
                Defaults to 5.0.

        Returns:
            Calibrated integral value.
        """
        trapz_func = getattr(_np, "trapezoid", getattr(_np, "trapz"))
        integral = trapz_func(self._wfm, self._tim)
        return float(integral / calibration_factor)

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
