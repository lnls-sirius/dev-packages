#!/usr/local/bin/python-sirius
"""Driver module."""

from pcaspy import Alarm as _Alarm, Severity as _Severity

from ...namesys import SiriusPVName
from ..app import App as _App
from ..pvs import ComputedPV as _ComputedPV

from .csdev import conv_dev_2_liname, Const as _Const
from .pvs import LIScalarDiffPV as _LIScalarDiffPV, \
    LIVecDiffPV as _LIVecDiffPV, \
    LIRFStatusPV as _LIRFStatusPV, \
    LIEGHVStatusPV as _LIEGHVStatusPV, \
    LIFilaPSStatusPV as _LIFilaPSStatusPV


class LIDiagApp(_App):
    """Main application responsible for updating DB."""

    def _create_computed_pvs(self, *args):
        # # RF devices
        for dev in _Const.RF_DEVICES:
            devname = SiriusPVName(self._prefix + dev)
            liname = conv_dev_2_liname(dev)

            # DiagAmpDiff-Mon
            pvs = [None]*2
            pvs[_LIScalarDiffPV.SP] = liname + ':SET_AMP'
            pvs[_LIScalarDiffPV.RB] = liname + ':GET_AMP'
            pvo = _ComputedPV(
                devname + ':DiagAmpDiff-Mon', _LIScalarDiffPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

            # DiagPhaseDiff-Mon
            pvs = [None]*2
            pvs[_LIScalarDiffPV.SP] = liname + ':SET_PHASE'
            pvs[_LIScalarDiffPV.RB] = liname + ':GET_PHASE'
            pvo = _ComputedPV(
                devname + ':DiagPhaseDiff-Mon', _LIScalarDiffPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

            # DiagIxQDiff-Mon
            pvs = [None]*4
            pvs[_LIVecDiffPV.I_SETT] = liname + ':GET_CH1_SETTING_I'
            pvs[_LIVecDiffPV.Q_SETT] = liname + ':GET_CH1_SETTING_Q'
            pvs[_LIVecDiffPV.I_DATA] = liname + ':GET_CH1_I'
            pvs[_LIVecDiffPV.Q_DATA] = liname + ':GET_CH1_Q'
            pvo = _ComputedPV(
                devname + ':DiagIxQDiff-Mon', _LIVecDiffPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

            # DiagStatus-Mon
            pvs = [None]*7
            pvs[_LIRFStatusPV.PV_STREAM] = liname + ':GET_STREAM'
            pvs[_LIRFStatusPV.PV_EXTTRG] = \
                liname + ':GET_EXTERNAL_TRIGGER_ENABLE'
            pvs[_LIRFStatusPV.PV_INTEGR] = liname + ':GET_INTEGRAL_ENABLE'
            pvs[_LIRFStatusPV.PV_FBMODE] = liname + ':GET_FB_MODE'
            pvs[_LIRFStatusPV.PV_AMPDIF] = devname + ':DiagAmpDiff-Mon'
            pvs[_LIRFStatusPV.PV_PHSDIF] = devname + ':DiagPhaseDiff-Mon'
            pvs[_LIRFStatusPV.PV_IXQDIF] = devname + ':DiagIxQDiff-Mon'
            pvo = _ComputedPV(
                devname + ':DiagStatus-Mon', _LIRFStatusPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

        # # Egun devices
        # HVPS
        devname = SiriusPVName(self._prefix + _Const.HVPS)
        liname = conv_dev_2_liname(devname)
        # DiagVoltDiff-Mon
        pvs = [None]*2
        pvs[_LIScalarDiffPV.SP] = liname + ':voltoutsoft'
        pvs[_LIScalarDiffPV.RB] = liname + ':voltinsoft'
        pvo = _ComputedPV(
            devname + ':DiagVoltDiff-Mon', _LIScalarDiffPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)
        # DiagStatus-Mon
        pvs = [None]*3
        pvs[_LIEGHVStatusPV.PV_SWITCH] = liname + ':swstatus'
        pvs[_LIEGHVStatusPV.PV_ENABLE] = liname + ':enstatus'
        pvs[_LIEGHVStatusPV.PV_VLTDIF] = devname + ':DiagVoltDiff-Mon'
        pvo = _ComputedPV(
            devname + ':DiagStatus-Mon', _LIEGHVStatusPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)

        # FilaPS
        devname = SiriusPVName(self._prefix + _Const.FILA)
        liname = conv_dev_2_liname(devname)
        # DiagCurrentDiff-Mon
        pvs = [None]*2
        pvs[_LIScalarDiffPV.SP] = liname + ':currentoutsoft'
        pvs[_LIScalarDiffPV.RB] = liname + ':currentinsoft'
        pvo = _ComputedPV(
            devname + ':DiagCurrentDiff-Mon', _LIScalarDiffPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)
        # DiagStatus-Mon
        pvs = [None]*2
        pvs[_LIFilaPSStatusPV.PV_SWITCH] = liname + ':swstatus'
        pvs[_LIFilaPSStatusPV.PV_CURDIF] = devname + ':DiagCurrentDiff-Mon'
        pvo = _ComputedPV(
            devname + ':DiagStatus-Mon', _LIFilaPSStatusPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)

        self._pvs_connected = {pv: False for pv in self.pvs}

    def _update_pvs(self):
        for pvo in self.pvs:
            if not pvo.connected:
                if self._pvs_connected[pvo]:
                    self.run_callbacks(
                        pvo.pvname, alarm=_Alarm.TIMEOUT_ALARM,
                        severity=_Severity.INVALID_ALARM,
                        field='status')
                self._pvs_connected[pvo] = False
                if 'DiagStatus' in pvo.pvname:
                    self.run_callbacks(pvo.pvname, value=pvo.value)
            else:
                if not self._pvs_connected[pvo]:
                    self.run_callbacks(
                        pvo.pvname, alarm=_Alarm.NO_ALARM,
                        severity=_Severity.NO_ALARM, field='status')
                self._pvs_connected[pvo] = True
                self.run_callbacks(pvo.pvname, value=pvo.value)
