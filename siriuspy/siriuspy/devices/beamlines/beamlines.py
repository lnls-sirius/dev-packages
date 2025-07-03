"""Beamlines Control."""

from ..device import DeviceSet as _DeviceSet
from . import CAXMirror, CAXSlit
from ..dvf import DVF, CAXDtc


class CAXCtrl(_DeviceSet):
    """."""

    class DEVICES:
        """."""

        CAX = "CAX"

        ALL = (CAX,)

    def __init__(self, devname=None, props2init="all", **kwargs):
        """."""
        if devname is None:
            devname = self.DEVICES.CAX
        if devname not in self.DEVICES.ALL:
            raise ValueError("Wrong value for devname")

        self.mirror = CAXMirror(
            devname=CAXMirror.DEVICES.CAX_FOE, props2init=props2init, **kwargs
        )
        self.slit_A1 = CAXSlit(
            devname=CAXSlit.DEVICES.CAX_A1, props2init=props2init, **kwargs
        )
        self.dvf_A1 = DVF(
            devname=DVF.DEVICES.CAX_A1, props2init=props2init, **kwargs
        )
        self.slit_B1 = CAXSlit(
            devname=CAXSlit.DEVICES.CAX_B1, props2init=props2init, **kwargs
        )
        self.dvf_B1 = CAXDtc(
            devname=CAXDtc.DEVICES.CAX_B1, props2init=props2init
        )

        devs = [
            self.mirror,
            self.slit_A1,
            self.dvf_A1,
            self.slit_B1,
            self.dvf_B1,
        ]

        super().__init__(devices=devs, devname=devname, **kwargs)


class PNRCtrl(_DeviceSet):
    """."""

    class DEVICES:
        """."""

        PNR = "PNR"

        ALL = (PNR,)

    def __init__(self, devname=None, prop2init="all"):
        """."""
        if devname is None:
            devname = self.DEVICES.PNR
        if devname not in self.DEVICES.ALL:
            raise ValueError("Wrong value for devname")

        self.dvf_A2 = DVF(devname=DVF.DEVICES.PNR_A2, props2init=prop2init)

        devs = [self.dvf_A2]

        super().__init__(devices=devs, devname=devname)


class EMACtrl(_DeviceSet):
    """."""

    class DEVICES:
        """."""

        EMA = "EMA"

        ALL = (EMA,)

    def __init__(self, devname=None, prop2init="all"):
        """."""
        if devname is None:
            devname = self.DEVICES.EMA
        if devname not in self.DEVICES.ALL:
            raise ValueError("Wrong value for devname")

        self.dvf_A2 = DVF(devname=DVF.DEVICES.EMA_A2, props2init=prop2init)

        devs = [self.dvf_A2]

        super().__init__(devices=devs, devname=devname)
