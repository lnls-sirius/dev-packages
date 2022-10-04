"""FOFB devices."""

import time as _time
import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from ..namesys import SiriusPVName as _PVName
from ..search import BPMSearch as _BPMSearch, PSSearch as _PSSearch
from ..fofb.csdev import HLFOFBConst as _Const, NR_BPM

from .device import Device as _Device, ProptyDevice as _ProptyDevice, \
    Devices as _Devices
from .bpm import BPMLogicalTrigger
from .timing import Event
from .pwrsupply import PowerSupplyFC
from .psconv import StrengthConv


class _FOFBCtrlBase:
    """FOFB Ctrl base."""

    _devices = {
        f'SI{i:02d}': f'IA-{i:02d}RaBPM:BS-FOFBCtrl' for i in range(1, 21)}
    DEVICES = _get_namedtuple('DEVICES', *zip(*_devices.items()))


class FOFBCtrlRef(_Device, _FOFBCtrlBase):
    """FOFB reference orbit controller device."""

    _properties = (
        'RefOrb-SP', 'RefOrb-RB',
    )

    def __init__(self, devname):
        """Init."""
        # check if device exists
        if devname not in self.DEVICES:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=FOFBCtrlRef._properties)

    @property
    def ref(self):
        """Reference orbit, first half reference for X, second, for Y."""
        ref = self['RefOrb-RB']
        # handle initial state of RefOrb PVs
        if len(ref) < 2*NR_BPM:
            value = _np.zeros(2*NR_BPM)
            value[:len(ref)] = ref
            ref = value
        return ref

    @ref.setter
    def ref(self, value):
        self['RefOrb-SP'] = _np.array(value, dtype=int)

    @property
    def refx(self):
        """Reference orbit X."""
        return self.ref[:NR_BPM]

    @refx.setter
    def refx(self, value):
        var = self.ref
        var[:NR_BPM] = _np.array(value, dtype=int)
        self.ref = var

    @property
    def refy(self):
        """Reference orbit Y."""
        return self.ref[NR_BPM:]

    @refy.setter
    def refy(self, value):
        var = self.ref
        var[NR_BPM:] = _np.array(value, dtype=int)
        self.ref = var

    def check_refx(self, value):
        """Check if first half of RefOrb is equal to value."""
        return self._check_reforbit('x', value)

    def check_refy(self, value):
        """Check if second half of RefOrb is equal to value."""
        return self._check_reforbit('y', value)

    def _check_reforbit(self, plane, value):
        refval = getattr(self, 'ref'+plane.lower())
        if not _np.all(refval == value):
            return False
        return True


class _DCCDevice(_ProptyDevice):
    """FOFB Diamond communication controller device."""

    DEF_TIMEOUT = 1
    DEF_FMC_BPMCNT = NR_BPM
    DEF_P2P_BPMCNT = 8

    _sync_sleep = 1.0  # [s]

    _properties = (
        'BPMId-RB', 'BPMCnt-Mon',
        'CCEnable-SP', 'CCEnable-RB',
        'TimeFrameLen-SP', 'TimeFrameLen-RB',
    )
    _properties_fmc = (
        'LinkPartnerCH0-Mon', 'LinkPartnerCH1-Mon',
        'LinkPartnerCH2-Mon', 'LinkPartnerCH3-Mon',
    )

    def __init__(self, devname, dccname):
        """Init."""
        self.dccname = dccname

        properties = _DCCDevice._properties
        if 'FMC' in self.dccname:
            properties += _DCCDevice._properties_fmc

        super().__init__(devname, dccname, properties=properties)
        prop2automon = [
            'BPMCnt-Mon', 'LinkPartnerCH0-Mon', 'LinkPartnerCH1-Mon',
            'LinkPartnerCH2-Mon', 'LinkPartnerCH3-Mon']
        for prop in prop2automon:
            self.set_auto_monitor(prop, True)

    @property
    def bpm_id(self):
        """BPM Id."""
        return self['BPMId-RB']

    @property
    def bpm_count(self):
        """BPM count."""
        return self['BPMCnt-Mon']

    @property
    def cc_enable(self):
        """Communication enable."""
        return self['CCEnable-RB']

    @cc_enable.setter
    def cc_enable(self, value):
        self['CCEnable-SP'] = value

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

    def cmd_sync(self, timeout=DEF_TIMEOUT):
        """Synchronize DCC."""
        self.cc_enable = 0
        if not self._wait('CCEnable-RB', 0, timeout/2):
            return False
        _time.sleep(_DCCDevice._sync_sleep)
        self.cc_enable = 1
        return self._wait('CCEnable-RB', 1, timeout/2)


