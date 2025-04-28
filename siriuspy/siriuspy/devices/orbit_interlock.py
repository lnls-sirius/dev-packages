"""Orbit Interlock devices."""

import numpy as _np

from ..clientconfigdb import ConfigDBClient
from ..search import BPMSearch as _BPMSearch, OrbIntlkSearch as _OrbIntlkSearch
from ..sofb.utils import si_calculate_bump as _si_calculate_bump
from ..util import ClassProperty as _classproperty
from .device import Device as _Device, DeviceSet as _DeviceSet


class BaseOrbitIntlk:
    """Base BPM Orbit Interlock Info."""

    CONV_NM2UM = 1e-3  # [nm] --> [um]

    UP_2_DOWN = {
        'M1': 'M2',
        'C1-1': 'C1-2',
        'C2': 'C3-1',
        'C3-2': 'C4',
    }
    DOWN_2_UP = {val: key for key, val in UP_2_DOWN.items()}

    __BPM_NAMES = None
    __BPM_NICKNAMES = None
    __BPM_POS = None
    __BPM_DOWNSTREAM = None
    __BPM_UPSTREAM = None

    @_classproperty
    def BPM_NAMES(cls):
        """BPM names."""
        if cls.__BPM_NAMES is not None:
            return cls.__BPM_NAMES

        cls.__BPM_NAMES = _BPMSearch.get_names({'sec': 'SI', 'dev': 'BPM'})
        cls.__BPM_NICKNAMES = _BPMSearch.get_nicknames(cls.__BPM_NAMES)
        cls.__BPM_POS = _BPMSearch.get_positions(cls.__BPM_NAMES)

        def _parse_nick_down_up(name, nick):
            sub, idx, *_ = nick.split('-') + ['']
            return name.substitute(sub=name.sub[:2]+sub, idx=idx)

        downnames, upnames = [], []
        for bpm in cls.__BPM_NAMES:
            nick = bpm.sub[2:]+('-' + bpm.idx if bpm.idx else '')
            if nick in BaseOrbitIntlk.DOWN_2_UP:
                down = bpm
                upnick = BaseOrbitIntlk.DOWN_2_UP[nick]
                upn = _parse_nick_down_up(bpm, upnick)
            elif nick in BaseOrbitIntlk.UP_2_DOWN:
                upn = bpm
                downnick = BaseOrbitIntlk.UP_2_DOWN[nick]
                down = _parse_nick_down_up(bpm, downnick)
            else:
                down, upn = '', ''
            downnames.append(down)
            upnames.append(upn)
        cls.__BPM_DOWNSTREAM = downnames
        cls.__BPM_UPSTREAM = upnames
        return cls.__BPM_NAMES

    @_classproperty
    def BPM_NICKNAMES(cls):
        """BPM nicknames."""
        cls.BPM_NAMES
        return cls.__BPM_NICKNAMES

    @_classproperty
    def BPM_POS(cls):
        """BPM positions."""
        cls.BPM_NAMES
        return cls.__BPM_POS

    @_classproperty
    def BPM_DOWNSTREAM(cls):
        """BPM downstream."""
        cls.BPM_NAMES
        return cls.__BPM_DOWNSTREAM

    @_classproperty
    def BPM_UPSTREAM(cls):
        """BPM upstream."""
        cls.BPM_NAMES
        return cls.__BPM_UPSTREAM

    def __init__(self):
        """Init."""
        self._oper = {
            'mean': self._mean,
            'diff': self._diff,
            'min': min,
        }

    @staticmethod
    def get_down_up_bpms(bpmname):
        """Return down and up BPM names for bpmname."""
        index = BaseOrbitIntlk.BPM_NAMES.index(bpmname)
        down = BaseOrbitIntlk.BPM_DOWNSTREAM[index]
        upn = BaseOrbitIntlk.BPM_UPSTREAM[index]
        return down, upn

    def calc_intlk_metric(self, posarray, operation='', metric=''):
        """Return interlock metric, position or angulation."""
        if not operation:
            if not metric:
                raise ValueError(
                    'either the operation or the metric is required')
            operation = 'mean' if 'pos' in metric.lower() else 'diff'

        data_values = list()
        for bpm in BaseOrbitIntlk.BPM_NAMES:
            down, upn = BaseOrbitIntlk.get_down_up_bpms(bpm)
            dval = posarray[BaseOrbitIntlk.BPM_NAMES.index(down)]
            uval = posarray[BaseOrbitIntlk.BPM_NAMES.index(upn)]
            func = self._oper[operation]
            val = func(dval, uval)
            data_values.append(val)
        return _np.array(data_values)

    @staticmethod
    def _mean(var1, var2):
        return (var1 + var2)/2

    @staticmethod
    def _diff(var1, var2):
        return var1 - var2


