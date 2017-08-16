"""Module to deal with correctors."""

import time as _time
import numpy as _np
import epics as _epics
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.envars import vaca_prefix as LL_PREF

_TIMEOUT = 0.05

TINY_INTERVAL = 0.01
NUM_TIMEOUT = 1000
WAIT_FOR_SIMULATOR = 3

NR_CH = 120
NR_CV = 160
SECTION = 'SI'


class Correctors:
    """Class to deal with correctors."""

    SLOW_REF = 0
    SLOW_REF_SYNC = 1

    def get_database(self):
        """Get the database of the class."""
        db = dict()
        pre = self.prefix
        db[pre + 'SyncKicks-Sel'] = {
            'type': 'enum', 'enums': ('Off', 'On'), 'value': 1,
            'fun_set_pv': self._set_corr_pvs_mode}
        db[pre + 'SyncKicks-Sts'] = {
            'type': 'enum', 'enums': ('Off', 'On'), 'value': 1}
        return db

    def __init__(self, prefix, callback):
        """Initialize the instance."""
        self.callback = callback
        self.prefix = prefix
        self.sync_kicks = True
        self.corr_pvs_opmode_sel = list()
        self.corr_pvs_opmode_sts = list()
        self.corr_pvs_opmode_ready = dict()
        self.corr_pvs_sp = list()
        self.corr_pvs_rb = list()
        self.corr_pvs_ref = list()
        self.corr_pvs_ready = dict()
        self.corr_pvs_applied = dict()

    def connect(self):
        """Connect to external PVs."""
        ch_names = _PSSearch.get_psnames({'section': 'SI',
                                          'discipline': 'PS',
                                          'device': 'CH'})
        cv_names = _PSSearch.get_psnames({'section': 'SI',
                                          'discipline': 'PS',
                                          'device': 'CV'})
        self.corr_names = ch_names + cv_names

        for dev in self.corr_names:
            self.corr_pvs_opmode_sel.append(
                _epics.PV(LL_PREF + dev + ':OpMode-Sel',
                          connection_timeout=_TIMEOUT))
            self.corr_pvs_opmode_sts.append(
                _epics.PV(LL_PREF + dev + ':OpMode-Sts',
                          connection_timeout=_TIMEOUT,
                          callback=self._corrIsOnMode))
            self.corr_pvs_opmode_ready[LL_PREF + dev + ':OpMode-Sts'] = False
            self.corr_pvs_sp.append(
                _epics.PV(LL_PREF + dev + ':Current-SP',
                          connection_timeout=_TIMEOUT))
            self.corr_pvs_rb.append(
                _epics.PV(LL_PREF + dev + ':Current-RB',
                          connection_timeout=_TIMEOUT,
                          callback=self._corrIsReady))
            self.corr_pvs_ref.append(
                _epics.PV(LL_PREF + dev + ':CurrentRef-Mon',
                          connection_timeout=_TIMEOUT,
                          callback=self._kickApplied))
            self.corr_pvs_ready[LL_PREF + dev + ':Current-RB'] = False
            self.corr_pvs_applied[LL_PREF + dev + ':CurrentRef-Mon'] = False
        self.rf_pv_sp = _epics.PV(LL_PREF + SECTION +
                                  '-03SP:RF-SRFCav:Freq-SP')
        self.rf_pv_rb = _epics.PV(LL_PREF + SECTION +
                                  '-03SP:RF-SRFCav:Freq-RB')
        self.event_pv_mode_sel = _epics.PV(SECTION +
                                           '-Glob:TI-Event:OrbitMode-Sel')
        self.event_pv_sp = _epics.PV(SECTION +
                                     '-Glob:TI-Event:OrbitExtTrig-Cmd')

    def apply_kicks(self, values):
        """Apply kicks."""
        # apply the RF kick
        if self.rf_pv_sp.connected:
            if not self._equalKick(values[-1], self.rf_pv_sp.value):
                self.rf_pv_sp.value = values[-1]
        else:
            self._call_callback(
                'Log-Mon',
                'PV ' + self.rf_pv_sp.pvname + ' Not Connected.'
                )
        # Send correctors setpoint
        for i, pv in enumerate(self.corr_pvs_sp):
            pvname_rb = pv.pvname.replace('-SP', '-RB')
            pvname_ref = pv.pvname.replace('-SP', 'Ref-Mon')
            self.corr_pvs_ready[pvname_rb] = True
            self.corr_pvs_applied[pvname_ref] = True
            if not pv.connected:
                self._call_callback('Log-Mon',
                                    'Err: PV ' + pv.pvname + ' Not Connected.')
                continue
            if self._equalKick(values[i], pv.value):
                continue
            self.corr_pvs_ready[pvname_rb] = False
            self.corr_pvs_applied[pvname_ref] = False
            pv.value = values[i]
        # Wait for readbacks to be updated
        if self._timed_out(self.corr_pvs_ready):
            self._call_callback('Log-Mon',
                                'Err: Timeout waiting Correctors RB')
            return
        # Send trigger signal for implementation
        if self.sync_kicks:
            if self.event_pv_sp.connected:
                self.event_pv_sp.value = 1
            else:
                self._call_callback('Log-Mon',
                                    'Kicks not sent, Timing PV Disconnected.')
                return
        # Wait for references to be updated
        if self._timed_out(self.corr_pvs_ready):
            self._call_callback('Log-Mon',
                                'Err: Timeout waiting Correctors Ref')
            return
        # wait for simulator to compute the orbit.
        _time.sleep(WAIT_FOR_SIMULATOR)

    @staticmethod
    def _timed_out(wait_dict):
        for i in range(NUM_TIMEOUT):
            if all(wait_dict.values()):
                return False
            _time.sleep(TINY_INTERVAL)
        return True

    def get_correctors_strength(self):
        """Get the correctors strengths."""
        corr_values = _np.zeros(len(self.corr_names)+1)
        for i, pv in enumerate(self.corr_pvs_ref):
            corr_values[i] = pv.value
        corr_values[-1] = self.rf_pv_rb.value
        return corr_values

    def _call_callback(self, pv, value):
        self.callback(self.prefix + pv, value)

    def _set_corr_pvs_mode(self, value):
        self.sync_kicks = True if value else False
        val = self.SLOW_REF_SYNC if self.sync_kicks else self.SLOW_REF
        for pv in self.corr_pvs_opmode_sel:
            if pv.connected:
                pv.value = val
        self._call_callback(
            'Log-Mon',
            'Setting Correctors PVs to {0:s} Mode'.format('Sync' if value
                                                          else 'Async')
            )
        self._call_callback('SyncKicks-Sts', value)
        return True

    @staticmethod
    def _equalKick(val1, val2):
        max_ = max(abs(val1), abs(val2))
        if not max_:
            return True
        if abs(val1-val2)/max_ <= 1e-12:
            return True
        return False

    def _corrIsReady(self, pvname, value, **kwargs):
        ind = self.corr_names.index(pvname.strip(LL_PREF).strip(':Current-RB'))
        self.corr_pvs_ready[pvname] = self._equalKick(
                                            self.corr_pvs_sp[ind].value,
                                            value)

    def _kickApplied(self, pvname, value, **kwargs):
        name = pvname.strip(LL_PREF).strip(': CurrentRef-Mon')
        ind = self.corr_names.index(name)
        self.corr_pvs_applied[pvname] = self._equalKick(
                                            self.corr_pvs_sp[ind].value,
                                            value)

    def _corrIsOnMode(self, pvname, value, **kwargs):
        val = self.SLOW_REF_SYNC if self.sync_kicks else self.SLOW_REF
        self.corr_pvs_opmode_ready[pvname] = (value == val)
        if all(self.corr_pvs_opmode_ready.values()):
            self._call_callback('SyncKicks-Sts', val == self.SLOW_REF_SYNC)
        else:
            self._call_callback('SyncKicks-Sts', val != self.SLOW_REF_SYNC)
