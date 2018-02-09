#!/usr/bin/env python-sirius
"""Test pwrsupply bsmp module."""
import unittest

from siriuspy.pwrsupply.bsmp import BSMPResponseSim
# Consts
from siriuspy.pwrsupply.bsmp import Const
from siriuspy.bsmp import Const as _ack


class TestBSMPResponseSim(unittest.TestCase):
    """Test BSMPResponseSim."""

    def setUp(self):
        """Common setup for all tests."""
        self.resp = BSMPResponseSim(ID_device=1, i_load_fluctuation_rms=0.0)

    def test_cmd_0x01(self):
        """Test cmd_0x01."""
        self.assertEqual(self.resp.cmd_0x01(ID_receiver=1),
                         (_ack.ok, Const.version))

    def test_cmd_0x11(self):
        """Test cmd_0x11."""
        variables = [0, 1, 2, 25, 26, 27, 28, 29, 30]
        for v in variables:
            self.assertEqual(self.resp.cmd_0x11(ID_receiver=1, ID_variable=v),
                             (_ack.ok, self.resp._state[v]))

    def test_cmd_0x13(self):
        """Test cmd_0x13."""
        pass


if __name__ == "__main__":
    unittest.main()
