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
        self.constants = _Const()
        super().__init__(devname, properties=FOFBCtrlRef._properties)

    @property
    def ref(self):
        """Reference orbit."""
        return self['RefOrb-RB']

    @property
    def refx(self):
        """Reference orbit X."""
        return self.ref[:NR_BPM]

    @refx.setter
    def refx(self, value):
        var = self.ref
        var[:NR_BPM] = _np.array(value, dtype=float)
        self.ref = var

    @property
    def refy(self):
        """Reference orbit Y."""
        return self.ref[NR_BPM:]

    @refy.setter
    def refy(self, value):
        var = self.ref
        var[NR_BPM:] = _np.array(value, dtype=float)
        self.ref = var

    def check_refx(self, value, atol=1e-5, rtol=1e-8):
        """Check if first half of RefOrb is equal to value."""
        return self._check_reforbit('x', value, atol, rtol)

    def check_refy(self, value, atol=1e-5, rtol=1e-8):
        """Check if second half of RefOrb is equal to value."""
        return self._check_reforbit('y', value, atol, rtol)

    def _check_reforbit(self, plane, value, atol, rtol):
        refval = getattr(self, 'ref'+plane.lower())
        if not _np.allclose(refval, value, rtol=rtol, atol=atol):
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

    def __init__(self, devname, dccname):
        """Init."""
        self.dccname = dccname
        super().__init__(
            devname, dccname, properties=_DCCDevice._properties)

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
        self.cc_enable = 1
        if not self._wait('CCEnable-RB', 1, timeout/2):
            return False
        _time.sleep(_DCCDevice._sync_sleep)
        self.cc_enable = 0
        return self._wait('CCEnable-RB', 0, timeout/2)


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
        self._ctl_refs, self._ctl_dccs, self._ctl_ids = dict(), dict(), dict()
        for ctl in _FOFBCtrlBase.DEVICES:
            self._ctl_ids[ctl] = self.FOFBCTRL_BPMID_OFFSET-1+int(ctl[3:5])
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

    def check_reforbx(self, value, rtol=1e-5, atol=1e-8):
        """Check whether RefOrbX is equal to value."""
        return self._check_reforb('x', value, rtol, atol)

    def check_reforby(self, value, rtol=1e-5, atol=1e-8):
        """Check whether RefOrbY is equal to value."""
        return self._check_reforb('y', value, rtol, atol)

    def _check_reforb(self, plane, value, rtol, atol):
        for ctrl in self._ctl_refs.values():
            fun = getattr(ctrl, 'check_ref' + plane.lower())
            if not fun(value, rtol=rtol, atol=atol):
                return False
        return True

    @property
    def bpmids_configured(self):
        """Check whether DCC BPMIds are configured."""
        if not self.connected:
            return False
        isconf = True
        for dcc, dev in self._ctl_dccs.items():
            ctl = _PVName(dcc).device_name
            isconf &= dev.bpm_id == self._ctl_ids[ctl]
        for bpm, dev in self._bpm_dccs.items():
            isconf &= dev.bpm_id == self._bpm_ids[bpm]
        return isconf

    @property
    def net_synced(self):
        """Check whether DCCs are synchronized."""
        if not self.connected:
            return False
        issync = True
        for dev in self._ctl_dccs.values():
            issync &= dev.is_synced
        for dev in self._bpm_dccs.values():
            issync &= dev.is_synced
        return issync

    def cmd_sync_net(self, timeout=DEF_TIMEOUT):
        """Command to synchronize DCCs."""
        devs = list(self._ctl_dccs.values()) + list(self._bpm_dccs.values())
        self._set_devices_propty(devs, 'CCEnable-SP', 1)
        if not self._wait_devices_propty(devs, 'CCEnable-RB', 1, timeout/2):
            return False
        self._set_devices_propty(devs, 'CCEnable-SP', 0)
        if not self._wait_devices_propty(devs, 'CCEnable-RB', 0, timeout/2):
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
        self._set_devices_propty(dccs, 'RcvSrc-Sel', value)
        if not self._wait_devices_propty(dccs, 'RcvSrc-Sts', value, timeout):
            return False
        return True

    @property
    def bpm_trigs_configured(self):
        """Check whether all BPM triggers are configured."""
        if not self.connected:
            return False
        isconf = True
        for dev in self._bpm_trgs.values():
            isconf &= dev.receiver_source == self.DEF_BPMTRIG_RCVSRC
            isconf &= dev.receiver_in_sel == self.DEF_BPMTRIG_RCVIN
        return isconf

    def cmd_config_bpm_trigs(self, timeout=DEF_TIMEOUT):
        """Command to configure BPM triggers."""
        devs = self._bpm_trgs.values()
        rsrc = self.DEF_BPMTRIG_RCVSRC
        rins = self.DEF_BPMTRIG_RCVIN
        self._set_devices_propty(devs, 'RcvSrc-Sel', rsrc)
        if not self._wait_devices_propty(devs, 'RcvSrc-Sts', rsrc, timeout/2):
            return False
        self._set_devices_propty(devs, 'RcvInSel-SP', rins)
        if not self._wait_devices_propty(devs, 'RcvInSel-RB', rins, timeout/2):
            return False
        return True


