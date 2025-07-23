"""Main Module of the IOC Logic."""

import logging as _log
import time as _time
from copy import deepcopy as _dcopy
from threading import Thread as _Thread

import numpy as _np
import scipy.optimize as _scyopt
import scipy.signal as _scysig

from ..callbacks import Callback as _Callback
from ..envars import VACA_PREFIX as _VACA_PREFIX
from ..epics import PV as _PV
from ..oscilloscope import Keysight as _Keysight, ScopeSignals as _ScopeSignals
from .csdev import Const as _Const, get_si_fpmosc_database as _get_database


class FPMOscApp(_Callback):
    """Main Class."""
    Const = _Const

    def __init__(self):
        """Class constructor."""
        super().__init__()
        self._pvs_database = _get_database()
        self._prefix = _VACA_PREFIX + ('-' if _VACA_PREFIX else '')

        # initialize vars
        self._time0 = _time.time()
        self._fillpat_fid_offset = 0
        self._fillpat_update_time = 5  # [s]
        self._fillpat_ref = _np.ones(_Const.FP_HARM_NUM) / _Const.FP_HARM_NUM
        self._fillpat_osc = _Keysight(
            scopesignal=_ScopeSignals.SI_FILL_PATTERN
        )
        self._fillpat_thread = None

        # pvs
        self._current_pv = _PV(
            self._prefix+'SI-Glob:AP-CurrInfo:Current-Mon',
            connection_timeout=0.05
        )
        self._rffreq_pv = _PV(
            self._prefix+'RF-Gen:GeneralFreq-RB', connection_timeout=0.05
        )

        self._current_pv.add_callback(self._callback_get_current)

    @property
    def pvs_database(self):
        """."""
        return _dcopy(self._pvs_database)

    def process(self, interval):
        """."""
        _time.sleep(interval)

    def init_database(self):
        """Set initial PV values."""
        self.run_callbacks('UpdateTime-SP', self._fillpat_update_time)
        self.run_callbacks('UpdateTime-RB', self._fillpat_update_time)
        self.run_callbacks('FiducialOffset-SP', self._fillpat_fid_offset)
        self.run_callbacks('FiducialOffset-RB', self._fillpat_fid_offset)
        self.run_callbacks('FillPatternRef-SP', self._fillpat_ref)
        self.run_callbacks('FillPatternRef-RB', self._fillpat_ref)

    def read(self, reason):
        """Read from IOC database."""
        _ = reason
        return None

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        if reason == 'UpdateTime-SP':
            self._fillpat_update_time = min(
                _Const.FP_MAX_UPDT_TIME, max(0, float(value))
            )
            self.run_callbacks('UpdateTime-RB', self._fillpat_update_time)
            return True
        elif reason == 'FiducialOffset-SP':
            self._fillpat_fid_offset = min(
                _Const.FP_HARM_NUM, max(-_Const.FP_HARM_NUM, int(value))
            )
            self.run_callbacks('FiducialOffset-RB', self._fillpat_fid_offset)
            return True
        elif reason == 'FillPatternRef-SP':
            if not isinstance(value, (_np.ndarray, list, tuple)):
                return False
            value = _np.array(value)
            if value.size != 864 or value.min() < 0:
                return False
            self._fillpat_ref = value / value.sum()
            self.run_callbacks('FillPatternRef-RB', self._fillpat_ref)
            return True
        return False

    def _callback_get_current(self, pvname, value, **kws):
        _ = kws, pvname

        # trigger update of filling pattern from oscilloscope.
        if (
            self._fillpat_thread is None or
            not self._fillpat_thread.is_alive()
        ):
            self._fillpat_thread = _Thread(
                target=self._update_filling_pattern,
                args=(value, ),
                daemon=True,
            )
            self._fillpat_thread.start()

    def _update_filling_pattern(self, current):
        t0_ = _time.time()
        frf = 499667557.37  # default value
        if self._rffreq_pv.connected:
            frf = self._rffreq_pv.value
        # first peak in Hilbert transform is compromized by dft issues, so get
        # data starting from second:
        bun_spacing = _np.arange(1, _Const.FP_HARM_NUM + 1) / frf * 1e9  # [ns]

        try:
            tim, fill = self._fillpat_osc.wfm_get_data()
            tim = tim[:_Const.FP_MAX_ARR_SIZE]
            fill = fill[:_Const.FP_MAX_ARR_SIZE]
        except Exception:
            _log.warning('Could not read oscilloscope data.')
            return
        tim *= 1e9  # from [s] to [ns]
        tim -= tim[0]
        fill -= fill.mean()
        # NOTE: I tried to filter the raw data at the harmonics of the
        # revolution frequency, around the RF frequency, but it didn't improve
        # the results. I decided to keep the processing as simple as possible.
        hil = _np.abs(_scysig.hilbert(fill))

        if tim[-1] < bun_spacing[-1]:
            _log.warning('oscilloscope data is incomplete.')
            return

        def get_interp(off, return_res=False):
            tim2ns = bun_spacing + off
            fil2ns = _np.interp(tim2ns, tim, hil)

            if return_res:
                return tim2ns, fil2ns
            hil_max = hil[200:-200].max()  # avoid borders
            weight = fil2ns[fil2ns > hil_max * 20/100]
            obj = weight - hil_max
            return obj * _np.sqrt(weight)

        try:
            init_guess_offset = 0.2  # [ns]
            res = _scyopt.least_squares(get_interp, init_guess_offset)
        except Exception:
            _log.warning('Fitting did not work.')
            return
        tim2ns, fil2ns = get_interp(res.x, return_res=True)
        fid = self._fillpat_fid_offset
        fil2ns = _np.roll(fil2ns, -fid)
        tim2ns = _np.roll(tim2ns, -fid)

        # Scale filling pattern so that its sum is equal to
        # the total current stored
        if current is None:
            _log.warning('Could not read current from DCCT.')
            return
        elif current <= 0.0:
            return
        fac = current / fil2ns.sum()
        fil2ns *= fac
        fill *= fac
        hil *= fac

        # Equivalent current for broad band induced heating. See:
        # https://accelconf.web.cern.ch/ipac2024/pdf/THPC44.pdf
        # for details
        equiv_curr = _np.sqrt(_np.sum(fil2ns**2)*_Const.FP_HARM_NUM)  # [mA]

        avg_curr = current / _Const.FP_HARM_NUM
        filref = self._fillpat_ref * current
        fil_err = _np.std(filref - fil2ns) / avg_curr * 100
        # Compute KL Divergence between distributions:
        idx = self._fillpat_ref > 0
        fil_kld = _np.sum(
            self._fillpat_ref[idx] * _np.log2(filref[idx]/fil2ns[idx]))

        # Update PVs:
        self.run_callbacks('UniFillEqCurrent-Mon', equiv_curr)
        self.run_callbacks('ErrorRelStd-Mon', fil_err)
        self.run_callbacks('ErrorKLDiv-Mon', fil_kld)
        self.run_callbacks('FillPattern-Mon', fil2ns)
        self.run_callbacks('FillPatternRef-Mon', filref)
        self.run_callbacks('Time-Mon', tim2ns)
        self.run_callbacks('TimeOffset-Mon', res.x)
        self.run_callbacks('Raw-Mon', fill)
        self.run_callbacks('RawAmp-Mon', hil)
        self.run_callbacks('RawTime-Mon', tim)

        # This thread is triggered by the update of the current, which is
        # faster than the frequency we want to update the filling pattern.
        # Hence, we need to wait here:
        dt_ = self._fillpat_update_time - (_time.time() - t0_)
        _time.sleep(max(dt_, 0))
