"""Power Supply BSMP."""

import time as _time
import numpy as _np
from siriuspy.bsmp import constants as _const_bsmp
from siriuspy.bsmp import BSMP as _BSMP
from . import bsmp as _bsmp
from siriuspy.pwrsupply.pru import PRU as _PRU


# version of the BSMP implementation of power supplies that is compatible
# with the current implemenation of this module.


class PSBSMP(_BSMP):
    """Power supply BSMP."""

    CONST_BSMP = _const_bsmp

    _timeout_read_variable = 100  # [us]
    _timeout_execute_function = 100  # [us]
    _timeout_remove_vars_groups = 100  # [us]
    _timeout_create_vars_groups = 100  # [us]
    _timeout_read_group_of_variables = 100  # [us]
    _timeout_request_curve_block = 100  # [us]
    _timeout_curve_block = 100  # [us]

    _sleep_turn_onoff = 0.020  # [s]
    _sleep_reset_udc = 0.500  # [s]

    _wfmref_pointers_var_ids = {
        0: (_bsmp.ConstPSBSMP.V_WFMREF0_START,
            _bsmp.ConstPSBSMP.V_WFMREF0_END,
            _bsmp.ConstPSBSMP.V_WFMREF0_IDX),
        1: (_bsmp.ConstPSBSMP.V_WFMREF1_START,
            _bsmp.ConstPSBSMP.V_WFMREF1_END,
            _bsmp.ConstPSBSMP.V_WFMREF1_IDX),
    }

    def __init__(self, slave_address, entities, pru=None):
        """Init BSMP."""
        if pru is None:
            self.pru = _PRU()
        else:
            self.pru = pru
        super().__init__(self.pru, slave_address, entities)
        self._wfmref_check_entities_consistency()

    @staticmethod
    def parse_firmware_version(version):
        """Process firmware version from BSMP device."""
        version = version[:version.index(b'\x00')]
        version = ''.join([chr(ord(v)) for v in version])
        return version

    def reset_groups_of_variables(self, var_ids_list):
        """Reset groups of variables."""
        # remove previous variables groups
        self.remove_all_groups_of_variables(
            timeout=PSBSMP._timeout_remove_vars_groups)

        # create variables groups
        for var_ids in var_ids_list:
            self.create_group_of_variables(
                var_ids, timeout=PSBSMP._timeout_create_vars_groups)

    # --- bsmp overriden methods ---

    def execute_function(
            self, func_id, input_val=None,
            timeout=_timeout_execute_function, read_flag=True):
        """."""
        # execute function
        # print('--- execute_function ---')
        # print('func_id: ', func_id)
        # print('input_val: ', input_val)
        # print('timeout: ', timeout)
        # print('read_flag: ', read_flag)
        response = super().execute_function(
            func_id=func_id, input_val=input_val,
            timeout=timeout, read_flag=read_flag)

        # introduces necessary sleeps
        # TODO: check with ELP if these numbers can be optimized further!
        if func_id == _bsmp.ConstPSBSMP.F_RESET_UDC:
            _time.sleep(PSBSMP._sleep_reset_udc)
        elif func_id in (_bsmp.ConstPSBSMP.F_TURN_ON,
                         _bsmp.ConstPSBSMP.F_TURN_OFF,
                         _bsmp.ConstPSBSMP.F_OPEN_LOOP,
                         _bsmp.ConstPSBSMP.F_CLOSE_LOOP):
            _time.sleep(PSBSMP._sleep_turn_onoff)

        return response

    def read_group_of_variables(
            self, group_id, timeout=_timeout_read_group_of_variables):
        """."""
        response = super().read_group_of_variables(
            group_id=group_id, timeout=timeout)

        return response

    # --- wfmref methods ---

    @property
    def wfmref_select(self):
        """Return ID of curve currently in use by DSP."""
        _, curve_id = self.read_variable(
            var_id=_bsmp.ConstPSBSMP.V_WFMREF_SELECTED,
            timeout=PSBSMP._timeout_read_variable)
        return curve_id

    @wfmref_select.setter
    def wfmref_select(self, curve_id):
        """Select ID of curve to be used by DSP."""
        ack, data = self.execute_function(
            func_id=_bsmp.ConstPSBSMP.F_SELECT_WFMREF,
            input_val=curve_id,
            timeout=PSBSMP._timeout_execute_function)
        return ack, data

    @property
    def wfmref_size(self):
        """Return WfmRef size in t_float units.

            This is the waveform size as last registered by the
        ARM controller.
        """
        # calculate wfmref size from buffer pointer values used by
        # ARM controller
        i_beg, i_end, _ = self._wfmref_bsmp_get_pointers_ids_of_selected()
        values = self._bsmp_get_variable_values(i_beg, i_end)
        return PSBSMP.curve_index_calc(values[0], values[1])

    @property
    def wfmref_idx(self):
        """Return WfmRef Index

            This index refers to the current waveform in use by the
        DSP controller.
        """
        # calculate wfmref index from buffer pointer values used by
        # ARM controller
        i_beg, _, i_idx = self._wfmref_bsmp_get_pointers_ids_of_selected()
        values = self._bsmp_get_variable_values(i_beg, i_idx)
        return PSBSMP.curve_index_calc(values[0], values[1])

    @property
    def wfmref_maxsize(self):
        """."""
        # curve with ids 0 and 1 should have same sizes.
        maxsize = self.curve_maxsize(curve_id=0)
        return maxsize

    @ property
    def wfmref_pointer_values(self):
        """Return pointer values of currently selected wfmref curve."""
        pointer_ids = self._wfmref_bsmp_get_pointers_ids_of_selected()
        pointer_values = self._bsmp_get_variable_values(*pointer_ids)
        return pointer_values

    def wfmref_read(self):
        """Return data of curve currently in use by DSP."""
        # get curve ID
        curve_id = self.wfmref_select

        # get curve data
        curve = self._curve_bsmp_read(curve_id=curve_id)
        return curve

    def wfmref_write(self, curve):
        """Write WfmRef to currently ."""
        # # get id of writable wfmref curve
        curve_id = self._wfmref_bsmp_select_writable_curve_id()

        # write curve
        curve = self.curve_write(curve_id, curve)

        _time.sleep(0.020)  # TODO: necessary??

        # execute selection of WfmRef to be used
        self.wfmref_select = curve_id

        return curve

    # --- curve methods ---

    def curve_read(self, curve_id):
        """Return curve."""
        curve = self._curve_bsmp_read(curve_id=curve_id)
        return curve

    def curve_write(self, curve_id, curve):
        """Write curve."""
        # check curve size
        self._curve_check_size(curve_id=curve_id, curve_size=len(curve))

        # send curve blocks
        self._curve_bsmp_write(curve_id, curve)

        # # get curve just written
        # curve = self.curve_read(curve_id)

        # return curve

        return _np.array(curve)

    def curve_maxsize(self, curve_id):
        """Return max size if t_float units according to BSMP spec."""
        curve_entity = self.entities.curves[curve_id]
        maxsize = curve_entity.max_size_t_float
        return maxsize

    @staticmethod
    def curve_index_calc(beg, end):
        """Calculate curve index."""
        return 1 + (end - beg) // 2

    # --- private methods ---

    def _wfmref_bsmp_get_pointers_ids_of_selected(self):
        curve_id = self.wfmref_select
        return PSBSMP._wfmref_pointers_var_ids[curve_id]

    def _wfmref_check_entities_consistency(self):
        # check consistency of curves with ids 0 and 1
        curves = self.entities.curves
        if 0 in curves and 1 in curves:
            curve0, curve1 = curves[0], curves[1]
            if False in (curve0.waccess, curve1.waccess) or \
               curve0.size != curve1.size or \
               curve0.nblocks != curve1.nblocks:
                raise ValueError('Inconsistent curves!')

    def _wfmref_bsmp_select_writable_curve_id(self):
        # read status
        var_ids = (
            _bsmp.ConstPSBSMP.V_PS_STATUS,
            _bsmp.ConstPSBSMP.V_WFMREF_SELECTED,
          )
        data = self._bsmp_get_variable_values(*var_ids)
        state = data[0] & 0b1111
        curve_id = data[1]
        if state in (_bsmp.ConstPSBSMP.E_STATE_RMPWFM,
                     _bsmp.ConstPSBSMP.E_STATE_MIGWFM):
            # select the other buffer and send curve blocks
            curve_id = 0 if curve_id == 1 else 1

        return curve_id

    def _curve_bsmp_read(self, curve_id):
        # select minimum curve size between spec and firmware.
        wfmref_size = self.wfmref_size
        wfmref_size_min = self._curve_get_implementable_size(
            curve_id, wfmref_size)

        # create initial output data
        curve = _np.zeros(wfmref_size_min)

        # read curve blocks
        curve_entity = self.entities.curves[curve_id]
        indices = curve_entity.get_indices(wfmref_size_min)
        # print('reading - curve id: ', curve_id)
        # print('reading - indices: ', indices)
        for block, idx in enumerate(indices):
            ack, data = self.request_curve_block(
                curve_id=curve_id,
                block=block,
                timeout=PSBSMP._timeout_request_curve_block)
            # print(sum(data))
            # print((hex(ack), sum(data)))
            if ack != self.CONST_BSMP.ACK_OK:
                self._anomalous_response(
                    self.CONST_BSMP.CMD_REQUEST_CURVE_BLOCK, ack,
                    curve_len=len(curve),
                    curve_id=curve_id,
                    block=block,
                    index=idx)
            idx_w = slice(idx[0], idx[1])
            idx_r = slice(0, idx[1] - idx[0])
            curve[idx_w] = data[idx_r]
        return curve

    def _curve_bsmp_write(self, curve_id, curve):
        # select minimum curve size between spec and firmware.
        wfmref_size_min = self._curve_get_implementable_size(
            curve_id, len(curve))

        # send curve blocks
        curve_entity = self.entities.curves[curve_id]
        indices = curve_entity.get_indices(wfmref_size_min)
        # print('writing - curve id: ', curve_id)
        # print('writing - indices: ', indices)

        for block, idx in enumerate(indices):
            data = curve[idx[0]:idx[1]]
            # print(sum(data))
            ack, data = self.curve_block(
                curve_id=curve_id,
                block=block,
                value=data,
                timeout=PSBSMP._timeout_curve_block)
            # print((hex(ack), data))
            if ack != self.CONST_BSMP.ACK_OK:
                self._anomalous_response(
                    self.CONST_BSMP.CMD_CURVE_BLOCK, ack,
                    curve_len=len(curve),
                    curve_id=curve_id,
                    block=block,
                    index=idx)

    def _bsmp_get_variable_values(self, *var_ids):
        values = [None] * len(var_ids)
        for i, var_id in enumerate(var_ids):
            _, values[i] = self.read_variable(
                var_id=var_id, timeout=PSBSMP._timeout_read_variable)
        return values

    def _curve_get_implementable_size(self, curve_id, curve_size):
        curve_entity = self.entities.curves[curve_id]
        curve_size_entity = curve_entity.max_size_t_float
        curve_size_min = min(curve_size_entity, curve_size)
        return curve_size_min

    def _curve_check_size(self, curve_id, curve_size):
        if curve_size > self.curve_maxsize(curve_id=curve_id):
            raise IndexError('Curve exceeds maximum size according to spec!')



