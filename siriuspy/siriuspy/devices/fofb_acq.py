"""FOFB acquisition devices."""

import time as _time
import numpy as _np

from ..search import PSSearch as _PSSearch, BPMSearch as _BPMSearch
from ..csdev import Const as _Const
from ..fofb.csdev import NR_BPM

from .device import DeviceSet as _DeviceSet, Device as _Device
from .fofb import FOFBCtrlBase as _FOFBCtrlBase
from .timing import Event
from .psconv import StrengthConv


class _FOFBCtrlAcqConst(_Const):
    """FOFB acquisition constants."""

    # TODO: when BPM IOC is updated, these acquisition core base classes
    # should be migrated to a common module to be shared.

    CHANNEL = ('lamp', 'invalid', 'sysid', 'sysid_applied')
    TRIGTYP = ('now', 'external', 'data', 'software')
    TRIGEVT = ('start', 'stop')
    REPEAT = ('normal', 'repetitive')
    STATES = (
        'Idle', 'Waiting', 'External Trig', 'Data Trig', 'Software Trig',
        'Acquiring', 'Error', 'Bad Post Samples', 'Too Many Samples',
        'No Samples', 'No Memory', 'Overflow')

    Channel = _Const.register('Channel', CHANNEL)
    TrigTyp = _Const.register('TrigTyp', TRIGTYP)
    TrigEvt = _Const.register('Events', TRIGEVT)
    Repeat = _Const.register('Repeat', REPEAT)
    States = _Const.register('States', STATES)

    STATES_NOTOK = {
        States.Error, States.No_Memory, States.Bad_Post_Samples,
        States.No_Samples, States.Too_Many_Samples, States.Overflow}
    STATES_STARTED = {
        States.Waiting, States.External_Trig, States.Data_Trig,
        States.Software_Trig, States.Acquiring}
    STATES_FINISHED = {States.Idle}
    STATES_FINISHED |= STATES_NOTOK


class _FOFBCtrlAcqBase(_Device, _FOFBCtrlBase, _FOFBCtrlAcqConst):
    """FOFB acquisition base device."""

    PROPERTIES_DEFAULT = (
        'Channel-Sel', 'Channel-Sts',
        'Shots-SP', 'Shots-RB',
        'UpdateTime-SP', 'UpdateTime-RB',
        'TriggerRep-Sel', 'TriggerRep-Sts',
        'SamplesPre-SP', 'SamplesPre-RB',
        'SamplesPost-SP', 'SamplesPost-RB',
        'Trigger-Sel', 'Trigger-Sts',
        'TriggerEvent-Cmd', 'Status-Mon', 'Count-Mon',
    )

    def __init__(self, devname, **kws):
        """Init."""
        # call base class constructor
        _Device.__init__(self, devname, **kws)

    @property
    def channel(self):
        """Channel enum index."""
        return self['Channel-Sts']

    @channel.setter
    def channel(self, val):
        self['Channel-Sel'] = val

    @property
    def channel_str(self):
        """Channel enum string."""
        return _FOFBCtrlAcqConst.CHANNEL[self.channel]

    @property
    def nrshots(self):
        """Number of shots in the acquisition."""
        return self['Shots-RB']

    @nrshots.setter
    def nrshots(self, val):
        self['Shots-SP'] = val

    @property
    def update_time(self):
        """Acquisition update time."""
        return self['UpdateTime-RB']  # / 1e3

    @update_time.setter
    def update_time(self, val):
        self['UpdateTime-SP'] = val  # * 1e3

    @property
    def repeat(self):
        """Whether the acquisition is repeat or normal."""
        return self['TriggerRep-Sts']

    @repeat.setter
    def repeat(self, val):
        self['TriggerRep-Sel'] = val

    @property
    def nrsamples_pre(self):
        """Number of samples previous to trigger acquisition."""
        return self['SamplesPre-RB']

    @nrsamples_pre.setter
    def nrsamples_pre(self, val):
        self['SamplesPre-SP'] = val

    @property
    def nrsamples_post(self):
        """Number of samples posterior to trigger acquisition."""
        return self['SamplesPost-RB']

    @nrsamples_post.setter
    def nrsamples_post(self, val):
        self['SamplesPost-SP'] = val

    @property
    def trigger(self):
        """Trigger."""
        return self['Trigger-Sts']

    @trigger.setter
    def trigger(self, val):
        self['Trigger-Sel'] = val

    @property
    def status(self):
        """Acquisition status."""
        return self['Status-Sts']

    @property
    def count(self):
        """Counter of number of acquisitions so far."""
        return self['Count-Mon']

    def cmd_ctrl(self, val):
        """Command to start or stop acquisition."""
        self['TriggerEvent-Cmd'] = val

    def wait_acq_finish(self, timeout=10):
        """Wait Acquisition to finish."""
        return self._wait(
            'Status-Sts', _FOFBCtrlAcqConst.STATES_FINISHED,
            timeout=timeout, comp=lambda x, y: x in y)

    def wait_acq_start(self, timeout=10):
        """Wait Acquisition to start."""
        return self._wait(
            'Status-Sts', _FOFBCtrlAcqConst.STATES_STARTED,
            timeout=timeout, comp=lambda x, y: x in y)


