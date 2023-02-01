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
    LIPUStatusPV as _LIPUStatusPV, \
    LIEGHVStatusPV as _LIEGHVStatusPV, \
    LIFilaPSStatusPV as _LIFilaPSStatusPV


class LIDiagApp(_App):
    """Main application responsible for updating DB."""

    def _create_computed_pvs(self, *args):
        pref = self._prefix + ('-' if self._prefix else '')

        # # RF devices
        for dev in _Const.RF_DEVICES:
            devname = SiriusPVName(dev)
            prefliname = pref + conv_dev_2_liname(dev)
            prefname = devname.substitute(prefix=self._prefix)

            # DiagAmpDiff-Mon
            pvs = [None]*2
            pvs[_LIScalarDiffPV.SP] = prefliname + ':SET_AMP'
            pvs[_LIScalarDiffPV.RB] = prefliname + ':GET_AMP'
            pvo = _ComputedPV(
                devname + ':DiagAmpDiff-Mon', _LIScalarDiffPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

            # DiagPhaseDiff-Mon
            pvs = [None]*2
            pvs[_LIScalarDiffPV.SP] = prefliname + ':SET_PHASE'
            pvs[_LIScalarDiffPV.RB] = prefliname + ':GET_PHASE'
            pvo = _ComputedPV(
                devname + ':DiagPhaseDiff-Mon', _LIScalarDiffPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

            # DiagIxQDiff-Mon
            pvs = [None]*4
            pvs[_LIVecDiffPV.I_SETT] = prefliname + ':GET_CH1_SETTING_I'
            pvs[_LIVecDiffPV.Q_SETT] = prefliname + ':GET_CH1_SETTING_Q'
            pvs[_LIVecDiffPV.I_DATA] = prefliname + ':GET_CH1_I'
            pvs[_LIVecDiffPV.Q_DATA] = prefliname + ':GET_CH1_Q'
            pvo = _ComputedPV(
                devname + ':DiagIxQDiff-Mon', _LIVecDiffPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

            # DiagStatus-Mon
            pvs = [None]*7
            pvs[_LIRFStatusPV.PV_STREAM] = prefliname + ':GET_STREAM'
            pvs[_LIRFStatusPV.PV_EXTTRG] = \
                prefliname + ':GET_EXTERNAL_TRIGGER_ENABLE'
            pvs[_LIRFStatusPV.PV_INTEGR] = prefliname + ':GET_INTEGRAL_ENABLE'
            pvs[_LIRFStatusPV.PV_FBMODE] = prefliname + ':GET_FB_MODE'
            pvs[_LIRFStatusPV.PV_AMPDIF] = prefname + ':DiagAmpDiff-Mon'
            pvs[_LIRFStatusPV.PV_PHSDIF] = prefname + ':DiagPhaseDiff-Mon'
            pvs[_LIRFStatusPV.PV_IXQDIF] = prefname + ':DiagIxQDiff-Mon'
            pvo = _ComputedPV(
                devname + ':DiagStatus-Mon', _LIRFStatusPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

        # # PU devices
        for dev in _Const.PU_DEVICES:
            devname = SiriusPVName(dev)
            prefliname = pref + conv_dev_2_liname(dev)

            # DiagVoltageDiff-Mon
            pvs = [None]*2
            pvs[_LIScalarDiffPV.SP] = prefliname + ':WRITE_V'
            pvs[_LIScalarDiffPV.RB] = prefliname + ':READV'
            pvo = _ComputedPV(
                devname + ':DiagVoltageDiff-Mon', _LIScalarDiffPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

            # DiagCurrentDiff-Mon
            pvs = [None]*2
            pvs[_LIScalarDiffPV.SP] = prefliname + ':WRITE_I'
            pvs[_LIScalarDiffPV.RB] = prefliname + ':READI'
            pvo = _ComputedPV(
                devname + ':DiagCurrentDiff-Mon', _LIScalarDiffPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

            # DiagStatus-Mon
            pvs = [None]*19
            pvs[_LIPUStatusPV.PV.CHARGES] = prefliname + ':CHARGE'
            pvs[_LIPUStatusPV.PV.TRIGOUT] = prefliname + ':TRIGOUT'
            pvs[_LIPUStatusPV.PV.RUNSTOP] = prefliname + ':Run/Stop'
            pvs[_LIPUStatusPV.PV.PREHEAT] = prefliname + ':PreHeat'
            pvs[_LIPUStatusPV.PV.CHRALLW] = prefliname + ':Charge_Allowed'
            pvs[_LIPUStatusPV.PV.TRGALLW] = prefliname + ':TrigOut_Allowed'
            pvs[_LIPUStatusPV.PV.EMRSTOP] = prefliname + ':Emer_Stop'
            pvs[_LIPUStatusPV.PV.CPS_ALL] = prefliname + ':CPS_ALL'
            pvs[_LIPUStatusPV.PV.THYHEAT] = prefliname + ':Thy_Heat'
            pvs[_LIPUStatusPV.PV.KLYHEAT] = prefliname + ':Kly_Heat'
            pvs[_LIPUStatusPV.PV.LVRDYOK] = prefliname + ':LV_Rdy_OK'
            pvs[_LIPUStatusPV.PV.HVRDYOK] = prefliname + ':HV_Rdy_OK'
            pvs[_LIPUStatusPV.PV.TRRDYOK] = prefliname + ':TRIG_Rdy_OK'
            pvs[_LIPUStatusPV.PV.SELFFLT] = prefliname + ':MOD_Self_Fault'
            pvs[_LIPUStatusPV.PV.SYS_RDY] = prefliname + ':MOD_Sys_Ready'
            pvs[_LIPUStatusPV.PV.TRGNORM] = prefliname + ':TRIG_Norm'
            pvs[_LIPUStatusPV.PV.PLSCURR] = prefliname + ':Pulse_Current'
            pvs[_LIPUStatusPV.PV.VLTDIFF] = prefliname + ':DiagVoltageDiff-Mon'
            pvs[_LIPUStatusPV.PV.CRRDIFF] = prefliname + ':DiagCurrentDiff-Mon'
            pvo = _ComputedPV(
                devname + ':DiagStatus-Mon', _LIPUStatusPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

        # # Egun devices
        # HVPS
        devname = SiriusPVName(_Const.HVPS)
        prefliname = pref + conv_dev_2_liname(devname)
        prefname = devname.substitute(prefix=self._prefix)
        # DiagVoltDiff-Mon
        pvs = [None]*2
        pvs[_LIScalarDiffPV.SP] = prefliname + ':voltoutsoft'
        pvs[_LIScalarDiffPV.RB] = prefliname + ':voltinsoft'
        pvo = _ComputedPV(
            devname + ':DiagVoltDiff-Mon', _LIScalarDiffPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)
        # DiagStatus-Mon
        pvs = [None]*3
        pvs[_LIEGHVStatusPV.PV_SWITCH] = prefliname + ':swstatus'
        pvs[_LIEGHVStatusPV.PV_ENABLE] = prefliname + ':enstatus'
        pvs[_LIEGHVStatusPV.PV_VLTDIF] = prefname + ':DiagVoltDiff-Mon'
        pvo = _ComputedPV(
            devname + ':DiagStatus-Mon', _LIEGHVStatusPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)

        # FilaPS
        devname = SiriusPVName(_Const.FILA)
        prefliname = pref + conv_dev_2_liname(devname)
        prefname = devname.substitute(prefix=self._prefix)
        # DiagCurrentDiff-Mon
        pvs = [None]*2
        pvs[_LIScalarDiffPV.SP] = prefliname + ':currentoutsoft'
        pvs[_LIScalarDiffPV.RB] = prefliname + ':currentinsoft'
        pvo = _ComputedPV(
            devname + ':DiagCurrentDiff-Mon', _LIScalarDiffPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)
        # DiagStatus-Mon
        pvs = [None]*2
        pvs[_LIFilaPSStatusPV.PV_SWITCH] = prefliname + ':swstatus'
        pvs[_LIFilaPSStatusPV.PV_CURDIF] = prefname + ':DiagCurrentDiff-Mon'
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