# --- DCDC ---


class FBP(PSBSMP):
    """BSMP with EntitiesFBP."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.CONST_PSBSMP = _bsmp.ConstFBP
        PSBSMP.__init__(self, slave_address, _bsmp.EntitiesFBP(), pru=pru)


class FAC_DCDC(PSBSMP):
    """BSMP with EntitiesFAC_DCDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.CONST_PSBSMP = _bsmp.ConstFAC_DCDC
        PSBSMP.__init__(self, slave_address, _bsmp.EntitiesFAC_DCDC(), pru=pru)


class FAC_2P4S_DCDC(PSBSMP):
    """BSMP with EntitiesFAC_2P4S_DCDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.CONST_PSBSMP = _bsmp.ConstFAC_2P4S_DCDC
        PSBSMP.__init__(self, slave_address, _bsmp.EntitiesFAC_2P4S_DCDC(), pru=pru)


class FAC_2S_DCDC(PSBSMP):
    """BSMP with EntitiesFAC_2S_DCDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.CONST_PSBSMP = _bsmp.ConstFAC_2S_DCDC
        PSBSMP.__init__(self, slave_address, _bsmp.EntitiesFAC_2S_DCDC(), pru=pru)


class FAP(PSBSMP):
    """BSMP with EntitiesFAP."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.CONST_PSBSMP = _bsmp.ConstFAP
        PSBSMP.__init__(self, slave_address, _bsmp.EntitiesFAP(), pru=pru)


class FAP_4P(PSBSMP):
    """BSMP with EntitiesFAP_4P."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.CONST_PSBSMP = _bsmp.ConstFAP_4P
        PSBSMP.__init__(self, slave_address, _bsmp.EntitiesFAP_4P(), pru=pru)


