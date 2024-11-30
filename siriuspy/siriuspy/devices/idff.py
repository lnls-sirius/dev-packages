"""Insertion Device Feedforward Devices."""

import inspect as _inspect
import time as _time

from ..idff.config import IDFFConfig as _IDFFConfig
from ..idff.csdev import IDFFConst as _IDFFConst
from ..namesys import SiriusPVName as _SiriusPVName
from ..search import IDSearch as _IDSearch
from .device import Device as _Device, DeviceSet as _DeviceSet
from .ids import ID as _ID
from .pwrsupply import PowerSupplyFBP as _PowerSupplyFBP


class _ParamPVs:
    """."""

    LOOPSTATE_SEL = 'LoopState-Sel'
    LOOPSTATE_STS = 'LoopState-Sts'
    LOG_MON = None
    LOOPFREQ_SP = None
    LOOPFREQ_RB = None
    POLARIZATION_MON = None
    CONFIGNAME_SP = None
    CONFIGNAME_RB = None
    CORRCONFIG_CMD = None
    CORRSTATUS_MON = None
    CORRSTATUSLABELS_CTE = None
    CORRCH1CURRENT_MON = None
    CORRCH2CURRENT_MON = None
    CORRCV1CURRENT_MON = None
    CORRCV2CURRENT_MON = None
    CORRQS1CURRENT_MON = None
    CORRQS2CURRENT_MON = None
    CORRLCHCURRENT_MON = None
    CORRQA1CURRENT_MON = None
    CORRQB1CURRENT_MON = None
    CORRQC1CURRENT_MON = None
    CORRQC2CURRENT_MON = None
    CORRQB2CURRENT_MON = None
    CORRQA2CURRENT_MON = None

    def __str__(self):
        """Print parameters."""
        str_ = ''
        strf = '{}: {}'
        for key, value in _inspect.getmembers(self):
            if not key.startswith('_') and value is not None:
                lstr = strf.format(key, value)
                str_ += lstr if str_ == '' else '\n' + lstr
        return str_


