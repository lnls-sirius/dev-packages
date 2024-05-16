"""."""
import time as _time
import logging as _logging

import numpy as _np
import matplotlib.pyplot as _mplt

from mathphys.functions import save as _save, load as _load, \
    get_namedtuple as _namedtuple
from .bpm_fam import FamBPMs as _FamBPMs
from .timing import Trigger
from .currinfo import CurrInfoSI as _CurrInfoSI


class EqualizeBPMs(_FamBPMs):
    """."""

    NR_POINTS = 2000
    MAX_MULTIPLIER = 0xffffff / (1 << 24)
    PROCMETHODSMEANING = {
        'AABS': 'All Antennas will be equalized in Both Semicycles',
        'EABS': 'Each Antenna will be equalized in Both Semicycles',
        'AAES': 'All Antennas will be equalized in Each Semicycle'
        }
    ProcMethods = _namedtuple('ProcMethods', ('AABS', 'EABS', 'AAES'))
    AcqStrategies = _namedtuple(
        'AcqStrategies', ('AssumeOrder', 'AcqInvRedGain'))

    def __init__(self, devname=None, bpmnames=None, logger=None):
        """."""
        self._logger = None
        if logger is not None:
            self.logger = logger
        self._proc_method = self.ProcMethods.EABS
        self._acq_strategy = self.AcqStrategies.AcqInvRedGain
        self._acq_inverse_reduced_gain = self.round_gains(0.95)
        self._acq_nrpoints = 2000
        self._acq_timeout = 30
        super().__init__(
            devname=devname, bpmnames=bpmnames, ispost_mortem=False,
            mturn_signals2acq='ABCD', props2init=[
                'SwDirGainA-RB', 'SwDirGainB-RB', 'SwDirGainC-RB',
                'SwDirGainD-RB', 'SwInvGainA-RB', 'SwInvGainB-RB',
                'SwInvGainC-RB', 'SwInvGainD-RB', 'SwDirGainA-SP',
                'SwInvGainA-SP', 'SwDirGainB-SP', 'SwInvGainB-SP',
                'SwDirGainC-SP', 'SwInvGainC-SP', 'SwDirGainD-SP',
                'SwInvGainD-SP', 'ACQTriggerEvent-Sel', 'ACQStatus-Sts',
                'GEN_AArrayData', 'GEN_BArrayData', 'GEN_CArrayData',
                'GEN_DArrayData', 'ACQTriggerRep-Sel', 'ACQChannel-Sel',
                'ACQTrigger-Sel', 'ACQSamplesPre-SP', 'ACQSamplesPost-SP',
                'INFOHarmonicNumber-RB', 'INFOTbTRate-RB', 'SwDivClk-RB',
                'ACQChannel-Sts', 'INFOFOFBRate-RB', 'PosKx-RB', 'PosKy-RB',
                'PosXOffset-RB', 'PosYOffset-RB'])
        self.currinfo = _CurrInfoSI(props2init=['Current-Mon', ])
        self.trigger = Trigger(
            'SI-Fam:TI-BPM', props2init=['Src-Sel', 'Src-Sts'])
        self._devices.append(self.currinfo)
        self._devices.append(self.trigger)
        self.data = dict()

    @property
    def logger(self):
        """Logger object. Must be an instance of `logging.Logger`."""
        return self._logger

    @logger.setter
    def logger(self, logger):
        if isinstance(logger, _logging.Logger):
            self._logger = logger
        else:
            self._log('ERR:Could no set logger. Wrong type.')

    @property
    def acq_strategy_str(self):
        """."""
        return self.AcqStrategies._fields[self._acq_strategy]

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

    def load_data(self, filename):
        """Load self.data from file.

        Args:
            fname (str): name of the file. If extension is not provided,
                '.pickle' will be added and a pickle file will be assumed. If
                provided, must be {'.pickle', '.pkl'} for pickle files or
                {'.h5', '.hdf5', '.hdf', '.hd5'} for HDF5 files.

        """
        self.data = _load(filename, )

    def save_data(self, fname, overwrite=False, makedirs=True, compress=False):
        """Save self.data to pickle or HDF5 file.

        Args:
            fname (str): name of the file. If extension is not provided,
                '.pickle' will be added and a pickle file will be assumed. If
                provided, must be {'.pickle', .pkl} for pickle files or
                {'.h5', '.hdf5', '.hdf', '.hd5'} for HDF5 files.
            overwrite (bool, optional): Whether to overwrite existing file.
                Defaults to False.
            makedirs (bool, optional): create dir, if it does not exist.
                Defaults to False.
            compress (bool, optional): If True, the file will be saved in
                compressed format, using gzip library. Defaults to False.

        Raises:
            FileExistsError: in case overwrite is False and file exists.

        """
        _save(
            self.data, fname=fname, overwrite=overwrite, makedirs=makedirs,
            compress=compress)

    def get_current_gains(self):
        """Return Current BPM gains as 3D numpy array.

        Returns:
            numpy.ndarray (4, nrbpms, 2): 3D numpy array with gains.
                 - The first index vary the antennas: 'A', 'B', 'C', 'D';
                 - The second index vary the BPMs, in the default high level
                convention order;
                 - The last index refers to the type of the gain in the
                following order: 'Direct', 'Inverse';

        """
        gains = []
        for bpm in self.bpms:
            gaind = [getattr(bpm, f'gain_direct_{a}') for a in 'abcd']
            gaini = [getattr(bpm, f'gain_inverse_{a}') for a in 'abcd']
            gains.append([gaind, gaini])
        gains = _np.array(gains).swapaxes(0, 1).swapaxes(0, -1)
        return gains

    def set_gains(self, gains):
        """Set gains matrix to BPMs.

        Args:
            gains (float or numpy.ndarray, (4, nrbpms, 2)): gain matrix. In
                the same format as the one provided by get_current_gains
                method. If a float is provided, then this same gain will be
                applied to all BPMs.

        Raises:
            ValueError: If gains is a numpy array with wrong shape.

        """
        nbpm = len(self.bpms)
        shape = (4, nbpm, 2)
        if not isinstance(gains, _np.ndarray):
            gains = _np.full(shape, gains)
        if gains.shape != shape:
            raise ValueError(f'Wrong shape for gains. Must be {shape}')

        for j, ant in enumerate('abcd'):
            gns = gains[j]
            for i, bpm in enumerate(self.bpms):
                g = gns[i]
                setattr(bpm, f'gain_direct_{ant}', g[0])
                setattr(bpm, f'gain_inverse_{ant}', g[1])

    @staticmethod
    def round_gains(gains):
        """Make gains compatible with 24 bits fixed point representation."""
        mult = 1 << 24
        return _np.int_(gains*mult) / mult

    def acquire_bpm_data(self):
        """."""
        self._log('Starting Acquisition.')
        self.data = dict()
        self.data['timestamp'] = _time.time()
        self.data['stored_current'] = self.currinfo.current
        self.data['gains_init'] = self.get_current_gains()

        init_source = self.trigger.source
        ini_dly = self.trigger.delay_raw
        try:
            self._do_acquire()
        except Exception as err:
            self._log('ERR:Problem with acquisition:')
            self._log(f'ERR:{str(err)}')

        self.trigger.source = init_source
        self.trigger.delay_raw = ini_dly
        self.set_gains(self.data['gains_init'])
        self._log('Acquisition Finished!')

    def _do_acquire(self):
        if self._acq_strategy == self.AcqStrategies.AssumeOrder:
            self.set_gains(self.MAX_MULTIPLIER)
        else:
            gains = _np.full((4, len(self.bpms), 2), self.MAX_MULTIPLIER)
            gains[:, :, 1] *= self._acq_inverse_reduced_gain
            self.set_gains(gains)
        self.data['acq_strategy'] = self._acq_strategy
        self.data['acq_inverse_reduced_gain'] = self._acq_inverse_reduced_gain

        # acquire antennas data in FOFB rate
        self._log('Preparing BPMs')
        ret = self.cmd_abort_mturn_acquisition()
        if ret > 0:
            self._log(
                f'ERR: BPM {self.bpm_names[ret-1]} did not abort '
                'previous acquistion.')
            return

        self.reset_mturn_initial_state()
        ret = self.config_mturn_acquisition(
            nr_points_after=self._acq_nrpoints, nr_points_before=0,
            acq_rate='FOFB', repeat=False, external=True)
        if ret > 0:
            self._log(
                f'ERR: BPM {self.bpm_names[ret-1]} did not start acquistion.')
            return

        self.trigger.delay_raw = 0
        self.trigger.source = self.trigger.source_options.index('Clock3')

        self._log('Waiting BPMs to update')
        ret = self.wait_update_mturn(timeout=self._acq_timeout)
        if ret > 0:
            self._log(
                f'ERR: BPM {self.bpm_names[ret-1]} did not update in time.')
            return
        elif ret < 0:
            self._log(f'ERR: Problem with acquisition. Error code {ret}')
            return
        self._log('BPMs updated.')

        self._log('Acquiring data.')
        fswtc = self.get_switching_frequency(1)
        fsamp = self.get_sampling_frequency(1)
        self.data['freq_switching'] = fswtc
        self.data['freq_sampling'] = fsamp
        if None in {fsamp, fswtc}:
            self._log('ERR: Not all BPMs are configured equally.')
            return
        elif fsamp % (2*fswtc):
            self._log('ERR: Sampling freq is not multiple of switching freq.')
            return

        posx_gain, posy_gain = [], []
        posx_offset, posy_offset = [], []
        for bpm in self.bpms:
            posx_gain.append(bpm.posx_gain)
            posy_gain.append(bpm.posy_gain)
            posx_offset.append(bpm.posx_offset)
            posy_offset.append(bpm.posy_offset)
        self.data['posx_gain'] = _np.array(posx_gain)
        self.data['posy_gain'] = _np.array(posy_gain)
        self.data['posx_offset'] = _np.array(posx_offset)
        self.data['posy_offset'] = _np.array(posy_offset)
        self.data['gains_acq'] = self.get_current_gains()

        _time.sleep(0.1)
        self.data['antennas'] = _np.array(
            self.get_mturn_signals()).swapaxes(-1, -2)

    def acquire_data_for_checking(self):
        """."""
        self._log('Starting Acquisition.')

        init_source = self.trigger.source
        ini_dly = self.trigger.delay_raw
        try:
            self._do_acquire_for_check()
        except Exception as err:
            self._log('ERR:Problem with acquisition:')
            self._log(f'ERR:{str(err)}')

        self.trigger.source = init_source
        self.trigger.delay_raw = ini_dly
        self._log('Acquisition Finished!')

    def _do_acquire_for_check(self):
        # acquire antennas data in FOFB rate
        self._log('Preparing BPMs')
        ret = self.cmd_abort_mturn_acquisition()
        if ret > 0:
            self._log(
                f'ERR: BPM {self.bpm_names[ret-1]} did not abort '
                'previous acquistion.')
            return

        fswtc = self.get_switching_frequency(1)
        fsamp = self.get_sampling_frequency(1)
        nrpts = int(fsamp / fswtc)

        self.reset_mturn_initial_state()
        ret = self.config_mturn_acquisition(
            nr_points_after=nrpts, nr_points_before=0,
            acq_rate='FOFB', repeat=False, external=True)
        if ret > 0:
            self._log(
                f'ERR: BPM {self.bpm_names[ret-1]} did not start acquistion.')
            return

        self.trigger.delay_raw = 0
        self.trigger.source = self.trigger.source_options.index('Clock3')

        self._log('Waiting BPMs to update')
        ret = self.wait_update_mturn(timeout=self._acq_timeout)
        if ret > 0:
            self._log(
                f'ERR: BPM {self.bpm_names[ret-1]} did not update in time.')
            return
        elif ret < 0:
            self._log(f'ERR: Problem with acquisition. Error code {ret}')
            return
        self._log('BPMs updated.')

        self._log('Acquiring data.')
        if None in {fsamp, fswtc}:
            self._log('ERR: Not all BPMs are configured equally.')
            return
        elif fsamp % (2*fswtc):
            self._log('ERR: Sampling freq is not multiple of switching freq.')
            return

        _time.sleep(0.1)
        self.data['antennas_for_check'] = _np.array(
            self.get_mturn_signals()).swapaxes(-1, -2)

    # --------- Methods for processing ------------

    def process_data(self):
        """Process data."""
        if 'antennas' not in self.data:
            self._log('ERR:There is no data to process. Acquire first.')
            return
        mean_antennas = self.calc_switching_levels(**self.data)
        self.calc_gains(mean_antennas)
        self.estimate_orbit_variation()

    def calc_switching_levels(
            self, antennas, fsamp=4, fswtc=1, acq_strategy=0,
            acq_inverse_reduced_gain=0.95, **kwargs):
        """Calculate average signal for each antenna in both switching states.

        Args:
            antennas (numpy.ndarray, (4, nrbpms, N)): Antennas data.
            fsamp (float, optional): Sampling frequency. Defaults to 4.
            fswtc (float, optional): Switching frequency. Defaults to 1.
            acq_strategy (int, optional): Whether we should assume states
                order in data, starting with the direct state, or if we should
                look for the higher levels (direct) and lower levels
                (inverse). Defaults to 0.
            acq_inverse_reduced_gain (float, optional): Level of the inverse
                state, if acq_strategy is 1. Must be the same value used in
                antennas gain during acquisition. Defaults to 0.95.

        Returns:
            mean (numpy.ndarray, (4, nrbpms, 2)): The levels of each switching
                state for each antenna.

        """
        _ = kwargs
        ants = antennas
        lsemicyc = int(fsamp // (2*fswtc))
        nbpm = len(self.bpms)
        nant = 4
        trunc = (ants.shape[-1] // (lsemicyc*2)) * (lsemicyc*2)
        if trunc < 5:
            self._log(
                f'ERR:Data not large enough. Acquire data with more points.')
            return
        elif ants.shape[-1] != trunc:
            ants = ants[:, :, :trunc]
            self._log(f'WARN:Truncating data at {trunc} points')
        ants = ants.reshape(nant, nbpm, -1, lsemicyc*2)
        ants = ants.mean(axis=2)
        self._log('Calculating switching levels.')
        self._log(
            f'AcqStrategy is {self.AcqStrategies._fields[acq_strategy]}.')
        if acq_strategy == self.AcqStrategies.AssumeOrder:
            ants = ants.reshape(nant, nbpm, 2, lsemicyc)
            mean = ants.mean(axis=-1)
            # Inverse comes first!:
            mean = mean[:, :, ::-1]
            idn = _np.tile(_np.arange(lsemicyc), (nbpm, 1))
            idp = idn + lsemicyc
        else:
            # Try to find out the two states by looking at different levels in
            # the sum of the four antennas of each BPM.
            dts = ants.sum(axis=0)
            idcs = dts - dts.mean(axis=-1)[..., None] > 0
            idp = idcs.nonzero()  # direct
            idn = (~idcs).nonzero()  # inverse
            cond = idp[0].size == nbpm*lsemicyc
            cond &= _np.unique(idp[0]).size == nbpm
            if not cond:
                self._log(
                    'ERR: Could not identify switching states appropriately.')
                return
            mean = _np.zeros((nant, nbpm, 2))
            dtp = ants[:, idp[0], idp[1]].reshape(nant, nbpm, lsemicyc)
            dtn = ants[:, idn[0], idn[1]].reshape(nant, nbpm, lsemicyc)
            mean[:, :, 0] = dtp.mean(axis=-1)
            mean[:, :, 1] = dtn.mean(axis=-1)
            # Re-scale the inverse state data to match the direct state:
            scl = self.MAX_MULTIPLIER / acq_inverse_reduced_gain
            mean[:, :, 1] *= scl
            idp = idp[1].reshape(nbpm, -1)
            idn = idn[1].reshape(nbpm, -1)
        self.data['antennas_mean'] = mean
        self.data['idcs_direct'] = idp
        self.data['idcs_inverse'] = idn
        return mean

    def calc_gains(self, mean):
        """Calculate gains given mean data from antennas for both semi-cycles.

        Args:
            mean (numpy.array, (nrbpms, 4, 2)): Mean data from antennas for
                both switching semi-cycle levels. Compatible with output of
                calc_switching_levels.

        """
        maxm = self.MAX_MULTIPLIER
        self._log('Calculating Gains.')
        self._log(
            f'ProcMethod is {self.ProcMethods._fields[self._proc_method]}')
        if self._proc_method == self.ProcMethods.EABS:
            # equalize each antenna for both semicycles
            min_ant = mean.min(axis=-1)
            min_ant = min_ant[:, :, None]
        elif self._proc_method == self.ProcMethods.AABS:
            # equalize the 4 antennas for both semicycles
            min_ant = mean.min(axis=0).min(axis=-1)
            min_ant = min_ant[None, :, None]
        elif self._proc_method == self.ProcMethods.AAES:
            # equalize the 4 antennas for each semicycle
            min_ant = mean.min(axis=0)
            min_ant = min_ant[None, :, :]
        min_ant *= maxm
        gains = self.round_gains(min_ant / mean)
        self.data['proc_method'] = self._proc_method
        self.data['gains_new'] = gains
        return gains

    def estimate_orbit_variation(self):
        """Estimate orbit variation between old and new gains."""
        self._log('Estimating Orbit Variation.')
        mean = self.data.get('antennas_mean')
        gains_init = self.data.get('gains_init')
        gains_new = self.data.get('gains_new')
        gnx = self.data.get('posx_gain')[:, None]
        gny = self.data.get('posy_gain')[:, None]
        ofx = self.data.get('posx_offset', _np.zeros(len(self.bpms)))[:, None]
        ofy = self.data.get('posy_offset', _np.zeros(len(self.bpms)))[:, None]
        if gains_new is None:
            self._log('ERR:Missing info. Acquire and process data first.')

        orbx_init, orby_init = self.calc_positions_from_amplitudes(
            mean * gains_init, gnx, gny, ofx, ofy)
        orbx_new, orby_new = self.calc_positions_from_amplitudes(
            mean * gains_new, gnx, gny, ofx, ofy)
        # Get the average over both semicycles
        self.data['orbx_init'] = orbx_init.mean(axis=-1)
        self.data['orby_init'] = orby_init.mean(axis=-1)
        self.data['orbx_new'] = orbx_new.mean(axis=-1)
        self.data['orby_new'] = orby_new.mean(axis=-1)
        dorbx = orbx_new - orbx_init
        dorby = orby_new - orby_init
        self.data['dorbx'] = dorbx.mean(axis=-1)
        self.data['dorby'] = dorby.mean(axis=-1)
        return dorbx, dorby

    # ---------------------- plot methods -------------------------------------

    def plot_orbit_distortion(self):
        """."""
        dorbx = self.data.get('dorbx')
        dorby = self.data.get('dorby')
        if dorbx is None:
            self._log('ERR:Must acquire data and process first.')
            return None, None

        fig, ax = _mplt.subplots(1, 1, figsize=(5, 3))
        ax.plot(dorbx, label=r'Horizontal')
        ax.plot(dorby, label=r'Vertical')
        ax.set_ylabel(r'$\Delta$ Orbit [$\mu$m]')
        ax.set_xlabel('BPM Index')
        ax.grid(True, alpha=0.5, ls='--', lw=1)
        ax.set_title('Orbit Variation: New - Old')
        ax.legend(loc='best', fontsize='x-small', ncol=2)
        fig.tight_layout()
        return fig, ax

    def plot_gains(self):
        """."""
        gini = self.data.get('gains_init')
        gnew = self.data.get('gains_new')
        if gnew is None:
            self._log('ERR:Must acquire data and process first.')
            return None, None

        fig, axs = _mplt.subplots(
            4, 2, figsize=(9, 8), sharex=True, sharey=True)
        ants = 'ABCD'
        for i in range(4):
            ldo = axs[i, 0].plot(gini[i, :, 0])[0]
            lio = axs[i, 1].plot(gini[i, :, 1], color=ldo.get_color())[0]
            ldn = axs[i, 0].plot(gnew[i, :, 0])[0]
            lin = axs[i, 1].plot(gnew[i, :, 1], color=ldn.get_color())[0]
            if not i:
                ldo.set_label('Old')
                ldn.set_label('New')
            axs[i, 0].set_ylabel(ants[i])
            axs[i, 0].grid(True, alpha=0.5, ls='--', lw=1)
            axs[i, 1].grid(True, alpha=0.5, ls='--', lw=1)

        axs[0, 0].set_title('Direct Gains')
        axs[0, 1].set_title('Inverse Gains')
        axs[0, 0].legend(loc='best')
        axs[-1, 0].set_xlabel('BPM Index')
        axs[-1, 1].set_xlabel('BPM Index')
        fig.tight_layout()
        return fig, axs

    def plot_semicycle_indices(self):
        """."""
        idp = self.data.get('idcs_direct')
        idn = self.data.get('idcs_inverse')
        acqs = self.data.get('acq_strategy')
        if idp is None:
            self._log('ERR:Must acquire data and process first.')
            return None, None

        fig, ax = _mplt.subplots(1, 1, figsize=(5, 3))
        ax.plot(idp, 'o', color='C0')[0].set_label('Direct')
        ax.plot(idn, 'o', color='C1')[0].set_label('Inverse')
        ax.set_ylabel('Switching Cycle Indices')
        ax.set_xlabel('BPM Index')
        ax.grid(axis='x', alpha=0.5, ls='--', lw=1)
        ax.legend(loc='best', ncol=2, fontsize='x-small')
        ax.set_title(f'Acq Strategy: ' + self.AcqStrategies._fields[acqs])
        fig.tight_layout()
        return fig, ax

    def plot_antennas_mean(self):
        """."""
        gnx = self.data.get('posx_gain')[:, None]
        gny = self.data.get('posx_gain')[:, None]
        ofx = self.data.get('posx_offset')[:, None]
        ofy = self.data.get('posx_offset')[:, None]
        gacq = self.data.get('gains_acq')
        gini = self.data.get('gains_init')
        gnew = self.data.get('gains_new')
        antm = self.data.get('antennas_mean')
        if gnew is None:
            self._log('ERR:Must acquire data and process first.')
            return None, None

        gains = (1, gacq, gini, gnew)
        titles = ('Unit Gain', 'Acquisition Gain', 'Old Gain', 'New Gain')
        labs = list('ABCDXYS')
        labs[-1] = 'Sum'
        labs = [lab + ' [a.u.]' for lab in labs]
        labs[4] = r'X [$\mu$m]'
        labs[5] = r'Y [$\mu$m]'

        antm /= 10**(_np.floor(_np.log10(antm.max())))

        fig, axs = _mplt.subplots(
            len(labs), len(gains), figsize=(16, 10), sharex=True, sharey='row')
        for j, gain in enumerate(gains):
            val = antm * gain
            for i in range(4):
                ax = axs[i, j]
                ld = ax.plot(val[i, :, 0], 'o-')[0]
                li = ax.plot(val[i, :, 1], 'o-')[0]
                if not i and not j:
                    ld.set_label('Direct')
                    li.set_label('Inverse')
            posx, posy = self.calc_positions_from_amplitudes(
                antm * gain, gnx, gny, ofx, ofy)
            sum_ = val.sum(axis=0)
            axs[4, j].plot(posx[:, 0], 'o-')
            axs[4, j].plot(posx[:, 1], 'o-')
            axs[5, j].plot(posy[:, 0], 'o-')
            axs[5, j].plot(posy[:, 1], 'o-')
            axs[6, j].plot(sum_[:, 0], 'o-')
            axs[6, j].plot(sum_[:, 1], 'o-')
            for i, lab in enumerate(labs):
                ax = axs[i, j]
                if not j:
                    ax.set_ylabel(lab)
                ax.grid(True, alpha=0.5, ls='--', lw=1)
            axs[0, j].set_title(titles[j])
            axs[-1, j].set_xlabel('BPM Index')

        axs[0, 0].legend(loc='best', fontsize='x-small', ncol=2)
        fig.tight_layout()
        return fig, axs

    def plot_antennas_for_check(self):
        """."""
        antd = self.data.get('antennas_for_check')
        if antd is None:
            self._log('ERR:Must acquire data for check first.')
            return None, None

        fig, axs = _mplt.subplots(
            4, 1, figsize=(6, 8), sharex=True, sharey=True)
        ants = 'ABCD'
        mean = antd.mean(axis=-1)[:, :, None]
        antd = antd / mean - 1
        nbpm = antd.shape[1]
        for j in range(nbpm):
            cor = _mplt.cm.jet(j/(nbpm-1))
            for i in range(4):
                axs[i].plot(antd[i, j], 'o-', color=cor)
                if not j:
                    axs[i].set_ylabel(ants[i] + ' [%]')
                    axs[i].grid(True, alpha=0.5, ls='--', lw=1)

        axs[0].set_title('Relative Variation')
        axs[-1].set_xlabel('Samples')
        fig.tight_layout()
        return fig, axs

    # ------- auxiliary methods ----------

    def _log(self, message, *args, level='INFO', **kwrgs):
        if self._logger is None:
            print(message, *args, **kwrgs)
        elif message.startswith('WARN:'):
            self._logger.warning(message[5:])
        elif message.startswith('ERR:'):
            self._logger.error(message[4:])
        else:
            self._logger.info(message)
