#!/usr/local/bin/python-sirius
"""Driver module."""

from pcaspy import Driver as _Driver
from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

from siriuspy.epics.computed_pv import ComputedPV as _ComputedPV
from siriuspy.thread import QueueThread as _QueueThread
from siriuspy.epics.psdiag_pv import PSStatusPV as _PSStatusPV
from siriuspy.epics.psdiag_pv import PSDiffPV as _PSDiffPV


class PSDiagDriver(_Driver):
    """Driver responsible for updating DB."""

    def __init__(self, prefix, psnames):
        """Create Computed PVs."""
        super().__init__()
        self._psnames = psnames
        self._queue = _QueueThread()
        self._prefix = prefix
        self.pvs = list()
        self._create_computed_pvs()

    def _create_computed_pvs(self):
        for psname in self._psnames:
            devname = self._prefix + psname
            magname = self._get_magname(psname)
            # DiagCurrentDiff-Mon
            pvs = [None, None]
            pvs[_PSDiffPV.CURRT_SP] = devname + ':Current-SP'
            pvs[_PSDiffPV.CURRT_MON] = devname + ':Current-Mon'
            pv = _ComputedPV(psname + ':DiagCurrentDiff-Mon',
                             _PSDiffPV(),
                             self._queue,
                             pvs,
                             monitor=False)
            self.pvs.append(pv)
            # DiagStatus-Mon
            pvs = [None, None, None, None, None, None]
            pvs[_PSStatusPV.OPMODE_SEL] = devname + ':OpMode-Sel'
            pvs[_PSStatusPV.OPMODE_STS] = devname + ':OpMode-Sts'
            pvs[_PSStatusPV.CURRT_DIFF] = devname + ':DiagCurrentDiff-Mon'
            pvs[_PSStatusPV.MAOPMD_SEL] = magname + ':OpMode-Sel'
            pvs[_PSStatusPV.INTLK_SOFT] = devname + ':IntlkSoft-Mon'
            pvs[_PSStatusPV.INTLK_HARD] = devname + ':IntlkHard-Mon'
            # TODO: Add other interlocks for PS types that have them
            pv = _ComputedPV(psname + ':DiagStatus-Mon',
                             _PSStatusPV(),
                             self._queue,
                             pvs,
                             monitor=False)
            self.pvs.append(pv)

    def _get_magname(self, psname):
        if psname in ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2'):
            return self._prefix + 'BO-Fam:MA-B'
        elif psname in ('SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2'):
            return self._prefix + 'SI-Fam:MA-B1B2'
        else:
            return self._prefix + psname.replace(':PS-', ':MA-')

    def read(self, reason):
        """Read method."""
        if 'DiagVersion-Cte' in reason:
            for pv in self.pvs:
                # pv.get()
                connected = False
                if not pv.connected:
                    connected = False
                    self.setParamStatus(pv.pvname,
                                        _Alarm.TIMEOUT_ALARM,
                                        _Severity.INVALID_ALARM)
                    if 'DiagStatus' in pv.pvname:
                        self.setParam(pv.pvname, pv.value)
                else:
                    if not connected:
                        self.setParamStatus(pv.pvname,
                                            _Alarm.NO_ALARM,
                                            _Severity.NO_ALARM)
                    connected = True
                    self.setParam(pv.pvname, pv.value)
            self.updatePVs()
        return super().read(reason)