class IDFFCtrlBase(_Device):
    """ID Feedforward Control Device Base."""

    _DEF_TIMEOUT = 2  # [s]

    PARAM_PVS = _ParamPVs()

    PROPERTIES_DEFAULT = \
        tuple(set(
            value for key, value in _inspect.getmembers(PARAM_PVS)
            if not key.startswith('_') and value is not None))

    def __init__(self, devname, props2init='all', auto_monitor_mon=True):
        """."""
        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)

    @property
    def loopstate(self):
        """Return loop state."""
        return self[self.PARAM_PVS.LOOPSTATE_STS]

    @property
    def correctors_status(self):
        """Return correctors status."""
        curr_sts = self.PARAM_PVS.CORRSTATUS_MON
        return self[curr_sts] if curr_sts else None

    @property
    def calc_corr_current_ch1(self):
        """Return calculated CH1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRCH1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_ch2(self):
        """Return calculated CH2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRCH2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_cv1(self):
        """Return calculated CV1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRCV1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_cv2(self):
        """Return calculated CV2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRCV2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qs1(self):
        """Return calculated QS1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQS1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qs2(self):
        """Return calculated Q2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQS2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_lch(self):
        """Return calculated LCH power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRLCHCURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qa1(self):
        """Return calculated QA1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQA1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qb1(self):
        """Return calculated QB1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQB1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qc1(self):
        """Return calculated QC1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQC1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qc2(self):
        """Return calculated QC2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQC2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qb2(self):
        """Return calculated QB2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQB2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qa2(self):
        """Return calculated QA2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQA2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def loopfreq(self):
        """Return FF loop frequency [Hz]."""
        loopfreq_rb_name = self.PARAM_PVS.LOOPFREQ_RB
        return self[loopfreq_rb_name] if loopfreq_rb_name else None

    @loopfreq.setter
    def loopfreq(self, value):
        """Set FF loop frequency [Hz]."""
        loopfreq_sp_name = self.PARAM_PVS.LOOPFREQ_SP
        if loopfreq_sp_name is not None:
            self[loopfreq_sp_name] = value

    def cmd_turn_on_feedforward(self, timeout=None):
        """."""
        timeout = timeout or self._DEF_TIMEOUT
        if self.loopstate == _IDFFConst.LoopState.Closed:
            return True
        self['LoopState-Sel'] = _IDFFConst.LoopState.Closed
        return self._wait(
            'LoopState-Sts', _IDFFConst.LoopState.Closed, timeout=timeout)

    def cmd_turn_off_feedforward(self, timeout=None):
        """."""
        timeout = timeout or self._DEF_TIMEOUT
        if self.loopstate == _IDFFConst.LoopState.Open:
            return True
        self['LoopState-Sel'] = _IDFFConst.LoopState.Open
        return self._wait(
            'LoopState-Sts', _IDFFConst.LoopState.Open, timeout=timeout)


class IDFFCtrlSoft(IDFFCtrlBase):
    """ID Feedforward Control Soft Device."""

    class DEVICES:
        """Device names."""

        DELTA52_10SB = 'SI-10SB:ID-DELTA52'
        ALL = (DELTA52_10SB, )

    PARAM_PVS = _ParamPVs()
    LOG_MON = 'Log-Mon'
    LOOPFREQ_SP = 'LoopFreq-SP'
    LOOPFREQ_RB = 'LoopFreq-RB'
    POLARIZATION_MON = 'Polarization-Mon'
    CONFIGNAME_SP = 'ConfigName-SP'
    CONFIGNAME_RB = 'ConfigName-RB'
    CORRCONFIG_CMD = 'CorrConfig-Cmd'
    CORRSTATUS_MON = 'CorrStatus-Mon'
    CORRSTATUSLABELS_CTE = 'CorrStatusLabels-Cte'
    CORRCH1CURRENT_MON = 'CorrCH1Current-Mon'
    CORRCH2CURRENT_MON = 'CorrCH2Current-Mon'
    CORRCV1CURRENT_MON = 'CorrCV1Current-Mon'
    CORRCV2CURRENT_MON = 'CorrCV2Current-Mon'
    CORRQS1CURRENT_MON = 'CorrQS1Current-Mon'
    CORRQS2CURRENT_MON = 'CorrQS2Current-Mon'

    PROPERTIES_DEFAULT = \
        tuple(set(
            value for key, value in _inspect.getmembers(PARAM_PVS)
            if not key.startswith('_') and value is not None))

    def __init__(self, devname=None, props2init='all', auto_monitor_mon=True):
        """."""
        # check if device exists
        if devname is None:
            devname = self.DEVICES.DELTA52_10SB
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)


class IDFFCtrlHard(IDFFCtrlBase):
    """ID Feedforward Control Hard Device."""

    class DEVICES:
        """Device names."""

        IVU18_08SB = 'SI-08SB:BS-IDFF-CHCV'
        IVU18_14SB = 'SI-14SB:BS-IDFF-CHCV'
        ALL = (IVU18_08SB, IVU18_14SB)

    @staticmethod
    def conv_iddevname_2_idffctrldevnames(iddevname):
        """."""
        if iddevname == _ID.DEVICES.IVU.IVU18_08SB:
            return IDFFCtrlHard.DEVICES.IVU18_08SB
        elif iddevname == _ID.DEVICES.IVU.IVU18_14SB:
            return IDFFCtrlHard.DEVICES.IVU18_14SB
        else:
            raise ValueError('Invalid iddevname!')


class IDFFCtrl(IDFFCtrlBase):
    """ID Feedforward Control Device."""

    class DEVICES:
        """Device names."""
        IDFFCtrlSoft = IDFFCtrlSoft.DEVICES
        IDFFCtrlHard = IDFFCtrlHard.DEVICES
        ALL = IDFFCtrlSoft.ALL + IDFFCtrlHard.ALL

    def __new__(cls, devname, **kwargs):
        """."""
        idclass, devname = IDFFCtrl.get_idclass(devname)
        if idclass:
            return idclass(devname, **kwargs)
        else:
            raise NotImplementedError(devname)

    @staticmethod
    def get_idclass(devname):
        """."""
        if devname in IDFFCtrlSoft.DEVICES.ALL:
            return IDFFCtrlSoft, devname
        elif devname in IDFFCtrlHard.DEVICES.ALL:
            return IDFFCtrlHard, devname
        else:
            try:
                devname = \
                    IDFFCtrlHard.conv_iddevname_2_idffctrldevnames(devname)
                return IDFFCtrlHard, devname
            except ValueError:
                pass
            return None


class IDFF(_DeviceSet):
    """ID Feedforward System Device."""

    class DEVICES(_ID.DEVICES):
        """."""

    def __init__(self, devname, with_devctrl=True):
        """."""
        devname = _SiriusPVName(devname)
        self._with_devctrl = with_devctrl

        # check if device exists
        if devname not in IDFF.DEVICES.ALL:
            raise NotImplementedError(devname)

        self._devname = devname  # needed for _create_devices
        self._idffconfig = _IDFFConfig()

        self._pparametername = \
            _IDSearch.conv_idname_2_pparameter_propty(devname)
        self._kparametername = \
            _IDSearch.conv_idname_2_kparameter_propty(devname)

        alldevs = self._create_devices(devname)
        (self._devctrl, self._devid, self._devsch, self._devscv,
         self._devsqs, self._devslc, self._devsqd) = alldevs

        self._lab2corrdevs = self._create_labels_2_corrdevs_dict()

        devices = list()
        if self._with_devctrl:
            devices += [self._devctrl, self._devid]
        else:
            devices += [self._devid, ]
        devices += self._devsch
        devices += self._devscv
        devices += self._devsqs
        devices += self._devslc
        devices += self._devsqd
        super().__init__(devices, devname=devname)

    @property
    def chnames(self):
        """Return CH corrector power supply names."""
        return _IDSearch.conv_idname_2_idff_chnames(self.devname)

    @property
    def cvnames(self):
        """Return CV corrector power supply names."""
        return _IDSearch.conv_idname_2_idff_cvnames(self.devname)

    @property
    def qsnames(self):
        """Return QS corrector power supply names."""
        return _IDSearch.conv_idname_2_idff_qsnames(self.devname)

    @property
    def lcnames(self):
        """Return LC corrector power supply names."""
        return _IDSearch.conv_idname_2_idff_lcnames(self.devname)

    @property
    def qdnames(self):
        """Return QD corrector power supply names."""
        return _IDSearch.conv_idname_2_idff_qdnames(self.devname)

    @property
    def ctrldev(self):
        """Return IDFFCtrl device."""
        return self._devctrl

    @property
    def iddev(self):
        """Return ID device."""
        return self._devid

    @property
    def chdevs(self):
        """Return CH corrector power supply devices."""
        return self._devsch

    @property
    def cvdevs(self):
        """Return CV corrector power supply devices."""
        return self._devscv

    @property
    def qsdevs(self):
        """Return QS corrector power supply names."""
        return self._devsqs

    @property
    def lcdevs(self):
        """Return LC corrector power supply names."""
        return self._devslc

    @property
    def qddevs(self):
        """Return QD corrector power supply names."""
        return self._devsqd

    @property
    def pparametername(self):
        """Return corresponding to ID pparameter."""
        return self._pparametername

    @property
    def kparametername(self):
        """Return corresponding to ID kparameter."""
        return self._kparametername

    @property
    def polarizations(self):
        """Return list of possible light polarizations for the ID."""
        return _IDSearch.conv_idname_2_polarizations(self.devname)

    @property
    def polarization_mon(self):
        """Return current ID polarization as a string (or None)."""
        return self.iddev.polarization_mon_str

    @property
    def pparameter_mon(self):
        """Return pparameter value."""
        if self._pparametername:
            return self._devid[self._pparametername]
        else:
            return None

    @property
    def kparameter_mon(self):
        """Return kparameter value."""
        return self._devid[self._kparametername]

    @property
    def idffconfig(self):
        """."""
        return self._idffconfig

    def get_correctors_offsets_values(self):
        """Read current corrector values."""
        corrlabels = _IDSearch.conv_idname_2_idff_offsets(self._devid.devname)
        offsets = dict()
        for corrlabel in corrlabels:
            corrdev = self._lab2corrdevs[corrlabel]
            offsets[corrlabel] = corrdev.current
        return offsets

    def find_configs(self):
        """Find si_idff configurations in configdb."""
        return self._idffconfig.configdbclient.find_configs()

    def load_config(self, name):
        """Load IDFF configuration."""
        self._idffconfig.name = name
        if self._idffconfig.name == name:
            self._idffconfig.load()
        else:
            raise ValueError('Could not load configuration.')

    def calculate_setpoints(
            self, pparameter_value=None, kparameter_value=None):
        """Return correctors setpoints for a particular ID config.

        polarization - a string defining the required polarization for
        setpoint calculation.
        """
        if not self._idffconfig:
            ValueError('IDFFConfig is not loaded!')

        polarization, pparameter_value, kparameter_value = \
            self.get_polarization_state(
                pparameter_value=pparameter_value,
                kparameter_value=kparameter_value)

        if polarization not in self.idffconfig.polarizations:
            raise ValueError('Polarization is not compatible with ID.')
        if pparameter_value is None:
            pparameter_value = self.pparameter_mon
        if kparameter_value is None:
            kparameter_value = self.kparameter_mon
        setpoints = self.idffconfig.calculate_setpoints(
            polarization, pparameter_value, kparameter_value)
        return setpoints, polarization, pparameter_value, kparameter_value

    def implement_setpoints(
            self, setpoints=None, corrdevs=None):
        """Implement setpoints in correctors."""
        if setpoints is None:
            setpoints, polarization, pparameter_value, kparameter_value = \
                self.calculate_setpoints(
                    pparameter_value=None,
                    kparameter_value=None)
        else:
            polarization, pparameter_value, kparameter_value = [None, ] * 3
        if corrdevs is None:
            corrdevs = \
                self._devsch + self._devscv + \
                self._devsqs + self._devslc + self._devsqd
        for pvname, value in setpoints.items():
            # find corrdev corresponding to pvname
            for dev in corrdevs:
                if dev.devname in pvname:
                    pvname = _SiriusPVName(pvname)
                    dev[pvname.propty] = value
                    break
        return polarization, pparameter_value, kparameter_value

    def check_valid_value(self, value):
        """Check consistency of SI_IDFF configuration."""
        if not super().check_valid_value(value):
            raise ValueError('Value incompatible with config template')

        configs = value['polarizations']
        pvnames = {
            key: value for key, value in value['pvnames']
            if key not in ('pparameters', 'kparameters')}
        corrlabels = set(pvnames.keys())

        # check pvnames in configs
        pvsconfig = set(pvnames.values())
        pvsidsearch = set(
            self.chnames + self.cvnames + self.qsnames + self.lcnames)
        symm_diff = pvsconfig ^ pvsidsearch
        if symm_diff:
            raise ValueError('List of pvnames in config is not consistent')

        # check polarizations in configs
        pconfig = set(configs.keys())
        pidsearch = set(_IDSearch.conv_idname_2_polarizations(self.devname))
        symm_diff = pconfig ^ pidsearch
        if symm_diff:
            raise ValueError(
                'List of polarizations in config is not consistent')

        # check polarization tables consistency
        for polarization, table in configs.items():
            corrtable = {
                key: value for key, value in table
                if key not in ('pparameters', 'kparameters')}

            # check 'pparameter'
            if 'pparameter' not in table:
                raise ValueError(
                    'Missing pparameter in polarization configuration.')

            # check 'kparameter'
            if 'kparameter' not in table:
                raise ValueError(
                    'Missing kparameter in polarization configuration.')

            # check corr label list
            corrlabels_config = set(corrtable.keys())
            symm_diff = corrlabels ^ corrlabels_config
            if symm_diff:
                raise ValueError(
                    'List of corrlabels in config is not consistent')

            # check nrpts in tables
            param = 'pparameter' if polarization == 'none' else 'kparameter'
            nrpts_corrtables = {len(table) for table in corrtable.values()}
            nrpts_kparameter = set([len(table[param]), ])
            symm_diff = nrpts_corrtables ^ nrpts_kparameter
            if symm_diff:
                raise ValueError(
                    'Corrector tables and kparameter list in config '
                    'are not consistent')
        return True

    def get_polarization_state(
            self, pparameter_value=None, kparameter_value=None):
        """."""
        if self.pparametername is None:
            if kparameter_value is None:
                kparameter_value = self.kparameter_mon
            return self.polarizations[0], pparameter_value, kparameter_value
        if pparameter_value is None:
            pparameter_value = self.pparameter_mon
        if kparameter_value is None:
            kparameter_value = self.kparameter_mon
        if None in (pparameter_value, kparameter_value):
            return None, pparameter_value, kparameter_value
        polarization = self.polarization_mon
        if polarization is None:
            polarization = self.idffconfig.get_polarization_state(
                pparameter=pparameter_value, kparameter=kparameter_value)
        return polarization, pparameter_value, kparameter_value

    def rampup_corr_currents(
            self, nrpts=50, time_interval=10,
            pparameter_value=None, kparameter_value=None,
            dry_run=False):
        """."""
        setpoints, polarization, pparameter_value, kparameter_value = \
            self.calculate_setpoints(pparameter_value, kparameter_value)
        if dry_run:
            print(f'polarization : {polarization}')
            print(f'pparameter   : {pparameter_value}')
            print(f'kparameter   : {kparameter_value}')
            print()
        devcorrs = []
        devcorrs += self.chdevs
        devcorrs += self.cvdevs
        devcorrs += self.qsdevs
        devcorrs += self.lcdevs
        corrs = dict()
        for devcorr in devcorrs:
            # TODO: check power supply status
            pvname_sp = devcorr.devname + ':Current-SP'
            curr0 = devcorr.current_mon  # after an interlock, RB <> Mon=0
            curr1 = setpoints[pvname_sp]
            corrs[devcorr.devname] = (devcorr, curr0, curr1)

        for idx in range(nrpts):
            delta_ramp = (idx + 1) / nrpts
            if dry_run:
                print(f'point {idx+1}/{nrpts}')
            for psname in corrs:
                devcorr, curr0, curr1 = corrs[psname]
                curr = curr0 + delta_ramp * (curr1 - curr0)
                if dry_run:
                    print(f'{psname:<20s}: {curr:+.6f}')
                else:
                    devcorr.current = curr
            if dry_run:
                print()
            _time.sleep(time_interval / (nrpts - 1))

    def _create_devices(self, devname):
        devctrl = IDFFCtrl(devname=devname) if self._with_devctrl else None
        pol_mon = _ID.get_idclass(devname).PARAM_PVS.POL_MON
        params = (
            self._pparametername, self._kparametername, pol_mon)
        props2init = tuple(param for param in params if param is not None)
        devid = _ID(
            devname=devname, props2init=props2init,
            auto_monitor_mon=False)
        devsch = [_PowerSupplyFBP(devname=dev) for dev in self.chnames]
        devscv = [_PowerSupplyFBP(devname=dev) for dev in self.cvnames]
        devsqs = [_PowerSupplyFBP(devname=dev) for dev in self.qsnames]
        devslc = [_PowerSupplyFBP(devname=dev) for dev in self.lcnames]
        devsqd = [_PowerSupplyFBP(devname=dev) for dev in self.qdnames]
        return devctrl, devid, devsch, devscv, devsqs, devslc, devsqd

    def _create_labels_2_corrdevs_dict(self):
        ch_labels = _IDSearch.IDFF_CH_LABELS
        cv_labels = _IDSearch.IDFF_CV_LABELS
        qs_labels = _IDSearch.IDFF_QS_LABELS
        lc_labels = _IDSearch.IDFF_LC_LABELS
        qd_labels = _IDSearch.IDFF_QD_LABELS
        devs = dict()
        devs.update({lab: self._devsch[lab] for lab in ch_labels})
        devs.update({lab: self._devscv[lab] for lab in cv_labels})
        devs.update({lab: self._devsqs[lab] for lab in qs_labels})
        devs.update({lab: self._devslc[lab] for lab in lc_labels})
        devs.update({lab: self._devsqd[lab] for lab in qd_labels})
        return devs
