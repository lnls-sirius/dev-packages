#!/usr/bin/env python-sirius

"""Unittest module for search.py."""

import unittest
from unittest import mock

import os
# from siriuspy import util
from siriuspy.search import ps_search
from siriuspy.search import PSSearch
# from siriuspy.pwrsupply.siggen import Signal
# from siriuspy.magnet.excdata import ExcitationData


_path = os.path.abspath(os.path.dirname(__file__))


def read_test_ma_excdata(path):
    """Read a file."""
    prefix = _path + '/test_data/servweb/magnet/excitation-data/'
    with open(prefix + path, "r") as fd:
        return fd.read()


class MockServConf(unittest.TestCase):
    """Mock."""

    def setUp(self):
        """Setup."""
        _p = mock.patch.object(ps_search, '_web', autospec=True)
        # _p = mock.patch.object(module, servweb, autospec=True)
        self.addCleanup(_p.stop)
        self.mock = _p.start()
        self.mock.ps_pstypes_names_read.return_value = \
            MockServConf.read_test_file('pwrsupply/pstypes-names.txt')
        self.mock.ps_pstype_data_read.side_effect = \
            MockServConf.read_test_ps_pstypes
        self.mock.ps_pstype_setpoint_limits.return_value = \
            MockServConf.read_test_file(
                'pwrsupply/pstypes-setpoint-limits.txt')
        self.mock.ps_siggen_configuration_read.return_value = \
            MockServConf.read_test_file('pwrsupply/siggen-configuration.txt')
        self.mock.pu_pstype_setpoint_limits.return_value = \
            MockServConf.read_test_file(
                'pwrsupply/putypes-setpoint-limits.txt')
        self.mock.ps_psmodels_read.return_value = \
            MockServConf.read_test_file('pwrsupply/psmodels.txt')
        self.mock.pu_psmodels_read.return_value = \
            MockServConf.read_test_file('pwrsupply/pumodels.txt')
        self.mock.beaglebone_power_supplies_mapping.return_value = \
            MockServConf.read_test_file(
                'pwrsupply/beaglebone-mapping.txt')

    @staticmethod
    def read_test_file(path):
        """Read a file."""
        prefix = _path + '/test_data/servweb/'
        with open(prefix + path, "r") as fd:
            return fd.read()

    @staticmethod
    def read_test_ps_pstypes(path):
        """Read a file."""
        prefix = _path + '/test_data/servweb/pwrsupply/pstypes-data/'
        with open(prefix + path, "r") as fd:
            return fd.read()


class TestPSSearch(MockServConf):
    """Test PSSearch."""

    def test_get_psnames(self):
        """Test get_psnames."""
        # without filters
        psnames = PSSearch.get_psnames()
        self.assertIsInstance(psnames, (list, tuple))
        # for psname in TestPSSearch.sample:
        #     self.assertIn(psname, psnames)
        # check sorted
        sorted_psnames = sorted(psnames)
        self.assertEqual(psnames, sorted_psnames)
        # with filters
        psnames = PSSearch.get_psnames({'dis': 'PU'})
        self.assertEqual(len(psnames), 12)
        for name in psnames:
            self.assertIn('PU', name)
        psnames = PSSearch.get_psnames({'sub': '0.M1'})
        self.assertEqual(len(psnames), 69)
        # exceptions
        self.assertRaises(TypeError, PSSearch.get_psnames, filters=23)
        self.assertRaises(TypeError, PSSearch.get_psnames, filters=23.4)
        self.assertRaises(TypeError, PSSearch.get_psnames, filters=[0, ])
        self.assertRaises(TypeError, PSSearch.get_psnames, filters=(0.0, ))


if __name__ == "__main__":
    unittest.main()
