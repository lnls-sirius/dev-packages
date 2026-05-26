"""Slit Control."""

# import inspect as _inspect
import time as _time
from types import SimpleNamespace as _SimpleNamespace

from ..device import Device as _Device
from ..device import _PVAccessor, _PVNames


class SlitBase(_PVAccessor, _Device):
    """Base Slit device."""

    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]
    _THRESHOLD_POS = 0.01  # [mm]
    _COUNT_LIM = 8
    _DELAY = 4  # [s]
    _TRIALS = 3

    # --- PVS ---
    PVS = _PVNames()

    PROPERTIES_DEFAULT = tuple(set(value for key, value in vars(PVS).items()))

    def __init__(self, devname=None, props2init="all", **kwargs):
        """Init."""
        # check if device exists
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init, **kwargs)


class CAXSlit(SlitBase):
    """."""

    class DEVICES:
        """Devices names."""

        CAX_A1 = "CAX:A:PP02"  # WBS1
        CAX_B1 = "CAX:B:PP01"  # WBS2

        ALL = (CAX_A1, CAX_B1)

    def __init__(self, devname=None, props2init="all", **kwargs):
        """Init."""
        if devname not in self.DEVICES.ALL:
            raise ValueError("Wrong value for devname")

        super().__init__(devname, props2init, **kwargs)

        self.PVS.TOP         = "A"
        self.PVS.TOP_SP      = "A.VAL"
        self.PVS.TOP_RB      = "A.VAL"   # That doesn't have a RB PV
        self.PVS.TOP_MON     = "A.RBV"   # RBV is not the pv of readback
        self.PVS.TOP_STOP    = "A.STOP"
        self.PVS.TOP_LOLM    = "A.LLM"
        self.PVS.TOP_HILM    = "A.HLM"
        self.PVS.TOP_ENBL    = "A.CNEN"
        self.PVS.TOP_DMVN    = "A.DMOV"
        self.PVS.TOP_MVN     = "A.MOVN"
        self.PVS.TOP_DESC    = "A.DESC"

        self.PVS.BOTTOM      = "B"
        self.PVS.BOTTOM_SP   = "B.VAL"
        self.PVS.BOTTOM_RB   = "B.VAL"   # That doesn't have a RB PV
        self.PVS.BOTTOM_MON  = "B.RBV"   # RBV is not the pv of readback
        self.PVS.BOTTOM_STOP = "B.STOP"
        self.PVS.BOTTOM_LOLM = "B.LLM"
        self.PVS.BOTTOM_HILM = "B.HLM"
        self.PVS.BOTTOM_DMVN = "B.DMOV"
        self.PVS.BOTTOM_MVN  = "B.MOVN"
        self.PVS.BOTTOM_ENBL = "B.CNEN"
        self.PVS.BOTTOM_DESC = "B.DESC"

        self.PVS.LEFT        = "C"
        self.PVS.LEFT_SP     = "C.VAL"
        self.PVS.LEFT_RB     = "C.VAL"   # That doesn't have a RB PV
        self.PVS.LEFT_MON    = "C.RBV"   # RBV is not the pv of readback
        self.PVS.LEFT_STOP   = "C.STOP"
        self.PVS.LEFT_LOLM   = "C.LLM"
        self.PVS.LEFT_HILM   = "C.HLM"
        self.PVS.LEFT_DMVN   = "C.DMOV"
        self.PVS.LEFT_MVN    = "C.MOVN"
        self.PVS.LEFT_ENBL   = "C.CNEN"
        self.PVS.LEFT_DESC   = "C.DESC"

        self.PVS.RIGHT       = "D"
        self.PVS.RIGHT_SP    = "D.VAL"
        self.PVS.RIGHT_RB    = "D.VAL"   # That doesn't have a RB PV
        self.PVS.RIGHT_MON   = "D.RBV"   # RBV is not the pv of readback
        self.PVS.RIGHT_STOP  = "D.STOP"
        self.PVS.RIGHT_LOLM  = "D.LLM"
        self.PVS.RIGHT_HILM  = "D.HLM"
        self.PVS.RIGHT_DMVN  = "D.DMOV"
        self.PVS.RIGHT_MVN   = "D.MOVN"
        self.PVS.RIGHT_ENBL  = "D.CNEN"
        self.PVS.RIGHT_DESC  = "D.DESC"

        self.PROPERTIES_DEFAULT = tuple(
            set(value for key, value in vars(self.PVS).items())
        )