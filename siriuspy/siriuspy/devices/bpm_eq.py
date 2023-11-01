"""."""
import time as _time

import numpy as _np

from mathphys.functions import save_pickle as _savep, load_pickle as _loadp, \
    get_namedtuple as _namedtuple
from .bpm import FamBPMs as _FamBPMs
from .timing import Trigger


class EqualizeBPMs(_FamBPMs):
    """."""

    NR_POINTS = 2000
    MAX_MULTIPLIER = 0xffffff / (1 << 24)
    ProcMethods = _namedtuple('ProcMethods', ('AABS', 'EABS', 'AAES'))
    AcqStrategies = _namedtuple(
        'AcqStrategies', ('AssumeOrder', 'AcqInvRedGain'))

    def __init__(self, bpmnames=None):
        """."""
        self._proc_method = self.ProcMethods.AAES
        self._acq_strategy = self.AcqStrategies.AssumeOrder
        self._acq_inverse_reduced_gain = self.round_gains(0.95)
        self._acq_nrpoints = 2000
        self._acq_timeout = 30
        super().__init__(
            bpmnames=bpmnames, ispost_mortem=False, props2init=[],
            mturn_signals2acq='ABCD')
        self.trigger = Trigger('SI-Fam:TI-BPM', props2init=[])
        self.freq_sampling = 4
        self.freq_switching = 2
        self.data = dict()

    @property
    def acq_strategy_str(self):
        """."""
        return self.AcqStrategies._fields._acq_strategy

    @property
    def acq_strategy(self):
        """."""
        return self._acq_strategy

    @acq_strategy.setter
    def acq_strategy(self, val):
        val = self._enum_selector(val, self.AcqStrategies)
        if val is not None:
            self._acq_strategy = val

    @property
    def acq_inverse_reduced_gain(self):
        """."""
        return self._acq_inverse_reduced_gain

    @acq_inverse_reduced_gain.setter
    def acq_inverse_reduced_gain(self, value):
        self._acq_inverse_reduced_gain = self.round_gains(value)

    @property
    def acq_nrpoints(self):
        """."""
        return self._acq_nrpoints

    @acq_nrpoints.setter
    def acq_nrpoints(self, value):
        if value > 4:
            self._acq_nrpoints = int(value)

    @property
    def acq_timeout(self):
        """."""
        return self._acq_timeout

    @acq_timeout.setter
    def acq_timeout(self, value):
        if value > 0:
            self._acq_timeout = value

    @property
    def proc_method_str(self):
        """."""
        return self.ProcMethods._fields[self._proc_method]

    @property
    def proc_method(self):
        """."""
        return self._proc_method

    @proc_method.setter
    def proc_method(self, meth):
        meth = self._enum_selector(meth, self.ProcMethods)
        if meth is not None:
            self._proc_method = meth

    def get_current_gains(self):
        """Return Current BPM gains as 3D numpy array.

        Returns:
            numpy.ndarray (nrbpms, 4, 2): 3D numpy array with gains.
                 - The first index vary the BPMs, in the default high level
                convention order;
                 - The second index vary the antennas: 'A', 'B', 'C', 'D';
                 - The last index refers to the type of the gain in the
                following order: 'Direct', 'Inverse';

        """
        gains = []
        for bpm in self._devices:
            gaind = [getattr(bpm, f'gain_direct_{a}') for a in 'abcd']
            gaini = [getattr(bpm, f'gain_inverse_{a}') for a in 'abcd']
            gains.append([gaind, gaini])
        gains = _np.array(gains).swapaxes(-1, -2)
        return gains

    def set_gains(self, gains):
        """Set gains matrix to BPMs.

        Args:
            gains (float or numpy.ndarray, (nrbpms, 4, 2)): gain matrix. In
                the same format as the one provided by get_current_gains
                method. If a float is provided, then this same gain will be
                applied to all BPMs.

        Raises:
            ValueError: If gains is a numpy array with wrong shape.

        """
        nbpm = len(self._devices)
        shape = (nbpm, 4, 2)
        if not isinstance(gains, _np.ndarray):
            gains = _np.full(shape, gains)
        if gains.shape != shape:
            raise ValueError(f'Wrong shape for gains. Must be {shape}')

        for i, bpm in enumerate(self._devices):
            gns = gains[i]
            for j, ant in enumerate('abcd'):
                g = gns[j]
                setattr(bpm, f'gain_direct_{ant}', g[0])
                setattr(bpm, f'gain_inverse_{ant}', g[1])

    @staticmethod
    def round_gains(gains):
        """Make gains compatible with 24 bits fixed point representation."""
        mult = 1 << 24
        return _np.int_(gains*mult) / mult

    def acquire_bpm_data(self):
        """."""
        self.data = dict()
        self.data['gains_init'] = self.get_current_gains()

        if self._acq_strategy == self.AcqStrategies.AssumeOrder:
            self.set_gains(self.MAX_MULTIPLIER)
        else:
            gains = _np.full((len(self._devices), 4, 2), self.MAX_MULTIPLIER)
            gains[:, :, 1] *= self._acq_inverse_reduced_gain
            self.set_gains(gains)
        self.data['acq_strategy'] = self._acq_strategy
        self.data['acq_inverse_reduced_gain'] = self._acq_inverse_reduced_gain

        # acquire antennas data in FOFB rate
        ret = self.cmd_mturn_acq_abort()
        if ret > 0:
            self._log(f'ERR: BPM {ret-1} did not abort previous acquistion.')
            return

        init_source = self.trigger.source
        self.trigger.source = self.trigger.source_options.index('Clock3')

        self.mturn_reset_flags_and_update_initial_timestamps()
        ret = self.mturn_config_acquisition(
            nr_points_after=self._acq_nrpoints, nr_points_before=0,
            acq_rate='FOFB', repeat=False, external=True)
        if ret > 0:
            self._log(f'ERR: BPM {ret-1} did not start acquistion.')
            return

        ret = self.mturn_wait_update(timeout=self._acq_timeout)
        if ret > 0:
            self._log(f'ERR: BPM {ret-1} did not update in time.')
            return
        elif ret < 0:
            self._log(f'ERR: Problem with acquisition. Error code {ret}')
            return

        fsamp = self.get_switching_frequency(1)
        fswtc = self.get_sampling_frequency(1)
        self.self.data['freq_switching'] = fsamp
        self.self.data['freq_sampling'] = fswtc
        if None in {fsamp, fswtc}:
            self._log('ERR: Not all BPMs are configured equally.')
            return
        elif fsamp % fswtc:
            self._log('ERR: Sampling freq is not multiple of switching freq.')
            return

        posx_gain, posy_gain = [], []
        for bpm in self._devices:
            posx_gain.append(bpm.posx_gain)
            posy_gain.append(bpm.posy_gain)
        self.data['posx_gain'] = _np.array(posx_gain)
        self.data['posy_gain'] = _np.array(posy_gain)

        _time.sleep(0.1)
        self.data['antennas'] = _np.array(
            self.get_mturn_signals()).swapaxes(1, 0)

        self.trigger.source = init_source
        self.set_gains(self.data['gains_init'])

    # --------- Methods for processing ------------

    def calc_switching_levels(
            self, antennas, fsamp=4, fswtc=2, acq_strategy=0,
            acq_inverse_reduced_gain=0.95, **kwargs):
        """Calculate average signal for each antenna in both switching states.

        Args:
            antennas (numpy.ndarray, (nrbpms, 4, N)): Antennas data.
            fsamp (float, optional): Sampling frequency. Defaults to 4.
            fswtc (float, optional): Switching frequency. Defaults to 2.
            acq_strategy (int, optional): Whether we should assume states
                order in data, starting with the direct state, or if we should
                look for the higher levels (direct) and lower levels
                (inverse). Defaults to 0.
            acq_inverse_reduced_gain (float, optional): Level of the inverse
                state, if acq_strategy is 1. Must be the same value used in
                antennas gain during acquisition. Defaults to 0.95.

        Returns:
            mean (numpy.ndarray, nrbpms, 4, 2): The levels of each switching
                state for each antenna.

        """
        _ = kwargs
        ants = antennas
        lcyc = int(fsamp // fswtc)
        nbpm = len(self._devices)
        nant = 4
        trunc = (ants.shape[-1] // (lcyc*2)) * (lcyc*2)
        if trunc < 5:
            self._log(
                f'ERR:Data not large enough. Acquire data with more points.')
            return
        elif ants.shape[-1] != trunc:
            ants = ants[:, :, :trunc]
            self._log(f'WARN:Truncating data at {trunc} points')
        ants = ants.reshape(nbpm, nant, -1, lcyc*2)
        ants = ants.mean(axis=2)
        if acq_strategy == self.AcqStrategies.AssumeOrder:
            ants = ants.reshape(nbpm, nant, 2, lcyc)
            mean = ants.mean(axis=-1)
        else:
            # Try to find out the two states by looking at different levels in
            # the sum of the four antennas of each BPM.
            dts = ants.sum(axis=1)
            idcs = dts - dts.mean(axis=-1)[..., None] > 0
            idp = idcs.nonzero()  # direct
            idn = (~idcs).nonzero()  # inverse
            cond = idp[0].size == nbpm*lcyc
            cond &= _np.unique(idp[0]).size == nbpm
            if not cond:
                self._log(
                    'ERR: Could not identify switching states appropriately.')
                return
            mean = _np.zeros((nbpm, nant, 2))
            dtp = ants[idp[0], :, idp[1]].reshape(nbpm, lcyc, nant)
            dtn = ants[idn[0], :, idn[1]].reshape(nbpm, lcyc, nant)
            mean[:, :, 0] = dtp.mean(axis=1)
            mean[:, :, 1] = dtn.mean(axis=1)
            # Re-scale the inverse state data to match the direct state:
            scl = self.MAX_MULTIPLIER / acq_inverse_reduced_gain
            mean[:, :, 1] *= scl
        self.data['antennas_mean'] = mean
        return mean

    def calc_gains(self, mean):
        """Calculate gains given mean data from antennas for both semi-cycles.

        Args:
            mean (numpy.array, (nrbpms, 4, 2)): Mean data from antennas for
                both switching semi-cycle levels. Compatible with output of
                calc_switching_levels.

        """
        maxm = self.MAX_MULTIPLIER
        if self._proc_method == self.ProcMethods.EABS:
            # equalize each antenna for both semicycles
            min_ant = mean.min(axis=-1)
            min_ant = min_ant[:, :, None]
        elif self._proc_method == self.ProcMethods.AABS:
            # equalize the 4 antennas for both semicycles
            min_ant = mean.min(axis=-1).min(axis=-1)
            min_ant = min_ant[:, None, None]
        elif self._proc_method == self.ProcMethods.AAES:
            # equalize the 4 antennas for each semicycle
            min_ant = mean.min(axis=1)
            min_ant = min_ant[:, None, :]
        min_ant *= maxm
        gains = self.round_gains(min_ant / mean)
        self.data['gains_new'] = gains
        return gains

    def estimate_orbit_variation(self):
        """Estimate orbit variation between old and new gains."""
        mean = self.data.get('antennas_mean')
        gains_init = self.data.get('gains_init')
        gains_new = self.data.get('gains_new')
        posx_gain = self.data.get('posx_gain')
        posy_gain = self.data.get('posy_gain')
        if None in [mean, gains_init, gains_new, posx_gain, posy_gain]:
            self._log(
                'ERR: Missing information acquire and process data first.')

        orbx_init, orby_init = self._estimate_orbit(
            mean, gains_init, posx_gain, posy_gain)
        orbx_new, orby_new = self._estimate_orbit(
            mean, gains_new, posx_gain, posy_gain)
        self.data['orbx_init'] = orbx_init
        self.data['orby_init'] = orby_init
        self.data['orbx_new'] = orbx_new
        self.data['orby_new'] = orby_new
        dorbx = orbx_new - orbx_init
        dorby = orby_new - orby_init
        self.data['dorbx'] = dorbx
        self.data['dorby'] = dorby
        return dorbx, dorby

    def process_data(self):
        """Process data."""
        if 'antennas' not in self.data:
            self._log('ERR:There is no data to process. Acquire first.')
            return
        mean_antennas = self.calc_switching_levels(**self.data)
        self.calc_gains(mean_antennas)
        self.estimate_orbit_variation()

    # ------- auxiliary methods ----------

    def _estimate_orbit(self, mean, gains, posx_gain, posy_gain):
        ant = mean * gains
        ac = ant[:, ::2]
        bd = ant[:, 1::2]
        dovs_ac = _np.diff(ac, axis=1) / ac.sum(axis=1)
        dovs_bd = _np.diff(bd, axis=1) / bd.sum(axis=1)
        posx = (dovs_ac - dovs_bd).mean(axis=-1)
        posy = (dovs_ac + dovs_bd).mean(axis=-1)
        posx *= posx_gain / 2
        posy *= posy_gain / 2
        return posx, posy

    def _log(self, *args, **kwrgs):
        print(*args, **kwrgs)
