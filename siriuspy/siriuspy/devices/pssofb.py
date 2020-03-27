"""."""
import numpy as _np

from ..search import PSSearch as _PSSearch
from ..namesys import SiriusPVName as _SiriusPVName
from ..pwrsupply.csdev import get_ps_sofbcurrent_propty_database as \
    _get_sofb_db

from . import Device as _Device
from . import Devices as _Devices
from . psconv import StrengthConv as _StrengthConv


class _PSCorrSOFBSim(_Device):
    """Simulated SOFB Device."""

    # NOTE: This class is transparent when SIMULATED = False

    SIMULATED = True

    def __init__(self, devname, properties):
        """."""
        # call base class constructor
        super().__init__(devname, properties=properties)

    @property
    def devname_first_udc(self):
        """."""
        raise NotImplementedError

    def _get_fake_pvs_database(self):
        dbase = _get_sofb_db()
        prefix = self.devname_first_udc + ':'
        return dbase, prefix

    def __setitem__(self, propty, value):
        """Set value of property."""
        if '-SP' not in propty:
            return
        if self.SIMULATED:
            # NOTE: this takes most of the execution time
            pvobj = self._pvs[propty]
            pvobj.value = value
            pvobj = self._pvs[propty.replace('-SP', '-RB')]
            pvobj.value = value
            pvobj = self._pvs[propty.replace('-SP', 'Ref-Mon')]
            pvobj.value = value
            pvobj = self._pvs[propty.replace('-SP', '-Mon')]
            pvobj.value = value
        else:
            super().__setitem__(propty, value)


class PSCorrSOFB(_PSCorrSOFBSim):
    """SOFB corrector device.

    Group SOFB setpoints of all corrector power supplies in a BeagleBone.
    """

    _curr_sp = 'SOFBCurrent-SP'
    _curr_rb = 'SOFBCurrent-RB'
    _curr_refmon = 'SOFBCurrentRef-Mon'
    _curr_mon = 'SOFBCurrent-Mon'

    _properties = (
        _curr_sp,
        _curr_rb,
        _curr_refmon,
        _curr_mon)

    def __init__(self, devname, psnames_ch=None, psnames_cv=None):
        """."""
        self._devname_orig = _SiriusPVName(devname)

        # check if device exists
        filt = {'sec': '(TB|BO|TS|SI)', 'dis': 'PS', 'dev': '(CH|CV)'}
        if devname not in _PSSearch.get_psnames(filt):
            raise NotImplementedError(devname)

        # get bbname and linked devices
        self._bbbname = _PSSearch.conv_psname_2_bbbname(devname)
        self._bsmpdevs = _PSSearch.conv_bbbname_2_bsmps(self._bbbname)

        # call base class constructor
        devname = self._bsmpdevs[0][0]
        super().__init__(devname, properties=PSCorrSOFB._properties)

        # get psnames and apply indices
        if psnames_ch is None or psnames_cv is None:
            self._psnames_ch, self._psnames_cv = \
                self._init_corr_names()
        else:
            self._psnames_ch, self._psnames_cv = psnames_ch, psnames_cv

        # get sofb indices
        self._sofb_indices, self._idx_corr = self._get_sofb_indices()

    @property
    def devname(self):
        """Device name."""
        return self._devname_orig

    @property
    def devname_first_udc(self):
        """Device name of first UDC power supply."""
        return self._bsmpdevs[0][0]

    @property
    def bbbname(self):
        """BBB name."""
        return self._bbbname

    @property
    def bsmpdevs(self):
        """BSMP devices."""
        return self._bsmpdevs

    @property
    def psnames_ch(self):
        """."""
        return self._psnames_ch

    @property
    def psnames_cv(self):
        """."""
        return self._psnames_cv

    @property
    def sofb_indices(self):
        """Return indices of devices in SOFB current vector."""
        return self._sofb_indices

    @property
    def current(self):
        """Return current readback in SOFB order."""
        # get readback
        values = self[self._curr_rb]

        # trim values
        values = _np.array(values)
        values = values[self._idx_corr]
        return values

    @current.setter
    def current(self, value):
        """Set current setpoints in SOFB order."""
        # trim set value
        value = _np.array(value)
        idx_val = _np.where((value == value) & _np.not_equal(value, None))[0]

        # combine refmon and  setpoint values
        values = self[self._curr_sp]
        idx_pv = self._idx_corr[idx_val]
        values[idx_pv] = value[idx_val]

        # set new values
        self[self._curr_sp] = values

    @property
    def current_sp(self):
        """Return current setpoint in SOFB order."""
        # get setpoints
        values = self[self._curr_sp]

        # trim values
        values = _np.array(values)
        values = values[self._idx_corr]
        return values

    @property
    def current_ref_mon(self):
        """Return current refmon in SOFB order."""
        # get refmon
        values = self[self._curr_refmon]

        # trim values
        values = _np.array(values)
        values = values[self._idx_corr]
        return values

    @property
    def current_mon(self):
        """Return current monitor in SOFB order."""
        # get rmon
        values = self[self._curr_mon]

        # trim values
        values = _np.array(values)
        values = values[self._idx_corr]
        return values

    # --- private methods ---

    def _init_corr_names(self):
        # get accelerator sector, power supply names
        sec = self._devname.sec
        corrh = {'sec': sec, 'dis': 'PS', 'dev': 'CH'}
        corrv = {'sec': sec, 'dis': 'PS', 'dev': 'CV'}
        # update class consts CH_NAMES and CV_NAMES
        psnames_ch = tuple(_PSSearch.get_psnames(corrh))
        psnames_cv = tuple(_PSSearch.get_psnames(corrv))
        return psnames_ch, psnames_cv

    def _get_sofb_indices(self):
        devids = sorted([dev[1] for dev in self._bsmpdevs])
        psnames = self._psnames_ch + self._psnames_cv
        indices = list()
        idx_corr = list()
        for devname, dev_id in self._bsmpdevs:
            if devname in psnames:
                idx_id = devids.index(dev_id)
                idx_ps = psnames.index(devname)
                idx_corr.append(idx_id)
                indices.append(idx_ps)
        indices = _np.array(indices)
        idx_corr = _np.array(idx_corr)
        return indices, idx_corr


