#!/usr/local/bin/python-sirius
"""PS Diag PVs."""

import numpy as _np

from epics import PV as _PV

from siriuspy.epics import connection_timeout as _connection_timeout
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.pwrsupply import ETypes as _ETypes
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.namesys import SiriusPVName as _PVName


class ComputedPV:
    """Computed PV class.

    Objects of this class are used for properties or process variables that are
    computed from other primary process variables. magnet strengths which
    are derived from power supply currents are typical examples of such
    computed process variables.
    """

    def __init__(self, pvname, computer, queue, pvs, monitor=True):
        """Initialize PVs."""
        # print('compute_pv: ', pvname, pvs)

        # starts computer_pvs queue, if not started yet
        self._queue = queue
        if not self._queue.running:
            self._queue.start()

        # --- properties ---

        self.pvname = pvname
        self._value = None
        self._set_limits((None,)*6)
        self.computer = computer
        self.pvs = self._create_primary_pvs_list(pvs)

        # flags if computed_pv is of the 'monitor' type.
        self._monitor_pv = \
            '-Mon' in self.pvname and 'Ref-Mon' not in self.pvname

        # add callback
        self._callbacks = {}
        self._monitor = monitor
        if self._monitor:
            if self._monitor_pv:
                # in order to optimize efficiency, if computed pv is of the
                # monitor type add callback only to the first primary pv, the
                # one corresponding to the main current.
                self.pvs[0].add_callback(self._value_update_callback)
            else:
                for pv in self.pvs:
                    pv.add_callback(self._value_update_callback)

        # init limits
        if self.connected:
            lims = self.computer.compute_limits(self)
            self._set_limits(lims)

        for pv in self.pvs:
            pv.run_callbacks()

    # --- public methods ---

    @property
    def connected(self):
        """Return wether all pvs are connected."""
        for pv in self.pvs:
            if not pv.connected:
                # print(pv.pvname)
                return False
        return True

    @property
    def value(self):
        """Return computed PV value."""
        return self.get()
        # return self._value

    def get(self):
        """Return current value of computed PV."""
        if self._monitor:
            pass
        else:
            self._update_value()
        return self._value

    def put(self, value):
        """Put `value` to the first pv of the pv list."""
        self._value = value
        self.computer.compute_put(self, value)

    def add_callback(self, func, index=None):
        """Add callback to be issued when a PV is updated."""
        if not callable(func):
            raise ValueError("Tried to set non callable as a callback")
        if index is None:
            index = 0 if len(self._callbacks) == 0 \
                else max(self._callbacks.keys()) + 1
        self._callbacks[index] = func
        return len(self._callbacks) - 1

    def run_callbacks(self):
        """Run all callbacks."""
        self._issue_callback(**{
            'pvname': self.pvname,
            'value': self._value,
            'hihi': self.upper_alarm_limit,
            'high': self.upper_warning_limit,
            'hilim': self.upper_disp_limit,
            'lolim': self.lower_disp_limit,
            'low': self.lower_warning_limit,
            'lolo': self.lower_alarm_limit,
        })

    def wait_for_connection(self, timeout):
        """Wait util computed PV is connected or until timeout."""
        pass

    # --- private methods ---

    def _set_limits(self, lims):
        self.upper_alarm_limit = lims[0]
        self.upper_warning_limit = lims[1]
        self.upper_disp_limit = lims[2]
        self.lower_disp_limit = lims[3]
        self.lower_warning_limit = lims[4]
        self.lower_alarm_limit = lims[5]

    def _create_primary_pvs_list(self, pvs):
        # get list of primary pvs
        ppvs = list()  # List with PVs used by the computed PV
        for pv in pvs:
            if isinstance(pv, str):  # give up string option.
                tpv = _PV(pv, connection_timeout=_connection_timeout)
                ppvs.append(tpv)
            else:
                ppvs.append(pv)
        return ppvs

    def _is_same(self, value):
        """."""
        # make sure vars are converted to numpy array, if it is the case
        # TODO: maybe this checking can be simplified. the class seems to be
        # converting values unnecessarily.
        if isinstance(self._value, _np.ndarray) or isinstance(value, _np.ndarray):
            if not isinstance(self._value, _np.ndarray):
                self._value = _np.array(self._value)
            if not isinstance(value, _np.ndarray):
                value = _np.array(value)

        if isinstance(value, _np.ndarray):
            return _np.all(self._value == value)
        else:
            return self._value == value

    def _process_new_value(self, kwargs):
        self._value = kwargs["value"]
        # Check if limits are in the return dict and update them
        if "high" in kwargs:
            self.upper_alarm_limit = kwargs["hihi"]
            self.upper_warning_limit = kwargs["high"]
            self.upper_disp_limit = kwargs["hilim"]
            self.lower_disp_limit = kwargs["lolim"]
            self.lower_warning_limit = kwargs["low"]
            self.lower_alarm_limit = kwargs["lolo"]
        self._issue_callback(pvname=self.pvname, **kwargs)

    def _update_value(self, pvname=None, value=None):
        # Get dict with pv props that changed
        kwargs = self.computer.compute_update(self, pvname, value)

        if kwargs is None:
            return None

        if self._value is None:
            self._process_new_value(kwargs)
            return None

        if not self._is_same(kwargs['value']):
            self._process_new_value(kwargs)
            return None

        if 'high' not in kwargs:
            return None
        elif kwargs['hihi'] != self.upper_alarm_limit or \
                kwargs['high'] != self.upper_warning_limit or \
                kwargs['hilim'] != self.upper_disp_limit or \
                kwargs['hilim'] != self.lower_disp_limit or \
                kwargs['low'] != self.lower_warning_limit or \
                kwargs['lolo'] != self.lower_alarm_limit:
            self._process_new_value(kwargs)

    def _value_update_callback(self, pvname, value, **kwargs):
        # if 'Current-Mon' not in pvname:
        #     print(pvname, value)
        if self.connected:
            self._queue.add_callback(self._update_value, pvname, value)

    def _issue_callback(self, **kwargs):
        for index, callback in self._callbacks.items():
            callback(**kwargs)


