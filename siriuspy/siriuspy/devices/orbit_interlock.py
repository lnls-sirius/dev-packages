"""Orbit Interlock devices."""

import numpy as _np

from ..search import BPMSearch as _BPMSearch
from ..util import ClassProperty as _classproperty
from .device import Device as _Device, Devices as _Devices


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
        return data_values

    @staticmethod
    def _mean(var1, var2):
        return (var1 + var2)/2

    @staticmethod
    def _diff(var1, var2):
        return var1 - var2


class BPMOrbitIntlk(BaseOrbitIntlk, _Device):
    """This device group the orbit interlock  PVs from one BPM."""

    _properties = (
        # ==============================================================
        # Basic properties
        'PosX-Mon', 'PosY-Mon', 'Sum-Mon',
        # ==============================================================
        # General
        # +++++++
        # General interlock enable:
        'IntlkEn-Sel', 'IntlkEn-Sts',
        # General interlock clear:
        'IntlkClr-Cmd',  # maybe -Cmd?
        # Minimum sum threshold enable:
        # Habilita interlock de órbita apenas quando threshold da soma
        # ultrapassar o valor em "IntlkLmtMinSum-SP"
        'IntlkMinSumEn-Sel', 'IntlkMinSumEn-Sts',
        # Minimum sum threshold (em contagens da Soma da taxa FAcq):
        'IntlkLmtMinSum-SP', 'IntlkLmtMinSum-RB',
        # Status Instantâneo:
        # Interlock instântaneo, dificilmente será detectado com
        # a implementação atual do gateware
        'Intlk-Mon',
        # Latch do interlock, limpo apenas acionando-se a PV "Clr"
        # correspondente
        'IntlkLtc-Mon',
        # ===============================================================
        # Position (interlock de posição)
        # +++++++++++++++++++++++++++++++++++++
        # ***************************************************************
        # Condição para interlock de posição:
        #   thres_min > (pos BPM downstream + pos BPM upstream)/2 or
        #   thres_max < (pos BPM downstream + pos BPM upstream)/2
        # BPMs são agrupados 2 a 2 seguindo a ordem do feixe:
        # - M1/M2
        # - C1-1/C1-2
        # - C2/C3-1
        # - C3-2/C4
        # BPM upstream é sempre o "primeiro" BPM da dupla acima e BPM
        # downstream é sempre o "segundo" BPM da dupla.
        # ***************************************************************
        # Position interlock enable:
        'IntlkPosEn-Sel', 'IntlkPosEn-Sts',
        # Position interlock clear:
        'IntlkPosClr-Cmd',
        # Thresholds (em nm da taxa Monit1):
        'IntlkLmtPosMaxX-SP', 'IntlkLmtPosMaxX-RB',
        'IntlkLmtPosMinX-SP', 'IntlkLmtPosMinX-RB',
        'IntlkLmtPosMaxY-SP', 'IntlkLmtPosMaxY-RB',
        'IntlkLmtPosMinY-SP', 'IntlkLmtPosMinY-RB',
        # Todos os interlocks são mascarados pelo "Enable"
        # Status Instantâneo:
        'IntlkPosLower-Mon', 'IntlkPosUpper-Mon',  # X ou Y
        'IntlkPosLowerX-Mon', 'IntlkPosUpperX-Mon',  # X
        'IntlkPosLowerY-Mon', 'IntlkPosUpperY-Mon',  # Y
        # Status Latch, limpo apenas acionando-se a PV "Clr" correspondente:
        'IntlkPosLowerLtc-Mon', 'IntlkPosUpperLtc-Mon',
        'IntlkPosLowerLtcX-Mon', 'IntlkPosUpperLtcX-Mon',
        'IntlkPosLowerLtcY-Mon', 'IntlkPosUpperLtcY-Mon',
        # =============================================================
        # Angular (interlock de ângulo)
        # +++++++++++++++++++++++++++++
        # *************************************************************
        # Condição para interlock de ângulo:
        #   thres_min > (posição BPM downstream - posição BPM upstream) or
        #   thres_max < (posição BPM downstream - posição BPM upstream)
        # BPMs são agrupados 2 a 2 seguindo a ordem do feixe:
        # - M1/M2
        # - C1-1/C1-2
        # - C2/C3-1
        # - C3-2/C4
        # BPM upstream é sempre o "primeiro" BPM da dupla acima e BPM
        # downstream é sempre o "segundo" BPM da dupla.
        # ************************************************************
        # Angulation interlock enable:
        'IntlkAngEn-Sel', 'IntlkAngEn-Sts',
        # Angulation interlock clear:
        'IntlkAngClr-Cmd',
        # Thresholds (em rad.nm da taxa FAcq).
        # Thresholds devem ser calculados como ângulo (em rad)
        #  entre os 2 BPMs adjacentes * distância (em nm) entre eles):
        'IntlkLmtAngMaxX-SP', 'IntlkLmtAngMaxX-RB',
        'IntlkLmtAngMinX-SP', 'IntlkLmtAngMinX-RB',
        'IntlkLmtAngMaxY-SP', 'IntlkLmtAngMaxY-RB',
        'IntlkLmtAngMinY-SP', 'IntlkLmtAngMinY-RB',
        # Todos os interlocks são mascarados pelo "Enable"
        # Status Instantâneo:
        'IntlkAngLower-Mon', 'IntlkAngUpper-Mon',
        'IntlkAngLowerX-Mon', 'IntlkAngUpperX-Mon',  # X
        'IntlkAngLowerY-Mon', 'IntlkAngUpperY-Mon',  # Y
        # Status Latch, limpo apenas acionando-se a PV "Clr" correspondente:
        'IntlkAngLowerLtc-Mon', 'IntlkAngUpperLtc-Mon',
        'IntlkAngLowerLtcX-Mon', 'IntlkAngUpperLtcX-Mon',
        'IntlkAngLowerLtcY-Mon', 'IntlkAngUpperLtcY-Mon',
        # ============================================================
        )

    def __init__(self, devname):
        """Init."""
        # call base class constructor
        BaseOrbitIntlk.__init__(self)
        if devname not in self.BPM_NAMES:
            raise ValueError(devname + ' is no a valid BPM name.')
        _Device.__init__(self, devname, properties=BPMOrbitIntlk._properties)

    @property
    def posx(self):
        """Position X, Monit rate."""
        return self['PosX-Mon'] * self.CONV_NM2UM

    @property
    def posy(self):
        """Position Y, Monit rate."""
        return self['PosY-Mon'] * self.CONV_NM2UM

    @property
    def possum(self):
        """Sum, Monit rate."""
        return self['Sum-Mon']

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
    def minsumthres_enable(self):
        """
        Minimum sum threshold enable.

        If enabled, generate orbit interlock only when sum threshold exceeds
        value in 'minsumthres' property.
        """
        return self['IntlkMinSumEn-Sts']

    @minsumthres_enable.setter
    def minsumthres_enable(self, value):
        self['IntlkMinSumEn-Sel'] = int(value)

    @property
    def minsumthres(self):
        """Minimum sum threshold [sum count, FAcq rate]."""
        return self['IntlkLmtMinSum-RB']

    @minsumthres.setter
    def minsumthres(self, value):
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
    def pos_thresminx(self):
        """Minimum X position threshold."""
        return self['IntlkLmtPosMinX-RB']

    @pos_thresminx.setter
    def pos_thresminx(self, value):
        self['IntlkLmtPosMinX-SP'] = value

    @property
    def pos_thresmaxx(self):
        """Maximum X position threshold."""
        return self['IntlkLmtPosMaxX-RB']

    @pos_thresmaxx.setter
    def pos_thresmaxx(self, value):
        self['IntlkLmtPosMaxX-SP'] = value

    @property
    def pos_thresminy(self):
        """Minimum Y position threshold."""
        return self['IntlkLmtPosMinY-RB']

    @pos_thresminy.setter
    def pos_thresminy(self, value):
        self['IntlkLmtPosMinY-SP'] = value

    @property
    def pos_thresmaxy(self):
        """Maximum Y position threshold."""
        return self['IntlkLmtPosMaxY-RB']

    @pos_thresmaxy.setter
    def pos_thresmaxy(self, value):
        self['IntlkLmtPosMaxY-SP'] = value

    @property
    def pos_inst_lower(self):
        """
        Instantaneous position interlock set when either X or Y
        minimum thresholds are exceeded.
        """
        return self['IntlkPosLower-Mon']

    @property
    def pos_inst_upper(self):
        """
        Instantaneous position interlock set when either X or Y
        maximum thresholds are exceeded.
        """
        return self['IntlkPosUpper-Mon']

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
    def pos_latch_lower(self):
        """
        Latch position interlock set when either X or Y
        minimum thresholds are exceeded.
        """
        return self['IntlkPosLowerLtc-Mon']

    @property
    def pos_latch_upper(self):
        """
        Latch position interlock set when either X or Y
        maximum thresholds are exceeded.
        """
        return self['IntlkPosUpperLtc-Mon']

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
    def ang_thresminx(self):
        """Minimum X angulation threshold."""
        return self['IntlkLmtAngMinX-RB']

    @ang_thresminx.setter
    def ang_thresminx(self, value):
        self['IntlkLmtAngMinX-SP'] = value

    @property
    def ang_thresmaxx(self):
        """Maximum X angulation threshold."""
        return self['IntlkLmtAngMaxX-RB']

    @ang_thresmaxx.setter
    def ang_thresmaxx(self, value):
        self['IntlkLmtAngMaxX-SP'] = value

    @property
    def ang_thresminy(self):
        """Minimum Y angulation threshold."""
        return self['IntlkLmtAngMinY-RB']

    @ang_thresminy.setter
    def ang_thresminy(self, value):
        self['IntlkLmtAngMinY-SP'] = value

    @property
    def ang_thresmaxy(self):
        """Maximum Y angulation threshold."""
        return self['IntlkLmtAngMaxY-RB']

    @ang_thresmaxy.setter
    def ang_thresmaxy(self, value):
        self['IntlkLmtAngMaxY-SP'] = value

    @property
    def ang_inst_lower(self):
        """
        Instantaneous angulation interlock set when either X or Y
        minimum thresholds are exceeded.
        """
        return self['IntlkAngLower-Mon']

    @property
    def ang_inst_upper(self):
        """
        Instantaneous angulation interlock set when either X or Y
        maximum thresholds are exceeded.
        """
        return self['IntlkAngUpper-Mon']

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
    def ang_latch_lower(self):
        """
        Latch angulation interlock set when either X or Y
        minimum thresholds are exceeded.
        """
        return self['IntlkAngLowerLtc-Mon']

    @property
    def ang_latch_upper(self):
        """
        Latch angulation interlock set when either X or Y
        maximum thresholds are exceeded.
        """
        return self['IntlkAngUpperLtc-Mon']

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