class BPMOrbitIntlk(BaseOrbitIntlk, _Device):
    """This device group the orbit interlock PVs from one BPM."""

    PROPERTIES_DEFAULT = (
        # ==============================================================
        # General
        # **************************************************************
        # General interlock enable:
        'IntlkEn-Sel', 'IntlkEn-Sts',
        # General interlock reset:
        'IntlkClr-Cmd',
        # Minimum sum threshold enable:
        # Enable orbit interlock only when sum is higher than IntlkLmtMinSum-RB
        'IntlkMinSumEn-Sel', 'IntlkMinSumEn-Sts',
        # Minimum sum threshold (sum counts in FAcq rate):
        'IntlkLmtMinSum-SP', 'IntlkLmtMinSum-RB',
        # Instantaneous interlock, difficult to be checked in the current
        # gateware implementation
        'Intlk-Mon',
        # Latch interlock, clean only when respective "Clr" PV is triggered
        'IntlkLtc-Mon',
        # ===============================================================
        # Position Interlock
        # ***************************************************************
        # Condition for position interlock:
        #   thres_min > (pos BPM downstream + pos BPM upstream)/2 or
        #   thres_max < (pos BPM downstream + pos BPM upstream)/2
        # BPMs are grouped 2 by 2 following the order seen by the beam:
        # - M1/M2
        # - C1-1/C1-2
        # - C2/C3-1
        # - C3-2/C4
        # upstream BPM is always the "first" BPM of the pairs above and
        # downstream BPM is always the "second" BPM of the pair.
        # ***************************************************************
        # Position interlock enable:
        'IntlkPosEn-Sel', 'IntlkPosEn-Sts',
        # Position interlock clear:
        'IntlkPosClr-Cmd',
        # Thresholds (nm, FAcq rate):
        'IntlkLmtPosMaxX-SP', 'IntlkLmtPosMaxX-RB',
        'IntlkLmtPosMinX-SP', 'IntlkLmtPosMinX-RB',
        'IntlkLmtPosMaxY-SP', 'IntlkLmtPosMaxY-RB',
        'IntlkLmtPosMinY-SP', 'IntlkLmtPosMinY-RB',
        # All interlocks are masked by the "Enable" state
        # Instantaneous Status:
        'IntlkPosLowerX-Mon', 'IntlkPosUpperX-Mon',  # X
        'IntlkPosLowerY-Mon', 'IntlkPosUpperY-Mon',  # Y
        # Latch Status, clean only when respective "Clr" PV is triggered
        'IntlkPosLowerLtcX-Mon', 'IntlkPosUpperLtcX-Mon',
        'IntlkPosLowerLtcY-Mon', 'IntlkPosUpperLtcY-Mon',
        # Position measure from orbit interlock core
        'IntlkPosX-Mon',
        'IntlkPosY-Mon',
        # =============================================================
        # Angle Interlock
        # *************************************************************
        # Condition for angle interlock:
        #   thres_min > (pos BPM downstream - pos BPM upstream) or
        #   thres_max < (pos BPM downstream - pos BPM upstream)
        # BPMs are grouped 2 by 2 following the order seen by the beam:
        # - M1/M2
        # - C1-1/C1-2
        # - C2/C3-1
        # - C3-2/C4
        # upstream BPM is always the "first" BPM of the pairs above and
        # downstream BPM is always the "second" BPM of the pair.
        # ************************************************************
        # Angle interlock enable:
        'IntlkAngEn-Sel', 'IntlkAngEn-Sts',
        # Angle interlock clear:
        'IntlkAngClr-Cmd',
        # Thresholds (rad.nm, FAcq rate).
        # Thresholds must be calculated as angle (rad)
        # between the 2 adjacent BPMs * distance (nm) between them:
        'IntlkLmtAngMaxX-SP', 'IntlkLmtAngMaxX-RB',
        'IntlkLmtAngMinX-SP', 'IntlkLmtAngMinX-RB',
        'IntlkLmtAngMaxY-SP', 'IntlkLmtAngMaxY-RB',
        'IntlkLmtAngMinY-SP', 'IntlkLmtAngMinY-RB',
        # All interlocks are masked by the "Enable" state
        # Intantaneous Status
        'IntlkAngLowerX-Mon', 'IntlkAngUpperX-Mon',  # X
        'IntlkAngLowerY-Mon', 'IntlkAngUpperY-Mon',  # Y
        # Latch Status, clean only when respective "Clr" PV is triggered
        'IntlkAngLowerLtcX-Mon', 'IntlkAngUpperLtcX-Mon',
        'IntlkAngLowerLtcY-Mon', 'IntlkAngUpperLtcY-Mon',
        # Angle measure from orbit interlock core
        'IntlkAngX-Mon',
        'IntlkAngY-Mon',
        # ============================================================
        )

    def __init__(self, devname, props2init='all'):
        """Init."""
        # call base class constructor
        BaseOrbitIntlk.__init__(self)
        if devname not in self.BPM_NAMES:
            raise ValueError(devname + ' is no a valid BPM name.')
        _Device.__init__(self, devname, props2init=props2init)

    @property
    def intlkposx(self):
        """Orbit interlock core Position X."""
        return self['IntlkPosX-Mon'] * self.CONV_NM2UM

    @property
    def intlkposy(self):
        """Orbit interlock core Position Y."""
        return self['IntlkPosY-Mon'] * self.CONV_NM2UM

    @property
    def intlkangx(self):
        """Orbit interlock core Angle X."""
        return self['IntlkAngX-Mon'] * self.CONV_NM2UM

    @property
    def intlkangy(self):
        """Orbit interlock core Angle Y."""
        return self['IntlkAngY-Mon'] * self.CONV_NM2UM

    @property
    def pair_down_up_bpms(self):
        """Return pair of downstream and upstream BPM names."""
        return self.get_down_up_bpms(self.devname)

    # --- general interlock ---

    @property
    def gen_enable(self):
        """General interlock enable."""
        return self['IntlkEn-Sts']

    @gen_enable.setter
    def gen_enable(self, value):
        self['IntlkEn-Sel'] = int(value)

    def cmd_reset_gen(self):
        """General interlock clear."""
        self['IntlkClr-Cmd'] = 1
        return True

    @property
    def gen_inst(self):
        """Instantaneous general interlock."""
        return self['Intlk-Mon']

    @property
    def gen_latch(self):
        """Latch general interlock."""
        return self['IntlkLtc-Mon']

    # --- minimum sum threshold ---

    @property
    def minsum_enable(self):
        """
        Minimum sum threshold enable.

        If enabled, generate orbit interlock only when sum exceeds
        value in 'minsum_thres' property.
        """
        return self['IntlkMinSumEn-Sts']

    @minsum_enable.setter
    def minsum_enable(self, value):
        self['IntlkMinSumEn-Sel'] = int(value)

    @property
    def minsum_thres(self):
        """Minimum sum threshold [sum count, FAcq rate]."""
        return self['IntlkLmtMinSum-RB']

    @minsum_thres.setter
    def minsum_thres(self, value):
        self['IntlkLmtMinSum-SP'] = int(value)

    # --- position interlock ---

    @property
    def pos_enable(self):
        """Position interlock enable."""
        return self['IntlkPosEn-Sts']

    @pos_enable.setter
    def pos_enable(self, value):
        self['IntlkPosEn-Sel'] = int(value)

    def cmd_reset_pos(self):
        """Position interlock clear."""
        self['IntlkPosClr-Cmd'] = 1
        return True

    @property
    def pos_x_min_thres(self):
        """Minimum X position threshold."""
        return self['IntlkLmtPosMinX-RB']

    @pos_x_min_thres.setter
    def pos_x_min_thres(self, value):
        self['IntlkLmtPosMinX-SP'] = value

    @property
    def pos_x_max_thres(self):
        """Maximum X position threshold."""
        return self['IntlkLmtPosMaxX-RB']

    @pos_x_max_thres.setter
    def pos_x_max_thres(self, value):
        self['IntlkLmtPosMaxX-SP'] = value

    @property
    def pos_y_min_thres(self):
        """Minimum Y position threshold."""
        return self['IntlkLmtPosMinY-RB']

    @pos_y_min_thres.setter
    def pos_y_min_thres(self, value):
        self['IntlkLmtPosMinY-SP'] = value

    @property
    def pos_y_max_thres(self):
        """Maximum Y position threshold."""
        return self['IntlkLmtPosMaxY-RB']

    @pos_y_max_thres.setter
    def pos_y_max_thres(self, value):
        self['IntlkLmtPosMaxY-SP'] = value

    @property
    def pos_inst_lower_x(self):
        """
        Instantaneous position interlock set when X
        minimum threshold is exceeded.
        """
        return self['IntlkPosLowerX-Mon']

    @property
    def pos_inst_upper_x(self):
        """
        Instantaneous position interlock set when X
        maximum threshold is exceeded.
        """
        return self['IntlkPosUpperX-Mon']

    @property
    def pos_inst_lower_y(self):
        """
        Instantaneous position interlock set when Y
        minimum threshold is exceeded.
        """
        return self['IntlkPosLowerY-Mon']

    @property
    def pos_inst_upper_y(self):
        """
        Instantaneous position interlock set when Y
        maximum threshold is exceeded.
        """
        return self['IntlkPosUpperY-Mon']

    @property
    def pos_latch_lower_x(self):
        """
        Latch position interlock set when X
        minimum threshold is exceeded.
        """
        return self['IntlkPosLowerLtcX-Mon']

    @property
    def pos_latch_upper_x(self):
        """
        Latch position interlock set when X
        maximum threshold is exceeded.
        """
        return self['IntlkPosUpperLtcX-Mon']

    @property
    def pos_latch_lower_y(self):
        """
        Latch position interlock set when Y
        minimum threshold is exceeded.
        """
        return self['IntlkPosLowerLtcY-Mon']

    @property
    def pos_latch_upper_y(self):
        """
        Latch position interlock set when Y
        maximum threshold is exceeded.
        """
        return self['IntlkPosUpperLtcY-Mon']

    #  --- angulation interlock ---

    @property
    def ang_enable(self):
        """Angulation interlock enable."""
        return self['IntlkAngEn-Sts']

    @ang_enable.setter
    def ang_enable(self, value):
        self['IntlkAngEn-Sel'] = int(value)

    def cmd_reset_ang(self):
        """Angulation interlock clear."""
        self['IntlkAngClr-Cmd'] = 1
        return True

    @property
    def ang_x_min_thres(self):
        """Minimum X angulation threshold."""
        return self['IntlkLmtAngMinX-RB']

    @ang_x_min_thres.setter
    def ang_x_min_thres(self, value):
        self['IntlkLmtAngMinX-SP'] = value

    @property
    def ang_x_max_thres(self):
        """Maximum X angulation threshold."""
        return self['IntlkLmtAngMaxX-RB']

    @ang_x_max_thres.setter
    def ang_x_max_thres(self, value):
        self['IntlkLmtAngMaxX-SP'] = value

    @property
    def ang_y_min_thres(self):
        """Minimum Y angulation threshold."""
        return self['IntlkLmtAngMinY-RB']

    @ang_y_min_thres.setter
    def ang_y_min_thres(self, value):
        self['IntlkLmtAngMinY-SP'] = value

    @property
    def ang_y_max_thres(self):
        """Maximum Y angulation threshold."""
        return self['IntlkLmtAngMaxY-RB']

    @ang_y_max_thres.setter
    def ang_y_max_thres(self, value):
        self['IntlkLmtAngMaxY-SP'] = value

    @property
    def ang_inst_lower_x(self):
        """
        Instantaneous angulation interlock set when X
        minimum threshold is exceeded.
        """
        return self['IntlkAngLowerX-Mon']

    @property
    def ang_inst_upper_x(self):
        """
        Instantaneous angulation interlock set when X
        maximum threshold is exceeded.
        """
        return self['IntlkAngUpperX-Mon']

    @property
    def ang_inst_lower_y(self):
        """
        Instantaneous angulation interlock set when Y
        minimum threshold is exceeded.
        """
        return self['IntlkAngLowerY-Mon']

    @property
    def ang_inst_upper_y(self):
        """
        Instantaneous angulation interlock set when Y
        maximum threshold is exceeded.
        """
        return self['IntlkAngUpperY-Mon']

    @property
    def ang_latch_lower_x(self):
        """
        Latch angulation interlock set when X
        minimum threshold is exceeded.
        """
        return self['IntlkAngLowerLtcX-Mon']

    @property
    def ang_latch_upper_x(self):
        """
        Latch angulation interlock set when X
        maximum threshold is exceeded.
        """
        return self['IntlkAngUpperLtcX-Mon']

    @property
    def ang_latch_lower_y(self):
        """
        Latch angulation interlock set when Y
        minimum threshold is exceeded.
        """
        return self['IntlkAngLowerLtcY-Mon']

    @property
    def ang_latch_upper_y(self):
        """
        Latch angulation interlock set when Y
        maximum threshold is exceeded.
        """
        return self['IntlkAngUpperLtcY-Mon']