class _FamFOFBAcqBase(_DeviceSet, _FOFBCtrlAcqConst):

    DEF_TIMEOUT = 10  # [s]
    FOFBCTRL_CLASS = _FOFBCtrlAcqBase
    FOFBPS_CLASS = _FOFBCtrlAcqBase

    def __init__(self, ctrlname=None, psnames=None, bpmnames=None, event=None):
        # FOFBCtrl devices
        ctrlnames = _FOFBCtrlBase.DEVICES if not ctrlname else [ctrlname, ]
        self._ctlrs, subs = dict(), list()
        for idx, ctl in enumerate(ctrlnames):
            self._ctlrs[ctl] = self.FOFBCTRL_CLASS(ctl, auto_monitor_mon=False)
            subs.append(f'{idx+1:02}')
        sub = '(' + '|'.join(subs) + ').*'

        # FOFBPS devices
        if psnames is None:
            chn = _PSSearch.get_psnames(dict(sec='SI', sub=sub, dev='FCH'))
            cvn = _PSSearch.get_psnames(dict(sec='SI', sub=sub, dev='FCV'))
            psnames = chn + cvn
        self._psnames = psnames
        self._psdevs = {
            psn: self.FOFBPS_CLASS(psn, auto_monitor_mon=False)
            for psn in self._psnames}
        self._psconv = {
            psn: StrengthConv(psn, 'Ref-Mon') for psn in self._psnames}

        # BPM names
        self._bpm_names = bpmnames or _BPMSearch.get_names(
            dict(sec='SI', sub=sub, dev='BPM'))

        # FOFBS event
        event = event or 'FOFBS'
        self._evt_fofb = Event(event)

        # call base class constructor
        devices = list()
        devices.extend(self._ctlrs.values())
        devices.extend(self._psdevs.values())
        devices.extend(self._psconv.values())
        _DeviceSet.__init__(self, devices, devname='SI-Glob:BS-FOFBAcq')

    @property
    def ctrldevs(self):
        """FOFBCtrl device list."""
        return self._ctlrs

    @property
    def psnames(self):
        """PS name list."""
        return list(self._psnames)

    @property
    def psdevs(self):
        """PS device list."""
        return self._psdevs

    @property
    def psconvs(self):
        """PS conversion device list."""
        return self._psconv

    @property
    def bpmnames(self):
        """BPM names."""
        return self._bpm_names

    @property
    def evtdev(self):
        """FOFBS event device."""
        return self._evt_fofb

    @property
    def channel(self):
        """Channel enum index for all controllers in ctrldevs."""
        return _np.array([dev.channel for dev in self._ctlrs.values()])

    @property
    def nrshots(self):
        """
        Number of shots in the acquisition for all
        controllers in ctrldevs.
        """
        return _np.array([dev.nrshots for dev in self._ctlrs.values()])

    @property
    def update_time(self):
        """Acquisition update time for all controllers in ctrldevs."""
        return _np.array([dev.update_time for dev in self._ctlrs.values()])

    @property
    def repeat(self):
        """
        Whether the acquisition is repeat or normal for all
        controllers in ctrldevs.
        """
        return _np.array([dev.repeat for dev in self._ctlrs.values()])

    @property
    def nrsamples_pre(self):
        """
        Number of samples previous to trigger acquisition for all
        controllers in ctrldevs.
        """
        return _np.array([dev.nrsamples_pre for dev in self._ctlrs.values()])

    @property
    def nrsamples_post(self):
        """
        Number of samples posterior to trigger acquisition for all
        controllers in ctrldevs.
        """
        return _np.array([dev.nrsamples_post for dev in self._ctlrs.values()])

    @property
    def trigger(self):
        """Trigger source for all controllers in ctrldevs."""
        return _np.array([dev.trigger for dev in self._ctlrs.values()])

    @property
    def status(self):
        """Acquisition status."""
        data = list()
        for dev in self._ctlrs.values():
            data.append(dev.status)

        if len(data) == 1:
            return data[0]
        return data

    def set_channel(self, val):
        """Set channel for all FOFBCtrl."""
        self._set_devices_propty(self._ctlrs, 'Channel-Sel', val)
        return self._wait_devices_propty(self._ctlrs, 'Channel-Sts', val)

    def set_nrshots(self, val):
        """Set nrshots for all FOFBCtrl."""
        self._set_devices_propty(self._ctlrs, 'Shots-SP', val)
        return self._wait_devices_propty(self._ctlrs, 'Shots-RB', val)

    def set_update_time(self, val):
        """Set update_time for all FOFBCtrl."""
        self._set_devices_propty(self._ctlrs, 'UpdateTime-SP', val)
        return self._wait_devices_propty(self._ctlrs, 'UpdateTime-RB', val)

    def set_repeat(self, val):
        """Set repeat for all FOFBCtrl."""
        self._set_devices_propty(self._ctlrs, 'TriggerRep-Sel', val)
        return self._wait_devices_propty(self._ctlrs, 'TriggerRep-Sts', val)

    def set_nrsamples_pre(self, val):
        """Set nrsamples_pre for all FOFBCtrl."""
        self._set_devices_propty(self._ctlrs, 'SamplesPre-SP', val)
        return self._wait_devices_propty(self._ctlrs, 'SamplesPre-RB', val)

    def set_nrsamples_post(self, val):
        """Set nrsamples_post for all FOFBCtrl."""
        self._set_devices_propty(self._ctlrs, 'SamplesPost-SP', val)
        return self._wait_devices_propty(self._ctlrs, 'SamplesPost-RB', val)

    def set_trigger(self, val):
        """Set trigger for all FOFBCtrl."""
        self._set_devices_propty(self._ctlrs, 'Trigger-Sel', val)
        return self._wait_devices_propty(self._ctlrs, 'Trigger-Sts', val)


# ------- system identification devices -------