class OrbitInterlock(BaseOrbitIntlk, _Devices):
    """Orbit Interlock device."""

    TIMEOUT = 10

    class DEVICES:
        """."""
        SI = 'SI-Fam:DI-BPM'
        ALL = (SI, )

    def __init__(self, devname=None):
        """Init."""
        if devname is None:
            devname = self.DEVICES.SI
        if devname not in self.DEVICES.ALL:
            raise ValueError('Wrong value for devname')
        BaseOrbitIntlk.__init__(self)
        devs = [BPMOrbitIntlk(dev) for dev in self.BPM_NAMES]
        _Devices.__init__(self, devname, devs)

    # --- general interlock ---

    def cmd_gen_enable(self, timeout=TIMEOUT):
        """Enable all BPM general interlock."""
        for dev in self.devices:
            dev.gen_enable = 1
        return self._wait_devices_propty(
            self.devices, 'IntlkEn-Sts', 1, timeout=timeout)

    def cmd_gen_disable(self, timeout=TIMEOUT):
        """Disable all BPM general interlock."""
        for dev in self.devices:
            dev.gen_enable = 0
        return self._wait_devices_propty(
            self.devices, 'IntlkEn-Sts', 0, timeout=timeout)

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

    def cmd_minsumthres_enable(self, timeout=TIMEOUT):
        """Enable all BPM minimum sum threshold."""
        for dev in self.devices:
            dev.minsumthres_enable = 1
        return self._wait_devices_propty(
            self.devices, 'IntlkMinSumEn-Sts', 1, timeout=timeout)

    def cmd_minsumthres_disable(self, timeout=TIMEOUT):
        """Disable all BPM minimum sum threshold."""
        for dev in self.devices:
            dev.minsumthres_enable = 0
        return self._wait_devices_propty(
            self.devices, 'IntlkMinSumEn-Sts', 0, timeout=timeout)

    @property
    def minsumthres(self):
        """Minimum sum thresholds.

        Returns:
            thres (numpy.ndarray, 160): min.sum threshold for each BPM.
        """
        return _np.array([b.minsumthres for b in self._devices])

    @minsumthres.setter
    def minsumthres(self, value):
        value = self._handle_thres_input(value)
        for idx, dev in enumerate(self.devices):
            dev.minsumthres = value[idx]

    # --- position interlock ---

    def cmd_pos_enable(self, timeout=TIMEOUT):
        """Enable all BPM position interlock."""
        for dev in self.devices:
            dev.pos_enable = 1
        return self._wait_devices_propty(
            self.devices, 'IntlkPosEn-Sts', 1, timeout=timeout)

    def cmd_pos_disable(self, timeout=TIMEOUT):
        """Disable all BPM position interlock."""
        for dev in self.devices:
            dev.pos_enable = 0
        return self._wait_devices_propty(
            self.devices, 'IntlkPosEn-Sts', 0, timeout=timeout)

    def cmd_reset_pos(self):
        """Reset all BPM position interlock."""
        for dev in self.devices:
            dev.cmd_reset_pos()
        return True

    @property
    def pos_thresminx(self):
        """Minimum x position thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min. x position threshold for each BPM.
        """
        return _np.array([b.pos_thresminx for b in self._devices])

    @pos_thresminx.setter
    def pos_thresminx(self, value):
        value = self._handle_thres_input(value)
        for idx, dev in enumerate(self.devices):
            dev.pos_thresminx = value[idx]

    @property
    def pos_thresmaxx(self):
        """Maximum x position thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                max. x position threshold for each BPM.
        """
        return _np.array([b.pos_thresmaxx for b in self._devices])

    @pos_thresmaxx.setter
    def pos_thresmaxx(self, value):
        value = self._handle_thres_input(value)
        for idx, dev in enumerate(self.devices):
            dev.pos_thresmaxx = value[idx]

    @property
    def pos_thresminy(self):
        """Minimum y position thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min. y position threshold for each BPM.
        """
        return _np.array([b.pos_thresminy for b in self._devices])

    @pos_thresminy.setter
    def pos_thresminy(self, value):
        value = self._handle_thres_input(value)
        for idx, dev in enumerate(self.devices):
            dev.pos_thresminy = value[idx]

    @property
    def pos_thresmaxy(self):
        """Maximum y position thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                max. y position threshold for each BPM.
        """
        return _np.array([b.pos_thresmaxy for b in self._devices])

    @pos_thresmaxy.setter
    def pos_thresmaxy(self, value):
        value = self._handle_thres_input(value)
        for idx, dev in enumerate(self.devices):
            dev.pos_thresmaxy = value[idx]

    @property
    def pos_inst_lower(self):
        """Instantaneous position interlock set when either X or Y
        minimum thresholds are exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.pos_inst_lower for b in self._devices])

    @property
    def pos_inst_upper(self):
        """Instantaneous position interlock set when either X or Y
        maximum thresholds are exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.pos_inst_upper for b in self._devices])

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
    def pos_latch_lower(self):
        """Latch position interlock set when either X or Y
        minimum thresholds are exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.pos_latch_lower for b in self._devices])

    @property
    def pos_latch_upper(self):
        """Latch position interlock set when either X or Y
        maximum thresholds are exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.pos_latch_upper for b in self._devices])

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

    def cmd_ang_enable(self, timeout=TIMEOUT):
        """Enable all BPM angulation interlock."""
        for dev in self.devices:
            dev.ang_enable = 1
        return self._wait_devices_propty(
            self.devices, 'IntlkAngEn-Sts', 1, timeout=timeout)

    def cmd_ang_disable(self, timeout=TIMEOUT):
        """Disable all BPM angulation interlock."""
        for dev in self.devices:
            dev.ang_enable = 0
        return self._wait_devices_propty(
            self.devices, 'IntlkAngEn-Sts', 0, timeout=timeout)

    def cmd_reset_ang(self):
        """Reset all BPM angulation interlock."""
        for dev in self.devices:
            dev.cmd_reset_ang()
        return True

    @property
    def ang_thresminx(self):
        """Minimum x angulation thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min. x angulation threshold for each BPM.
        """
        return _np.array([b.ang_thresminx for b in self._devices])

    @ang_thresminx.setter
    def ang_thresminx(self, value):
        value = self._handle_thres_input(value)
        for idx, dev in enumerate(self.devices):
            dev.ang_thresminx = value[idx]

    @property
    def ang_thresmaxx(self):
        """Maximum x angulation thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                max. x angulation threshold for each BPM.
        """
        return _np.array([b.ang_thresmaxx for b in self._devices])

    @ang_thresmaxx.setter
    def ang_thresmaxx(self, value):
        value = self._handle_thres_input(value)
        for idx, dev in enumerate(self.devices):
            dev.ang_thresmaxx = value[idx]

    @property
    def ang_thresminy(self):
        """Minimum y angulation thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                min. y angulation threshold for each BPM.
        """
        return _np.array([b.ang_thresminy for b in self._devices])

    @ang_thresminy.setter
    def ang_thresminy(self, value):
        value = self._handle_thres_input(value)
        for idx, dev in enumerate(self.devices):
            dev.ang_thresminy = value[idx]

    @property
    def ang_thresmaxy(self):
        """Maximum y angulation thresholds.

        Returns:
            thres (numpy.ndarray, 160):
                max. y angulation threshold for each BPM.
        """
        return _np.array([b.ang_thresmaxy for b in self._devices])

    @ang_thresmaxy.setter
    def ang_thresmaxy(self, value):
        value = self._handle_thres_input(value)
        for idx, dev in enumerate(self.devices):
            dev.ang_thresmaxy = value[idx]

    @property
    def ang_inst_lower(self):
        """Instantaneous angulation interlock set when either X or Y
        minimum thresholds are exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.ang_inst_lower for b in self._devices])

    @property
    def ang_inst_upper(self):
        """Instantaneous angulation interlock set when either X or Y
        maximum thresholds are exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.ang_inst_upper for b in self._devices])

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
    def ang_latch_lower(self):
        """Latch angulation interlock set when either X or Y
        minimum thresholds are exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.ang_latch_lower for b in self._devices])

    @property
    def ang_latch_upper(self):
        """Latch angulation interlock set when either X or Y
        maximum thresholds are exceeded.

        Returns:
            intlk (numpy.ndarray, 160): interlock status for each BPM.
        """
        return _np.array([b.ang_latch_upper for b in self._devices])

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
    def slow_orbit(self):
        """Slow orbit vectors.

        Returns:
            orbx (numpy.ndarray, 160): Horizontal Orbit.
            orby (numpy.ndarray, 160): Vertical Orbit.

        """
        orbx, orby = [], []
        for bpm in self._devices:
            orbx.append(bpm.posx)
            orby.append(bpm.posy)
        orbx = _np.array(orbx)
        orby = _np.array(orby)
        return orbx, orby

    @property
    def possum(self):
        """Sum vector, at Monit rate.

        Returns:
            possum (numpy.ndarray, 160): Sum vector, at Monit rate.
        """
        return _np.array([b.possum for b in self._devices])

    @property
    def position(self):
        """Position vectors.

        Position at each BPM is defined as:
            (pos BPM downstream + pos BPM upstream)/2

        Returns:
            posx (numpy.ndarray, 160): Horizontal Position.
            posy (numpy.ndarray, 160): Vertical Position.
        """
        orbx, orby = self.slow_orbit
        posx = _np.array(self.calc_intlk_metric(orbx, metric='pos'))
        posy = _np.array(self.calc_intlk_metric(orby, metric='pos'))
        return posx, posy

    @property
    def angulation(self):
        """Angulation vectors.

        Angulation at each BPM is defined as:
            (posição BPM downstream - posição BPM upstream)

        Returns:
            angx (numpy.ndarray, 160): Horizontal Angulation.
            angy (numpy.ndarray, 160): Vertical Angulation.
        """
        orbx, orby = self.slow_orbit
        angx = _np.array(self.calc_intlk_metric(orbx, metric='ang'))
        angy = _np.array(self.calc_intlk_metric(orby, metric='ang'))
        return angx, angy

    def _handle_thres_input(self, value):
        if isinstance(value, (int, float, _np.int_, _np.float_)):
            return [value, ] * len(self.BPM_NAMES)
        if len(value) != len(self.devices):
            raise ValueError(
                'the expected length is {0}, not {1}'.format(
                    len(self.devices), len(value)))
        return value
