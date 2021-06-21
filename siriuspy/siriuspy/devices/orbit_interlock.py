"""."""

import numpy as _np

from .device import Device as _Device
from ..search import BPMSearch as _BPMSearch


class BPMInterlock(_Device):
    """BPM Device"""

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
        #   (posição BPM downstream + posição BPM upstream)/2 > threshold
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
        'IntlkTransSmallerX-Mon', 'IntlkTransBiggerX-Mon',  # X
        'IntlkTransSmallerY-Mon', 'IntlkTransBiggerY-Mon',  # Y
        'IntlkTransSmallerAny-Mon', 'IntlkTransBiggerAny-Mon',  # X ou Y
        # limpo apenas acionando-se a PV "Clr" correspondente
        'IntlkTransSmallerLtc-Mon', 'IntlkTransBiggerLtc-Mon',
        'IntlkTransSmallerLtcX-Mon', 'IntlkTransBiggerLtcX-Mon',
        'IntlkTransSmallerLtcY-Mon', 'IntlkTransBiggerLtcY-Mon',
        # =============================================================
        # Angular (interlock de ângulo)
        # +++++++++++++++++++++++++++++
        # *************************************************************
        # Condição para interlock de ângulo:
        #   (posição BPM downstream - posição BPM upstream) > threshold
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
        # Thresholds (em rad.nm da taxa Monit1.
        #  Thresholds devem ser calculados como ângulo (em rad)
        #  entre os 2 BPMs adjacentes * distância (em nm) entre eles):
        'IntlkLmtAngMaxX-SP', 'IntlkLmtAngMaxX-RB',
        'IntlkLmtAngMinX-SP', 'IntlkLmtAngMinX-RB',
        'IntlkLmtAngMaxY-SP', 'IntlkLmtAngMaxY-RB',
        'IntlkLmtAngMinY-SP', 'IntlkLmtAngMinY-RB',
        # Status Instantâneo:
        #  X ou Y mascarado pelo "Enable"
        'IntlkAngSmaller-Mon', 'IntlkAngBigger-Mon',
        'IntlkAngSmallerAny-Mon', 'IntlkAngBiggerAny-Mon',  # X ou Y
        'IntlkAngSmallerX-Mon', 'IntlkAngBiggerX-Mon',  # X
        'IntlkAngSmallerY-Mon', 'IntlkAngBiggerY-Mon',  # Y
        # limpo apenas acionando-se a PV "Clr" correspondente
        'IntlkAngSmallerLtc-Mon', 'IntlkAngBiggerLtc-Mon',
        'IntlkAngSmallerLtcX-Mon', 'IntlkAngBiggerLtcX-Mon',
        'IntlkAngSmallerLtcY-Mon', 'IntlkAngBiggerLtcY-Mon',
        # ============================================================
        )

    CONV_NM2UM = 1e-3  # [nm] --> [um]

    def __init__(self, devname):
        """."""
        # call base class constructor
        if not _BPMSearch.is_valid_devname(devname):
            raise ValueError(devname + ' is no a valid BPM or PBPM name.')
        super().__init__(devname, properties=BPMInterlock._properties)

    @property
    def enabled(self):
        """.General interlock enable."""
        return self['IntlkEn-Sts']

    @enabled.setter
    def enabled(self, value):
        self['IntlkEn-Sel'] = int(value)

    def cmd_reset(self):
        """General interlock clear."""
        self['IntlkClr-Sel'] = 1