class PSApplySOFB(_Devices):
    """SOFB corrector devices.

    Group SOFB setpoints of all corrector power supplies.
    """

    _dipole_propty = 'Ref-Mon'

    class DEVICES:
        """."""

        BO = 'BO'
        SI = 'SI'
        ALL = (BO, SI)

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in PSApplySOFB.DEVICES.ALL:
            raise NotImplementedError(devname)

        # get devices
        devices, self._psnames_ch, self._psnames_cv = \
            PSApplySOFB._get_devices(devname)

        # call base class constructor
        super().__init__(devname, devices=devices)

        # psconv objects
        self._psconvs, self._pstype2psconv = \
            self._get_psconvs()

    @property
    def psnames_ch(self):
        """."""
        return self._psnames_ch

    @property
    def psnames_cv(self):
        """."""
        return self._psnames_cv

    @property
    def nr_correctors(self):
        """Return number of correctors."""
        return len(self._psnames_ch) + len(self._psnames_cv)

    @property
    def current(self):
        """Return CurrentRef-Mon vector in SOFB order."""
        currents = self._get_current('current')
        return currents

    @current.setter
    def current(self, value):
        """Set current setpoints in SOFB order."""
        value = _np.array(value)
        for corr in self.devices:
            inds = corr.sofb_indices
            current = value[inds]
            corr.current = current

    @property
    def current_ref_mon(self):
        """Return CurrentRef-Mon vector in SOFB order."""
        currents = self._get_current('current_ref_mon')
        return currents

    @property
    def current_mon(self):
        """Return CurrentRef-Mon vector in SOFB order."""
        currents = self._get_current('current_mon')
        return currents

    # --- private methods ---

    def _get_psconvs(self):
        pstype2psconv = dict()
        psconvs = []
        for psname in self._psnames_ch + self._psnames_cv:
            pstype = _PSSearch.conv_psname_2_pstype(psname)
            if pstype in pstype2psconv:
                conv = pstype2psconv[pstype]
            else:
                conv = _StrengthConv(
                    psname, PSApplySOFB._dipole_propty)
            psconvs.append(conv)
        return psconvs, pstype2psconv

    def _get_current(self, propty):
        values = _np.zeros(len(self._psnames_ch) + len(self._psnames_cv))
        for corr in self.devices:
            inds = corr.sofb_indices
            vals = getattr(corr, propty)
            values[inds] = vals
        return values

    @staticmethod
    def _get_devices(devname):
        # get ps names
        if devname == PSApplySOFB.DEVICES.SI:
            sec = 'SI'
        elif devname == PSApplySOFB.DEVICES.BO:
            sec = 'BO'
        filt = {'sec': sec, 'dis': 'PS', 'dev': '(CH|CV)'}
        psnames = _PSSearch.get_psnames(filt)
        devices = dict()
        psnames_ch, psnames_cv = None, None
        for psname in psnames:
            sofb_corr = PSCorrSOFB(psname, psnames_ch, psnames_cv)
            psnames_ch, psnames_cv = sofb_corr.psnames_ch, sofb_corr.psnames_cv
            devname = sofb_corr.devname_first_udc
            if devname not in devices:
                devices[devname] = sofb_corr
        return list(devices.values()), psnames_ch, psnames_cv
