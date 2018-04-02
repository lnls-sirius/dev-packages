#!/usr/bin/env python-sirius
"""Test pwrsupply bsmp module."""
import unittest
from unittest import mock

from siriuspy.pwrsupply.bsmp import BSMPMasterSlaveSim, BSMPMasterSlave
# Consts
from siriuspy.pwrsupply.bsmp import Const
from siriuspy.bsmp import Const as _ack
from siriuspy.pwrsupply.controller import ControllerPSSim


class TestBSMPMasterSlaveSim(unittest.TestCase):
    """Test BSMPMasterSlaveSim."""

    def setUp(self):
        """Common setup for all tests."""
        ps_c = ControllerPSSim()
        self.resp = BSMPMasterSlaveSim(ID_device=1, pscontroller=ps_c)

    def test_cmd_0x01(self):
        """Test cmd_0x01."""
        self.assertEqual(self.resp.cmd_0x01(ID_receiver=1),
                         (_ack.ok, Const.version))

    def test_cmd_0x11(self):
        """Test cmd_0x11."""
        variables = [0, 1, 2, 25, 26, 27, 28, 29, 30]
        for v in variables:
            resp, val = self.resp.cmd_0x11(ID_receiver=1, ID_variable=v)
            e_resp, e_val = (_ack.ok, self.resp._pscontroller[v])
            self.assertEqual(resp, e_resp)
            if v == 27:
                self.assertAlmostEqual(val, e_val, places=1)
            else:
                self.assertEqual(val, e_val)

    def test_cmd_0x13(self):
        """Test cmd_0x13."""
        self.assertEqual(self.resp.cmd_0x13(1, 3), (_ack.invalid_id, None))

    def test_create_group(self):
        """Test create group."""
        self.resp.create_group(1, 5, [25, 26])
        ret, var = self.resp.cmd_0x13(1, 5)
        self.assertEqual(ret, _ack.ok)
        self.assertIn(25, var)
        self.assertIn(26, var)
        self.assertEqual(len(var), 2)

    def test_remove_group(self):
        """Test remove_groups."""
        self.resp.remove_groups(1)
        self.assertEqual(self.resp.cmd_0x13(1, 0), (_ack.invalid_id, None))
        self.assertEqual(self.resp.cmd_0x13(1, 1), (_ack.invalid_id, None))
        self.assertEqual(self.resp.cmd_0x13(1, 2), (_ack.invalid_id, None))

    def test_cmd_0x51_set_slowref(self):
        """Test cmd_0x51."""
        status, ret = self.resp.cmd_0x51(
            ID_receiver=1, ID_function=Const.set_slowref, setpoint=5.0)
        self.assertEqual(status, _ack.ok)
        self.assertEqual(ret, None)
        sts, ret = self.resp.cmd_0x11(1, Const.ps_setpoint)
        self.assertEqual(ret, 5.0)

    def test_cmd_0x51_select_op_mode(self):
        """Test cmd_0x51 select_op_mode cmd."""
        status, ret = self.resp.cmd_0x51(
            ID_receiver=1, ID_function=Const.select_op_mode, op_mode=4)
        self.assertEqual(status, _ack.ok)
        self.assertEqual(ret, None)
        sts, ret = self.resp.cmd_0x11(1, Const.ps_status)
        self.assertEqual(ret, 4)

    def test_cmd_0x51_turn_on(self):
        """Test cmd_0x51 turn_on/turn_off cmd."""
        status, ret = self.resp.cmd_0x51(
            ID_receiver=1, ID_function=Const.turn_on)
        self.assertEqual(status, _ack.ok)
        self.assertEqual(ret, None)
        # Assert state is on
        sts, ret = self.resp.cmd_0x11(1, Const.ps_status)
        self.assertEqual(ret, 3)

    def test_cmd_0x51_turn_off(self):
        """Test cmd_0x51 turn_on/turn_off cmd."""
        status, ret = self.resp.cmd_0x51(
            ID_receiver=1, ID_function=Const.turn_off)
        self.assertEqual(status, _ack.ok)
        self.assertEqual(ret, None)
        # Assert state is off
        sts, ret = self.resp.cmd_0x11(1, Const.ps_status)
        self.assertEqual(ret, 0)

    def test_cmd_0x51_reset_interlocks(self):
        """Test cmd_0x51 reset interlocks cmd."""
        sts, ret = self.resp.cmd_0x51(
            ID_receiver=1, ID_function=Const.reset_interlocks)
        self.assertEqual(sts, _ack.ok)
        self.assertEqual(ret, None)

    def test_cmd_0x51_close_loop(self):
        """Test cmd_0x51 reset interlocks cmd."""
        sts, ret = self.resp.cmd_0x51(
            ID_receiver=1, ID_function=Const.close_loop)
        # self.status_mock.set_openloop.assert_called_once()
        self.assertEqual(sts, _ack.ok)
        self.assertEqual(ret, None)


class TestBSMPMasterSlave(unittest.TestCase):
    """Test BSMPMasterSlave."""

    def setUp(self):
        """Common setup for all tests."""
        self.pru = mock.Mock()
        self.pru.UART_read.return_value = \
            ['\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00']
        self.resp = BSMPMasterSlave(ID_device=1, PRU=self.pru)

    def test_create_group(self):
        """Test create_group."""
        query = [chr(2), '\x30', '\x00', '\x02', chr(0), chr(2)]
        query = BSMPMasterSlave.includeChecksum(query)
        ret = self.resp.create_group(2, 0, [0, 2])
        self.pru.UART_write.assert_called_with(query, timeout=100)
        self.assertEqual(ret, (0, None))

    def test_remove_groups(self):
        """Test remove_groups."""
        query = [chr(2), '\x32', '\x00', '\x00']
        query = BSMPMasterSlave.includeChecksum(query)
        ret = self.resp.remove_groups(2)
        self.pru.UART_write.assert_called_with(query, timeout=100)
        self.assertEqual(ret, (0, None))

    def test_cmd_0x01(self):
        """Test cmd_0x01."""
        query = [chr(2), '\x00', '\x00', '\x00']
        query = BSMPMasterSlave.includeChecksum(query)
        ret = self.resp.cmd_0x01(2)
        self.pru.UART_write.assert_called_with(query, timeout=100)
        self.assertEqual(ret, (0, '0.0.0'))

    def test_cmd_0x11(self):
        """Test cmd 0x11."""
        # TODO: only accepts Const.frmware_version?
        # var = 0
        # ret = self.resp.cmd_0x11(2, var)
        # query = [chr(2), '\x10', '\x00', '\x01', chr(var)]
        # query = BSMPMasterSlave.includeChecksum(query)
        # self.pru.UART_write.assert_called_with(query, timeout=10)
        pass

    def test_cmd_0x13(self):
        """Test cmd_0x13."""
        # Only ID_group accpeted is 3?
        pass

    def test_cmd_0x13_id_cmd(self):
        """Test cmd_0x13."""
        # Only ID_group accepted is 3?
        # ret_val = \
        #     ['\x00', '\x13', '\x04', '\x00', '\x00', '\x00', '\x00', '\x00']
        # ret_val = BSMPMasterSlave.includeChecksum(ret_val)
        # self.pru.UART_read.return_value = ret_val
        #
        # id_group = 3
        # query = [chr(2), '\x12', '\x00', '\x01', chr(id_group)]
        # query = BSMPMasterSlave.includeChecksum(query)
        #
        # ret = self.resp.cmd_0x13(1, id_group)
        # print(ret)
        pass

    def test_cmd_0x51(self):
        """Test cmd_0x51."""
        pass


if __name__ == "__main__":
    unittest.main()