class FOFBCtrlDCC(_DCCDevice, _FOFBCtrlBase):
    """FOFBCtrl DCC device."""

    class PROPDEVICES:
        """DCC devices."""

        FMC = 'DCCFMC'
        P2P = 'DCCP2P'
        ALL = (FMC, P2P)

    def __init__(self, devname, dccname):
        """Init."""
        if devname not in self.DEVICES:
            raise NotImplementedError(devname)
        if dccname not in self.PROPDEVICES.ALL:
            raise NotImplementedError(dccname)
        super().__init__(devname, dccname)

    @property
    def linkpartners(self):
        """Return linked partners."""
        linkpart_props = [
            'LinkPartnerCH0-Mon', 'LinkPartnerCH1-Mon',
            'LinkPartnerCH2-Mon', 'LinkPartnerCH3-Mon']
        return set(self[prop] for prop in linkpart_props)


class BPMDCC(_DCCDevice):
    """BPM DCC device."""

    def __init__(self, devname):
        """Init."""
        if not _BPMSearch.is_valid_devname(devname):
            raise NotImplementedError(devname)
        super().__init__(devname, 'DCCP2P')


class FamFOFBControllers(_Devices):
    """Family of FOFBCtrl and related BPM devices."""

    DEF_TIMEOUT = 10  # [s]
    DEF_DCC_TIMEFRAMELEN = 5000
    DEF_BPMTRIG_RCVSRC = 0
    DEF_BPMTRIG_RCVIN = 5
    BPM_TRIGS_IDS = [1, 2, 20]
    FOFBCTRL_BPMID_OFFSET = 480

    def __init__(self):
        """Init."""
        # FOFBCtrl Refs and DCCs
        bpmids = _np.array(
            [self.FOFBCTRL_BPMID_OFFSET - 1 + i for i in range(1, 21)])
        lpcw = _np.roll(bpmids, 1)
        lpaw = _np.roll(bpmids, -1)
        self._ctl_ids, self._ctl_part = dict(), dict()
        self._ctl_refs, self._ctl_dccs = dict(), dict()
        for idx, ctl in enumerate(_FOFBCtrlBase.DEVICES):
            self._ctl_ids[ctl] = bpmids[idx]
            self._ctl_part[ctl] = {lpcw[idx], lpaw[idx]}
            self._ctl_refs[ctl] = FOFBCtrlRef(ctl)
            for dcc in FOFBCtrlDCC.PROPDEVICES.ALL:
                self._ctl_dccs[ctl + ':' + dcc] = FOFBCtrlDCC(ctl, dcc)
        # BPM DCCs and triggers
        bpmnames = _BPMSearch.get_names({'sec': 'SI', 'dev': 'BPM'})
        bpmids = _np.roll(
            _np.array([i-1 if i % 2 == 1 else i for i in range(NR_BPM)]), -1)
        self._bpm_dccs, self._bpm_trgs, self._bpm_ids = dict(), dict(), dict()
        for idx, bpm in enumerate(bpmnames):
            self._bpm_ids[bpm] = bpmids[idx]
            self._bpm_dccs[bpm] = BPMDCC(bpm)
            for trig in self.BPM_TRIGS_IDS:
                trigname = bpm + ':TRIGGER' + str(trig)
                self._bpm_trgs[trigname] = BPMLogicalTrigger(bpm, trig)
        # fofb event
        self._evt_fofb = Event('FOFBS')

        devices = list()
        devices.extend(self._ctl_refs.values())
        devices.extend(self._ctl_dccs.values())
        devices.extend(self._bpm_dccs.values())
        devices.extend(self._bpm_trgs.values())
        devices.append(self._evt_fofb)

        super().__init__('SI-Glob:BS-FOFB', devices)

    def set_reforbx(self, value):
        """Set RefOrbX for all FOFB controllers."""
        return self._set_reforb('x', value)

    def set_reforby(self, value):
        """Set RefOrbY for all FOFB controllers."""
        return self._set_reforb('y', value)

    def _set_reforb(self, plane, value):
        for ctrl in self._ctl_refs.values():
            setattr(ctrl, 'ref' + plane.lower(), value)
        return True

    def check_reforbx(self, value):
        """Check whether RefOrbX is equal to value."""
        return self._check_reforb('x', value)

    def check_reforby(self, value):
        """Check whether RefOrbY is equal to value."""
        return self._check_reforb('y', value)

    def _check_reforb(self, plane, value):
        if not self.connected:
            return False
        for ctrl in self._ctl_refs.values():
            fun = getattr(ctrl, 'check_ref' + plane.lower())
            if not fun(value):
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
            if not dev.linkpartners & self._ctl_part[ctl]:
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

    @property
    def net_synced(self):
        """Check whether DCCs are synchronized."""
        if not self.connected:
            return False
        for dev in self._ctl_dccs.values():
            if not dev.is_synced:
                return False
        return True

    def cmd_sync_net(self, timeout=DEF_TIMEOUT):
        """Command to synchronize DCCs."""
        devs = list(self._ctl_dccs.values()) + list(self._bpm_dccs.values())
        self._set_devices_propty(devs, 'CCEnable-SP', 0)
        if not self._wait_devices_propty(
                devs, 'CCEnable-RB', 0, timeout=timeout/2):
            return False
        self._set_devices_propty(devs, 'CCEnable-SP', 1)
        if not self._wait_devices_propty(
                devs, 'CCEnable-RB', 1, timeout=timeout/2):
            return False
        self._evt_fofb.cmd_external_trigger()
        return True

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