class FamFastCorrs(_Devices):
    """Family of FOFB fast correctors."""

    DEF_TIMEOUT = 10  # [s]
    OPMODE_SEL = PowerSupplyFC.OPMODE_SEL
    OPMODE_STS = PowerSupplyFC.OPMODE_STS

    def __init__(self, psnames, test=False):
        """Init."""
        if not psnames:
            chn = _PSSearch.get_psnames({'sec': 'SI', 'dev': 'FCH'})
            cvn = _PSSearch.get_psnames({'sec': 'SI', 'dev': 'FCV'})
            psnames = chn + cvn
        self._psnames = psnames
        self._psdevs = [PowerSupplyFC(psn) for psn in self._psnames]
        self._psconv = [StrengthConv(psn, 'Ref-Mon') for psn in self._psnames]
        self._test = test
        super().__init__('SI-Glob:PS-FCHV', self._psdevs)

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
        strength_dipole = 3.0 if self._test else None
        return _np.array(
            [p.conv_strength_2_current(1, strengths_dipole=strength_dipole)
             for p in self._psconv])

    def set_pwrstate(
            self, state, psnames=None, psindices=None):
        """Command to set power supply pwrstate."""
        devs = self._get_devices(psnames, psindices)
        return self._set_devices_propty(devs, 'PwrState-Sel', state)

    def check_pwrstate(
            self, state, psnames=None, psindices=None,
            timeout=DEF_TIMEOUT):
        """Check whether power supplies are in desired pwrstate."""
        devs = self._get_devices(psnames, psindices)
        return self._wait_devices_propty(
            devs, 'PwrState-Sts', state, timeout=timeout)

    def set_opmode(
            self, opmode, psnames=None, psindices=None):
        """Command to set power supply opmode."""
        devs = self._get_devices(psnames, psindices)
        return self._set_devices_propty(devs, 'OpMode-Sel', opmode)

    def check_opmode(
            self, opmode, psnames=None, psindices=None,
            timeout=DEF_TIMEOUT):
        """Check whether power supplies are in desired opmode."""
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
            rtol=1e-5, atol=1e-8):
        """Check power supplies correction coefficients."""
        if not isinstance(values, (list, tuple, _np.ndarray)):
            raise ValueError('Value must be iterable.')
        values = _np.asarray(values)
        devs = self._get_devices(psnames, psindices)
        if not values.shape[0] == len(devs):
            raise ValueError('Values and indices must have the same size.')
        impltd = _np.asarray([d.invrespmat_row for d in devs])
        if _np.allclose(values, impltd, rtol=rtol, atol=atol):
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
            rtol=1e-5, atol=1e-8):
        """Check whether power supplies have desired correction gain."""
        if not isinstance(values, (list, tuple, _np.ndarray)):
            raise ValueError('Value must be iterable.')
        values = _np.asarray(values)
        devs = self._get_devices(psnames, psindices)
        impltd = _np.asarray([d.fofbacc_gain for d in devs])
        if _np.allclose(values, impltd, rtol=rtol, atol=atol):
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
        elif indices and not isinstance(indices, (list, tuple, _np.ndarray)):
            indices = [indices, ]
        if not indices:
            indices = [i for i in range(len(self._psnames))]
        return [self._psdevs[i] for i in indices]
