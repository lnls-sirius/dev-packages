"""FamBPM deviceSet."""

import logging as _log
import sys
import time as _time
from copy import deepcopy as _dcopy

import numpy as _np

from ..namesys import SiriusPVName as _PVName
from ..search import BPMSearch as _BPMSearch
from .bpm import BPM
from .device import DeviceSet as _DeviceSet

# from threading import Event as _Flag


class FamBPMs(_DeviceSet):
    """."""

    TIMEOUT = 10
    RFFEATT_MAX = 30
    PROPERTIES_ACQ = BPM.PROPERTIES_ACQ
    PROPERTIES_DEFAULT = BPM.PROPERTIES_DEFAULT
    ALL_MTURN_SIGNALS2ACQ = ('A', 'B', 'C', 'D', 'X', 'Y', 'Q', 'S')

    class DEVICES:
        """."""

        SI = 'SI-Fam:DI-BPM'
        BO = 'BO-Fam:DI-BPM'
        ALL = (BO, SI)

    def __init__(
            self, devname=None, bpmnames=None, ispost_mortem=False,
            props2init='all', mturn_signals2acq=('X', 'Y')):
        """Family of BPMs.

        Args:
            devname (str, optional): Device name. If not provided, defaults to
                DEVICES.SI. Determine the list of BPM names.
            bpmnames ((list, tuple), optional): BPM names list. If provided,
                it takes priority over 'devname' parameter. Defaults to None.
            ispost_mortem (bool, optional):  Whether to control PM acquisition
                core. Defaults to False.
            props2init (str|list|tuple, optional): list of properties to
                initialize in object creation. If a string is passed, it can
                be either "all" or "acq". Defaults to "all".
            mturn_signals2acq (str|list|tuple, optional): Which signals to
                acquire. Signals can be defined by:
                    X: x position;
                    Y: y position;
                    S: antennas sum signal;
                    Q: skew position;
                    A: amplitude of antenna A;
                    B: amplitude of antenna B;
                    C: amplitude of antenna C;
                    D: amplitude of antenna D.
                Defaults to "XY".

        """
        if devname is None:
            devname = self.DEVICES.SI
        if devname not in self.DEVICES.ALL:
            raise ValueError('Wrong value for devname')

        devname = _PVName(devname)
        bpm_names = bpmnames or _BPMSearch.get_names(
            filters={'sec': devname.sec, 'dev': devname.dev})
        self._ispost_mortem = ispost_mortem

        self._mturn_signals2acq = ''
        self.bpms = [BPM(
            dev, auto_monitor_mon=False, ispost_mortem=ispost_mortem,
            props2init=props2init) for dev in bpm_names]

        # use property here to ensure auto_monitor
        self.mturn_signals2acq = list(mturn_signals2acq)

        super().__init__(self.bpms[:], devname=devname)
        self._bpm_names = bpm_names
        self._csbpm = self.bpms[0].csdata
        self._initial_timestamps = None
        self._initial_signals = None

        self._mturn_flags = dict()
        # NOTE: ACQCount-Mon need to be fixed on BPM's IOC
        # for bpm in devs:
        #     pvo = bpm.pv_object('ACQCount-Mon')
        #     pvo.auto_monitor = True
        #     self._mturn_flags[pvo.pvname] = _Flag()
        #     pvo.add_callback(self._set_mturn_flag)

    @property
    def bpm_names(self):
        """Return BPM names."""
        return self._bpm_names

    @property
    def csbpm(self):
        """Return control system BPM constants class."""
        return self._csbpm

    @property
    def mturn_signals2acq(self):
        """Return which signals will be acquired by get_mturn_signals."""
        return _dcopy(self._mturn_signals2acq)

    @mturn_signals2acq.setter
    def mturn_signals2acq(self, sigs):
        sigs = [s.upper() for s in sigs]
        diff = set(sigs) - set(self.ALL_MTURN_SIGNALS2ACQ)
        if diff:
            raise ValueError('The following signals do not exist: '+str(diff))
        self._configure_automonitor_acquisition_pvs(state=False)
        self._mturn_signals2acq = sigs
        self._configure_automonitor_acquisition_pvs(state=True)

    @staticmethod
    def calc_positions_from_amplitudes(
        amps, gainx=None, gainy=None, offx=0.0, offy=0.0
    ):
        """Calculate transverse positions from antennas amplitudes.

        Args:
            amps (list|numpy.ndarray, (4, ...)): A list or N-D array
                containing the amplitudes of the four antennas in the order
                A, B, C, D.
            gainx (float|numpy.ndarray, optional): Horizontal gain in [um]. If
                None, then the nominal value of 12/sqrt(2) of the storage ring
                will be used. Defaults to None. An array can be used to
                specify different values for each BPM. In this case the gain
                array must match the shape of the antennas arrays or satisfy
                the broadcast rules in relation to them.
            gainy (float|numpy.ndarray, optional): Vertical gain in [um]. If
                None, then the nominal value of 12/sqrt(2) of the storage ring
                will be used. Defaults to None. An array can be used to
                specify different values for each BPM. In this case the gain
                array must match the shape of the antennas arrays or satisfy
                the broadcast rules in relation to them.
            offx (float|numpy.ndarray, optional): Horizontal offset in [um].
                Defaults to 0.0. An array can be used to specify different
                values for each BPM. In this case the gain array must match
                the shape of the antennas arrays or satisfy the broadcast
                rules in relation to them.
            offy (float|numpy.ndarray, optional): Vertical offset in [um].
                Defaults to 0.0. An array can be used to specify different
                values for each BPM. In this case the gain array must match
                the shape of the antennas arrays or satisfy the broadcast
                rules in relation to them.

        Returns:
            posx (numpy.ndarray, (...)): Horizontal position in [um]. Same
                shape of antennas array.
            posy (numpy.ndarray, (...)): Vertical position in [um]. Same
                shape of antennas array.

        """
        a, b, c, d = amps

        radius = 12e3  # [um]
        gainx = radius / _np.sqrt(2) if gainx is None else gainx
        gainy = radius / _np.sqrt(2) if gainy is None else gainy
        gainx = _np.atleast_1d(gainx)
        gainy = _np.atleast_1d(gainy)
        offx = _np.atleast_1d(offx)
        offy = _np.atleast_1d(offy)

        # Calculate difference over sum for each pair
        a_c = (a - c) / (a + c)
        b_d = (b - d) / (b + d)
        # Get the positions:
        posx = (a_c - b_d) / 2
        posy = (a_c + b_d) / 2
        # Apply position gains:
        posx *= gainx
        posy *= gainy
        # Subtract offsets:
        posx -= offx
        posy -= offy
        return posx, posy

    def set_attenuation(self, value=RFFEATT_MAX, timeout=TIMEOUT):
        """."""
        for bpm in self:
            bpm.rffe_att = value

        mstr = ''
        okall = True
        t0 = _time.time()
        for bpm in self:
            tout = timeout - (_time.time() - t0)
            if not bpm._wait('RFFEAtt-RB', value, timeout=tout):
                okall = False
                mstr += (
                    f'\n{bpm.devname:<20s}: ' +
                    f'rb {bpm.rffe_att:.0f} != sp {value:.0f}')

        stg = ', except:' if mstr else '.'
        _log.info('RFFE attenuation set confirmed in all BPMs%s', stg)
        if mstr:
            _log.info(mstr)
        return okall

    def get_slow_orbit(self):
        """Get slow orbit vectors.

        Returns:
            orbx (numpy.ndarray, 160): Horizontal Orbit.
            orby (numpy.ndarray, 160): Vertical Orbit.

        """
        orbx, orby = [], []
        for bpm in self.bpms:
            orbx.append(bpm.posx)
            orby.append(bpm.posy)
        orbx = _np.array(orbx)
        orby = _np.array(orby)
        return orbx, orby

    def get_mturn_signals(self):
        """Get Multiturn signals matrices.

        Returns:
            list: Each component of the list is an numpy.ndarray with shape
                (N, 160), containing the values for the signals acquired.

        """
        sigs = [[] for _ in self._mturn_signals2acq]

        mini = int(sys.maxsize)  # a very large integer
        for bpm in self.bpms:
            for i, sn in enumerate(self._mturn_signals2acq):
                sn = 'sum' if sn == 'S' else sn.lower()
                name = 'mt_' + ('ampl' if sn in 'abcd' else 'pos') + sn
                sigs[i].append(getattr(bpm, name))
            mini = min(mini, _np.min([s[-1].size for s in sigs]))

        for i, sig in enumerate(sigs):
            for j, s in enumerate(sig):
                sig[j] = s[:mini]
            sigs[i] = _np.array(sig).T
        return sigs

    def get_mturn_timestamps(self):
        """Get Multiturn data timestamps.

        Returns:
            tsmps (numpy.ndarray, (N, 160)): The i-th column has the timestamp
                of the i-th bpm for the N aquired signals.

        """
        tsmps = _np.zeros(
            (len(self._mturn_signals2acq), len(self.bpms)), dtype=float)
        for i, s in enumerate(self._mturn_signals2acq):
            for j, bpm in enumerate(self.bpms):
                s = 'SUM' if s == 'S' else s
                pvo = bpm.pv_object(f'GEN_{s}ArrayData')
                tv = pvo.get_timevars(timeout=self.TIMEOUT)
                tsmps[i, j] = pvo.timestamp if tv is None else tv['timestamp']
        return tsmps

    def get_sampling_frequency(self, rf_freq: float, acq_rate='') -> float:
        """Return the sampling frequency of the acquisition.

        Args:
            rf_freq (float): RF frequency.
            acq_rate (str, optional): acquisition rate. Defaults to ''.
            If empty string, it gets the configured acq. rate on BPMs

        Returns:
            float: acquisition frequency.

        """
        fs_bpms = {
            dev.get_sampling_frequency(rf_freq, acq_rate)
            for dev in self.bpms}
        if len(fs_bpms) == 1:
            return fs_bpms.pop()
        else:
            _log.warning('BPMs are not configured with the same ACQChannel.')
            return None

    def get_switching_frequency(self, rf_freq: float) -> float:
        """Return the switching frequency.

        Args:
            rf_freq (float): RF frequency.

        Returns:
            float: switching frequency.

        """
        fsw_bpms = {
            dev.get_switching_frequency(rf_freq) for dev in self.bpms}
        if len(fsw_bpms) == 1:
            return fsw_bpms.pop()
        else:
            _log.warning('BPMs are not configured with the same SwMode.')
            return None

    def config_mturn_acquisition(
            self, nr_points_after: int, nr_points_before=0,
            acq_rate='FAcq', repeat=True, external=True) -> int:
        """Configure acquisition for BPMs.

        Args:
            nr_points_after (int): number of points after trigger.
            nr_points_before (int): number of points after trigger.
                Defaults to 0.
            acq_rate (int|str, optional): Acquisition rate name ('TbT',
                'TbTPha', 'FOFB', 'FOFBPha', 'FAcq', 'ADC', 'ADCSwp') or value.
                Defaults to 'FAcq'.
            repeat (bool, optional): Whether or not acquisition should be
                repetitive. Defaults to True.
            external (bool, optional): Whether or not external trigger should
                be used. Defaults to True.

        Returns:
            int: code describing what happened:
                =0: BPMs are ready.
                <0: Index of the first BPM which did not stop last acq. plus 1.
                >0: Index of the first BPM which is not ready for acq. plus 1.

        """
        dic = {
            'facq': self._csbpm.AcqChan.FAcq,
            'fofbpha': self._csbpm.AcqChan.FOFBPha,
            'fofb': self._csbpm.AcqChan.FOFB,
            'tbtpha': self._csbpm.AcqChan.TbTPha,
            'tbt': self._csbpm.AcqChan.TbT,
            'adcswp': self._csbpm.AcqChan.ADCSwp,
            'adc': self._csbpm.AcqChan.ADC,
        }
        if isinstance(acq_rate, str):
            acq_rate = dic.get(acq_rate.lower())
        if acq_rate not in self._csbpm.AcqChan:
            raise ValueError(
                str(acq_rate) + ' is not a valid acquisition rate.')

        rep = self._csbpm.AcqRepeat.Normal
        if repeat:
            rep = self._csbpm.AcqRepeat.Repetitive

        trig = self._csbpm.AcqTrigTyp.Now
        if external:
            trig = self._csbpm.AcqTrigTyp.External

        ret = self.cmd_abort_mturn_acquisition()
        if ret > 0:
            return -ret

        for bpm in self.bpms:
            bpm.acq_repeat = rep
            bpm.acq_channel = acq_rate
            bpm.acq_trigger = trig
            bpm.acq_nrsamples_pre = nr_points_before
            bpm.acq_nrsamples_post = nr_points_after

        return self.cmd_start_mturn_acquisition()

    def cmd_abort_mturn_acquisition(self, wait=True, timeout=10) -> int:
        """Abort BPMs acquistion.

        Args:
            wait (bool, optional): whether or not to wait BPMs get ready.
                Defaults to True.
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: BPMs are ready.
                >0: Index of the first BPM which did not update plus 1.

        """
        for bpm in self.bpms:
            bpm.acq_ctrl = self._csbpm.AcqEvents.Abort

        if wait:
            return self.wait_acquisition_finish(timeout=timeout)
        return 0

    def wait_acquisition_finish(self, timeout=10) -> int:
        """Wait for all BPMs to be ready for acquisition.

        Args:
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: BPMs are ready.
                >0: Index of the first BPM which did not update plus 1.

        """
        for i, bpm in enumerate(self.bpms):
            t0_ = _time.time()
            if not bpm.wait_acq_finish(timeout):
                return i + 1
            timeout -= _time.time() - t0_
        return 0

    def cmd_start_mturn_acquisition(self, wait=True, timeout=10) -> int:
        """Start BPMs acquisition.

        Args:
            wait (bool, optional): whether or not to wait BPMs get ready.
                Defaults to True.
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: BPMs are ready.
                >0: Index of the first BPM which did not update plus 1.

        """
        for bpm in self.bpms:
            bpm.acq_ctrl = self._csbpm.AcqEvents.Start
        if wait:
            return self.wait_acquisition_start(timeout=timeout)
        return 0

    def wait_acquisition_start(self, timeout=10) -> bool:
        """Wait for all BPMs to be ready for acquisition.

        Args:
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: BPMs are ready.
                >0: Index of the first BPM which did not update plus 1.

        """
        for i, bpm in enumerate(self.bpms):
            t0_ = _time.time()
            if not bpm.wait_acq_start(timeout):
                return i + 1
            timeout -= _time.time() - t0_
        return 0

    def set_switching_mode(self, mode='direct'):
        """Set switching mode of BPMS.

        Args:
            mode ((str, int), optional): Desired mode, must be in
                {'direct', 'switching', 1, 3}. Defaults to 'direct'.

        Raises:
            ValueError: When mode is not in {'direct', 'switching', 1, 3}.

        """
        if mode not in ('direct', 'switching', 1, 3):
            raise ValueError('Value must be in ("direct", "switching", 1, 3).')

        for bpm in self.bpms:
            bpm.switching_mode = mode

    def update_mturn_initial_signals(self):
        """Call this method before acquisition to get orbit for comparison."""
        sig = _np.array(self.get_mturn_signals())
        self._initial_signals = sig if sig.shape[1] != 0 else None

    def update_mturn_initial_timestamps(self):
        """Call this method before acquisition to get orbit for comparison."""
        self._initial_timestamps = self.get_mturn_timestamps()

    def reset_mturn_flags(self):
        """Reset Multiturn flags to wait for a new orbit update."""
        for flag in self._mturn_flags.values():
            flag.clear()

    def reset_mturn_initial_state(self):
        """Set initial state to wait for orbit acquisition to start."""
        self.reset_mturn_flags()
        self.update_mturn_initial_timestamps()
        self.update_mturn_initial_signals()

    def wait_update_mturn_flags(self, timeout=10):
        """Wait for all acquisition flags to be updated.

        Args:
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: BPMs are ready.
                >0: Index of the first BPM which did not update plus 1.

        """
        for i, flag in enumerate(self._mturn_flags.values()):
            t00 = _time.time()
            if not flag.wait(timeout=timeout):
                return i + 1
            timeout -= _time.time() - t00
            timeout = max(timeout, 0)
        return 0

    def wait_update_mturn_timestamps(self, timeout=10) -> int:
        """Call this method after acquisition to check for timestamps update.

        For this method to work it is necessary to call
            update_mturn_initial_timestamps
        before the acquisition starts, so that a reference for comparison is
        created.

        Args:
            timeout (int, optional): Waiting timeout. Defaults to 10.

        Returns:
            int|float: code describing what happened:
                -2: size of timestamps changed in relation to initial timestamp
                -1: initial timestamps were not defined;
                =0: data updated.
                >0: timeout waiting BPMs. The returned value is a float of
                    form X.Y, where:
                        X: The integer part indicates the index of the first
                            BPM which did not update plus 1.
                        Y: The fractional part indicates which signal, from
                            1 to N, that didn't update.

        """
        if self._initial_timestamps is None:
            return -1

        tsmp0 = self._initial_timestamps
        while timeout > 0:
            t00 = _time.time()
            tsmp = self.get_mturn_timestamps()
            if tsmp.shape != tsmp0.shape:
                return -2
            errors = _np.equal(tsmp, tsmp0)
            if not _np.any(errors):
                return 0
            _time.sleep(0.1)
            timeout -= _time.time() - t00

        bpm_idx = int(_np.nonzero(_np.any(errors, axis=0))[0][0])
        code = bpm_idx + 1
        code += (int(_np.nonzero(errors[:, bpm_idx])[0][0]) + 1) / 10
        return code

    def wait_update_mturn_signals(self, timeout=10) -> int:
        """Call this method after acquisition to check for data update.

        For this method to work it is necessary to call
            update_mturn_initial_signals
        before the acquisition starts, so that a reference for comparison is
        created.

        Args:
            timeout (int, optional): Waiting timeout. Defaults to 10.

        Returns:
            int|float: code describing what happened:
                -2: size of signals is 0;
                -1: initial signals were not defined;
                =0: signals updated.
                >0: timeout waiting BPMs. The returned value is a float of
                    form X.Y, where:
                        X: The integer part indicates the index of the first
                            BPM which did not update plus 1.
                        Y: The fractional part indicates which signal, from
                            1 to N, that didn't update.

        """
        if self._initial_signals is None:
            return -1

        sig0 = self._initial_signals
        while timeout > 0:
            t00 = _time.time()
            sig = _np.array(self.get_mturn_signals())
            siz = min(sig.shape[1], sig0.shape[1])
            if siz == 0:
                return -2
            errors = _np.all(_np.equal(sig[:, :siz], sig0[:, :siz]), axis=1)
            if not _np.any(errors):
                return 0
            _log.debug('Signals did not update yet. Trying again.')
            _time.sleep(0.1)
            timeout -= _time.time() - t00

        bpm_idx = int(_np.nonzero(_np.any(errors, axis=0))[0][0])
        code = bpm_idx + 1
        code += (int(_np.nonzero(errors[:, bpm_idx])[0][0]) + 1) / 10
        return code

    def wait_update_mturn(self, timeout=10) -> int:
        """Combine all methods to wait update data.

        Args:
            timeout (int, optional): Waiting timeout. Defaults to 10.

        Returns:
            int|float: code describing what happened:
                -2: size of timestamps changed in relation to initial timestamp
                -1: initial timestamps were not defined;
                =0: data updated.
                >0: timeout waiting BPMs. The returned value is a float of
                    form X.Y, where:
                        X: The integer part indicates the index of the first
                            BPM which did not update plus 1.
                        Y: The fractional part indicates which signal, from
                            1 to N, that didn't update.

        """
        t00 = _time.time()
        ret = self.wait_update_mturn_flags(timeout)
        if ret > 0:
            return ret
        t01 = _time.time()
        dtime = t01 - t00
        timeout -= dtime
        _log.debug("Flags updated (ETA: %.3fs).", dtime)

        ret = self.wait_update_mturn_timestamps(timeout)
        if ret != 0:
            return ret
        t02 = _time.time()
        dtime = t02 - t01
        timeout -= dtime
        _log.debug("Timestamps updated (ETA: %.3fs).", dtime)

        ret = self.wait_update_mturn_signals(timeout)
        if ret != 0:
            return ret
        dtime = _time.time() - t02
        _log.debug("Data updated (ETA: %.3fs).", dtime)
        return ret

    # ---------------------- Auxiliary methods ------------------------------
    def _configure_automonitor_acquisition_pvs(self, state):
        for bpm in self.bpms:
            for sig in self._mturn_signals2acq:
                sig = 'SUM' if sig.upper() == 'S' else sig.upper()
                bpm.pv_object(f'GEN_{sig}ArrayData').auto_monitor = state

    def _set_mturn_flag(self, pvname, **kwargs):
        _ = kwargs
        self._mturn_flags[pvname].set()