class FOFBCtrlSysId(_FOFBCtrlAcqBase):
    """FOFB controller system identification device."""

    PROPERTIES_DEFAULT = _FOFBCtrlAcqBase.PROPERTIES_DEFAULT
    PROPERTIES_DEFAULT += ('TimeFrameData', 'DataType')
    PROPERTIES_DEFAULT += tuple([f'BPM{i}PosXData' for i in range(8)])
    PROPERTIES_DEFAULT += tuple([f'BPM{i}PosYData' for i in range(8)])
    PROPERTIES_DEFAULT += (
        'PRBSSyncEn-Sel', 'PRBSSyncEn-Sts',
        'PRBSStepDuration-SP', 'PRBSStepDuration-RB',
        'PRBSLFSRLength-SP', 'PRBSLFSRLength-RB',
        'PRBSFOFBAccMovAvgTaps-SP', 'PRBSFOFBAccMovAvgTaps-RB',
        'PRBSFOFBAccEn-Sel', 'PRBSFOFBAccEn-Sts',
        'PRBSBPMPosEn-Sel', 'PRBSBPMPosEn-Sts',
        'PRBSBPMPosXLvl0-SP', 'PRBSBPMPosXLvl0-RB',
        'PRBSBPMPosXLvl1-SP', 'PRBSBPMPosXLvl1-RB',
        'PRBSBPMPosYLvl0-SP', 'PRBSBPMPosYLvl0-RB',
        'PRBSBPMPosYLvl1-SP', 'PRBSBPMPosYLvl1-RB',
        'PRBSData',
    )

    def __init__(self, devname, auto_monitor_mon=True, props2init='all'):
        """Init."""
        # call base class constructor
        super().__init__(
            devname + ':SYSID', props2init=props2init,
            auto_monitor_mon=auto_monitor_mon)

    @property
    def data_type(self):
        """Data type."""
        return self['DataType']

    @data_type.setter
    def data_type(self, val):
        self['DataType'] = val

    @property
    def timeframe_data(self):
        """Time frame data."""
        return self['TimeFrameData']

    def get_bpm_posx(self, bpm_index):
        """Return BPM PosXData for BPM of index bpm_index."""
        return self[f'BPM{bpm_index}PosXData']

    def get_bpm_posy(self, bpm_index):
        """Return BPM PosYData for BPM of index bpm_index."""
        return self[f'BPM{bpm_index}PosYData']

    @property
    def prbs_data(self):
        """PRBS Data."""
        return self['PRBSData']

    @property
    def prbs_sync_enbl(self):
        """PRBS sync enable."""
        return self['PRBSSyncEn-Sts']

    @prbs_sync_enbl.setter
    def prbs_sync_enbl(self, val):
        self['PRBSSyncEn-Sel'] = val

    @property
    def prbs_step_duration(self):
        """PRBS step duration."""
        return self['PRBSStepDuration-RB']

    @prbs_step_duration.setter
    def prbs_step_duration(self, val):
        self['PRBSStepDuration-SP'] = val

    @property
    def prbs_lfsr_len(self):
        """PRBS LFSR length."""
        return self['PRBSLFSRLength-RB']

    @prbs_lfsr_len.setter
    def prbs_lfsr_len(self, val):
        self['PRBSLFSRLength-SP'] = val

    @property
    def prbs_mov_avg_taps(self):
        """Number of taps of the PRBS moving average filter."""
        return self['PRBSFOFBAccMovAvgTaps-RB']

    @prbs_mov_avg_taps.setter
    def prbs_mov_avg_taps(self, val):
        self['PRBSFOFBAccMovAvgTaps-SP'] = val

    @property
    def prbs_fofbacc_enbl(self):
        """Whether to enable or not PRBS actuation in correctors."""
        return self['PRBSFOFBAccEn-Sts']

    @prbs_fofbacc_enbl.setter
    def prbs_fofbacc_enbl(self, val):
        self['PRBSFOFBAccEn-Sel'] = val

    @property
    def prbs_bpmpos_enbl(self):
        """Whether to enable or not PRBS excitation in BPMs PosX."""
        return self['PRBSBPMPosEn-Sts']

    @prbs_bpmpos_enbl.setter
    def prbs_bpmpos_enbl(self, val):
        self['PRBSBPMPosEn-Sel'] = val

    @property
    def prbs_bpmposx_lvl0(self):
        """Array with all BPMs PosX value for PRBS level 0  [nm]."""
        return self['PRBSBPMPosXLvl0-RB']

    @prbs_bpmposx_lvl0.setter
    def prbs_bpmposx_lvl0(self, val):
        self['PRBSBPMPosXLvl0-SP'] = _np.array(val, dtype=int)

    @property
    def prbs_bpmposx_lvl1(self):
        """Array with all BPMs PosX value for PRBS level 1  [nm]."""
        return self['PRBSBPMPosXLvl1-RB']

    @prbs_bpmposx_lvl1.setter
    def prbs_bpmposx_lvl1(self, val):
        self['PRBSBPMPosXLvl1-SP'] = _np.array(val, dtype=int)

    @property
    def prbs_bpmposy_lvl0(self):
        """Array with all BPMs PosY value for PRBS level 0  [nm]."""
        return self['PRBSBPMPosYLvl0-RB']

    @prbs_bpmposy_lvl0.setter
    def prbs_bpmposy_lvl0(self, val):
        self['PRBSBPMPosYLvl0-SP'] = _np.array(val, dtype=int)

    @property
    def prbs_bpmposy_lvl1(self):
        """Array with all BPMs PosY value for PRBS level 1  [nm]."""
        return self['PRBSBPMPosYLvl1-RB']

    @prbs_bpmposy_lvl1.setter
    def prbs_bpmposy_lvl1(self, val):
        self['PRBSBPMPosYLvl1-SP'] = _np.array(val, dtype=int)