class PSDiffPV:
    """Diff of a PS current setpoint and a readback."""

    CURRT_SP = 0
    CURRT_MON = 1


    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute difference between SP and Mon current values."""
        disconnected = \
            not computed_pv.pvs[PSDiffPV.CURRT_SP].connected or \
            not computed_pv.pvs[PSDiffPV.CURRT_MON].connected
        if disconnected:
            return None
        value_sp = computed_pv.pvs[PSDiffPV.CURRT_SP].value
        value_rb = computed_pv.pvs[PSDiffPV.CURRT_MON].value
        diff = value_rb - value_sp
        return {'value': diff}


class PSStatusPV:
    """Power Supply Status PV."""

    # TODO: Add other interlocks for some PS types

    BIT_PSCONNECT = 0b000001
    BIT_PWRSTATON = 0b000010
    BIT_OPMODEDIF = 0b000100
    BIT_CURRTDIFF = 0b001000
    BIT_INTERLKOK = 0b010000
    BIT_BOWFMDIFF = 0b100000

    PWRSTE_STS = 0
    INTLK_SOFT = 1
    INTLK_HARD = 2
    OPMODE_SEL = 3
    OPMODE_STS = 4
    CURRT_DIFF = 5
    WAVFRM_MON = 6

    DTOLWFM_DICT = dict()

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute PS Status PV."""
        psname = _PVName(computed_pv.pvs[0].pvname).device_name
        value = 0
        # ps connected?
        disconnected = \
            not computed_pv.pvs[PSStatusPV.PWRSTE_STS].connected or \
            not computed_pv.pvs[PSStatusPV.INTLK_SOFT].connected or \
            not computed_pv.pvs[PSStatusPV.INTLK_HARD].connected or \
            not computed_pv.pvs[PSStatusPV.OPMODE_SEL].connected or \
            not computed_pv.pvs[PSStatusPV.OPMODE_STS].connected or \
            not computed_pv.pvs[PSStatusPV.CURRT_DIFF].connected
        if disconnected:
            value |= PSStatusPV.BIT_PSCONNECT
            value |= PSStatusPV.BIT_PWRSTATON
            value |= PSStatusPV.BIT_INTERLKOK
            value |= PSStatusPV.BIT_OPMODEDIF
            value |= PSStatusPV.BIT_CURRTDIFF
            value |= PSStatusPV.BIT_BOWFMDIFF
            return {'value': value}

        # pwrstate?
        pwrsts = computed_pv.pvs[PSStatusPV.PWRSTE_STS].value
        if pwrsts != _PSConst.PwrStateSts.On or pwrsts is None:
            value |= PSStatusPV.BIT_PWRSTATON

        # opmode?
        sel = computed_pv.pvs[PSStatusPV.OPMODE_SEL].value
        sts = computed_pv.pvs[PSStatusPV.OPMODE_STS].value
        if sel is not None and sts is not None:
            opmode_sel = _ETypes.OPMODES[sel]
            opmode_sts = _ETypes.STATES[sts]
            if opmode_sel != opmode_sts:
                value |= PSStatusPV.BIT_OPMODEDIF
            # current-diff?
            if sts == _PSConst.States.SlowRef:
                severity = computed_pv.pvs[PSStatusPV.CURRT_DIFF].severity
                if severity != 0:
                    value |= PSStatusPV.BIT_CURRTDIFF
            # waveform diff?
            elif (psname.sec == 'BO') and (sts == _PSConst.States.RmpWfm):
                mon = computed_pv.pvs[PSStatusPV.WAVFRM_MON].value
                if psname not in PSStatusPV.DTOLWFM_DICT.keys():
                    pstype = _PSSearch.conv_psname_2_pstype(psname)
                    PSStatusPV.DTOLWFM_DICT[psname] = _PSSearch.get_splims(
                        pstype, 'DTOL_WFM')
                if not _np.allclose(mon, 0.0,
                                    atol=PSStatusPV.DTOLWFM_DICT[psname]):
                    value |= PSStatusPV.BIT_BOWFMDIFF
        else:
            value |= PSStatusPV.BIT_OPMODEDIF

        # interlocks?
        intlksoft = computed_pv.pvs[PSStatusPV.INTLK_SOFT].value
        intlkhard = computed_pv.pvs[PSStatusPV.INTLK_HARD].value
        if intlksoft != 0 or intlksoft is None or \
                intlkhard != 0 or intlkhard is None:
            value |= PSStatusPV.BIT_INTERLKOK
        return {'value': value}