class OrbitInterlock(BaseOrbitIntlk, _DeviceSet):
    """Orbit Interlock device."""

    TIMEOUT = 10

    class DEVICES:
        """."""
        SI = 'SI-Fam:DI-BPM'
        ALL = (SI, )

    def __init__(self, devname=None, props2init='all'):
        """Init."""
        if devname is None:
            devname = self.DEVICES.SI
        if devname not in self.DEVICES.ALL:
            raise ValueError('Wrong value for devname')
        BaseOrbitIntlk.__init__(self)
        devs = [
            BPMOrbitIntlk(dev, props2init=props2init)
            for dev in self.BPM_NAMES]
        _DeviceSet.__init__(self, devs, devname=devname)

    # --- general interlock ---

    @property
    def gen_enable(self):
        """General interlock enable.

        Returns:
            enbl (numpy.ndarray, 160):
                enable state for each BPM.
        """
        return _np.array([b.gen_enable for b in self._devices])

    def set_gen_enable(self, value, timeout=TIMEOUT, return_prob=False):
        """Set enable state for BPM general interlock."""
        self._set_devices_propty(self.devices, 'IntlkEn-Sel', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkEn-Sts', value, timeout=timeout,
            return_prob=return_prob)

    def cmd_gen_enable(self, timeout=TIMEOUT, return_prob=False):
        """Enable all BPM general interlock."""
        for dev in self.devices:
            dev.gen_enable = 1
        return self._wait_devices_propty(
            self.devices, 'IntlkEn-Sts', 1, timeout=timeout,
            return_prob=return_prob)

    def cmd_gen_disable(self, timeout=TIMEOUT, return_prob=False):
        """Disable all BPM general interlock."""
        for dev in self.devices:
            dev.gen_enable = 0
        return self._wait_devices_propty(
            self.devices, 'IntlkEn-Sts', 0, timeout=timeout,
            return_prob=return_prob)

    def cmd_reset_gen(self):
        """Reset all BPM general interlock."""
        for dev in self.devices:
            dev.cmd_reset_gen()
        return True

    @property
    def gen_inst(self):
        """General instantaneous interlocks.

        Returns:
            gen_inst (numpy.ndarray, 160):
                general instantaneous interlock for each BPM.
        """
        return _np.array([b.gen_inst for b in self._devices])

    @property
    def gen_latch(self):
        """General latch interlocks.

        Returns:
            gen_latch (numpy.ndarray, 160):
                general latch interlock for each BPM.
        """
        return _np.array([b.gen_latch for b in self._devices])

    # --- minimum sum threshold ---

    @property
    def minsum_enable(self):
        """Minimum sum threshold enable.

        Returns:
            enbl (numpy.ndarray, 160):
                enable state for each BPM.
        """
        return _np.array([b.minsum_enable for b in self._devices])

    def set_minsum_enable(self, value, timeout=TIMEOUT, return_prob=False):
        """Set enable state for BPM minimum sum interlock."""
        self._set_devices_propty(self.devices, 'IntlkMinSumEn-Sel', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkMinSumEn-Sts', value, timeout=timeout,
            return_prob=return_prob)

    def cmd_minsum_enable(self, timeout=TIMEOUT, return_prob=False):
        """Enable all BPM minimum sum threshold."""
        for dev in self.devices:
            dev.minsum_enable = 1
        return self._wait_devices_propty(
            self.devices, 'IntlkMinSumEn-Sts', 1, timeout=timeout,
            return_prob=return_prob)

    def cmd_minsum_disable(self, timeout=TIMEOUT, return_prob=False):
        """Disable all BPM minimum sum threshold."""
        for dev in self.devices:
            dev.minsum_enable = 0
        return self._wait_devices_propty(
            self.devices, 'IntlkMinSumEn-Sts', 0, timeout=timeout,
            return_prob=return_prob)

    @property
    def minsum_thres(self):
        """Minimum sum thresholds.

        Returns:
            thres (numpy.ndarray, 160): min.sum threshold for each BPM.
        """
        return _np.array([b.minsum_thres for b in self._devices])

    def set_minsum_thres(self, value, timeout=TIMEOUT, return_prob=False):
        """Set minimum sum thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum sum.
            timeout (float, optional): timeout to wait. Defaults to TIMEOUT.

        Returns:
            bool: True if set was successful.

        """
        value = self._handle_thres_input(value)
        self._set_devices_propty(self.devices, 'IntlkLmtMinSum-SP', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkLmtMinSum-RB', value, timeout=timeout,
            return_prob=return_prob)

    # --- position interlock ---

    @property
    def pos_enable(self):
        """Position interlock enable.

        Returns:
            enbl (numpy.ndarray, 160):
                enable state for each BPM.
        """
        return _np.array([b.pos_enable for b in self._devices])

    def set_pos_enable(self, value, timeout=TIMEOUT, return_prob=False):
        """Set enable state for BPM position interlock."""
        self._set_devices_propty(self.devices, 'IntlkPosEn-Sel', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkPosEn-Sts', value, timeout=timeout,
            return_prob=return_prob)

    def cmd_pos_enable(self, timeout=TIMEOUT, return_prob=False):
        """Enable all BPM position interlock."""
        for dev in self.devices:
            dev.pos_enable = 1
        return self._wait_devices_propty(
            self.devices, 'IntlkPosEn-Sts', 1, timeout=timeout,
            return_prob=return_prob)

    def cmd_pos_disable(self, timeout=TIMEOUT, return_prob=False):
        """Disable all BPM position interlock."""
        for dev in self.devices:
            dev.pos_enable = 0
        return self._wait_devices_propty(
            self.devices, 'IntlkPosEn-Sts', 0, timeout=timeout,
            return_prob=return_prob)

    def cmd_reset_pos(self):
        """Reset all BPM position interlock."""
        for dev in self.devices:
            dev.cmd_reset_pos()
        return True

    @property
    def pos_x_min_thres(self):
        """Minimum x position thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min. x position threshold for each BPM.
        """
        return _np.array([b.pos_x_min_thres for b in self._devices])

    def set_pos_x_min_thres(self, value, timeout=TIMEOUT, return_prob=False):
        """Set minimum x position thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum sum.
            timeout (float, optional): timeout to wait. Defaults to TIMEOUT.

        Returns:
            bool: True if set was successful.

        """
        value = self._handle_thres_input(value)
        self._set_devices_propty(self.devices, 'IntlkLmtPosMinX-SP', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkLmtPosMinX-RB', value, timeout=timeout,
            return_prob=return_prob)

    @property
    def pos_x_max_thres(self):
        """Maximum x position thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                max. x position threshold for each BPM.
        """
        return _np.array([b.pos_x_max_thres for b in self._devices])

    def set_pos_x_max_thres(self, value, timeout=TIMEOUT, return_prob=False):
        """Set maximum x position thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum sum.
            timeout (float, optional): timeout to wait. Defaults to TIMEOUT.

        Returns:
            bool: True if set was successful.

        """
        value = self._handle_thres_input(value)
        self._set_devices_propty(self.devices, 'IntlkLmtPosMaxX-SP', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkLmtPosMaxX-RB', value, timeout=timeout,
            return_prob=return_prob)

    @property
    def pos_y_min_thres(self):
        """Minimum y position thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min. y position threshold for each BPM.
        """
        return _np.array([b.pos_y_min_thres for b in self._devices])

    def set_pos_y_min_thres(self, value, timeout=TIMEOUT, return_prob=False):
        """Set minimum y position thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum sum.
            timeout (float, optional): timeout to wait. Defaults to TIMEOUT.

        Returns:
            bool: True if set was successful.

        """
        value = self._handle_thres_input(value)
        self._set_devices_propty(self.devices, 'IntlkLmtPosMinY-SP', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkLmtPosMinY-RB', value, timeout=timeout,
            return_prob=return_prob)

    @property
    def pos_y_max_thres(self):
        """Maximum y position thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                max. y position threshold for each BPM.
        """
        return _np.array([b.pos_y_max_thres for b in self._devices])

    def set_pos_y_max_thres(self, value, timeout=TIMEOUT, return_prob=False):
        """Set maximum y position thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum sum.
            timeout (float, optional): timeout to wait. Defaults to TIMEOUT.

        Returns:
            bool: True if set was successful.

        """
        value = self._handle_thres_input(value)
        self._set_devices_propty(self.devices, 'IntlkLmtPosMaxY-SP', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkLmtPosMaxY-RB', value, timeout=timeout,
            return_prob=return_prob)

    @property
    def pos_inst_lower_x(self):
        """Instantaneous position interlock set when X
        minimum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.pos_inst_lower_x for b in self._devices])

    @property
    def pos_inst_upper_x(self):
        """Instantaneous position interlock set when X
        maximum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.pos_inst_upper_x for b in self._devices])

    @property
    def pos_inst_lower_y(self):
        """Instantaneous position interlock set when Y
        minimum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.pos_inst_lower_y for b in self._devices])

    @property
    def pos_inst_upper_y(self):
        """Instantaneous position interlock set when Y
        maximum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.pos_inst_upper_y for b in self._devices])

    @property
    def pos_latch_lower_x(self):
        """Latch position interlock set when X
        minimum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.pos_latch_lower_x for b in self._devices])

    @property
    def pos_latch_upper_x(self):
        """Latch position interlock set when X
        maximum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.pos_latch_upper_x for b in self._devices])

    @property
    def pos_latch_lower_y(self):
        """Latch position interlock set when Y
        minimum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.pos_latch_lower_y for b in self._devices])

    @property
    def pos_latch_upper_y(self):
        """Latch position interlock set when Y
        maximum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.pos_latch_upper_y for b in self._devices])

    #  --- angulation interlock ---

    @property
    def ang_enable(self):
        """Angle interlock enable.

        Returns:
            enbl (numpy.ndarray, 160):
                enable state for each BPM.
        """
        return _np.array([b.ang_enable for b in self._devices])

    def set_ang_enable(self, value, timeout=TIMEOUT, return_prob=False):
        """Set enable state for BPM angulation interlock."""
        self._set_devices_propty(self.devices, 'IntlkAngEn-Sel', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkAngEn-Sts', value, timeout=timeout,
            return_prob=return_prob)

    def cmd_ang_enable(self, timeout=TIMEOUT, return_prob=False):
        """Enable all BPM angulation interlock."""
        for dev in self.devices:
            dev.ang_enable = 1
        return self._wait_devices_propty(
            self.devices, 'IntlkAngEn-Sts', 1, timeout=timeout,
            return_prob=return_prob)

    def cmd_ang_disable(self, timeout=TIMEOUT, return_prob=False):
        """Disable all BPM angulation interlock."""
        for dev in self.devices:
            dev.ang_enable = 0
        return self._wait_devices_propty(
            self.devices, 'IntlkAngEn-Sts', 0, timeout=timeout,
            return_prob=return_prob)

    def cmd_reset_ang(self):
        """Reset all BPM angulation interlock."""
        for dev in self.devices:
            dev.cmd_reset_ang()
        return True

    @property
    def ang_x_min_thres(self):
        """Minimum x angulation thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min. x angulation threshold for each BPM.
        """
        return _np.array([b.ang_x_min_thres for b in self._devices])

    def set_ang_x_min_thres(self, value, timeout=TIMEOUT, return_prob=False):
        """Set minimum x angle thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum sum.
            timeout (float, optional): timeout to wait. Defaults to TIMEOUT.

        Returns:
            bool: True if set was successful.

        """
        value = self._handle_thres_input(value)
        self._set_devices_propty(self.devices, 'IntlkLmtAngMinX-SP', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkLmtAngMinX-RB', value, timeout=timeout,
            return_prob=return_prob)

    @property
    def ang_x_max_thres(self):
        """Maximum x angulation thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                max. x angulation threshold for each BPM.
        """
        return _np.array([b.ang_x_max_thres for b in self._devices])

    def set_ang_x_max_thres(self, value, timeout=TIMEOUT, return_prob=False):
        """Set maximum x angle thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum sum.
            timeout (float, optional): timeout to wait. Defaults to TIMEOUT.

        Returns:
            bool: True if set was successful.

        """
        value = self._handle_thres_input(value)
        self._set_devices_propty(self.devices, 'IntlkLmtAngMaxX-SP', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkLmtAngMaxX-RB', value, timeout=timeout,
            return_prob=return_prob)

    @property
    def ang_y_min_thres(self):
        """Minimum y angulation thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min. y angulation threshold for each BPM.
        """
        return _np.array([b.ang_y_min_thres for b in self._devices])

    def set_ang_y_min_thres(self, value, timeout=TIMEOUT, return_prob=False):
        """Set minimum y angle thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum sum.
            timeout (float, optional): timeout to wait. Defaults to TIMEOUT.

        Returns:
            bool: True if set was successful.

        """
        value = self._handle_thres_input(value)
        self._set_devices_propty(self.devices, 'IntlkLmtAngMinY-SP', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkLmtAngMinY-RB', value, timeout=timeout,
            return_prob=return_prob)

    @property
    def ang_y_max_thres(self):
        """Maximum y angulation thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                max. y angulation threshold for each BPM.
        """
        return _np.array([b.ang_y_max_thres for b in self._devices])

    def set_ang_y_max_thres(self, value, timeout=TIMEOUT, return_prob=False):
        """Set maximum y angle thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum sum.
            timeout (float, optional): timeout to wait. Defaults to TIMEOUT.

        Returns:
            bool: True if set was successful.

        """
        value = self._handle_thres_input(value)
        self._set_devices_propty(self.devices, 'IntlkLmtAngMaxY-SP', value)
        return self._wait_devices_propty(
            self.devices, 'IntlkLmtAngMaxY-RB', value, timeout=timeout,
            return_prob=return_prob)

    @property
    def ang_inst_lower_x(self):
        """Instantaneous angulation interlock set when X
        minimum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.ang_inst_lower_x for b in self._devices])

    @property
    def ang_inst_upper_x(self):
        """Instantaneous angulation interlock set when X
        maximum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.ang_inst_upper_x for b in self._devices])

    @property
    def ang_inst_lower_y(self):
        """Instantaneous angulation interlock set when Y
        minimum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.ang_inst_lower_y for b in self._devices])

    @property
    def ang_inst_upper_y(self):
        """Instantaneous angulation interlock set when Y
        maximum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.ang_inst_upper_y for b in self._devices])

    @property
    def ang_latch_lower_x(self):
        """Latch angulation interlock set when X
        minimum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.ang_latch_lower_x for b in self._devices])

    @property
    def ang_latch_upper_x(self):
        """Latch angulation interlock set when X
        maximum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.ang_latch_upper_x for b in self._devices])

    @property
    def ang_latch_lower_y(self):
        """Latch angulation interlock set when Y
        minimum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.ang_latch_lower_y for b in self._devices])

    @property
    def ang_latch_upper_y(self):
        """Latch angulation interlock set when Y
        maximum threshold is exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.ang_latch_upper_y for b in self._devices])

    @property
    def position(self):
        """Position vectors.

        Position at each BPM is defined as:
            (pos BPM downstream + pos BPM upstream)/2

        Returns:
            posx (numpy.ndarray, 160): Horizontal Position.
            posy (numpy.ndarray, 160): Vertical Position.
        """
        posx = _np.array([b.intlkposx for b in self._devices])
        posy = _np.array([b.intlkposy for b in self._devices])
        return posx, posy

    @property
    def angle(self):
        """Angle vectors.

        Angle at each BPM is defined as:
            (posição BPM downstream - posição BPM upstream)

        Returns:
            angx (numpy.ndarray, 160): Horizontal Angle.
            angy (numpy.ndarray, 160): Vertical Angle.
        """
        angx = _np.array([b.intlkangx for b in self._devices])
        angy = _np.array([b.intlkangy for b in self._devices])
        return angx, angy

    def _handle_thres_input(self, value):
        typs = (bool, int, float, _np.bool_, _np.int64, _np.float64)
        if isinstance(value, typs):
            return [value, ] * len(self.BPM_NAMES)
        if len(value) != len(self.BPM_NAMES):
            raise ValueError(
                f'Expected length is {len(self.BPM_NAMES)}, not {len(value)}'
            )
        return value