class FamFastCorrs(_Devices):
    """Family of FOFB fast correctors."""

    DEF_TIMEOUT = 10  # [s]
    OPMODE_SEL = PowerSupplyFC.OPMODE_SEL
    OPMODE_STS = PowerSupplyFC.OPMODE_STS
    DEF_ATOL_INVRESPMATROW = 2**-17
    DEF_ATOL_FOFBACCGAIN = 2**-12

    def __init__(self, psnames=None):
        """Init."""
        if not psnames:
            chn = _PSSearch.get_psnames({'sec': 'SI', 'dev': 'FCH'})
            cvn = _PSSearch.get_psnames({'sec': 'SI', 'dev': 'FCV'})
            psnames = chn + cvn
        self._psnames = psnames
        self._psdevs = [PowerSupplyFC(psn) for psn in self._psnames]
        self._psconv = [StrengthConv(psn, 'Ref-Mon', auto_mon=True)
                        for psn in self._psnames]
        super().__init__('SI-Glob:PS-FCHV', self._psdevs + self._psconv)

    @property
    def psnames(self):
        """PS name list."""
        return list(self._psnames)

    @property
    def pwrstate(self):
        """Power State.

        Returns:
            state (numpy.ndarray, NR_BPMS):
                PwrState for each power supply.
        """
        return _np.array([p.pwrstate for p in self._psdevs])

    @property
    def opmode(self):
        """Operation Mode.

        Returns:
            mode (numpy.ndarray, NR_BPM):
                OpMode for each power supply.
        """
        return _np.array([p.opmode for p in self._psdevs])

    @property
    def fofbacc_gain(self):
        """FOFB pre-accumulator gain.

        Returns:
            gain (numpy.ndarray, NR_BPM):
                FOFB pre-accumulator gain for each power supply.
        """
        return _np.array([p.fofbacc_gain for p in self._psdevs])

    @property
    def fofbacc_freeze(self):
        """FOFB pre-accumulator freeze state.

        Returns:
            gain (numpy.ndarray, NR_BPM):
                FOFB pre-accumulator freeze state for each power supply.
        """
        return _np.array([p.fofbacc_freeze for p in self._psdevs])

    @property
    def curr_gain(self):
        """Current gain.

        Returns:
            gain (numpy.ndarray, NR_BPM):
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

    def set_invrespmat_row(self, values, psnames=None, psindices=None):
        """Command to set power supply correction coefficients value."""
        if not isinstance(values, (list, tuple, _np.ndarray)):
            raise ValueError('Value must be iterable.')
        devs = self._get_devices(psnames, psindices)
        if any([len(v) != 2*NR_BPM for v in values]):
            raise ValueError(f'Value must have size {2*NR_BPM}.')
        for i, dev in enumerate(devs):
            dev.invrespmat_row = values[i]
        return True

    def check_invrespmat_row(
            self, values, psnames=None, psindices=None,
            atol=DEF_ATOL_INVRESPMATROW):
        """Check power supplies correction coefficients."""
        if not self.connected:
            return False
        if not isinstance(values, (list, tuple, _np.ndarray)):
            raise ValueError('Value must be iterable.')
        values = _np.asarray(values)
        devs = self._get_devices(psnames, psindices)
        if not values.shape[0] == len(devs):
            raise ValueError('Values and indices must have the same size.')
        impltd = _np.asarray([d.invrespmat_row for d in devs])
        if _np.allclose(values, impltd, atol=atol):
            return True
        return False

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
        return self._wait_devices_propty(
            devs, 'FOFBAccFreeze-Sts', values, timeout=timeout)

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


class HLFOFB(_Device):
    """Control high level FOFB IOC."""

    class DEVICES:
        """Devices names."""

        SI = 'SI-Glob:AP-FOFB'
        ALL = (SI, )

    _properties = (
        'LoopState-Sel', 'LoopState-Sts',
        'LoopGain-SP', 'LoopGain-RB',
        'CorrStatus-Mon', 'CorrConfig-Cmd',
        'CorrSetOpModeManual-Cmd', 'CorrSetAccFreezeDsbl-Cmd',
        'CorrSetAccFreezeEnbl-Cmd', 'CorrSetAccClear-Cmd',
        'FOFBCtrlStatus-Mon', 'FOFBCtrlSyncNet-Cmd', 'FOFBCtrlSyncRefOrb-Cmd',
        'FOFBCtrlConfTFrameLen-Cmd', 'FOFBCtrlConfBPMLogTrg-Cmd',
        'RefOrbX-SP', 'RefOrbX-RB', 'RefOrbY-SP', 'RefOrbY-RB',
        'GetRefOrbFromSlowOrb-Cmd',
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

    _default_timeout_respm = 2 * 60 * 60  # [s]

    def __init__(self, devname=None):
        """Init."""
        # check if device exists
        if devname is None:
            devname = HLFOFB.DEVICES.SI
        if devname not in HLFOFB.DEVICES.ALL:
            raise NotImplementedError(devname)

        self._data = _Const()

        # call base class constructor
        super().__init__(devname, properties=self._properties)

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

    @property
    def loop_gain(self):
        """Loop gain."""
        return self['LoopGain-RB']

    @loop_gain.setter
    def loop_gain(self, value):
        self['LoopGain-SP'] = value

    @property
    def corr_status(self):
        """Corrector status."""
        return self['CorrStatus-Mon']

    def cmd_corr_config(self):
        """Command to configure correctors in use."""
        self['CorrConfig-Cmd'] = 1
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

    @property
    def fofbctrl_status(self):
        """FOFB controller status."""
        return self['FOFBCtrlStatus-Mon']

    def cmd_fofbctrl_syncnet(self):
        """Command to sync FOFB controller net."""
        self['FOFBCtrlSyncNet-Cmd'] = 1
        return True

    def cmd_fofbctrl_syncreforb(self):
        """Command to sync FOFB controller RefOrb."""
        self['FOFBCtrlSyncRefOrb-Cmd'] = 1
        return True

    def cmd_fofbctrl_conf_timeframelen(self):
        """Command to configure all FOFB controller TimeFrameLen."""
        self['FOFBCtrlConfTFrameLen-Cmd'] = 1
        return True

    def cmd_fofbctrl_conf_bpmlogtrig(self):
        """Command to configure all BPM logical triggers related to FOFB."""
        self['FOFBCtrlConfBPMLogTrg-Cmd'] = 1
        return True

    @property
    def refx(self):
        """RefOrb X."""
        return self['RefOrbX-RB']

    @refx.setter
    def refx(self, value):
        self['RefOrbX-SP'] = value

    @property
    def refy(self):
        """RefOrb Y."""
        return self['RefOrbY-RB']

    @refy.setter
    def refy(self, value):
        self['RefOrbY-SP'] = value

    def cmd_reforb_fromsloworb(self):
        """Command to get FOFB controller RefOrb from SlowOrb."""
        self['GetRefOrbFromSlowOrb-Cmd'] = 1
        return True

    @property
    def bpmxenbl(self):
        """BPM X enable list."""
        return self['BPMXEnblList-RB']

    @bpmxenbl.setter
    def bpmxenbl(self, value):
        self['BPMXEnblList-SP'] = value

    @property
    def bpmyenbl(self):
        """BPM Y enable list."""
        return self['BPMYEnblList-RB']

    @bpmyenbl.setter
    def bpmyenbl(self, value):
        self['BPMYEnblList-SP'] = value

    @property
    def chenbl(self):
        """CH enable list."""
        return self['CHEnblList-RB']

    @chenbl.setter
    def chenbl(self, value):
        self['CHEnblList-SP'] = value

    @property
    def cvenbl(self):
        """CV enable list."""
        return self['CVEnblList-RB']

    @cvenbl.setter
    def cvenbl(self, value):
        self['CVEnblList-SP'] = value

    @property
    def rfenbl(self):
        """Use RF in RespMat calculation."""
        return self['UseRF-Sts']

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
