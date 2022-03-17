"""Orbit Interlock devices."""

import numpy as _np

from ..search import BPMSearch as _BPMSearch
from ..util import ClassProperty as _classproperty
from .device import Device as _Device, Devices as _Devices


class BaseOrbitIntlk:
    """Base BPM Orbit Interlock Info."""

    CONV_NM2UM = 1e-3  # [nm] --> [um]

    DOWN_2_UP = {
        'M1': 'M2',
        'C1-1': 'C1-2',
        'C2': 'C3-1',
        'C3-2': 'C4',
    }
    UP_2_DOWN = {val: key for key, val in DOWN_2_UP.items()}

    __BPM_NAMES = None
    __BPM_NICKNAMES = None
    __BPM_POS = None
    __BPM_DOWNSTREAM = None
    __BPM_UPSTREAM = None

    @_classproperty
    def BPM_NAMES(cls):
        """BPM names."""
        if cls.__BPM_NAMES is None:
            cls.__BPM_NAMES = _BPMSearch.get_names({'sec': 'SI', 'dev': 'BPM'})
            cls.__BPM_NICKNAMES = _BPMSearch.get_nicknames(cls.__BPM_NAMES)
            cls.__BPM_POS = _BPMSearch.get_positions(cls.__BPM_NAMES)

            def _parse_nick_down_up(name, nick):
                if '-' in nick:
                    sub, idx = nick.split('-')
                else:
                    sub, idx = nick, ''
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

    def get_intlk_metric(self, posarray, operation='', metric=''):
        """Return interlock metric, translation or angulation."""
        if not operation:
            if not metric:
                raise ValueError(
                    'either the operation or the metric is required')
            operation = 'mean' if 'trans' in metric.lower() else 'diff'

        data_values = list()
        for bpm in BaseOrbitIntlk.BPM_NAMES:
            down, upn = BaseOrbitIntlk.get_down_up_bpms(bpm)
            if down:
                dval = posarray[BaseOrbitIntlk.BPM_NAMES.index(down)]
                uval = posarray[BaseOrbitIntlk.BPM_NAMES.index(upn)]
                func = self._oper[operation]
                val = func(dval, uval)
            else:
                val = 0
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
        # General
        # +++++++
        # General interlock enable:
        'IntlkEn-Sel', 'IntlkEn-Sts',
        # General interlock clear:
        'IntlkClr-Sel',
        # Minimum sum threshold enable:
        # Habilita interlock de óbita apenas quando threshold da soma
        # ultrapassar o valor em "IntlkLmtMinSum-SP"
        'IntlkMinSumEn-Sel', 'IntlkMinSumEn-Sts',
        # Minimum sum threshold (em contagens da Soma da taxa Monit1):
        'IntlkLmtMinSum-SP', 'IntlkLmtMinSum-RB',
        # Status Instantâneo:
        # Interlock instântaneo, dificilmente será detectado com
        # a implementação atual do gateware
        'Intlk-Mon',
        # Latch do interlock, limpo apenas acionando-se a PV "Clr"
        # correspondente
        'IntlkLtc-Mon',
        # ===============================================================
        # Translation (interlock de translação)
        # +++++++++++++++++++++++++++++++++++++
        # ***************************************************************
        # Condição para interlock de translação:
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
        # Translation interlock enable:
        'IntlkTransEn-Sel', 'IntlkTransEn-Sts',
        # Translation interlock clear:
        'IntlkTransClr-Sel',
        # Thresholds (em nm da taxa Monit1):
        'IntlkLmtTransMaxX-SP', 'IntlkLmtTransMaxX-RB',
        'IntlkLmtTransMinX-SP', 'IntlkLmtTransMinX-RB',
        'IntlkLmtTransMaxY-SP', 'IntlkLmtTransMaxY-RB',
        'IntlkLmtTransMinY-SP', 'IntlkLmtTransMinY-RB',
        # Status Instantâneo:
        #   XouY mascarado pelo "Enable"
        'IntlkTransSmaller-Mon', 'IntlkTransBigger-Mon',
        # the ones bellow are not masked by "Enable"
        'IntlkTransSmallerAny-Mon', 'IntlkTransBiggerAny-Mon',  # X ou Y
        'IntlkTransSmallerX-Mon', 'IntlkTransBiggerX-Mon',  # X
        'IntlkTransSmallerY-Mon', 'IntlkTransBiggerY-Mon',  # Y
        # limpo apenas acionando-se a PV "Clr" correspondente
        'IntlkTransSmallerLtc-Mon', 'IntlkTransBiggerLtc-Mon',
        'IntlkTransSmallerLtcX-Mon', 'IntlkTransBiggerLtcX-Mon',
        'IntlkTransSmallerLtcY-Mon', 'IntlkTransBiggerLtcY-Mon',
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
        # Anglation interlock enable:
        'IntlkAngEn-Sel', 'IntlkAngEn-Sts',
        # Anglation interlock clear:
        'IntlkAngClr-Sel',
        # Thresholds (em rad.nm da taxa Monit1).
        #  Thresholds devem ser calculados como ângulo (em rad)
        #  entre os 2 BPMs adjacentes * distância (em nm) entre eles):
        'IntlkLmtAngMaxX-SP', 'IntlkLmtAngMaxX-RB',
        'IntlkLmtAngMinX-SP', 'IntlkLmtAngMinX-RB',
        'IntlkLmtAngMaxY-SP', 'IntlkLmtAngMaxY-RB',
        'IntlkLmtAngMinY-SP', 'IntlkLmtAngMinY-RB',
        # Status Instantâneo:
        #  X ou Y mascarado pelo "Enable"
        'IntlkAngSmaller-Mon', 'IntlkAngBigger-Mon',
        # the ones bellow are not masked by "Enable"
        'IntlkAngSmallerAny-Mon', 'IntlkAngBiggerAny-Mon',  # X ou Y
        'IntlkAngSmallerX-Mon', 'IntlkAngBiggerX-Mon',  # X
        'IntlkAngSmallerY-Mon', 'IntlkAngBiggerY-Mon',  # Y
        # limpo apenas acionando-se a PV "Clr" correspondente
        'IntlkAngSmallerLtc-Mon', 'IntlkAngBiggerLtc-Mon',
        'IntlkAngSmallerLtcX-Mon', 'IntlkAngBiggerLtcX-Mon',
        'IntlkAngSmallerLtcY-Mon', 'IntlkAngBiggerLtcY-Mon',
        # ============================================================
        )

    def __init__(self, devname):
        """Init."""
        # call base class constructor
        BaseOrbitIntlk.__init__(self)
        if devname not in self.BPM_NAMES:
            raise ValueError(devname + ' is no a valid BPM or PBPM name.')
        _Device.__init__(self, devname, properties=BPMOrbitIntlk._properties)

    @property
    def pair_down_up_bpms(self):
        """Return pair of downstream and upstream BPM names."""
        return self.get_down_up_bpms(self.devname)

    # --- general interlock ---

    @property
    def enable(self):
        """General interlock enable."""
        return self['IntlkEn-Sts']

    @enable.setter
    def enable(self, value):
        self['IntlkEn-Sel'] = int(value)

    def cmd_reset(self):
        """General interlock clear."""
        self['IntlkClr-Sel'] = 1
        return True

    @property
    def interlock_inst(self):
        """Instantaneous general interlock."""
        return self['Intlk-Mon']

    @property
    def interlock_latch(self):
        """Latch general interlock."""
        return self['IntlkLtc-Mon']

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
        """Minimum sum threshold [sum count, Monit1 rate]."""
        return self['IntlkLmtMinSum-RB']

    @minsumthres.setter
    def minsumthres(self, value):
        self['IntlkLmtMinSum-SP'] = int(value)

    # --- translation interlock ---

    @property
    def trans_enable(self):
        """Translation interlock enable."""
        return self['IntlkTransEn-Sts']

    @trans_enable.setter
    def trans_enable(self, value):
        self['IntlkTransEn-Sel'] = int(value)

    def cmd_reset_trans(self):
        """Translation interlock clear."""
        self['IntlkTransClr-Sel'] = 1
        return True

    @property
    def trans_thresminx(self):
        """Minimum X translation threshold."""
        return self['IntlkLmtTransMinX-RB']

    @trans_thresminx.setter
    def trans_thresminx(self, value):
        self['IntlkLmtTransMinX-SP'] = value

    @property
    def trans_thresmaxx(self):
        """Maximum X translation threshold."""
        return self['IntlkLmtTransMaxX-RB']

    @trans_thresmaxx.setter
    def trans_thresmaxx(self, value):
        self['IntlkLmtTransMaxX-SP'] = value

    @property
    def trans_thresminy(self):
        """Minimum Y translation threshold."""
        return self['IntlkLmtTransMinY-RB']

    @trans_thresminy.setter
    def trans_thresminy(self, value):
        self['IntlkLmtTransMinY-SP'] = value

    @property
    def trans_thresmaxy(self):
        """Maximum Y translation threshold."""
        return self['IntlkLmtTransMaxY-RB']

    @trans_thresmaxy.setter
    def trans_thresmaxy(self, value):
        self['IntlkLmtTransMaxY-SP'] = value

    @property
    def trans_interlock_mask_smaller(self):
        """
        Instantaneous translation interlock set when either X or Y
        minimum thresholds are exceeded, masked by general enable.
        """
        return self['IntlkTransSmaller-Mon']

    @property
    def trans_interlock_mask_bigger(self):
        """
        Instantaneous translation interlock set when either X or Y
        maximum thresholds are exceeded, masked by general enable.
        """
        return self['IntlkTransBigger-Mon']

    @property
    def trans_interlock_inst_smaller(self):
        """
        Instantaneous translation interlock set when either X or Y
        minimum thresholds are exceeded.
        """
        return self['IntlkTransSmallerAny-Mon']

    @property
    def trans_interlock_inst_bigger(self):
        """
        Instantaneous translation interlock set when either X or Y
        maximum thresholds are exceeded.
        """
        return self['IntlkTransBiggerAny-Mon']

    @property
    def trans_interlock_inst_smaller_x(self):
        """
        Instantaneous translation interlock set when X
        minimum threshold is exceeded.
        """
        return self['IntlkTransSmallerX-Mon']

    @property
    def trans_interlock_inst_bigger_x(self):
        """
        Instantaneous translation interlock set when X
        maximum threshold is exceeded.
        """
        return self['IntlkTransBiggerX-Mon']

    @property
    def trans_interlock_inst_smaller_y(self):
        """
        Instantaneous translation interlock set when Y
        minimum threshold is exceeded.
        """
        return self['IntlkTransSmallerY-Mon']

    @property
    def trans_interlock_inst_bigger_y(self):
        """
        Instantaneous translation interlock set when Y
        maximum threshold is exceeded.
        """
        return self['IntlkTransBiggerY-Mon']

    @property
    def trans_interlock_latch_smaller(self):
        """
        Latch translation interlock set when either X or Y
        minimum thresholds are exceeded.
        """
        return self['IntlkTransSmallerLtc-Mon']

    @property
    def trans_interlock_latch_bigger(self):
        """
        Latch translation interlock set when either X or Y
        maximum thresholds are exceeded.
        """
        return self['IntlkTransBiggerLtc-Mon']

    @property
    def trans_interlock_latch_smaller_x(self):
        """
        Latch translation interlock set when X
        minimum threshold is exceeded.
        """
        return self['IntlkTransSmallerLtcX-Mon']

    @property
    def trans_interlock_latch_bigger_x(self):
        """
        Latch translation interlock set when X
        maximum threshold is exceeded.
        """
        return self['IntlkTransBiggerLtcX-Mon']

    @property
    def trans_interlock_latch_smaller_y(self):
        """
        Latch translation interlock set when Y
        minimum threshold is exceeded.
        """
        return self['IntlkTransSmallerLtcY-Mon']

    @property
    def trans_interlock_latch_bigger_y(self):
        """
        Latch translation interlock set when Y
        maximum threshold is exceeded.
        """
        return self['IntlkTransBiggerLtcY-Mon']

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
        self['IntlkAngClr-Sel'] = 1
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
    def ang_interlock_mask_smaller(self):
        """
        Instantaneous angulation interlock set when either X or Y
        minimum thresholds are exceeded, masked by general enable.
        """
        return self['IntlkAngSmaller-Mon']

    @property
    def ang_interlock_mask_bigger(self):
        """
        Instantaneous angulation interlock set when either X or Y
        maximum thresholds are exceeded, masked by general enable.
        """
        return self['IntlkAngBigger-Mon']

    @property
    def ang_interlock_inst_smaller(self):
        """
        Instantaneous angulation interlock set when either X or Y
        minimum thresholds are exceeded.
        """
        return self['IntlkAngSmallerAny-Mon']

    @property
    def ang_interlock_inst_bigger(self):
        """
        Instantaneous angulation interlock set when either X or Y
        maximum thresholds are exceeded.
        """
        return self['IntlkAngBiggerAny-Mon']

    @property
    def ang_interlock_inst_smaller_x(self):
        """
        Instantaneous angulation interlock set when X
        minimum threshold is exceeded.
        """
        return self['IntlkAngSmallerX-Mon']

    @property
    def ang_interlock_inst_bigger_x(self):
        """
        Instantaneous angulation interlock set when X
        maximum threshold is exceeded.
        """
        return self['IntlkAngBiggerX-Mon']

    @property
    def ang_interlock_inst_smaller_y(self):
        """
        Instantaneous angulation interlock set when Y
        minimum threshold is exceeded.
        """
        return self['IntlkAngSmallerY-Mon']

    @property
    def ang_interlock_inst_bigger_y(self):
        """
        Instantaneous angulation interlock set when Y
        maximum threshold is exceeded.
        """
        return self['IntlkAngBiggerY-Mon']

    @property
    def ang_interlock_latch_smaller(self):
        """
        Latch angulation interlock set when either X or Y
        minimum thresholds are exceeded.
        """
        return self['IntlkAngSmallerLtc-Mon']

    @property
    def ang_interlock_latch_bigger(self):
        """
        Latch angulation interlock set when either X or Y
        maximum thresholds are exceeded.
        """
        return self['IntlkAngBiggerLtc-Mon']

    @property
    def ang_interlock_latch_smaller_x(self):
        """
        Latch angulation interlock set when X
        minimum threshold is exceeded.
        """
        return self['IntlkAngSmallerLtcX-Mon']

    @property
    def ang_interlock_latch_bigger_x(self):
        """
        Latch angulation interlock set when X
        maximum threshold is exceeded.
        """
        return self['IntlkAngBiggerLtcX-Mon']

    @property
    def ang_interlock_latch_smaller_y(self):
        """
        Latch angulation interlock set when Y
        minimum threshold is exceeded.
        """
        return self['IntlkAngSmallerLtcY-Mon']

    @property
    def ang_interlock_latch_bigger_y(self):
        """
        Latch angulation interlock set when Y
        maximum threshold is exceeded.
        """
        return self['IntlkAngBiggerLtcY-Mon']


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

    def cmd_reset(self):
        """Reset all BPM general interlock."""
        for dev in self.devices:
            dev.cmd_reset()
        return True

    def cmd_reset_trans(self):
        """Reset all BPM translation interlock."""
        for dev in self.devices:
            dev.cmd_reset_trans()
        return True

    def cmd_reset_ang(self):
        """Reset all BPM angulation interlock."""
        for dev in self.devices:
            dev.cmd_reset_ang()
        return True