class HLOrbitInterlock(BaseOrbitIntlk, _Device):
    """."""

    TIMEOUT = 10

    class DEVICES:
        """."""
        SI = 'SI-Glob:AP-OrbIntlk'
        ALL = (SI, )

    PROPERTIES_DEFAULT = (
        'Enable-Sel', 'Enable-Sts', 'Reset-Cmd',
        'BPMStatus-Mon', 'TimingStatus-Mon', 'LLRFStatus-Mon',
        'PosXMaxLim-SP', 'PosXMaxLim-RB',
        'PosXMinLim-SP', 'PosXMinLim-RB',
        'AngXMaxLim-SP', 'AngXMaxLim-RB',
        'AngXMinLim-SP', 'AngXMinLim-RB',
        'PosYMaxLim-SP', 'PosYMaxLim-RB',
        'PosYMinLim-SP', 'PosYMinLim-RB',
        'AngYMaxLim-SP', 'AngYMaxLim-RB',
        'AngYMinLim-SP', 'AngYMinLim-RB',
        'MinSumLim-SP', 'MinSumLim-RB',
        'PosEnblList-SP', 'PosEnblList-RB',
        'AngEnblList-SP', 'AngEnblList-RB',
        'MinSumEnblList-SP', 'MinSumEnblList-RB',
    )

    def __init__(self, props2init='all'):
        """."""
        _Device.__init__(self, devname=self.DEVICES.SI, props2init=props2init)
        BaseOrbitIntlk.__init__(self)

    @property
    def enable(self):
        """General interlock enable.

        Returns:
            enbl (numpy.ndarray, 160): enable state for each BPM.
        """
        return self['Enable-Sts']

    def set_enable(self, value, timeout=TIMEOUT):
        """Set enable state for BPM general interlock."""
        self['Enable-Sel'] = bool(value)
        return self._wait('Enable-Sts', bool(value), timeout=timeout)

    def cmd_enable(self, timeout=TIMEOUT):
        """Enable all BPM general interlock."""
        return self.set_enable(True, timeout=timeout)

    def cmd_disable(self, timeout=TIMEOUT):
        """Disable all BPM general interlock."""
        return self.set_enable(False, timeout=timeout)

    def cmd_reset(self, timeout=TIMEOUT):
        """Enable all BPM general interlock."""
        val = self['Reset-Cmd']
        self['Reset-Cmd'] = True
        return self._wait('Reset-Cmd', val+1, timeout=timeout)

    @property
    def pos_x_min_thres(self):
        """Minimum x position thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min. x position threshold for each BPM.
        """
        return self['PosXMinLim-RB']

    @pos_x_min_thres.setter
    def pos_x_min_thres(self, value):
        """Set minimum x position thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum x position.
        """
        self['PosXMinLim-SP'] = self._handle_thres_input(value)

    @property
    def pos_x_max_thres(self):
        """Maximum x position thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                max. x position threshold for each BPM.
        """
        return self['PosXMaxLim-RB']

    @pos_x_max_thres.setter
    def pos_x_max_thres(self, value):
        """Set maximum x position thresholds.

        Args:
            value (numpy.ndarray|float): Values for maximum x position.
        """
        self['PosXMaxLim-SP'] = self._handle_thres_input(value)

    @property
    def pos_y_min_thres(self):
        """Minimum y position thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min. y position threshold for each BPM.
        """
        return self['PosYMinLim-RB']

    @pos_y_min_thres.setter
    def pos_y_min_thres(self, value):
        """Set minimum y position thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum y position.
        """
        self['PosYMinLim-SP'] = self._handle_thres_input(value)

    @property
    def pos_y_max_thres(self):
        """Maximum y position thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                max. y position threshold for each BPM.
        """
        return self['PosYMaxLim-RB']

    @pos_y_max_thres.setter
    def pos_y_max_thres(self, value):
        """Set maximum y position thresholds.

        Args:
            value (numpy.ndarray|float): Values for maximum y position.
        """
        self['PosYMaxLim-SP'] = self._handle_thres_input(value)

    @property
    def ang_x_min_thres(self):
        """Minimum x angulation thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min. x angulation threshold for each BPM.
        """
        return self['AngXMinLim-RB']

    @ang_x_min_thres.setter
    def ang_x_min_thres(self, value):
        """Set minimum x angle thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum x angle.
        """
        self['AngXMinLim-SP'] = self._handle_thres_input(value)

    @property
    def ang_x_max_thres(self):
        """Maximum x angulation thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                max. x angulation threshold for each BPM.
        """
        return self['AngXMaxLim-RB']

    @ang_x_max_thres.setter
    def ang_x_max_thres(self, value):
        """Set maximum x angle thresholds.

        Args:
            value (numpy.ndarray|float): Values for maximum x angle.
        """
        self['AngXMaxLim-SP'] = self._handle_thres_input(value)

    @property
    def ang_y_min_thres(self):
        """Minimum y angulation thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min. y angulation threshold for each BPM.
        """
        return self['AngYMinLim-RB']

    @ang_y_min_thres.setter
    def ang_y_min_thres(self, value):
        """Set minimum y angle thresholds.

        Args:
            value (numpy.ndarray|float): Values for minimum y angle.
        """
        self['AngYMinLim-SP'] = self._handle_thres_input(value)

    @property
    def ang_y_max_thres(self):
        """Maximum y angulation thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                max. y angulation threshold for each BPM.
        """
        return self['AngYMaxLim-RB']

    @ang_y_max_thres.setter
    def ang_y_max_thres(self, value):
        """Set maximum y angle thresholds.

        Args:
            value (numpy.ndarray|float): Values for maximum y angle.
        """
        self['AngYMaxLim-SP'] = self._handle_thres_input(value)

    @property
    def minsum_thres(self):
        """Min sum thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min sum threshold for each BPM.
        """
        return self['MinSumLim-RB']

    @minsum_thres.setter
    def minsum_thres(self, value):
        """Set min sum thresholds.

        Args:
            value (numpy.ndarray|float): Values for min sum.
        """
        self['MinSumLim-SP'] = self._handle_thres_input(value)

    @property
    def pos_enbl_list(self):
        """Position enable list.

        Returns:
            enbl_list (numpy.ndarray, 160): position enable list for each BPM.
        """
        return self['PosEnblList-RB']

    @pos_enbl_list.setter
    def pos_enbl_list(self, value):
        """Set position enable list.

        Args:
            value (numpy.ndarray|bool): Values for enable list.
        """
        self['PosEnblList-SP'] = self._handle_thres_input(value)

    @property
    def ang_enbl_list(self):
        """Angle enable list.

        Returns:
            enbl_list (numpy.ndarray, 160): angle enable list for each BPM.
        """
        return self['AngEnblList-RB']

    @ang_enbl_list.setter
    def ang_enbl_list(self, value):
        """Set angle enable list.

        Args:
            value (numpy.ndarray|bool): Values for enable list.
        """
        self['AngEnblList-SP'] = self._handle_thres_input(value)

    @property
    def minsum_enbl_list(self):
        """Min sum enable list.

        Returns:
            enbl_list (numpy.ndarray, 160): min sum enable list for each BPM.
        """
        return self['MinSumEnblList-RB']

    @minsum_enbl_list.setter
    def minsum_enbl_list(self, value):
        """Set min sum enable list.

        Args:
            value (numpy.ndarray|bool): Values for enable list.
        """
        self['MinSumEnblList-SP'] = self._handle_thres_input(value)

    def get_standard_interlock_limits_definitions(self):
        """Get default interlock limits from control-system-constants table."""
        return _OrbIntlkSearch.get_limits()

    def set_interlock_limits(self, refx=None, refy=None, limits=None):
        """Set interlock limits based on input config or default values.

        Args:
            refx (numpy.ndarray, optional): Horizontal reference orbit around
                which limits will be calculated. Defaults to None. If None,
                then the current 'bba_orb' will be used.
            refy (numpy.ndarray, optional): Vertical reference orbit around
                which limits will be calculated. Defaults to None.If None,
                then the current 'bba_orb' will be used.
            limits (dict, optional): Dictionary whose keys are the name of the
                subsection (ex. '01SA', '04BC') where to apply the interlock
                limits and values are dictionaries with keys:
                    'agx', 'agy', 'psx', 'psy'
                defining the values of the interlock limits around the
                reference orbit. The rest of the ring will have its limits set
                to 1.2 times the largest respective limit. Defaults to None.
                If None, then the standard definition from the
                control-system-constants table will be used.

        Raises:
            ValueError: In case inputs don't match the description above.
            TypeError: In case inputs don't match the description above.
            RunTimeError: In case interlock is enabled.
        """
        if self.enable:
            raise RuntimeError(
                'Cannot set limits, orbit interlock is enabled.'
            )
        if refx is None or refy is None:
            clt = ConfigDBClient(config_type='si_orbit')
            refo = clt.get_config_value('bba_orb')
            if refx is None:
                refx = _np.array(refo['x'])
            if refy is None:
                refy = _np.array(refo['y'])
        if limits is None:
            limits = self.get_standard_interlock_limits_definitions()

        if {len(refx), len(refy)} - {len(self.BPM_NAMES)}:
            raise ValueError('Length of reference orbit must match BPMs.')
        if not isinstance(limits, dict):
            raise TypeError('Limits must be a dictionary')

        entries = {'psx', 'psy', 'agx', 'agy'}
        for k, v in limits.items():
            if not isinstance(k, str):
                raise ValueError('Every key of limits must be a str.')
            if not isinstance(v, dict):
                raise TypeError('Every entry of limits must be dictionary.')
            if not v.keys() == entries:
                raise ValueError(
                    'Every entry of limits must have keys: ' +
                    ', '.join(entries)
                )

        limits = limits.copy()

        flag = _np.zeros(refx.size, dtype=bool)
        zer = refx*0.0
        agx, agy = zer.copy(), zer.copy()
        psx, psy = zer.copy(), zer.copy()
        mxp, myp, mxa, mya = 0.0, 0.0, 0.0, 0.0
        for ssec, idd in limits.items():
            # Position
            ids = idd.copy()
            [ids.pop(k) for k in ('agx', 'agy')]
            bpx, bpy = _si_calculate_bump(zer, zer, subsec=ssec, **ids)
            flg = bpx != 0.0
            psx[flg] = bpx.max()
            psy[flg] = bpy.max()
            mxp, myp = max(mxp, bpx.max()), max(myp, bpy.max())

            # Angle
            ids = idd.copy()
            [ids.pop(k) for k in ('psx', 'psy')]
            bpx, bpy = _si_calculate_bump(zer, zer, subsec=ssec, **ids)
            agx[flg] = bpx.max()*2  # NOTE: not valid for BC, C1, C2. Needs
            agy[flg] = bpy.max()*2  # generalization of BPM firmware.
            mxa, mya = max(mxa, bpx.max()*2), max(mya, bpy.max()*2)

            flag |= flg

        psx[~flag] = mxp * 1.2
        psy[~flag] = myp * 1.2
        agx[~flag] = mxa * 1.2
        agy[~flag] = mya * 1.2

        # set limits
        refx_pos = self.calc_intlk_metric(refx, metric='pos')
        refy_pos = self.calc_intlk_metric(refy, metric='pos')
        refx_ang = self.calc_intlk_metric(refx, metric='ang')
        refy_ang = self.calc_intlk_metric(refy, metric='ang')

        # needs convertion from [um] to [nm]:
        self.pos_x_max_thres = _np.round((refx_pos + psx) * 1e3)
        self.pos_x_min_thres = _np.round((refx_pos - psx) * 1e3)
        self.pos_y_max_thres = _np.round((refy_pos + psy) * 1e3)
        self.pos_y_min_thres = _np.round((refy_pos - psy) * 1e3)
        self.ang_x_max_thres = _np.round((refx_ang + agx) * 1e3)
        self.ang_x_min_thres = _np.round((refx_ang - agx) * 1e3)
        self.ang_y_max_thres = _np.round((refy_ang + agy) * 1e3)
        self.ang_y_min_thres = _np.round((refy_ang - agy) * 1e3)

        self.pos_enbl_list = flag
        self.ang_enbl_list = flag

    def _handle_thres_input(self, value):
        return OrbitInterlock._handle_thres_input(self, value)
