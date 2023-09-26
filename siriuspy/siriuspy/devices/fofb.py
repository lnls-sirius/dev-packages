"""FOFB devices."""

import time as _time
import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from ..namesys import SiriusPVName as _PVName
from ..search import BPMSearch as _BPMSearch, PSSearch as _PSSearch
from ..fofb.csdev import HLFOFBConst as _Const, NR_BPM

from .device import Device as _Device, DeviceSet as _DeviceSet
from .afc_acq_core import AFCACQLogicalTrigger
from .timing import Event
from .pwrsupply import PowerSupplyFC
from .psconv import StrengthConv


class FOFBCtrlBase:
    """FOFB Ctrl base."""

    _devices = {
        f'SI{i:02d}': f'IA-{i:02d}RaBPM:BS-FOFBCtrl' for i in range(1, 21)}
    DEVICES = _get_namedtuple('DEVICES', *zip(*_devices.items()))


# ---------------- ref device  ----------------

class FOFBCtrlRef(_Device, FOFBCtrlBase):
    """FOFB reference orbit controller device."""

    PROPERTIES_DEFAULT = (
        'RefOrbX-SP', 'RefOrbX-RB',
        'RefOrbY-SP', 'RefOrbY-RB',
        'MaxOrbDistortion-SP', 'MaxOrbDistortion-RB',
        'MaxOrbDistortionEnbl-Sel', 'MaxOrbDistortionEnbl-Sts',
        'MinBPMCnt-SP', 'MinBPMCnt-RB',
        'MinBPMCntEnbl-Sel', 'MinBPMCntEnbl-Sts',
        'LoopIntlk-Mon', 'LoopIntlkReset-Cmd',
        'SYSIDPRBSFOFBAccEn-Sel', 'SYSIDPRBSFOFBAccEn-Sts',
        'SYSIDPRBSBPMPosEn-Sel', 'SYSIDPRBSBPMPosEn-Sts',
        )

    def __init__(self, devname, props2init='all'):
        """Init."""
        # call base class constructor
        _Device.__init__(
            self, devname, props2init=props2init, auto_monitor_mon=True)

    @property
    def refx(self):
        """Reference orbit X."""
        return self['RefOrbX-RB']

    @refx.setter
    def refx(self, value):
        self['RefOrbX-SP'] = _np.array(value, dtype=int)

    @property
    def refy(self):
        """Reference orbit Y."""
        return self['RefOrbY-RB']

    @refy.setter
    def refy(self, value):
        self['RefOrbY-SP'] = _np.array(value, dtype=int)

    def check_refx(self, value):
        """Check whether RefOrbX is equal to value."""
        if not _np.all(self.refx == value):
            return False
        return True

    def check_refy(self, value):
        """Check whether RefOrbY is equal to value."""
        if not _np.all(self.refy == value):
            return False
        return True

    @property
    def max_orb_distortion(self):
        """Orbit distortion threshold [nm]."""
        return self['MaxOrbDistortion-RB']

    @max_orb_distortion.setter
    def max_orb_distortion(self, value):
        self['MaxOrbDistortion-SP'] = value

    @property
    def max_orb_distortion_enbl(self):
        """Orbit distortion above threshold detection enable status."""
        return self['MaxOrbDistortionEnbl-Sts']

    @max_orb_distortion_enbl.setter
    def max_orb_distortion_enbl(self, value):
        self['MaxOrbDistortionEnbl-Sel'] = value

    @property
    def min_bpm_count(self):
        """Minimum BPM packet count."""
        return self['MinBPMCnt-RB']

    @min_bpm_count.setter
    def min_bpm_count(self, value):
        self['MinBPMCnt-SP'] = value

    @property
    def min_bpm_count_enbl(self):
        """Packet loss detection enable status."""
        return self['MinBPMCntEnbl-Sts']

    @min_bpm_count_enbl.setter
    def min_bpm_count_enbl(self, value):
        self['MinBPMCntEnbl-Sel'] = value

    @property
    def sysid_fofbacc_exc_state(self):
        """SYSID core PRBS excitation enable state for correctors."""
        return self['SYSIDPRBSFOFBAccEn-Sts']

    @sysid_fofbacc_exc_state.setter
    def sysid_fofbacc_exc_state(self, value):
        self['SYSIDPRBSFOFBAccEn-Sel'] = value

    @property
    def sysid_bpm_exc_state(self):
        """SYSID core PRBS excitation enable state for BPMs."""
        return self['SYSIDPRBSBPMPosEn-Sts']

    @sysid_bpm_exc_state.setter
    def sysid_bpm_exc_state(self, value):
        self['SYSIDPRBSBPMPosEn-Sel'] = value

    @property
    def interlock(self):
        """Interlock status."""
        return self['LoopIntlk-Mon']

    def cmd_reset(self):
        """Reset interlocks."""
        self['LoopIntlkReset-Cmd'] = 1
        return True


# ---------------- DCC devices ----------------

class _DCCDevice(_Device):
    """FOFB Diamond communication controller device."""

    DEF_TIMEOUT = 1
    DEF_FMC_BPMCNT = NR_BPM
    DEF_P2P_BPMCNT = 8

    PROPERTIES_DEFAULT = (
        'BPMId-SP', 'BPMId-RB', 'BPMCnt-Mon',
        'CCEnable-Sel', 'CCEnable-Sts',
        'TimeFrameLen-SP', 'TimeFrameLen-RB',
        )
    _properties_fmc = (
        'LinkPartnerCH0-Mon', 'LinkPartnerCH1-Mon',
        'LinkPartnerCH2-Mon', 'LinkPartnerCH3-Mon',
        )

    def __init__(self, devname, dccname, props2init='all'):
        """Init."""
        self.dccname = dccname

        if props2init == 'all':
            props2init = list(_DCCDevice.PROPERTIES_DEFAULT)
            if 'FMC' in self.dccname:
                props2init += _DCCDevice._properties_fmc

        super().__init__(
            devname + ':' + dccname, props2init=props2init,
            auto_monitor_mon=True)

    @property
    def bpm_id(self):
        """BPM Id."""
        return self['BPMId-RB']

    @bpm_id.setter
    def bpm_id(self, value):
        self['BPMId-SP'] = value

    @property
    def bpm_count(self):
        """BPM count."""
        return self['BPMCnt-Mon']

    @property
    def cc_enable(self):
        """Communication enable."""
        return self['CCEnable-Sts']

    @cc_enable.setter
    def cc_enable(self, value):
        self['CCEnable-Sel'] = value

    @property
    def time_frame_len(self):
        """Time frame length."""
        return self['TimeFrameLen-RB']

    @time_frame_len.setter
    def time_frame_len(self, value):
        self['TimeFrameLen-SP'] = value

    @property
    def is_synced(self):
        """Is synchronized."""
        if not self.connected:
            return False
        cnt = self.DEF_FMC_BPMCNT if 'FMC' in self.dccname \
            else self.DEF_P2P_BPMCNT
        return self['BPMCnt-Mon'] == cnt


