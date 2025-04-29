"""Insertion Device Feedforward Devices."""

import inspect as _inspect
import time as _time
from copy import deepcopy as _dcopy

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
    CORRCH_1CURRENT_MON = None
    CORRCH_2CURRENT_MON = None
    CORRCV_1CURRENT_MON = None
    CORRCV_2CURRENT_MON = None
    CORRQS_1CURRENT_MON = None
    CORRQS_2CURRENT_MON = None
    CORRLCHCURRENT_MON = None
    CORRLCVCURRENT_MON = None
    CORRQD1_1CURRENT_MON = None
    CORRQF_1CURRENT_MON = None
    CORRQD2_1CURRENT_MON = None
    CORRQD2_2CURRENT_MON = None
    CORRQF_2CURRENT_MON = None
    CORRQD1_2CURRENT_MON = None
    CORRCC1_1CURRENT_MON = None
    CORRCC2_1CURRENT_MON = None
    CORRCC2_2CURRENT_MON = None
    CORRCC1_2CURRENT_MON = None

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

    IDFF_CH_LABELS = tuple()
    IDFF_CV_LABELS = tuple()
    IDFF_QS_LABELS = tuple()
    IDFF_LC_LABELS = tuple()
    IDFF_QN_LABELS = tuple()
    IDFF_CC_LABELS = tuple()

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
    def calc_corr_current_ch_1(self):
        """Return calculated CH_1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRCH_1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_ch_2(self):
        """Return calculated CH_2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRCH_2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_cv_1(self):
        """Return calculated CV_1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRCV_1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_cv_2(self):
        """Return calculated CV_2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRCV_2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qs_1(self):
        """Return calculated QS_1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQS_1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qs_2(self):
        """Return calculated Q_2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQS_2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_lch(self):
        """Return calculated LCH power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRLCHCURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_lcv(self):
        """Return calculated LCV power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRLCVCURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qd1_1(self):
        """Return calculated QD1_1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQD1_1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qf_1(self):
        """Return calculated QF_1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQF_1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qd2_1(self):
        """Return calculated QD2_1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQD2_1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qd2_2(self):
        """Return calculated QD2_2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQD2_2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qf_2(self):
        """Return calculated QF_2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQF_2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_qd1_2(self):
        """Return calculated QD1_2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRQB1_2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_cc1_1(self):
        """Return calculated CC1_1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRCC1_1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_cc2_1(self):
        """Return calculated CC2_1 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRCC2_1CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_cc2_2(self):
        """Return calculated CC2_2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRCC2_2CURRENT_MON
        return self[curr_name] if curr_name else None

    @property
    def calc_corr_current_cc1_2(self):
        """Return calculated CC1_2 power supply current [A]."""
        curr_name = self.PARAM_PVS.CORRCC1_2CURRENT_MON
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

    @staticmethod
    def conv_idffdevname_2_iddevname(idffdevname):
        """."""
        iddevname = _SiriusPVName(idffdevname)
        iddevname = iddevname.substitute(dis='ID', idx='')
        if iddevname.sub in ('08SB', '14SB'):
            iddevname = iddevname.substitute(dev='IVU18')
        elif iddevname.sub in ('06SB', '07SP'):
            iddevname = iddevname.substitute(dev='VPU29')
        elif iddevname.sub in ('10SB', ):
            iddevname = iddevname.substitute(dev='DELTA52')
        else:
            pass
        return iddevname

    @staticmethod
    def _add_devices(devset_base, devset_derived):
        for key, value in _inspect.getmembers(devset_derived):
            if key == 'ALL':
                alldevs = devset_base.ALL + value
                devset_base.ALL = alldevs
            elif not key.startswith('_'):
                setattr(devset_base, key, value)


class IDFFCtrlSoft(IDFFCtrlBase):
    """ID Feedforward Control Soft Device."""

    class DEVICES:
        """Device names."""
        ALL = tuple()
        # should be added in derived classes

    PARAM_PVS = _dcopy(IDFFCtrlBase.PARAM_PVS)
    PARAM_PVS.LOG_MON = 'Log-Mon'
    PARAM_PVS.LOOPFREQ_SP = 'LoopFreq-SP'
    PARAM_PVS.LOOPFREQ_RB = 'LoopFreq-RB'
    PARAM_PVS.POLARIZATION_MON = 'Polarization-Mon'
    PARAM_PVS.CONFIGNAME_SP = 'ConfigName-SP'
    PARAM_PVS.CONFIGNAME_RB = 'ConfigName-RB'
    PARAM_PVS.CORRCONFIG_CMD = 'CorrConfig-Cmd'
    PARAM_PVS.CORRSTATUS_MON = 'CorrStatus-Mon'
    PARAM_PVS.CORRSTATUSLABELS_CTE = 'CorrStatusLabels-Cte'

    PROPERTIES_DEFAULT = \
        tuple(set(
            value for key, value in _inspect.getmembers(PARAM_PVS)
            if not key.startswith('_') and value is not None))


class IDFFCtrlSoftDELTA(IDFFCtrlSoft):
    """ID Feedforward Control Soft Device for DELTA."""

    class DEVICES:
        """Device names."""

        DELTA52_10SB_SOFT = 'SI-10SB:AP-IDFF'
        ALL = (DELTA52_10SB_SOFT, )

    IDFFCtrlBase._add_devices(IDFFCtrlSoft.DEVICES, DEVICES)

    IDFF_CH_LABELS = _IDSearch.IDFF_CH_LABELS
    IDFF_CV_LABELS = _IDSearch.IDFF_CV_LABELS
    IDFF_QS_LABELS = _IDSearch.IDFF_QS_LABELS

    PARAM_PVS = _dcopy(IDFFCtrlSoft.PARAM_PVS)
    PARAM_PVS.CORRCH_1CURRENT_MON = 'CorrCH_1Current-Mon'
    PARAM_PVS.CORRCH_2CURRENT_MON = 'CorrCH_2Current-Mon'
    PARAM_PVS.CORRCV_1CURRENT_MON = 'CorrCV_1Current-Mon'
    PARAM_PVS.CORRCV_2CURRENT_MON = 'CorrCV_2Current-Mon'
    PARAM_PVS.CORRQS_1CURRENT_MON = 'CorrQS_1Current-Mon'
    PARAM_PVS.CORRQS_2CURRENT_MON = 'CorrQS_2Current-Mon'

    PROPERTIES_DEFAULT = \
        tuple(set(
            value for key, value in _inspect.getmembers(PARAM_PVS)
            if not key.startswith('_') and value is not None))

    def __init__(self, devname=None, props2init='all', auto_monitor_mon=True):
        """."""
        # check if device exists
        if devname is None:
            devname = self.DEVICES.DELTA52_10SB_SOFT
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)


class IDFFCtrlSoftIVU(IDFFCtrlSoft):
    """ID Feedforward Control Soft Device for IVU."""

    class DEVICES:
        """Device names."""

        IVU18_08SB_SOFT = 'SI-08SB:AP-IDFF'
        IVU18_14SB_SOFT = 'SI-14SB:AP-IDFF'
        ALL = (IVU18_08SB_SOFT, IVU18_14SB_SOFT)

    IDFFCtrlBase._add_devices(IDFFCtrlSoft.DEVICES, DEVICES)

    # IDFF_LC_LABELS = _IDSearch.IDFF_LC_LABELS
    IDFF_QN_LABELS = _IDSearch.IDFF_QN_LABELS

    PARAM_PVS = _dcopy(IDFFCtrlSoft.PARAM_PVS)
    PARAM_PVS.CORRQD1_1CURRENT_MON = 'CorrQD1_1Current-Mon'
    PARAM_PVS.CORRQF_1CURRENT_MON = 'CorrQF_1Current-Mon'
    PARAM_PVS.CORRQD2_1CURRENT_MON = 'CorrQD2_1Current-Mon'
    PARAM_PVS.CORRQD1_2CURRENT_MON = 'CorrQD1_2Current-Mon'
    PARAM_PVS.CORRQF_2CURRENT_MON = 'CorrQF_2Current-Mon'
    PARAM_PVS.CORRQD2_2CURRENT_MON = 'CorrQD2_2Current-Mon'

    PROPERTIES_DEFAULT = \
        tuple(set(
            value for key, value in _inspect.getmembers(PARAM_PVS)
            if not key.startswith('_') and value is not None))

    def __init__(self, devname=None, props2init='all', auto_monitor_mon=True):
        """."""
        # check if device exists
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)


class IDFFCtrlSoftVPU(IDFFCtrlSoft):
    """ID Feedforward Control Soft Device for VPU."""

    class DEVICES:
        """Device names."""

        VPU29_06SB_SOFT = 'SI-06SB:AP-IDFF'
        VPU29_07SP_SOFT = 'SI-07SP:AP-IDFF'
        ALL = (VPU29_06SB_SOFT, VPU29_07SP_SOFT)

    IDFFCtrlBase._add_devices(IDFFCtrlSoft.DEVICES, DEVICES)

    # IDFF_LC_LABELS = _IDSearch.IDFF_LC_LABELS
    IDFF_CC_LABELS = _IDSearch.IDFF_CC_LABELS

    PARAM_PVS = IDFFCtrlSoft.PARAM_PVS
    PARAM_PVS.CORRCC1_1CURRENT_MON = 'CorrCC1_1Current-Mon'
    PARAM_PVS.CORRCC2_1CURRENT_MON = 'CorrCC2_1Current-Mon'
    PARAM_PVS.CORRCC2_2CURRENT_MON = 'CorrCC2_2Current-Mon'
    PARAM_PVS.CORRCC1_2CURRENT_MON = 'CorrCC1_2Current-Mon'

    PROPERTIES_DEFAULT = \
        tuple(set(
            value for key, value in _inspect.getmembers(PARAM_PVS)
            if not key.startswith('_') and value is not None))

    def __init__(self, devname=None, props2init='all', auto_monitor_mon=True):
        """."""
        # check if device exists
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)


class IDFFCtrlHard(IDFFCtrlBase):
    """ID Feedforward Control Hard Device."""

    class DEVICES:
        """Device names."""
        ALL = tuple()
        # should be added in derived classes

    PARAM_PVS = _dcopy(IDFFCtrlBase.PARAM_PVS)

    PROPERTIES_DEFAULT = \
        tuple(set(
            value for key, value in _inspect.getmembers(PARAM_PVS)
            if not key.startswith('_') and value is not None))


class IDFFCtrlHardIVU(IDFFCtrlHard):
    """ID Feedforward Control IVU Device."""

    class DEVICES:
        """Device names."""

        IVU18_08SB_HARD = 'SI-08SB:BS-IDFF-CHCV'
        IVU18_14SB_HARD = 'SI-14SB:BS-IDFF-CHCV'
        ALL = (IVU18_08SB_HARD, IVU18_14SB_HARD)

    IDFFCtrlBase._add_devices(IDFFCtrlHard.DEVICES, DEVICES)

    IDFF_CH_LABELS = _IDSearch.IDFF_CH_LABELS
    IDFF_CV_LABELS = _IDSearch.IDFF_CV_LABELS


class IDFFCtrlHardVPU(IDFFCtrlHard):
    """ID Feedforward Control VPU Device."""

    class DEVICES:
        """Device names."""

        VPU29_06SB_HARD = 'SI-06SB:BS-IDFF-CC_HARD'
        VPU29_07SP_HARD = 'SI-07SP:BS-IDFF-CC_HARD'
        ALL = (VPU29_06SB_HARD, VPU29_07SP_HARD)

    IDFFCtrlBase._add_devices(IDFFCtrlHard.DEVICES, DEVICES)

    IDFF_CC_LABELS = _IDSearch.IDFF_CC_LABELS


class IDFFCtrl(IDFFCtrlBase):
    """ID Feedforward Control Device."""

    class DEVICES:
        """Device names."""
        IDFFCtrlSoft = IDFFCtrlSoft.DEVICES
        IDFFCtrlHard = IDFFCtrlHard.DEVICES
        ALL = IDFFCtrlSoft.ALL + IDFFCtrlHard.ALL

    def __new__(cls, devname, **kwargs):
        """."""
        idclass = IDFFCtrl.get_idffclass(devname)
        if idclass:
            return idclass(devname, **kwargs)
        else:
            raise NotImplementedError(devname)

    @staticmethod
    def get_idffclass(devname):
        """."""
        if devname in IDFFCtrlSoftDELTA.DEVICES.ALL:
            return IDFFCtrlSoftDELTA
        if devname in IDFFCtrlSoftIVU.DEVICES.ALL:
            return IDFFCtrlSoftIVU
        elif devname in IDFFCtrlHardIVU.DEVICES.ALL:
            return IDFFCtrlHardIVU
        if devname in IDFFCtrlSoftVPU.DEVICES.ALL:
            return IDFFCtrlSoftVPU
        elif devname in IDFFCtrlHardVPU.DEVICES.ALL:
            return IDFFCtrlHardVPU
        return None


class IDFF(_DeviceSet):
    """ID Feedforward System Device."""

    class DEVICES:
        """Device names."""
        ALL = tuple()

    IDFFCtrlBase._add_devices(DEVICES, IDFFCtrl.DEVICES)

    def __init__(self, devname, with_devctrl=True):
        """."""
        self._with_devctrl = with_devctrl

        # check if device exists
        if devname not in IDFF.DEVICES.ALL:
            raise NotImplementedError(devname)
        self._devname = devname
        self._idffclass = IDFFCtrl.get_idffclass(self._devname)
        self._iddevname = IDFFCtrlBase.conv_idffdevname_2_iddevname(devname)

        # self._devname = iddevname  # needed for _create_devices
        self._idffconfig = _IDFFConfig()

        self._pparametername = \
            _IDSearch.conv_idname_2_pparameter_propty(self._iddevname)
        self._kparametername = \
            _IDSearch.conv_idname_2_kparameter_propty(self._iddevname)

        alldevs = self._create_devices()
        (self._devctrl, self._devid, self._devsch, self._devscv,
         self._devsqs, self._devslc, self._devsqn, self._devscc) = alldevs

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
        devices += self._devsqn
        devices += self._devscc
        super().__init__(devices, devname=devname)

    @property
    def idffclass(self):
        """Return IDFFCtrl class."""
        return self._idffclass

    @property
    def iddevname(self):
        """."""
        return self._iddevname

    @property
    def chnames(self):
        """Return CH corrector power supply names."""
        return self._get_corrnames(self.idffclass.IDFF_CH_LABELS)

    @property
    def cvnames(self):
        """Return CV corrector power supply names."""
        return self._get_corrnames(self.idffclass.IDFF_CV_LABELS)

    @property
    def qsnames(self):
        """Return QS corrector power supply names."""
        return self._get_corrnames(self.idffclass.IDFF_QS_LABELS)

    @property
    def lcnames(self):
        """Return LC corrector power supply names."""
        return self._get_corrnames(self.idffclass.IDFF_LC_LABELS)

    @property
    def qnnames(self):
        """Return QN trim corrector power supply names."""
        return self._get_corrnames(self.idffclass.IDFF_QN_LABELS)

    @property
    def ccnames(self):
        """Return CC corrector power supply names."""
        return self._get_corrnames(self.idffclass.IDFF_CC_LABELS)

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
    def qndevs(self):
        """Return QD corrector power supply names."""
        return self._devsqn

    @property
    def ccdevs(self):
        """Return CC corrector power supply names."""
        return self._devscc

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
        return _IDSearch.conv_idname_2_polarizations(self.iddevname)

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

    def read_corr_offset_values(self):
        """Read current corrector values."""
        offsets = dict()
        for label, corrdev in self._lab2corrdevs.items():
            offsets[label] = corrdev.current
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
                self._devsqs + self._devslc + self._devsqn + self._devscc
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
            self.chnames + self.cvnames + self.qsnames +
            self.lcnames + self.ccnames)
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
        devcorrs += self.ccdevs
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

    def _create_devices(self):

        devctrl = None if not self._with_devctrl else IDFFCtrl(
            devname=self._devname)
        pol_mon = _ID.get_idclass(self.iddevname).PARAM_PVS.POL_MON
        params = (
            self._pparametername, self._kparametername, pol_mon)
        props2init = tuple(param for param in params if param is not None)
        devid = _ID(
            devname=self.iddevname, props2init=props2init,
            auto_monitor_mon=False)
        devsch = [_PowerSupplyFBP(devname=dev) for dev in self.chnames]
        devscv = [_PowerSupplyFBP(devname=dev) for dev in self.cvnames]
        devsqs = [_PowerSupplyFBP(devname=dev) for dev in self.qsnames]
        devslc = [_PowerSupplyFBP(devname=dev) for dev in self.lcnames]
        devsqn = [_PowerSupplyFBP(devname=dev) for dev in self.qnnames]
        devscc = [_PowerSupplyFBP(devname=dev) for dev in self.ccnames]
        return devctrl, devid, devsch, devscv, devsqs, devslc, devsqn, devscc

    def _create_labels_2_corrdevs_dict(self):
        ch_labels = self.idffclass.IDFF_CH_LABELS
        cv_labels = self.idffclass.IDFF_CV_LABELS
        qs_labels = self.idffclass.IDFF_QS_LABELS
        lc_labels = self.idffclass.IDFF_LC_LABELS
        qn_labels = self.idffclass.IDFF_QN_LABELS
        cc_labels = self.idffclass.IDFF_CC_LABELS
        devs = dict()
        devs.update({lab: dev for lab, dev in zip(ch_labels, self._devsch)})
        devs.update({lab: dev for lab, dev in zip(cv_labels, self._devscv)})
        devs.update({lab: dev for lab, dev in zip(qs_labels, self._devsqs)})
        devs.update({lab: dev for lab, dev in zip(lc_labels, self._devslc)})
        devs.update({lab: dev for lab, dev in zip(qn_labels, self._devsqn)})
        devs.update({lab: dev for lab, dev in zip(cc_labels, self._devscc)})
        return devs

    def _get_corrnames(self, labels):
        conv = _IDSearch.conv_idname_labels_2_corrnames
        return conv(self.iddevname, labels)
