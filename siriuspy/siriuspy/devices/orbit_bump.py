"""Orbit bump device."""

import time as _time
import numpy as _np

from ..clientconfigdb import ConfigDBClient
from .device import DeviceSet as _DeviceSet
from .sofb import SOFB


class OrbBump(_DeviceSet):
    """Orbit bump device."""

    TIMEOUT = 10
    NR_BPM = 4
    MAX_TOL_ORB = (
        50  # [um] Max allowed orbit correction residue for unsuccessful bump
    )
    NR_ITERS = (
        20  # Max number of iterations to wait for orbit correction convergence
    )

    class DEVICES:
        """Devices names."""

        SI = "SI-Glob:AP-SOFB"
        ALL = (SI,)

    def __init__(self, devname=None, props2init="all"):
        """Init."""
        if devname is None:
            devname = self.DEVICES.SI
        if devname not in self.DEVICES.ALL:
            raise ValueError("Wrong value for devname")
        self.sofb = SOFB(devname, props2init=props2init)
        self.bpmxenbl_init = self.sofb.bpmxenbl.copy()
        self.bpmyenbl_init = self.sofb.bpmyenbl.copy()
        clt = ConfigDBClient(config_type="si_orbit")
        self.ref_orb = clt.get_config_value("ref_orb")
        super().__init__(devices=[self.sofb], devname=devname)

    def _get_rms(self, refx, refy, idx):
        dorbx = self.sofb.orbx - refx
        dorby = self.sofb.orby - refy
        dorbx = dorbx[idx]
        dorby = dorby[idx]
        return _np.hstack([dorbx, dorby]).std()

    def implement_bump(
        self,
        subsec=None,
        refx=None,
        refy=None,
        agx=0,
        agy=0,
        psx=0,
        psy=0,
        tol_orb=1,
        bpmxenbl_sofb=None,
        bpmyenbl_sofb=None,
    ):
        """Implement orbit bump at given subsection.

        Args:
            subsec (str, optional): Subsection where to apply bump.
                Defaults to '09SA'.
            refx (numpy.ndarray, optional): Horizontal reference orbit.
                Defaults to None, in which case it reads from ConfigDB.
            refy (numpy.ndarray, optional): Vertical reference orbit.
                Defaults to None, in which case it reads from ConfigDB.
            agx (float, optional): Horizontal angle bump amplitude.
                Defaults to 0.
            agy (float, optional): Vertical angle bump amplitude.
                Defaults to 0.
            psx (float, optional): Horizontal position bump amplitude.
                Defaults to 0.
            psy (float, optional): Vertical position bump amplitude.
                Defaults to 0.
            tol_orb (float, optional): Tolerance for orbit correction
                residue in um. Defaults to 1.
            bpmxenbl_sofb (numpy.ndarray, optional): Horizontal BPM
                enable list. Defaults to None, in which case the
                current SOFB value is used.
            bpmyenbl_sofb (numpy.ndarray, optional): Vertical BPM
                enable list. Defaults to None, in which case the
                current SOFB value is used.

        Raises:
            ValueError: When orbit correction fails.
        """
        if subsec is None:
            raise ValueError("subsec must be specified.")
        if bpmxenbl_sofb is None:
            bpmxenbl_sofb = self.bpmxenbl_init.copy()
        if bpmyenbl_sofb is None:
            bpmyenbl_sofb = self.bpmyenbl_init.copy()

        if refx is None or refy is None:
            refx = _np.array(self.ref_orb["x"])
            refy = _np.array(self.ref_orb["y"])

        orbx, orby = self.sofb.si_calculate_bumps(
            refx, refy, subsec=subsec, agx=agx, agy=agy, psx=psx, psy=psy
        )

        max_dorbx = _np.max(_np.abs(orbx - self.sofb.refx))
        max_dorby = _np.max(_np.abs(orby - self.sofb.refy))

        if max(max_dorbx, max_dorby) > 10:
            print(f"Dorb max: {max(max_dorbx, max_dorby)} um")

        dummy, _ = self.sofb.si_calculate_bumps(
            refx, refy, subsec=subsec, agx=10
        )
        idx = ~_np.isclose(dummy, refx)
        strt = idx.nonzero()[0][0]

        self.sofb.refx = orbx
        self.sofb.refy = orby

        nr_bpms = self.NR_BPM
        enbl = _np.zeros(bpmxenbl_sofb.size, dtype=bool)
        enbl[strt - nr_bpms : strt] = True
        enbl[strt + 2 : strt + 2 + nr_bpms] = True

        xenbl_sofb = bpmxenbl_sofb
        yenbl_sofb = bpmyenbl_sofb
        xenbl_sofb[enbl] = False
        yenbl_sofb[enbl] = False
        self.sofb.bpmxenbl = xenbl_sofb
        self.sofb.bpmyenbl = yenbl_sofb

        rms_residue = tol_orb + 1

        for i in range(self.NR_ITERS):
            rms_residue = self._get_rms(orbx, orby, idx)
            print(f"    rms_residue = {rms_residue:.3f} um")
            if rms_residue <= tol_orb:
                break
            if rms_residue > self.MAX_TOL_ORB:
                raise ValueError("Could not correct orbit.")
            _time.sleep(1.5)
        else:
            raise ValueError("Could not correct orbit.")

    def restore_sofb_reforb(self, bpmxenbl=None, bpmyenbl=None):
        """Restore SOFB reference orbit and BPM enable lists.

        Args:
            bpmxenbl_sofb (numpy.ndarray, optional): Horizontal BPM
                enable list. Defaults to None, in which case the
                current SOFB value is used.
            bpmyenbl_sofb (numpy.ndarray, optional): Vertical BPM
                enable list. Defaults to None, in which case the
                current SOFB value is used.
        """
        if bpmxenbl is None:
            bpmxenbl = self.bpmxenbl_init.copy()
        if bpmyenbl is None:
            bpmyenbl = self.bpmyenbl_init.copy()

        refx = _np.array(self.ref_orb["x"])
        refy = _np.array(self.ref_orb["y"])
        self.sofb.refx = refx
        self.sofb.refy = refy
        self.sofb.bpmxenbl = bpmxenbl
        self.sofb.bpmyenbl = bpmyenbl