class FOFBCtrlDCC(_DCCDevice, FOFBCtrlBase):
    """FOFBCtrl DCC device."""

    class PROPDEVICES:
        """DCC devices."""

        FMC = 'DCCFMC'
        P2P = 'DCCP2P'
        ALL = (FMC, P2P)

    def __init__(self, devname, dccname, props2init='all'):
        """Init."""
        if dccname not in self.PROPDEVICES.ALL:
            raise NotImplementedError(dccname)
        _DCCDevice.__init__(self, devname, dccname, props2init=props2init)

    @property
    def linkpartners(self):
        """Return linked partners."""
        linkpart_props = [
            'LinkPartnerCH0-Mon', 'LinkPartnerCH1-Mon',
            'LinkPartnerCH2-Mon', 'LinkPartnerCH3-Mon']
        return set(self[prop] for prop in linkpart_props)


class BPMDCC(_DCCDevice):
    """BPM DCC device."""

    def __init__(self, devname, props2init='all'):
        """Init."""
        super().__init__(devname, 'DCCP2P', props2init=props2init)


# ---------------- Fam devices ----------------

class FamFOFBControllers(_DeviceSet):
    """Family of FOFBCtrl and related BPM devices."""

    DEF_TIMEOUT = 10  # [s]
    DEF_DCC_TIMEFRAMELEN = 5000
    DEF_BPMTRIG_RCVSRC = 0
    DEF_BPMTRIG_RCVIN = 5
    BPM_TRIGS_ID = 20
    FOFBCTRL_BPMID_OFFSET = 480
    BPM_DCC_PAIRS = {
        'M1': 'M2',
        'C1-1': 'C1-2',
        'C2': 'C3-1',
        'C3-2': 'C4',
    }
    BPM_DCC_PAIRS.update({bd: bu for bu, bd in BPM_DCC_PAIRS.items()})

    def __init__(self):
        """Init."""
        # FOFBCtrl Refs and DCCs
        bpmids = _np.array(
            [self.FOFBCTRL_BPMID_OFFSET - 1 + i for i in range(1, 21)])
        lpcw = _np.roll(bpmids, 1)
        lpaw = _np.roll(bpmids, -1)
        self._ctl_ids, self._ctl_part = dict(), dict()
        self._ctl_refs, self._ctl_dccs = dict(), dict()
        for idx, ctl in enumerate(FOFBCtrlBase.DEVICES):
            self._ctl_ids[ctl] = bpmids[idx]
            self._ctl_part[ctl] = {lpcw[idx], lpaw[idx]}
            self._ctl_refs[ctl] = FOFBCtrlRef(ctl)
            for dcc in FOFBCtrlDCC.PROPDEVICES.ALL:
                self._ctl_dccs[ctl + ':' + dcc] = FOFBCtrlDCC(ctl, dcc)
        # BPM DCCs and triggers
        self._bpmnames = _BPMSearch.get_names({'sec': 'SI', 'dev': 'BPM'})
        bpmids = [((i + 1) // 2) * 2 % 160 for i in range(NR_BPM)]
        self._bpm_dccs, self._bpm_trgs, self._bpm_ids = dict(), dict(), dict()
        for idx, bpm in enumerate(self._bpmnames):
            self._bpm_ids[bpm] = bpmids[idx]
            self._bpm_dccs[bpm] = BPMDCC(bpm)
            self._bpm_trgs[bpm] = AFCACQLogicalTrigger(bpm, self.BPM_TRIGS_ID)
        bpm2dsbl = [
            'SI-'+sub+':DI-BPM-'+idx
            for sub in ['06SB', '07SP', '08SB', '09SA', '10SB', '11SP', '12SB']
            for idx in ['1', '2']
        ]
        self._bpmdcc2dsbl = dict()
        for bpm in bpm2dsbl:
            self._bpmdcc2dsbl[bpm] = BPMDCC(bpm)
        # fofb event
        self._evt_fofb = Event('FOFBS')

        devices = list()
        devices.extend(self._ctl_refs.values())
        devices.extend(self._ctl_dccs.values())
        devices.extend(self._bpm_dccs.values())
        devices.extend(self._bpm_trgs.values())
        devices.append(self._evt_fofb)

        super().__init__(devices, devname='SI-Glob:BS-FOFB')

    @property
    def ctrlrefdevs(self):
        """FOFBCtrlRef device list."""
        return self._ctl_refs

    @property
    def ctrldccdevs(self):
        """FOFBCtrlDCC device list."""
        return self._ctl_dccs

    @property
    def bpmdccdevs(self):
        """BPMDCC device list."""
        return self._bpm_dccs

    @property
    def bpmtrigdevs(self):
        """AFCACQLogicalTrigger device list."""
        return self._bpm_trgs

    @property
    def fofbevtdev(self):
        """FOFBS Event device."""
        return self._evt_fofb

    def set_reforbx(self, value):
        """Set RefOrbX for all FOFB controllers."""
        for ctrl in self._ctl_refs.values():
            ctrl.refx = value
        return True

    def set_reforby(self, value):
        """Set RefOrbY for all FOFB controllers."""
        for ctrl in self._ctl_refs.values():
            ctrl.refy = value
        return True

    def check_reforbx(self, value):
        """Check whether RefOrbX is equal to value."""
        if not self.connected:
            return False
        for ctrl in self._ctl_refs.values():
            if not ctrl.check_refx(value):
                return False
        return True

    def check_reforby(self, value):
        """Check whether RefOrbY is equal to value."""
        if not self.connected:
            return False
        for ctrl in self._ctl_refs.values():
            if not ctrl.check_refy(value):
                return False
        return True

    @property
    def max_orb_distortion(self):
        """Orbit distortion threshold [nm].

        Returns:
            threshold (numpy.ndarray, 20):
                orbit distortion threshold for each FOFB controller.
        """
        devs = self._ctl_refs.values()
        return _np.array([d.max_orb_distortion for d in devs])

    def set_max_orb_distortion(self, value, timeout=DEF_TIMEOUT):
        """Set orbit distortion threshold [nm]."""
        devs = list(self._ctl_refs.values())
        self._set_devices_propty(devs, 'MaxOrbDistortion-SP', value)
        if not self._wait_devices_propty(
                devs, 'MaxOrbDistortion-RB', value, timeout=timeout):
            return False
        return True

    @property
    def max_orb_distortion_enbl(self):
        """Orbit distortion above threshold detection enable status.

        Returns:
            status (numpy.ndarray, 20):
                orbit distortion detection status for each FOFB controller.
        """
        devs = self._ctl_refs.values()
        return _np.array([d.max_orb_distortion_enbl for d in devs])

    def set_max_orb_distortion_enbl(self, value, timeout=DEF_TIMEOUT):
        """Set orbit distortion above threshold detection enable status."""
        devs = list(self._ctl_refs.values())
        self._set_devices_propty(devs, 'MaxOrbDistortionEnbl-Sel', value)
        if not self._wait_devices_propty(
                devs, 'MaxOrbDistortionEnbl-Sts', value, timeout=timeout):
            return False
        return True

    @property
    def min_bpm_count(self):
        """Minimum BPM packet count.

        Returns:
            minimum (numpy.ndarray, 20):
                minimum BPM packet count for each FOFB controller.
        """
        devs = self._ctl_refs.values()
        return _np.array([d.min_bpm_count for d in devs])

    def set_min_bpm_count(self, value, timeout=DEF_TIMEOUT):
        """Set minimum BPM packet count."""
        devs = list(self._ctl_refs.values())
        self._set_devices_propty(devs, 'MinBPMCnt-SP', value)
        if not self._wait_devices_propty(
                devs, 'MinBPMCnt-RB', value, timeout=timeout):
            return False
        return True

    @property
    def min_bpm_count_enbl(self):
        """Packet loss detection enable status.

        Returns:
            status (numpy.ndarray, 20):
                packet loss detection status for each FOFB controller.
        """
        devs = self._ctl_refs.values()
        return _np.array([d.min_bpm_count_enbl for d in devs])

    def set_min_bpm_count_enbl(self, value, timeout=DEF_TIMEOUT):
        """Set orbit distortion above threshold detection enable status."""
        devs = list(self._ctl_refs.values())
        self._set_devices_propty(devs, 'MinBPMCntEnbl-Sel', value)
        if not self._wait_devices_propty(
                devs, 'MinBPMCntEnbl-Sts', value, timeout=timeout):
            return False
        return True

    @property
    def interlock(self):
        """Interlock status.

        Returns:
            status (numpy.ndarray, 20):
                interlock status for each FOFB controller.
        """
        devs = self._ctl_refs.values()
        return _np.array([d.interlock for d in devs])

    @property
    def interlock_ok(self):
        """Interlock ok status."""
        if not self.connected:
            return False
        return _np.all(self.interlock == 0)

    def cmd_reset(self, timeout=DEF_TIMEOUT):
        """Send reset interlock command for all FOFB controllers."""
        devs = list(self._ctl_refs.values())
        self._set_devices_propty(devs, 'LoopIntlkReset-Cmd', 1)
        if not self._wait_devices_propty(
                devs, 'LoopIntlk-Mon', 0, timeout=timeout):
            return False
        return True

    @property
    def bpm_id(self):
        """Return DCC BPMIds."""
        if not self.connected:
            return False
        bpmids = dict()
        for dev in self._ctl_dccs.values():
            bpmids[dev.pv_object('BPMId-RB').pvname] = dev.bpm_id
        for dev in self._bpm_dccs.values():
            bpmids[dev.pv_object('BPMId-RB').pvname] = dev.bpm_id
        return bpmids

    @property
    def bpm_id_configured(self):
        """Check whether DCC BPMIds are configured."""
        if not self.connected:
            return False
        for dcc, dev in self._ctl_dccs.items():
            ctl = _PVName(dcc).device_name
            if not dev.bpm_id == self._ctl_ids[ctl]:
                return False
        for bpm, dev in self._bpm_dccs.items():
            if not dev.bpm_id == self._bpm_ids[bpm]:
                return False
        return True

    def cmd_config_bpm_id(self):
        """Command to configure DCC BPMIds."""
        if not self.connected:
            return False
        for dcc, dev in self._ctl_dccs.items():
            ctl = _PVName(dcc).device_name
            dev.bpm_id = self._ctl_ids[ctl]
        for bpm, dev in self._bpm_dccs.items():
            dev.bpm_id = self._bpm_ids[bpm]
        return True

    @property
    def linkpartners(self):
        """Return link partners."""
        if not self.connected:
            return False
        partners = dict()
        for dev in self._ctl_dccs.values():
            if 'FMC' not in dev.dccname:
                continue
            partners[dev.devname] = dev.linkpartners
        return partners

    @property
    def linkpartners_connected(self):
        """Check whether adjacent partners are connected."""
        if not self.connected:
            return False
        for dcc, dev in self._ctl_dccs.items():
            if 'FMC' not in dev.dccname:
                continue
            ctl = _PVName(dcc).device_name
            nrpart = len(self._ctl_part[ctl])
            if not len(dev.linkpartners & self._ctl_part[ctl]) == nrpart:
                return False
        return True

    @property
    def bpm_count(self):
        """Return DCC BPMCnt."""
        if not self.connected:
            return False
        bpmids = dict()
        for dev in self._ctl_dccs.values():
            bpmids[dev.pv_object('BPMCnt-Mon').pvname] = dev.bpm_count
        for dev in self._bpm_dccs.values():
            bpmids[dev.pv_object('BPMCnt-Mon').pvname] = dev.bpm_count
        return bpmids

    def cmd_sync_net(self, bpms=None, timeout=DEF_TIMEOUT):
        """Command to synchronize DCCs."""
        alldccs = list(self._ctl_dccs.values()) + list(self._bpm_dccs.values())
        enbdccs = list(self._ctl_dccs.values())
        if bpms is None:
            bpms = self._bpmnames
        for bpm in bpms:
            enbdccs.append(self._bpm_dccs[bpm])

        # temporary solution: disable BPM DCCs that are not in FOFB network
        dcc2dsbl = list(self._bpmdcc2dsbl.values())
        self._set_devices_propty(dcc2dsbl, 'CCEnable-Sel', 0)
        if not self._wait_devices_propty(
                dcc2dsbl, 'CCEnable-Sts', 0, timeout=timeout/2):
            return False

        self._set_devices_propty(alldccs, 'CCEnable-Sel', 0)
        if not self._wait_devices_propty(
                alldccs, 'CCEnable-Sts', 0, timeout=timeout/2):
            return False
        self._set_devices_propty(enbdccs, 'CCEnable-Sel', 1)
        if not self._wait_devices_propty(
                enbdccs, 'CCEnable-Sts', 1, timeout=timeout/2):
            return False
        self._evt_fofb.cmd_external_trigger()
        return True

    def check_net_synced(self, bpms=None):
        """Check whether DCCs are synchronized."""
        if not self.connected:
            return False
        if bpms is None:
            bpms = self._bpmnames
        dccfmc_bpmcount = len(self.get_dccfmc_visible_bpms(bpms))
        for dev in self._ctl_dccs.values():
            if dev.dccname != 'DCCFMC':
                continue
            if not dev.bpm_count == dccfmc_bpmcount:
                return False
        for bpm in bpms:
            if not self._bpm_dccs[bpm].cc_enable == 1:
                return False
        return True

    def get_dccfmc_visible_bpms(self, bpms):
        """Return DCCFMC visible BPMs."""
        dccenbl = set()
        for bpm in bpms:
            name = _PVName(bpm)
            nick = name.sub[2:] + ('-' + name.idx if name.idx else '')
            nickpair = self.BPM_DCC_PAIRS[nick]
            nps = nickpair.split('-')
            if len(nps) == 1:
                nps.append('')
            pair = name.substitute(sub=name.sub[:2] + nps[0], idx=nps[1])
            dccenbl.add(bpm)
            dccenbl.add(pair)
        return dccenbl

    @property
    def time_frame_len(self):
        """Time frame length.

        Returns:
            length (numpy.ndarray, 20*2+160):
                time frame length for each FOFB controller DCC and for
                each BPM DCC.
        """
        dccs = list(self._ctl_dccs.values()) + list(self._bpm_dccs.values())
        return _np.array([d.time_frame_len for d in dccs])

    def set_time_frame_len(
            self, value=DEF_DCC_TIMEFRAMELEN, timeout=DEF_TIMEOUT):
        """Set DCCs TimeFrameLen."""
        dccs = list(self._ctl_dccs.values()) + list(self._bpm_dccs.values())
        self._set_devices_propty(dccs, 'TimeFrameLen-SP', value)
        if not self._wait_devices_propty(
                dccs, 'TimeFrameLen-RB', value, timeout=timeout):
            return False
        return True

    @property
    def bpm_trigs_configuration(self):
        """Return BPM logical triggers configuration."""
        if not self.connected:
            return False
        conf = dict()
        for dev in self._bpm_trgs.values():
            conf[dev.pv_object('RcvSrc-Sts').pvname] = dev.receiver_source
            conf[dev.pv_object('RcvInSel-RB').pvname] = dev.receiver_in_sel
        return conf

    @property
    def bpm_trigs_configured(self):
        """Check whether all BPM triggers are configured."""
        if not self.connected:
            return False
        for dev in self._bpm_trgs.values():
            if not dev.receiver_source == self.DEF_BPMTRIG_RCVSRC:
                return False
            if not dev.receiver_in_sel == self.DEF_BPMTRIG_RCVIN:
                return False
        return True

    def cmd_config_bpm_trigs(self, timeout=DEF_TIMEOUT):
        """Command to configure BPM triggers."""
        devs = list(self._bpm_trgs.values())
        rsrc = self.DEF_BPMTRIG_RCVSRC
        rins = self.DEF_BPMTRIG_RCVIN
        self._set_devices_propty(devs, 'RcvSrc-Sel', rsrc)
        if not self._wait_devices_propty(
                devs, 'RcvSrc-Sts', rsrc, timeout=timeout/2):
            return False
        self._set_devices_propty(devs, 'RcvInSel-SP', rins)
        if not self._wait_devices_propty(
                devs, 'RcvInSel-RB', rins, timeout=timeout/2):
            return False
        return True

    def check_sysid_exc_disabled(self):
        """Check whether SYSID excitation is disabled."""
        if not self.connected:
            return False
        for ctl in self._ctl_refs.values():
            if ctl.sysid_fofbacc_exc_state or ctl.sysid_bpm_exc_state:
                return False
        return True

    def cmd_dsbl_sysid_exc(self, timeout=DEF_TIMEOUT):
        """Command to disable SYSID excitation."""
        devs = list(self._ctl_refs.values())
        self._set_devices_propty(devs, 'SYSIDPRBSFOFBAccEn-Sel', 0)
        if not self._wait_devices_propty(
                devs, 'SYSIDPRBSFOFBAccEn-Sts', 0, timeout=timeout/2):
            return False
        self._set_devices_propty(devs, 'SYSIDPRBSBPMPosEn-Sel', 0)
        if not self._wait_devices_propty(
                devs, 'SYSIDPRBSBPMPosEn-Sts', 0, timeout=timeout/2):
            return False
        self._evt_fofb.cmd_external_trigger()
        return True


class FamFastCorrs(_DeviceSet):
    """Family of FOFB fast correctors."""

    DEF_TIMEOUT = 10  # [s]
    OPMODE_SEL = PowerSupplyFC.OPMODE_SEL
    OPMODE_STS = PowerSupplyFC.OPMODE_STS
    DEF_ATOL_INVRESPMATROW = 2**-17
    DEF_ATOL_FOFBACCGAIN = 2**-12
    DEF_ATOL_FOFBACCSAT = 2e-2
    DEF_ATOL_CURRENT_RB = 1e-6
    DEF_ATOL_CURRENT_MON = 2e-2

    def __init__(self, psnames=None):
        """Init."""
        if not psnames:
            chn = _PSSearch.get_psnames({'sec': 'SI', 'dev': 'FCH'})
            cvn = _PSSearch.get_psnames({'sec': 'SI', 'dev': 'FCV'})
            psnames = chn + cvn
        self._psnames = psnames
        self._psdevs = [PowerSupplyFC(psn) for psn in self._psnames]
        self._psconv = [
            StrengthConv(psn, 'Ref-Mon', auto_monitor_mon=True)
            for psn in self._psnames]
        super().__init__(
            self._psdevs + self._psconv, devname='SI-Glob:PS-FCHV')

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
    def pwrstate(self):
        """Power State.

        Returns:
            state (numpy.ndarray, 160):
                PwrState for each power supply.
        """
        return _np.array([p.pwrstate for p in self._psdevs])

    @property
    def opmode(self):
        """Operation Mode.

        Returns:
            mode (numpy.ndarray, 160):
                OpMode for each power supply.
        """
        return _np.array([p.opmode for p in self._psdevs])

    @property
    def current(self):
        """Current readback.

        Returns:
            current (numpy.ndarray, 160):
                OpMode for each power supply.
        """
        return _np.array([p.current for p in self._psdevs])

    @property
    def current_mon(self):
        """Implemented current.

        Returns:
            current (numpy.ndarray, 160):
                OpMode for each power supply.
        """
        return _np.array([p.current_mon for p in self._psdevs])

    @property
    def fofbacc_gain(self):
        """FOFB pre-accumulator gain.

        Returns:
            gain (numpy.ndarray, 160):
                FOFB pre-accumulator gain for each power supply.
        """
        return _np.array([p.fofbacc_gain for p in self._psdevs])

    @property
    def fofbacc_freeze(self):
        """FOFB pre-accumulator freeze state.

        Returns:
            gain (numpy.ndarray, 160):
                FOFB pre-accumulator freeze state for each power supply.
        """
        return _np.array([p.fofbacc_freeze for p in self._psdevs])

    @property
    def fofbacc_satmax(self):
        """FOFB pre-accumulator maximum saturation current [A].

        Returns:
            gain (numpy.ndarray, 160):
                FOFB pre-accumulator maximum saturation current
                for each power supply.
        """
        return _np.array([p.fofbacc_satmax for p in self._psdevs])

    @property
    def fofbacc_satmin(self):
        """FOFB pre-accumulator minimum saturation current [A].

        Returns:
            gain (numpy.ndarray, 160):
                FOFB pre-accumulator minimum saturation current
                for each power supply.
        """
        return _np.array([p.fofbacc_satmin for p in self._psdevs])

    @property
    def fofbacc_decimation(self):
        """FOFB pre-accumulator decimation.

        Returns:
            counts (numpy.ndarray, 160):
                FOFB pre-accumulator decimation for each power supply.
        """
        return _np.array([p.fofbacc_decimation for p in self._psdevs])

    @property
    def curr_gain(self):
        """Current gain.

        Returns:
            gain (numpy.ndarray, 160):
                current gain for each power supply.
        """
        return _np.array([p.curr_gain for p in self._psdevs])

    @property
    def strength_2_current_factor(self):
        """Strength to current convertion factor.

        Returns:
            factor (numpy.ndarray, NR_BPM):
                convertion factor for each power supply.
        """
        return _np.array(
            [p.conv_strength_2_current(1, strengths_dipole=3.0)
             for p in self._psconv])

    def set_pwrstate(
            self, state, psnames=None, psindices=None):
        """Command to set power supply pwrstate."""
        devs = self._get_devices(psnames, psindices)
        self._set_devices_propty(devs, 'PwrState-Sel', state)
        return True

    def check_pwrstate(
            self, state, psnames=None, psindices=None,
            timeout=DEF_TIMEOUT):
        """Check whether power supplies are in desired pwrstate."""
        if not self.connected:
            return False
        devs = self._get_devices(psnames, psindices)
        return self._wait_devices_propty(
            devs, 'PwrState-Sts', state, timeout=timeout)

    def set_opmode(
            self, opmode, psnames=None, psindices=None):
        """Command to set power supply opmode."""
        devs = self._get_devices(psnames, psindices)
        self._set_devices_propty(devs, 'OpMode-Sel', opmode)
        return True

    def check_opmode(
            self, opmode, psnames=None, psindices=None,
            timeout=DEF_TIMEOUT):
        """Check whether power supplies are in desired opmode."""
        if not self.connected:
            return False
        devs = self._get_devices(psnames, psindices)
        return self._wait_devices_propty(
            devs, 'OpMode-Sts', opmode, timeout=timeout)

    def set_current(self, values, psnames=None, psindices=None):
        """Set power supply current."""
        devs = self._get_devices(psnames, psindices)
        if isinstance(values, (int, float, bool)):
            values = len(devs) * [values]
        for i, dev in enumerate(devs):
            dev.current = values[i]
        return True

    def check_current(
            self, values, psnames=None, psindices=None,
            atol=DEF_ATOL_CURRENT_RB):
        """Check whether power supplies have desired current."""
        if not self.connected:
            return False
        devs = self._get_devices(psnames, psindices)
        impltd = _np.asarray([d.current for d in devs])
        if isinstance(values, (int, float, bool)):
            values = len(devs) * [values]
        if _np.allclose(values, impltd, atol=atol):
            return True
        return False

    def check_current_mon(
            self, values, psnames=None, psindices=None,
            atol=DEF_ATOL_CURRENT_MON):
        """Check whether power supplies have desired implemented current."""
        if not self.connected:
            return False
        devs = self._get_devices(psnames, psindices)
        impltd = _np.asarray([d.current_mon for d in devs])
        if isinstance(values, (int, float, bool)):
            values = len(devs) * [values]
        if _np.allclose(values, impltd, atol=atol):
            return True
        return False

    def set_invrespmat_row(self, values, psnames=None, psindices=None):
        """Command to set power supply correction coefficients value."""
        if not isinstance(values, (list, tuple, _np.ndarray)):
            raise ValueError('Value must be iterable.')
        devs = self._get_devices(psnames, psindices)
        if not len(values) == len(devs):
            raise ValueError('Values and indices must have the same size.')
        if any([len(v) != 2*NR_BPM for v in values]):
            raise ValueError(f'Value must have size {2*NR_BPM}.')
        for i, dev in enumerate(devs):
            dev.invrespmat_row_x = values[i][:NR_BPM]
            dev.invrespmat_row_y = values[i][NR_BPM:]
        return True

    def check_invrespmat_row(
            self, values, psnames=None, psindices=None,
            atol=DEF_ATOL_INVRESPMATROW):
        """Check power supplies correction coefficients."""
        if not self.connected:
            return False
        if not isinstance(values, (list, tuple, _np.ndarray)):
            raise ValueError('Value must be iterable.')
        devs = self._get_devices(psnames, psindices)
        if not len(values) == len(devs):
            raise ValueError('Values and indices must have the same size.')
        for i, dev in enumerate(devs):
            impltd = _np.hstack([dev.invrespmat_row_x, dev.invrespmat_row_y])
            if len(values[i]) != len(impltd):
                return False
            if not _np.allclose(values[i], impltd, atol=atol):
                return False
        return True

    def set_fofbacc_gain(self, values, psnames=None, psindices=None):
        """Command to set power supply correction gain."""
        if not isinstance(values, (list, tuple, _np.ndarray)):
            raise ValueError('Value must be iterable.')
        devs = self._get_devices(psnames, psindices)
        for i, dev in enumerate(devs):
            dev.fofbacc_gain = values[i]
        return True

    def check_fofbacc_gain(
            self, values, psnames=None, psindices=None,
            atol=DEF_ATOL_FOFBACCGAIN):
        """Check whether power supplies have desired correction gain."""
        if not self.connected:
            return False
        if not isinstance(values, (list, tuple, _np.ndarray)):
            raise ValueError('Value must be iterable.')
        values = _np.asarray(values)
        devs = self._get_devices(psnames, psindices)
        impltd = _np.asarray([d.fofbacc_gain for d in devs])
        if _np.allclose(values, impltd, atol=atol):
            return True
        return False

    def set_fofbacc_freeze(self, values, psnames=None, psindices=None):
        """Command to set power supply pre-accumulator freeze state."""
        devs = self._get_devices(psnames, psindices)
        if isinstance(values, (int, float, bool)):
            values = len(devs) * [values]
        for i, dev in enumerate(devs):
            dev.fofbacc_freeze = values[i]
        return True

    def check_fofbacc_freeze(
            self, values, psnames=None, psindices=None,
            timeout=DEF_TIMEOUT):
        """Check whether power supplies have desired freeze state."""
        if not self.connected:
            return False
        devs = self._get_devices(psnames, psindices)
        if isinstance(values, (int, float, bool)):
            values = len(devs) * [values]
        values = list(values)
        return self._wait_devices_propty(
            devs, 'FOFBAccFreeze-Sts', values, timeout=timeout)

    def set_fofbacc_satmax(self, values, psnames=None, psindices=None):
        """Set power supply pre-accumulator max.saturation current."""
        devs = self._get_devices(psnames, psindices)
        if isinstance(values, (int, float, bool)):
            values = len(devs) * [values]
        for i, dev in enumerate(devs):
            dev.fofbacc_satmax = values[i]
        return True

    def check_fofbacc_satmax(
            self, values, psnames=None, psindices=None,
            atol=DEF_ATOL_FOFBACCSAT):
        """Check whether power supplies have desired max.saturation value."""
        if not self.connected:
            return False
        devs = self._get_devices(psnames, psindices)
        impltd = _np.asarray([d.fofbacc_satmax for d in devs])
        if isinstance(values, (int, float, bool)):
            values = len(devs) * [values]
        if _np.allclose(values, impltd, atol=atol):
            return True
        return False

    def set_fofbacc_satmin(self, values, psnames=None, psindices=None):
        """Set power supply pre-accumulator min.saturation current."""
        devs = self._get_devices(psnames, psindices)
        if isinstance(values, (int, float, bool)):
            values = len(devs) * [values]
        for i, dev in enumerate(devs):
            dev.fofbacc_satmin = values[i]
        return True

    def check_fofbacc_satmin(
            self, values, psnames=None, psindices=None,
            atol=DEF_ATOL_FOFBACCSAT):
        """Check whether power supplies have desired min.saturation value."""
        if not self.connected:
            return False
        devs = self._get_devices(psnames, psindices)
        impltd = _np.asarray([d.fofbacc_satmin for d in devs])
        if isinstance(values, (int, float, bool)):
            values = len(devs) * [values]
        if _np.allclose(values, impltd, atol=atol):
            return True
        return False

    def set_fofbacc_decimation(self, values, psnames=None, psindices=None):
        """Set power supply pre-accumulator decimation."""
        devs = self._get_devices(psnames, psindices)
        if isinstance(values, (int, float, bool)):
            values = len(devs) * [values]
        for i, dev in enumerate(devs):
            dev.fofbacc_decimation = values[i]
        return True

    def check_fofbacc_decimation(
            self, values, psnames=None, psindices=None,
            atol=DEF_ATOL_CURRENT_MON):
        """Check whether power supplies have desired decimation value."""
        if not self.connected:
            return False
        devs = self._get_devices(psnames, psindices)
        impltd = _np.asarray([d.fofbacc_decimation for d in devs])
        if isinstance(values, (int, float, bool)):
            values = len(devs) * [values]
        if _np.allclose(values, impltd, atol=atol):
            return True
        return False

    def cmd_fofbacc_clear(self, psnames=None, psindices=None):
        """Send clear power supplies pre-accumulator."""
        for dev in self._get_devices(psnames, psindices):
            dev.cmd_fofbacc_clear()
        return True

    # ----- private methods -----

    def _get_devices(self, names, indices):
        if names:
            indices = [self._psnames.index(psn) for psn in names]
        elif indices is not None and \
                not isinstance(indices, (list, tuple, _np.ndarray)):
            indices = [indices, ]
        if indices is None:
            indices = [i for i in range(len(self._psnames))]
        return [self._psdevs[i] for i in indices]


# ----------------  HL device  ----------------

class HLFOFB(_Device):
    """Control high level FOFB IOC."""

    class DEVICES:
        """Devices names."""

        SI = 'SI-Glob:AP-FOFB'
        ALL = (SI, )

    PROPERTIES_DEFAULT = (
        'LoopState-Sel', 'LoopState-Sts',
        'LoopGainH-SP', 'LoopGainH-RB', 'LoopGainH-Mon',
        'LoopGainV-SP', 'LoopGainV-RB', 'LoopGainV-Mon',
        'LoopMaxOrbDistortion-SP', 'LoopMaxOrbDistortion-RB',
        'LoopMaxOrbDistortionEnbl-Sel', 'LoopMaxOrbDistortionEnbl-Sts',
        'LoopPacketLossDetecEnbl-Sel', 'LoopPacketLossDetecEnbl-Sts',
        'CorrStatus-Mon', 'CorrConfig-Cmd',
        'CorrSetPwrStateOn-Cmd', 'CorrSetPwrStateOff-Cmd',
        'CorrSetOpModeManual-Cmd',
        'CorrSetAccFreezeDsbl-Cmd', 'CorrSetAccFreezeEnbl-Cmd',
        'CorrSetAccClear-Cmd', 'CorrSetCurrZero-Cmd',
        'CorrSetCurrZeroDuration-SP', 'CorrSetCurrZeroDuration-RB',
        'CHAccSatMax-SP', 'CHAccSatMax-RB',
        'CVAccSatMax-SP', 'CVAccSatMax-RB',
        'CtrlrStatus-Mon', 'CtrlrConfBPMId-Cmd',
        'CtrlrSyncNet-Cmd', 'CtrlrSyncRefOrb-Cmd',
        'CtrlrSyncTFrameLen-Cmd', 'CtrlrConfBPMLogTrg-Cmd',
        'CtrlrSyncMaxOrbDist-Cmd', 'CtrlrSyncPacketLossDetec-Cmd',
        'CtrlrReset-Cmd',
        'KickCHAcc-Mon', 'KickCVAcc-Mon',
        'KickCHRef-Mon', 'KickCVRef-Mon',
        'KickCH-Mon', 'KickCV-Mon',
        'RefOrbX-SP', 'RefOrbX-RB', 'RefOrbY-SP', 'RefOrbY-RB',
        'RefOrbHwX-Mon', 'RefOrbHwY-Mon',
        'BPMXEnblList-SP', 'BPMXEnblList-RB',
        'BPMYEnblList-SP', 'BPMYEnblList-RB',
        'CHEnblList-SP', 'CHEnblList-RB',
        'CVEnblList-SP', 'CVEnblList-RB',
        'UseRF-Sel', 'UseRF-Sts',
        'MinSingValue-SP', 'MinSingValue-RB',
        'TikhonovRegConst-SP', 'TikhonovRegConst-RB',
        'SingValuesRaw-Mon', 'SingValues-Mon', 'NrSingValues-Mon',
        'RespMat-SP', 'RespMat-RB', 'RespMat-Mon', 'InvRespMat-Mon',
        'SingValuesHw-Mon', 'RespMatHw-Mon', 'InvRespMatHw-Mon',
        'InvRespMatNormMode-Sel', 'InvRespMatNormMode-Sts',
        'CorrCoeffs-Mon', 'CorrGains-Mon',
        'MeasRespMat-Cmd', 'MeasRespMat-Mon',
        'MeasRespMatKickCH-SP', 'MeasRespMatKickCH-RB',
        'MeasRespMatKickCV-SP', 'MeasRespMatKickCV-RB',
        'MeasRespMatKickRF-SP', 'MeasRespMatKickRF-RB',
        'MeasRespMatWait-SP', 'MeasRespMatWait-RB',
    )

    _default_timeout = 10
    _default_timeout_respm = 2 * 60 * 60  # [s]

    def __init__(self, devname=None, props2init='all'):
        """Init."""
        # check if device exists
        if devname is None:
            devname = HLFOFB.DEVICES.SI
        if devname not in HLFOFB.DEVICES.ALL:
            raise NotImplementedError(devname)

        self._data = _Const()

        # call base class constructor
        super().__init__(devname, props2init=props2init)

    @property
    def data(self):
        """IOC constants."""
        return self._data

    @property
    def loop_state(self):
        """Loop state."""
        return self['LoopState-Sts']

    @loop_state.setter
    def loop_state(self, value):
        self['LoopState-Sel'] = value

    def cmd_turn_on_loop_state(self, timeout=None):
        """Turn on loop state."""
        if self.loop_state == _Const.LoopState.Closed:
            return True
        self['LoopState-Sel'] = _Const.LoopState.Closed
        return self._wait(
            'LoopState-Sts', _Const.LoopState.Closed, timeout=timeout)

    def cmd_turn_off_loop_state(self, timeout=None):
        """Turn off loop state."""
        if self.loop_state == _Const.LoopState.Open:
            return True
        self['LoopState-Sel'] = _Const.LoopState.Open
        return self._wait(
            'LoopState-Sts', _Const.LoopState.Open, timeout=timeout)

    @property
    def loop_gain_h(self):
        """Loop gain H."""
        return self['LoopGainH-RB']

    @loop_gain_h.setter
    def loop_gain_h(self, value):
        self['LoopGainH-SP'] = value

    @property
    def loop_gain_h_mon(self):
        """Implemented horizontal loop gain."""
        return self['LoopGainH-Mon']

    @property
    def loop_gain_v(self):
        """Loop gain V."""
        return self['LoopGainV-RB']

    @loop_gain_v.setter
    def loop_gain_v(self, value):
        self['LoopGainV-SP'] = value

    @property
    def loop_gain_v_mon(self):
        """Implemented vertical loop gain."""
        return self['LoopGainV-Mon']

    @property
    def loop_max_orb_dist(self):
        """Loop orbit distortion threshold."""
        return self['LoopMaxOrbDistortion-RB']

    @loop_max_orb_dist.setter
    def loop_max_orb_dist(self, value):
        self['LoopMaxOrbDistortion-SP'] = value

    @property
    def loop_max_orb_dist_enbl(self):
        """Loop orbit distortion detection enable status."""
        return self['LoopMaxOrbDistortionEnbl-Sts']

    @loop_max_orb_dist_enbl.setter
    def loop_max_orb_dist_enbl(self, value):
        self['LoopMaxOrbDistortionEnbl-Sel'] = value

    @property
    def loop_packloss_detec_enbl(self):
        """Loop packet loss detection enable status."""
        return self['LoopPacketLossDetecEnbl-Sts']

    @loop_packloss_detec_enbl.setter
    def loop_packloss_detec_enbl(self, value):
        self['LoopPacketLossDetecEnbl-Sel'] = value

    @property
    def corr_status(self):
        """Corrector status."""
        return self['CorrStatus-Mon']

    def cmd_corr_config(self):
        """Command to configure correctors in use."""
        self['CorrConfig-Cmd'] = 1
        return True

    def cmd_corr_set_pwrstate_on(self):
        """Command to set all corrector pwrstate to on."""
        self['CorrSetPwrStateOn-Cmd'] = 1
        return True

    def cmd_corr_set_pwrstate_off(self):
        """Command to set all corrector pwrstate to off."""
        self['CorrSetPwrStateOff-Cmd'] = 1
        return True

    def cmd_corr_set_opmode_manual(self):
        """Command to set all corrector opmode to manual."""
        self['CorrSetOpModeManual-Cmd'] = 1
        return True

    def cmd_corr_set_accfreeze_dsbl(self):
        """Command to set all corrector FOFBAccFreeze to Dsbl."""
        self['CorrSetAccFreezeDsbl-Cmd'] = 1
        return True

    def cmd_corr_set_accfreeze_enbl(self):
        """Command to set all corrector FOFBAccFreeze to Enbl."""
        self['CorrSetAccFreezeEnbl-Cmd'] = 1
        return True

    def cmd_corr_accclear(self):
        """Command to clear all corrector accumulator."""
        self['CorrSetAccClear-Cmd'] = 1
        return True

    def cmd_corr_set_current_zero(self):
        """Command to set correctors current to zero."""
        self['CorrSetCurrZero-Cmd'] = 1
        duration = self['CorrSetCurrZeroDuration-RB'] or self._default_timeout
        _time.sleep(duration)
        return True

    @property
    def corr_set_current_zero_duration(self):
        """Duration of command to set correctors current to zero."""
        return self['CorrSetCurrZeroDuration-RB']

    @corr_set_current_zero_duration.setter
    def corr_set_current_zero_duration(self, value):
        self['CorrSetCurrZeroDuration-SP'] = value

    @property
    def ch_accsatmax(self):
        """CH accumulator maximum saturation limit."""
        return self['CHAccSatMax-RB']

    @ch_accsatmax.setter
    def ch_accsatmax(self, value):
        self['CHAccSatMax-SP'] = value

    @property
    def cv_accsatmax(self):
        """CH accumulator maximum saturation limit."""
        return self['CVAccSatMax-RB']

    @cv_accsatmax.setter
    def cv_accsatmax(self, value):
        self['CVAccSatMax-SP'] = value

    @property
    def fofbctrl_status(self):
        """FOFB controller status."""
        return self['CtrlrStatus-Mon']

    def cmd_fofbctrl_conf_bpmid(self):
        """Command to configure all FOFB DCC BPMIds."""
        self['CtrlrConfBPMId-Cmd'] = 1
        return True

    def cmd_fofbctrl_syncnet(self):
        """Command to sync FOFB controller net."""
        self['CtrlrSyncNet-Cmd'] = 1
        return True

    def cmd_fofbctrl_syncreforb(self):
        """Command to sync FOFB controller RefOrb."""
        self['CtrlrSyncRefOrb-Cmd'] = 1
        return True

    def cmd_fofbctrl_sync_timeframelen(self):
        """Command to sync all FOFB controller TimeFrameLen."""
        self['CtrlrSyncTFrameLen-Cmd'] = 1
        return True

    def cmd_fofbctrl_conf_bpmlogtrig(self):
        """Command to configure all BPM logical triggers related to FOFB."""
        self['CtrlrConfBPMLogTrg-Cmd'] = 1
        return True

    def cmd_fofbctrl_sync_maxorbdist(self):
        """Command to sync all FOFB controllers orbit distortion detection."""
        self['CtrlrSyncMaxOrbDist-Cmd'] = 1
        return True

    def cmd_fofbctrl_sync_packlossdet(self):
        """Command to sync all FOFB controllers packet loss detection."""
        self['CtrlrSyncPacketLossDetec-Cmd'] = 1
        return True

    def cmd_fofbctrl_reset(self):
        """Command to reset interlocks of all FOFB controllers."""
        self['CtrlrReset-Cmd'] = 1
        return True

    @property
    def kickch_acc(self):
        """Return CH kicks related to FOFBAcc-Mon PVs."""
        return self['KickCHAcc-Mon']

    @property
    def kickcv_acc(self):
        """Return CV kicks related to FOFBAcc-Mon PVs."""
        return self['KickCVAcc-Mon']

    @property
    def kickch_ref(self):
        """Return CH kicks related to CurrentRef-Mon PVs."""
        return self['KickCHRef-Mon']

    @property
    def kickcv_ref(self):
        """Return CV kicks related to CurrentRef-Mon PVs."""
        return self['KickCVRef-Mon']

    @property
    def kickch(self):
        """Return CH kicks related to Current-Mon PVs."""
        return self['KickCH-Mon']

    @property
    def kickcv(self):
        """Return CV kicks related to Current-Mon PVs."""
        return self['KickCV-Mon']

    @property
    def refx(self):
        """RefOrb X."""
        return self['RefOrbX-RB']

    @refx.setter
    def refx(self, value):
        self['RefOrbX-SP'] = value

    @property
    def refx_hw(self):
        """RefOrb X in hardware units."""
        return self['RefOrbHwX-Mon']

    @property
    def refy(self):
        """RefOrb Y."""
        return self['RefOrbY-RB']

    @refy.setter
    def refy(self, value):
        self['RefOrbY-SP'] = value

    @property
    def refy_hw(self):
        """RefOrb Y in hardware units."""
        return self['RefOrbHwY-Mon']

    @property
    def bpmxenbl(self):
        """BPM X enable list."""
        return _np.array(self['BPMXEnblList-RB'], dtype=bool)

    @bpmxenbl.setter
    def bpmxenbl(self, value):
        self['BPMXEnblList-SP'] = value

    @property
    def bpmyenbl(self):
        """BPM Y enable list."""
        return _np.array(self['BPMYEnblList-RB'], dtype=bool)

    @bpmyenbl.setter
    def bpmyenbl(self, value):
        self['BPMYEnblList-SP'] = value

    @property
    def chenbl(self):
        """CH enable list."""
        return _np.array(self['CHEnblList-RB'], dtype=bool)

    @chenbl.setter
    def chenbl(self, value):
        self['CHEnblList-SP'] = value

    @property
    def cvenbl(self):
        """CV enable list."""
        return _np.array(self['CVEnblList-RB'], dtype=bool)

    @cvenbl.setter
    def cvenbl(self, value):
        self['CVEnblList-SP'] = value

    @property
    def rfenbl(self):
        """Use RF in RespMat calculation."""
        return bool(self['UseRF-Sts'])

    @rfenbl.setter
    def rfenbl(self, value):
        self['UseRF-Sel'] = value

    @property
    def singval_min(self):
        """Minimum singular value."""
        return self['MinSingValue-RB']

    @singval_min.setter
    def singval_min(self, value):
        self['MinSingValue-SP'] = value

    @property
    def tikhonov_reg_const(self):
        """Tikhonov regularization constant."""
        return self['TikhonovRegConst-RB']

    @tikhonov_reg_const.setter
    def tikhonov_reg_const(self, value):
        self['TikhonovRegConst-SP'] = value

    @property
    def singvalsraw_mon(self):
        """Raw singular values of physical unit respmat."""
        return self['SingValuesRaw-Mon']

    @property
    def singvals_mon(self):
        """Singular values of physical unit respmat in use."""
        return self['SingValues-Mon']

    @property
    def nr_singvals(self):
        """Number of singular values."""
        return self['NrSingValues-Mon']

    @property
    def respmat(self):
        """RespMat in physical units."""
        return self['RespMat-RB'].reshape(self._data.nr_bpms*2, -1)

    @respmat.setter
    def respmat(self, mat):
        self['RespMat-SP'] = _np.array(mat).ravel()

    @property
    def respmat_mon(self):
        """RespMat in physical units in use."""
        return self['RespMat-Mon'].reshape(self._data.nr_bpms*2, -1)

    @property
    def invrespmat_mon(self):
        """InvRespMat in physical units in use."""
        return self['InvRespMat-Mon'].reshape(-1, self._data.nr_bpms*2)

    @property
    def singvalshw_mon(self):
        """Singular values of hardware unit respmat."""
        return self['SingValuesHw-Mon']

    @property
    def respmathw_mon(self):
        """RespMat in hardware units in use."""
        return self['RespMatHw-Mon'].reshape(self._data.nr_bpms*2, -1)

    @property
    def invrespmathw_mon(self):
        """InvRespMat in physical units in use."""
        return self['InvRespMatHw-Mon'].reshape(-1, self._data.nr_bpms*2)

    @property
    def invrespmat_normmode(self):
        """InvRespMat normalization mode."""
        return self['InvRespMatNormMode-Sts']

    @invrespmat_normmode.setter
    def invrespmat_normmode(self, value):
        self['InvRespMatNormMode-Sel'] = value

    @property
    def corrcoeffs(self):
        """InvRespMatRow setpoint for all correctors."""
        return self['CorrCoeffs-Mon'].reshape(-1, self._data.nr_bpms*2)

    @property
    def corrgains(self):
        """FOFBAccGain setpoint for all correctors."""
        return self['CorrGains-Mon']

    def cmd_measrespmat_start(self):
        """Command to start response matrix measure."""
        self['MeasRespMat-Cmd'] = self._data.MeasRespMatCmd.Start
        return True

    def cmd_measrespmat_stop(self):
        """Command to stop response matrix measure."""
        self['MeasRespMat-Cmd'] = self._data.MeasRespMatCmd.Stop
        return True

    def cmd_measrespmat_reset(self):
        """Command to reset response matrix measure."""
        self['MeasRespMat-Cmd'] = self._data.MeasRespMatCmd.Reset
        return True

    @property
    def measrespmat_mon(self):
        """RespMat measure status."""
        return self['MeasRespMat-Mon']

    @property
    def measrespmat_kickch(self):
        """RespMat measure CH kick."""
        return self['MeasRespMatKickCH-RB']

    @measrespmat_kickch.setter
    def measrespmat_kickch(self, value):
        self['MeasRespMatKickCH-SP'] = value

    @property
    def measrespmat_kickcv(self):
        """RespMat measure CV kick."""
        return self['MeasRespMatKickCV-RB']

    @measrespmat_kickcv.setter
    def measrespmat_kickcv(self, value):
        self['MeasRespMatKickCV-SP'] = value

    @property
    def measrespmat_kickrf(self):
        """RespMat measure RF kick."""
        return self['MeasRespMatKickRF-RB']

    @measrespmat_kickrf.setter
    def measrespmat_kickrf(self, value):
        self['MeasRespMatKickRF-SP'] = value

    @property
    def measrespmat_wait(self):
        """RespMat measure wait interval."""
        return self['MeasRespMatWait-RB']

    @measrespmat_wait.setter
    def measrespmat_wait(self, value):
        self['MeasRespMatWait-SP'] = value

    def wait_respm_meas(self, timeout=None):
        """Wait for response matrix measure."""
        timeout = timeout or self._default_timeout_respm
        return self._wait(
            'MeasRespMat-Mon', self._data.MeasRespMatMon.Measuring,
            timeout=timeout, comp='ne')