class FOFBPSSysId(_Device):
    """FOFB power supply system identification device."""

    PROPERTIES_DEFAULT = (
        'SYSIDFOFBAccRawData', 'SYSIDFOFBAccData',
        'SYSIDPRBSFOFBAccLvl0-SP', 'SYSIDPRBSFOFBAccLvl0-RB',
        'SYSIDPRBSFOFBAccLvl1-SP', 'SYSIDPRBSFOFBAccLvl1-RB',
        'CurrLoopKp-SP', 'CurrLoopKp-RB',
        'CurrLoopTi-SP', 'CurrLoopTi-RB',
    )

    def __init__(self, devname, auto_monitor_mon=True, props2init='all'):
        """Init."""
        # call base class constructor
        super().__init__(
            devname, props2init=props2init,
            auto_monitor_mon=auto_monitor_mon)

    @property
    def fofbacc_rawdata(self):
        """FOFB accumulator raw data for SYSID core."""
        return self['SYSIDFOFBAccRawData']

    @property
    def fofbacc_data(self):
        """FOFB accumulator data for SYSID core."""
        return self['SYSIDFOFBAccData']

    @property
    def prbs_fofbacc_lvl0(self):
        """Actuation value for level 0 of SYSID PRBS signal."""
        return self['SYSIDPRBSFOFBAccLvl0-RB']

    @prbs_fofbacc_lvl0.setter
    def prbs_fofbacc_lvl0(self, val):
        self['SYSIDPRBSFOFBAccLvl0-SP'] = val

    @property
    def prbs_fofbacc_lvl1(self):
        """Actuation value for level 1 of SYSID PRBS signal."""
        return self['SYSIDPRBSFOFBAccLvl1-RB']

    @prbs_fofbacc_lvl1.setter
    def prbs_fofbacc_lvl1(self, val):
        self['SYSIDPRBSFOFBAccLvl1-SP'] = val

    @property
    def currloop_kp(self):
        """Current control loop Kp parameter."""
        return self['CurrLoopKp-RB']

    @currloop_kp.setter
    def currloop_kp(self, value):
        self['CurrLoopKp-SP'] = value

    @property
    def currloop_ti(self):
        """Current control loop Ti parameter."""
        return self['CurrLoopTi-RB']

    @currloop_ti.setter
    def currloop_ti(self, value):
        self['CurrLoopTi-SP'] = value


