#!/usr/bin/env python-sirius

"""Module to test AS-AP-CurrInfo Current Soft IOC main module."""

import unittest
from unittest import mock
import siriuspy.util as util
from siriuspy.currinfo.csdev import Const
from as_ap_currinfo.as_ap_currinfo import _PCASDriver
from as_ap_currinfo.main import SIApp


valid_interface = (
    'pvs_database',
    'init_database',
    'process',
    'read',
    'write',
)


class TestASAPCurrInfoCurrentMain(unittest.TestCase):
    """Test AS-AP-CurrInfo Soft IOC."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            SIApp, valid_interface, print_flag=True)
        self.assertTrue(valid)

    def test_write_DCCTFltCheck(self):
        """Test write DCCTFltCheck-Sel."""
        app = SIApp()
        app.write('DCCTFltCheck-Sel', Const.DCCTFltCheck.On)
        self.assertEqual(app._dcctfltcheck_mode, Const.DCCTFltCheck.On)

    def test_write_DCCT_FltCheckOn(self):
        """Test write DCCT-Sel."""
        app = SIApp()
        app._dcctfltcheck_mode = Const.DCCTFltCheck.On
        init_status = app._dcct_mode
        app.write('DCCT-Sel', Const.DCCT.Avg)
        app.write('DCCT-Sel', Const.DCCT.DCCT13C4)
        app.write('DCCT-Sel', Const.DCCT.DCCT14C4)
        end_status = app._dcct_mode
        self.assertEqual(init_status, end_status)

    def test_write_DCCT_FltCheckOff(self):
        """Test write DCCT-Sel."""
        app = SIApp()
        app.write('DCCTFltCheck-Sel', Const.DCCTFltCheck.Off)
        app.write('DCCT-Sel', Const.DCCT.DCCT13C4)
        self.assertEqual(app._dcct_mode, Const.DCCT.DCCT13C4)


if __name__ == "__main__":
    unittest.main()
