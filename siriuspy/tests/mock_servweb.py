#!/usr/bin/env python-sirius

"""Unittest module for search.py."""
import unittest
from unittest import mock

import os
from siriuspy.search import ps_search
from siriuspy.search import ma_search
from siriuspy.magnet import excdata


_path = os.path.abspath(os.path.dirname(__file__))


class MockServConf(unittest.TestCase):
    """Mock ServConf methods."""

    def setUp(self):
        """Setup."""
        # --- mock objects ps_search _web ---
        _p = mock.patch.object(ps_search, '_web', autospec=True)
        self.addCleanup(_p.stop)
        self.mock1 = _p.start()
        # mocked functions
        self.mock1.ps_pstypes_names_read.return_value = \
            MockServConf.read_test_file('pwrsupply/pstypes-names.txt')
        self.mock1.ps_pstype_data_read.side_effect = \
            MockServConf.ps_pstype_data_read
        self.mock1.ps_pstype_setpoint_limits.return_value = \
            MockServConf.read_test_file(
                'pwrsupply/pstypes-setpoint-limits.txt')
        self.mock1.ps_siggen_configuration_read.return_value = \
            MockServConf.read_test_file('pwrsupply/siggen-configuration.txt')
        self.mock1.pu_pstype_setpoint_limits.return_value = \
            MockServConf.read_test_file(
                'pwrsupply/putypes-setpoint-limits.txt')
        self.mock1.ps_psmodels_read.return_value = \
            MockServConf.read_test_file('pwrsupply/psmodels.txt')
        self.mock1.pu_psmodels_read.return_value = \
            MockServConf.read_test_file('pwrsupply/pumodels.txt')
        self.mock1.beaglebone_bsmp_mapping.return_value = \
            MockServConf.read_test_file('beaglebone/beaglebone-bsmp.txt')
        self.mock1.beaglebone_freqs_mapping.return_value = \
            MockServConf.read_test_file('beaglebone/beaglebone-freq.txt')
        self.mock1.bbb_udc_mapping.return_value = \
            MockServConf.read_test_file('beaglebone/beaglebone-udc.txt')
        self.mock1.udc_ps_mapping.return_value = \
            MockServConf.read_test_file('beaglebone/udc-bsmp.txt')

        # --- mock objects ma_search _web ---
        _p = mock.patch.object(ma_search, '_web', autospec=True)
        # _p = mock.patch.object(module, servweb, autospec=True)
        self.addCleanup(_p.stop)
        self.mock2 = _p.start()
        # mocked functions
        self.mock2.server_online.return_value = True
        self.mock2.magnets_excitation_ps_read.return_value = \
            MockServConf.read_test_file('magnet/magnet-excitation-ps.txt')
        self.mock2.magnets_setpoint_limits.return_value = \
            MockServConf.read_test_file('magnet/magnet-setpoint-limits.txt')
        self.mock2.pulsed_magnets_setpoint_limits.return_value = \
            MockServConf.read_test_file(
                'magnet/pulsed-magnet-setpoint-limits.txt')
        self.mock2.ps_pstypes_names_read.return_value = \
            MockServConf.read_test_file('pwrsupply/pstypes-names.txt')
        self.mock2.ps_pstype_data_read.side_effect = \
            MockServConf.ps_pstype_data_read
        self.mock2.ps_pstype_setpoint_limits.return_value = \
            MockServConf.read_test_file(
                'pwrsupply/pstypes-setpoint-limits.txt')
        # self.ps_mock_web.pu_pstype_setpoint_limits.return_value = \
        #     MockServConf.read_test_file('pwrsupply/putypes-setpoint-limits.txt')

        # --- mock objects excdata _web ---
        _p = mock.patch.object(excdata, '_web', autospec=True)
        self.addCleanup(_p.stop)
        self.mock3 = _p.start()
        # mocked functions
        self.mock3.magnets_excitation_data_read.side_effect = \
            MockServConf.magnets_excitation_data_read

    @staticmethod
    def read_test_file(path):
        """Read a file."""
        prefix = _path + '/test_data/servweb/'
        with open(prefix + path, "r") as fd:
            return fd.read()

    @staticmethod
    def ps_pstype_data_read(path):
        """Read a file."""
        prefix = _path + '/test_data/servweb/pwrsupply/pstypes-data/'
        with open(prefix + path, "r") as fd:
            return fd.read()

    @staticmethod
    def magnets_excitation_data_read(label):
        """Read a file."""
        prefix = _path + '/test_data/servweb/magnet/excitation-data/'
        with open(prefix + label, "r") as fd:
            return fd.read()