class FamFOFBSysId(_FamFOFBAcqBase):
    """Family of FOFB SYSID acquisition device."""

    FOFBCTRL_CLASS = FOFBCtrlSysId
    FOFBPS_CLASS = FOFBPSSysId
    DEF_ATOL_FOFBACC = 1e-6

    def __init__(self, **kws):
        """."""
        super().__init__(**kws)
        self._initial_timestamps = None

    @property
    def data_type(self):
        """Data type of all controllers in ctrldevs."""
        return _np.array(
            [dev.data_type for dev in self._ctlrs.values()])

    @property
    def timeframe_data(self):
        """Time frame data of all controllers in ctrldevs."""
        return [dev.timeframe_data for dev in self._ctlrs.values()]

    @property
    def prbs_data(self):
        """PRBS Data of all controllers in ctrldevs."""
        return [dev.prbs_data for dev in self._ctlrs.values()]

    @property
    def prbs_step_duration(self):
        """PRBS step duration of all controllers in ctrldevs."""
        return _np.array(
            [dev.prbs_step_duration for dev in self._ctlrs.values()])

    @property
    def prbs_lfsr_len(self):
        """PRBS LFSR length of all controllers in ctrldevs."""
        return _np.array(
            [dev.prbs_lfsr_len for dev in self._ctlrs.values()])

    @property
    def prbs_mov_avg_taps(self):
        """
        Number of taps of the PRBS moving average filter of all controllers.
        """
        return _np.array(
            [dev.prbs_mov_avg_taps for dev in self._ctlrs.values()])

    @property
    def prbs_sync_enbl(self):
        """PRBS sync enable of all controllers in ctrldevs."""
        return _np.array(
            [dev.prbs_sync_enbl for dev in self._ctlrs.values()])

    @property
    def prbs_fofbacc_enbl(self):
        """
        Whether to enable or not PRBS actuation in correctors
        of all controllers in ctrldevs.
        """
        return _np.array(
            [dev.prbs_fofbacc_enbl for dev in self._ctlrs.values()])

    @property
    def prbs_fofbacc_lvl0(self):
        """Array with correctors actuation value for PRBS level 0 [A]."""
        return _np.array(
            [self._psdevs[psn].prbs_fofbacc_lvl0 for psn in self._psnames])

    @property
    def prbs_fofbacc_lvl1(self):
        """Array with correctors actuation value for PRBS level 1 [A]."""
        return _np.array(
            [self._psdevs[psn].prbs_fofbacc_lvl1 for psn in self._psnames])

    @property
    def prbs_bpmpos_enbl(self):
        """
        Whether to enable or not PRBS excitation in BPMs PosX
        of all controllers in ctrldevs.
        """
        return _np.array(
            [dev.prbs_bpmpos_enbl for dev in self._ctlrs.values()])

    @property
    def prbs_bpmposx_lvl0(self):
        """
        Array with all BPMs PosX value for PRBS level 0 of all
        controllers in ctrldevs [nm].
        """
        return _np.array(
            [dev.prbs_bpmposx_lvl0 for dev in self._ctlrs.values()])

    @property
    def prbs_bpmposx_lvl1(self):
        """
        Array with all BPMs PosX value for PRBS level 1 of all
        controllers in ctrldevs [nm].
        """
        return _np.array(
            [dev.prbs_bpmposx_lvl1 for dev in self._ctlrs.values()])

    @property
    def prbs_bpmposy_lvl0(self):
        """
        Array with all BPMs PosY value for PRBS level 0 of all
        controllers in ctrldevs [nm].
        """
        return _np.array(
            [dev.prbs_bpmposy_lvl0 for dev in self._ctlrs.values()])

    @property
    def prbs_bpmposy_lvl1(self):
        """
        Array with all BPMs PosY value for PRBS level 1 of all
        controllers in ctrldevs [nm].
        """
        return _np.array(
            [dev.prbs_bpmposy_lvl1 for dev in self._ctlrs.values()])

    @property
    def currloop_kp(self):
        """Current Loop Kp.

        Returns:
            kp (numpy.ndarray, 160):
                current loop Kp for each power supply.
        """
        return _np.array(
            [self._psdevs[psn].currloop_kp for psn in self._psnames])

    @property
    def currloop_ti(self):
        """Current Loop Ti.

        Returns:
            ti (numpy.ndarray, 160):
                current loop Ti for each power supply.
        """
        return _np.array(
            [self._psdevs[psn].currloop_ti for psn in self._psnames])

    @property
    def strength_2_current_factor(self):
        """Strength to current convertion factor.

        Returns:
            factor (numpy.ndarray, NR_BPM):
                convertion factor for each power supply.
        """
        return _np.array(
            [self._psconv[psn].conv_strength_2_current(1, strengths_dipole=3.0)
             for psn in self._psnames])

    def set_data_type(self, value):
        """Configure acquisition data type for FOFB controllers.

        Args:
            data_type (int): acquisition data type
                (0:raw, 1:lamp, 2:sysid).
        """
        for ctl in self._ctlrs.values():
            ctl.data_type = value
        return True

    def check_data_valid(self):
        """Check whether acquisition TimeFrameData are valid.

        Returns:
            int: code describing what happened:
                -1: TimeFrameData is not monotonic;
                =0: data is valid.
                >0: index of the first FOFB controller which have time frame
                    or PRBS data different from controller 01.

        """
        # check whether time frame data are synced between controllers
        ctlr01_tfdata = self.timeframe_data[0]
        for idx, data in enumerate(self.timeframe_data):
            if not _np.all(data == ctlr01_tfdata):
                return idx+1
        # check if timeframe data is monotonic
        if not all(v in (1, -2**16+1) for v in _np.diff(ctlr01_tfdata)):
            return -1
        # check whether prbs data are synced between controllers
        ctlr01_prbsdata = self.prbs_data[0]
        for idx, data in enumerate(self.prbs_data):
            if not _np.all(data == ctlr01_prbsdata):
                return idx+1
        return 0

    def set_prbs_mov_avg_taps(self, value):
        """Configure number of taps of the PRBS moving average filter
        for all FOFB controllers.

        Args:
            value (int): number of taps.
        """
        for ctl in self._ctlrs.values():
            ctl.prbs_mov_avg_taps = value
        return True

    def config_prbs(self, step_duration, lfsr_len):
        """Configure PRBS for FOFB controllers.

        Args:
            step_duration (int): step duration.
            lfsr_len (int): LFSR length.
        """
        for ctl in self._ctlrs.values():
            ctl.prbs_step_duration = step_duration
            ctl.prbs_lfsr_len = lfsr_len
        return True

    def cmd_sync_prbs(self, timeout=_FamFOFBAcqBase.DEF_TIMEOUT):
        """Command to sync PRBS signal for all controllers."""
        ctrls = list(self._ctlrs.values())

        self._set_devices_propty(ctrls, 'PRBSSyncEn-Sel', 1)
        if not self._wait_devices_propty(
                ctrls, 'PRBSSyncEn-Sts', 1, timeout=timeout/2):
            return False

        self._evt_fofb.cmd_external_trigger()
        _time.sleep(2)

        self._set_devices_propty(ctrls, 'PRBSSyncEn-Sel', 0)
        if not self._wait_devices_propty(
                ctrls, 'PRBSSyncEn-Sts', 0, timeout=timeout/2):
            return False
        return True

    def set_prbs_fofbacc_levels(self, level0, level1=None):
        """Set power supply FOFBAcc PRBS excitation levels.

        Args:
            level0 (numpy.ndarray, (NR_CORRS,)):
                desired values for power supplies PRBS excitation level 0
                in psnames order.
            level1 (optional, numpy.ndarray, (NR_CORRS,)):
                If None, we consider level1 = -level0. Defaults to None.

        """
        level0, level1 = self._handle_corr_levels(level0, level1)
        for i, psn in enumerate(self._psnames):
            dev = self._psdevs[psn]
            dev.prbs_fofbacc_lvl0 = level0[i]
            dev.prbs_fofbacc_lvl1 = level1[i]
        return True

    def check_prbs_fofbacc_levels(
            self, level0, level1=None, atol=DEF_ATOL_FOFBACC):
        """
        Check whether power supply FOFBAcc PRBS excitation levels are equal to
        desired values.

        Args:
            level0 (numpy.ndarray, (NR_CORRS,)):
                desired values for power supplies PRBS excitation level 0
                in psnames order.
            level1 (optional, numpy.ndarray, (NR_CORRS,)):
                If None, we consider level1 = -level0. Defaults to None.
            atol (optional, float):
                Absolute tolerance for values comparison.

        Returns:
            bool: indicate whether levels 0 and 1 of power supply FOFBAcc PRBS
                excitation are in desired values.

        """
        level0, level1 = self._handle_corr_levels(level0, level1)
        impltd0 = _np.array(
            [self._psdevs[psn].prbs_fofbacc_lvl0 for psn in self._psnames])
        if not _np.allclose(level0, impltd0, atol=atol):
            return False
        impltd1 = _np.array(
            [self._psdevs[psn].prbs_fofbacc_lvl1 for psn in self._psnames])
        if not _np.allclose(level1, impltd1, atol=atol):
            return False
        return True

    def wait_prbs_fofbacc_levels(
            self, level0, level1=None, atol=DEF_ATOL_FOFBACC,
            timeout=_FamFOFBAcqBase.DEF_TIMEOUT):
        """
        Wait for power supply FOFBAcc PRBS excitation levels to be equal to
        desired values. Refer to check_prbs_fofbacc_levels for more details
        on arguments and returns.
        """
        _t0 = _time.time()
        while _time.time() - _t0 < timeout:
            if self.check_prbs_fofbacc_levels(level0, level1, atol):
                return True
            _time.sleep(0.1)
        return False

    def _handle_corr_levels(self, level0, level1):
        nr_ps = len(self._psnames)
        if isinstance(level0, (int, float, bool)):
            level0 = nr_ps * [level0]
        level0 = _np.asarray(level0)
        if level1 is None:
            level1 = -1 * level0
        if len(level0) != nr_ps or len(level1) != nr_ps:
            raise ValueError('Levels and psnames must have the same length.')
        return level0, level1

    def cmd_prbs_fofbacc_enable(self, timeout=_FamFOFBAcqBase.DEF_TIMEOUT):
        """Command to enable PRBS for correctors."""
        ctrls = list(self._ctlrs.values())
        self._set_devices_propty(ctrls, 'PRBSFOFBAccEn-Sel', 1)
        if not self._wait_devices_propty(
                ctrls, 'PRBSFOFBAccEn-Sts', 1, timeout=timeout):
            return False
        return True

    def cmd_prbs_fofbacc_disable(self, timeout=_FamFOFBAcqBase.DEF_TIMEOUT):
        """Command to disable PRBS for correctors."""
        ctrls = list(self._ctlrs.values())
        self._set_devices_propty(ctrls, 'PRBSFOFBAccEn-Sel', 0)
        if not self._wait_devices_propty(
                ctrls, 'PRBSFOFBAccEn-Sts', 0, timeout=timeout/2):
            return False
        return True

    def set_prbs_bpmposx_levels(self, level0, level1=None):
        """Set BPM PosX PRBS excitation levels.

        Args:
            level0 (numpy.ndarray, (NR_BPM,)):
                desired values for BPM PosX PRBS excitation level 0.
            level1 (optional, numpy.ndarray, (NR_BPM,)):
                If None, we consider level1 = -level0. Defaults to None.

        """
        level0, level1 = self._handle_bpm_levels(level0, level1)
        for ctl in self._ctlrs.values():
            ctl.prbs_bpmposx_lvl0 = level0
            ctl.prbs_bpmposx_lvl1 = level1
        return True

    def check_prbs_bpmposx_levels(self, level0, level1=None):
        """
        Check whether BPM PosX PRBS excitation levels are equal to
        desired values.

        Args:
            level0 (numpy.ndarray, (NR_BPM,)):
                desired values for BPM PosX PRBS excitation level 0.
            level1 (optional, numpy.ndarray, (NR_BPM,)):
                If None, we consider level1 = -level0. Defaults to None.

        Returns:
            bool: indicate whether levels 0 and 1 of BPM PosX PRBS
                excitation are in desired values.

        """
        level0, level1 = self._handle_bpm_levels(level0, level1)
        for ctl in self._ctlrs.values():
            if not _np.all(ctl.prbs_bpmposx_lvl0 == level0):
                return False
            if not _np.all(ctl.prbs_bpmposx_lvl1 == level1):
                return False
        return True

    def wait_prbs_bpmposx_levels(
            self, level0, level1=None, timeout=_FamFOFBAcqBase.DEF_TIMEOUT):
        """
        Wait for BPM PosX PRBS excitation levels to be equal to desired
        values. Refer to check_prbs_bpmposx_levels for more details on
        arguments and returns.
        """
        _t0 = _time.time()
        while _time.time() - _t0 < timeout:
            if self.check_prbs_bpmposx_levels(level0, level1):
                return True
            _time.sleep(0.1)
        return False

    def set_prbs_bpmposy_levels(self, level0, level1=None):
        """Set BPM PosY PRBS excitation levels.

        Args:
            level0 (numpy.ndarray, (NR_BPM,)):
                desired values for BPM PosX PRBS excitation level 0.
            level1 (optional, numpy.ndarray, (NR_BPM,)):
                If None, we consider level1 = -level0. Defaults to None.

        """
        level0, level1 = self._handle_bpm_levels(level0, level1)
        for ctl in self._ctlrs.values():
            ctl.prbs_bpmposy_lvl0 = level0
            ctl.prbs_bpmposy_lvl1 = level1
        return True

    def check_prbs_bpmposy_levels(self, level0, level1=None):
        """
        Check whether BPM PosY PRBS excitation levels are equal to
        desired values.

        Args:
            level0 (numpy.ndarray, (NR_BPM,)):
                desired values for BPM PosY PRBS excitation level 0.
            level1 (optional, numpy.ndarray, (NR_BPM,)):
                If None, we consider level1 = -level0. Defaults to None.

        Returns:
            bool: indicate whether levels 0 and 1 of BPM PosY PRBS
                excitation are in desired values.

        """
        level0, level1 = self._handle_bpm_levels(level0, level1)
        for ctl in self._ctlrs.values():
            if not _np.all(ctl.prbs_bpmposy_lvl0 == level0):
                return False
            if not _np.all(ctl.prbs_bpmposy_lvl1 == level1):
                return False
        return True

    def wait_prbs_bpmposy_levels(
            self, level0, level1=None, timeout=_FamFOFBAcqBase.DEF_TIMEOUT):
        """
        Wait for BPM PosY PRBS excitation levels to be equal to desired
        values. Refer to check_prbs_bpmposx_levels for more details on
        arguments and returns.
        """
        _t0 = _time.time()
        while _time.time() - _t0 < timeout:
            if self.check_prbs_bpmposy_levels(level0, level1):
                return True
            _time.sleep(0.1)
        return False

    def _handle_bpm_levels(self, level0, level1):
        if len(level0) != NR_BPM or \
                (level1 is not None and len(level1) != NR_BPM):
            raise ValueError('Levels must have length equal to NR_BPM.')
        level0 = _np.asarray(level0)
        if level1 is None:
            level1 = -1 * level0
        # handle FOFB BPM ordering
        level0 = _np.roll(level0, 1)
        level1 = _np.roll(level1, 1)
        return level0, level1

    def cmd_prbs_bpms_enable(self, timeout=_FamFOFBAcqBase.DEF_TIMEOUT):
        """Command to enable PRBS for BPMs."""
        ctrls = list(self._ctlrs.values())
        self._set_devices_propty(ctrls, 'PRBSBPMPosEn-Sel', 1)
        if not self._wait_devices_propty(
                ctrls, 'PRBSBPMPosEn-Sts', 1, timeout=timeout):
            return False
        return True

    def cmd_prbs_bpms_disable(self, timeout=_FamFOFBAcqBase.DEF_TIMEOUT):
        """Command to disable PRBS for BPMs."""
        ctrls = list(self._ctlrs.values())
        self._set_devices_propty(ctrls, 'PRBSBPMPosEn-Sel', 0)
        if not self._wait_devices_propty(
                ctrls, 'PRBSBPMPosEn-Sts', 0, timeout=timeout/2):
            return False
        return True

    def get_data(self, bpmenbl=None, correnbl=None):
        """Get data matrices.

        Returns:
            orbx (numpy.ndarray, NxNR_BPM): Horizontal Orbit.
            orby (numpy.ndarray, NxNR_BPM): Vertical Orbit.
            currdata (numpy.ndarray, NxNR_CORR): Corrector current data.
            kickdata (numpy.ndarray, NxNR_CORR): Corrector kick data.

        """
        # bpm data
        orbx, orby = [], []
        if bpmenbl is None:
            bpmenbl = _np.ones(160, dtype=bool)
        bpmenbl = _np.roll(bpmenbl, 1)
        bpmenbl = bpmenbl.reshape(-1, 8)

        minbpm, mtx = None, None

        for i, ctrl in enumerate(self._ctlrs.values()):
            for idx in range(8):
                if not bpmenbl[i, idx]:
                    continue
                mtx = ctrl.get_bpm_posx(idx)
                mty = ctrl.get_bpm_posy(idx)
                orbx.append(mtx)
                orby.append(mty)

            if mtx is None:
                continue
            if minbpm is None:
                minbpm = mtx.size
            minbpm = _np.min([minbpm, mtx.size, mty.size])

        # # create numpy matrices
        for i, (obx, oby) in enumerate(zip(orbx, orby)):
            orbx[i] = obx[:minbpm]
            orby[i] = oby[:minbpm]
        orbx = _np.array(orbx).T
        orby = _np.array(orby).T

        # # handle FOFB BPM ordering
        orbx = _np.roll(orbx, -1, axis=1)
        orby = _np.roll(orby, -1, axis=1)

        # corrs data
        currdata, kickdata = [], []
        if correnbl is None:
            correnbl = _np.ones(160, dtype=bool)

        mincorr, mtc = None, None

        for i, psn in enumerate(self._psnames):
            if not correnbl[i]:
                continue
            dev = self._psdevs[psn]
            devconv = self._psconv[psn]
            mtc = dev.fofbacc_data
            currdata.append(mtc)
            kickdata.append(devconv.conv_current_2_strength(mtc))

            if mincorr is None:
                mincorr = mtc.size
            mincorr = min(mincorr, mtc.size)

        # # create numpy matrices
        for i, cur in enumerate(currdata):
            currdata[i] = cur[:mincorr]
            kickdata[i] = kickdata[i][:mincorr]
        currdata = _np.array(currdata).T
        kickdata = _np.array(kickdata).T

        return orbx, orby, currdata, kickdata

    def config_acquisition(
            self, nr_points_before: int, nr_points_after=0,
            channel=_FOFBCtrlAcqConst.Channel.sysid_applied,
            repeat=False, external=True) -> int:
        """Configure acquisition for FOFB controllers.

        Args:
            nr_points_before (int): number of points after trigger.
            nr_points_after (int): number of points after trigger.
                Defaults to 0.
            channel (int): acquisition channel (2: sysid, 3: sysid_applied).
                Defaults to 3.
            repeat (bool, optional): Whether or not acquisition should be
                repetitive. Defaults to True.
            external (bool, optional): Whether or not external trigger should
                be used. Defaults to True.

        Returns:
            int: code describing what happened:
                =0: FOFB controllers are ready.
                <0: Index of the first controller which did not stop
                    last acq. plus 1.
                >0: Index of the first controller which is not ready
                    for acq. plus 1.

        """
        if repeat:
            repeat = _FOFBCtrlAcqConst.Repeat.repetitive
        else:
            repeat = _FOFBCtrlAcqConst.Repeat.normal

        if external:
            trig = _FOFBCtrlAcqConst.TrigTyp.external
        else:
            trig = _FOFBCtrlAcqConst.TrigTyp.now

        ret = self.cmd_stop()
        if ret > 0:
            return -ret

        for ctl in self._ctlrs.values():
            ctl.repeat = repeat
            ctl.channel = channel
            ctl.trigger = trig
            ctl.nrsamples_pre = nr_points_before
            ctl.nrsamples_post = nr_points_after

        return self.cmd_start()

    def cmd_stop(self, wait=True, timeout=10) -> int:
        """Stop acquistion.

        Args:
            wait (bool, optional): whether or not to wait controllers
                get ready. Defaults to True.
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: FOFB controllers are ready.
                >0: Index of the first FOFB controller which did not
                    update plus 1.

        """
        for ctl in self._ctlrs.values():
            ctl.cmd_ctrl(_FOFBCtrlAcqConst.TrigEvt.stop)

        if wait:
            _time.sleep(2)
            return 0
            # return self.wait_acquisition_finish(timeout=timeout)
        return 0

    def wait_acquisition_finish(self, timeout=10) -> int:
        """Wait for all FOFB controllers to be ready for acquisition.

        Args:
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: FOFB controllers are ready.
                >0: Index of the first FOFB controller which did not
                    update plus 1.

        """
        for i, ctl in enumerate(self.ctrldevs.values()):
            t0_ = _time.time()
            if not ctl.wait_acq_finish(timeout):
                return i + 1
            timeout -= _time.time() - t0_
        return 0

    def cmd_start(self, wait=True, timeout=10) -> int:
        """Start acquisition.

        Args:
            wait (bool, optional): whether or not to wait controllers
                get ready. Defaults to True.
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: FOFB controllers are ready.
                >0: Index of the first FOFB controller which did not
                    update plus 1.

        """
        for ctl in self._ctlrs.values():
            ctl.cmd_ctrl(_FOFBCtrlAcqConst.TrigEvt.start)

        if wait:
            _time.sleep(2)
            return 0
            # return self.wait_acquisition_start(timeout=timeout)
        return 0

    def wait_acquisition_start(self, timeout=10) -> bool:
        """Wait for all FOFB controllers to be ready for acquisition.

        Args:
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: FOFB controllers are ready.
                >0: Index of the first FOFB controller which did not
                    update plus 1.

        """
        for i, bpm in enumerate(self.ctrldevs.values()):
            t0_ = _time.time()
            if not bpm.wait_acq_start(timeout):
                return i + 1
            timeout -= _time.time() - t0_
        return 0

    def update_initial_timestamps(self, bpmenbl=None, correnbl=None):
        """Call this method before acquisition to get data for comparison."""
        self._initial_timestamps = self._get_data_timestamps(bpmenbl, correnbl)

    def wait_update_data(self, timeout=10, bpmenbl=None, correnbl=None) -> int:
        """Call this method after acquisition to check if data was updated.

        For this method to work it is necessary to call
            update_initial_timestamps
        before the acquisition starts, so that a reference for comparison is
        created.

        Args:
            timeout (int, optional): Waiting timeout. Defaults to 10.

        Returns:
            int: code describing what happened:
                -4: initial timestamps were not defined;
                -3: TimeFrame data did not update;
                -2: PRBS data did not update;
                -1: FOFB Acc data did not update;
                =0: data updated.
                >0: index of the first BPM which did not update data plus 1.

        """
        if self._initial_timestamps is None:
            return -4

        tsmp0 = self._initial_timestamps
        while timeout > 0:
            t00 = _time.time()
            tsmp = self._get_data_timestamps(bpmenbl, correnbl)
            errs = [_np.equal(t, t0) for t, t0 in zip(tsmp, tsmp0)]
            continue_ = _np.any(errs[:2]) or _np.any(errs[2]) \
                or _np.any(errs[3:])
            if not continue_:
                return 0
            _time.sleep(0.1)
            timeout -= _time.time() - t00

        # check bpm data timestamps
        errs_bpm = _np.any(errs[:2], axis=0)
        if errs_bpm.any():
            return int(errs_bpm.nonzero()[0][0])+1

        # check timeframe data timestamps
        errs_timeframe = _np.any(errs[-2])
        if errs_timeframe.any():
            return -3

        # check prbs data timestamps
        errs_prbs = _np.any(errs[-1])
        if errs_prbs.any():
            return -2

        # if we reached this point, FOFB Acc data did not update
        return -1

    def _get_data_timestamps(self, bpmenbl=None, correnbl=None):
        """Get data timestamps.

        Returns:
            tsmpx (numpy.ndarray, NxNr BPMs): BPM PosX PVs timestamps.
            tsmpy (numpy.ndarray, NxNr BPMs): BPM PosY PVs timestamps.
            tsmpf (numpy.ndarray, NxNr Corr.): FOFB Acc Data PVs timestamps.
            tsmpt (numpy.ndarray, Nx20): Time Frame Data PVs timestamps.
            tsmpp (numpy.ndarray, Nx20): PRBS Data PVs timestamps.

        """
        # bpm
        tsmpx, tsmpy = [], []
        if bpmenbl is None:
            bpmenbl = _np.ones(160, dtype=bool)
        bpmenbl = _np.roll(bpmenbl, 1)
        bpmenbl = bpmenbl.reshape(-1, 8)

        for i, ctrl in enumerate(self._ctlrs.values()):
            for idx in range(8):
                if not bpmenbl[i, idx]:
                    continue
                pvox = ctrl.pv_object(f'BPM{idx}PosXData')
                pvoy = ctrl.pv_object(f'BPM{idx}PosYData')
                varx = pvox.get_timevars(timeout=self.DEF_TIMEOUT)
                vary = pvoy.get_timevars()
                tsmpx.append(
                    pvox.timestamp if varx is None else varx['timestamp'])
                tsmpy.append(
                    pvoy.timestamp if vary is None else vary['timestamp'])

        # corrs
        tsmpf = []
        if correnbl is None:
            correnbl = _np.ones(160, dtype=bool)

        for i, psn in enumerate(self._psnames):
            if not correnbl[i]:
                continue
            dev = self._psdevs[psn]
            pvof = dev.pv_object('SYSIDFOFBAccData')
            varf = pvof.get_timevars()
            tsmpf.append(pvof.timestamp if varf is None else varf['timestamp'])

        # time frame and prbs
        tsmpt, tsmpp = [], []
        for ctl in self._ctlrs.values():
            pvot = ctl.pv_object('TimeFrameData')
            vart = pvot.get_timevars()
            tsmpt.append(pvot.timestamp if vart is None else vart['timestamp'])
            pvop = ctl.pv_object('PRBSData')
            varp = pvop.get_timevars()
            tsmpp.append(pvop.timestamp if varp is None else varp['timestamp'])

        return tsmpx, tsmpy, tsmpf, tsmpt, tsmpp

    def set_currloop_kp(self, values):
        """Set current loop Kp parameter for all correctors.

        Args:
            values (numpy.ndarray, (160,)):
                Array with values to be applied to correctors Kp
                parameter in psnames order.

        """
        for i, psn in enumerate(self._psnames):
            dev = self._psdevs[psn]
            dev.currloop_kp = values[i]
        return True

    def set_currloop_ti(self, values):
        """Set current loop Ti parameter for all correctors.

        Args:
            values (numpy.ndarray, (160,)):
                Array with values to be applied to correctors Ti
                parameter in psnames order.

        """
        for i, psn in enumerate(self._psnames):
            dev = self._psdevs[psn]
            dev.currloop_ti = values[i]
        return True


# ------- rtmlamp acquisition devices -------

class FOFBCtrlLamp(_FOFBCtrlAcqBase):
    """FOFB controller RTMLAMP acquisition device."""

    def __init__(self, devname, auto_monitor_mon=True, props2init='all'):
        """Init."""
        # call base class constructor
        super().__init__(
            devname+':LAMP', props2init=props2init,
            auto_monitor_mon=auto_monitor_mon)


class FOFBPSLamp(_Device):
    """FOFB power supply RTMLAMP acquisition device."""

    PROPERTIES_DEFAULT = (
        'LAMPCurrentRawData', 'LAMPCurrentData',
        'LAMPVoltageRawData', 'LAMPVoltageData',
        )

    def __init__(self, devname, auto_monitor_mon=True, props2init='all'):
        """Init."""
        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)


class FamFOFBLamp(_FamFOFBAcqBase):
    """FOFB RTMLAMP acquisition device."""

    FOFBCTRL_CLASS = FOFBCtrlLamp
    FOFBPS_CLASS = FOFBPSLamp