class FAP_2P2S(PSBSMP):
    """BSMP with EntitiesFAP_2P2S."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.CONST_PSBSMP = _bsmp.ConstFAP_2P2S
        PSBSMP.__init__(self, slave_address, _bsmp.EntitiesFAP_2P2S(), pru=pru)



# --- ACDC ---


class FBP_DCLink(PSBSMP):
    """BSMP with EntitiesFBP_DCLink."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.CONST_PSBSMP = _bsmp.ConstFBP_DCLink
        PSBSMP.__init__(self, slave_address, _bsmp.EntitiesFBP_DCLink(), pru=pru)


class FAC_2P4S_ACDC(PSBSMP):
    """BSMP with EntitiesFAC_2P4S_ACDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.CONST_PSBSMP = _bsmp.ConstFAC_2P4S_ACDC
        PSBSMP.__init__(self, slave_address, _bsmp.EntitiesFAC_2P4S_ACDC(), pru=pru)


class FAC_2S_ACDC(PSBSMP):
    """BSMP with EntitiesFAC_2S_ACDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.CONST_PSBSMP = _bsmp.ConstFAC_2S_ACDC
        PSBSMP.__init__(self, slave_address, _bsmp.EntitiesFAC_2S_ACDC(), pru=pru)


class PSBSMPFactory:
    """."""

    psname_2_psbsmp = {
        'FBP': FBP,
        'FBP_DCLink': FBP_DCLink,
        'FBP_FOFB': FBP,
        'FAC_DCDC': FAC_DCDC,
        'FAC_2S_DCDC': FAC_2S_DCDC,
        'FAC_2S_ACDC': FAC_2S_ACDC,
        'FAC_2P4S_DCDC': FAC_2P4S_DCDC,
        'FAC_2P4S_ACDC': FAC_2P4S_ACDC,
        'FAP': FAP,
        'FAP_2P2S': FAP_2P2S,
        'FAP_4P': FAP_4P,
    }

    @staticmethod
    def create(psmodel, *args, **kwargs):
        """Return PSModel object."""

        if psmodel in PSBSMPFactory.psname_2_psbsmp:
            factory = PSBSMPFactory.psname_2_psbsmp[psmodel]
            return factory(*args, **kwargs)
        else:
            raise ValueError('PS Model "{}" not defined'.format(psmodel))
