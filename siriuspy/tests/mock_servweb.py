#!/usr/bin/env python-sirius

"""Unittest module for search.py."""
from unittest import mock

import os
from siriuspy.search import ps_search
from siriuspy.search import ma_search
from siriuspy.search import hl_time_search
from siriuspy.search import ll_time_search
from siriuspy.search import bpms_search
from siriuspy.magnet import excdata


_path = os.path.abspath(os.path.dirname(__file__))


# --- auxiliar methods ---
def _read_test_file(path):
    """Read a file."""
    prefix = _path + '/test_data/servweb/'
    with open(prefix + path, "r") as fd:
        return fd.read()


def _ps_pstype_data_read(path):
    """Read a file."""
    prefix = _path + '/test_data/servweb/pwrsupply/pstypes-data/'
    with open(prefix + path, "r") as fd:
        return fd.read()


def _magnets_excitation_data_read(label):
    """Read a file."""
    prefix = _path + '/test_data/servweb/magnet/excitation-data/'
    with open(prefix + label, "r") as fd:
        return fd.read()


# --- Define Mocks ---

# --- mock objects ps_search _web ---
_p = mock.patch.object(ps_search, '_web', autospec=True)
mock1 = _p.start()
mock1.ps_pstypes_names_read.return_value = _read_test_file(
    'pwrsupply/pstypes-names.txt')
mock1.ps_pstype_data_read.side_effect = _ps_pstype_data_read
mock1.ps_pstype_setpoint_limits.return_value = _read_test_file(
    'pwrsupply/pstypes-setpoint-limits.txt')
mock1.ps_siggen_configuration_read.return_value = _read_test_file(
    'pwrsupply/siggen-configuration.txt')
mock1.pu_pstype_setpoint_limits.return_value = _read_test_file(
    'pwrsupply/putypes-setpoint-limits.txt')
mock1.ps_psmodels_read.return_value = _read_test_file(
    'pwrsupply/psmodels.txt')
mock1.pu_psmodels_read.return_value = _read_test_file(
    'pwrsupply/pumodels.txt')
mock1.beaglebone_freq_mapping.return_value = _read_test_file(
    'beaglebone/beaglebone-freq.txt')
mock1.bbb_udc_mapping.return_value = _read_test_file(
    'beaglebone/beaglebone-udc.txt')
mock1.udc_ps_mapping.return_value = _read_test_file('beaglebone/udc-bsmp.txt')

# --- mock objects ma_search _web ---
_p = mock.patch.object(ma_search, '_web', autospec=True)
mock2 = _p.start()
mock2.server_online.return_value = True
mock2.magnets_excitation_ps_read.return_value = _read_test_file(
    'magnet/magnet-excitation-ps.txt')
mock2.ps_pstypes_names_read.return_value = _read_test_file(
    'pwrsupply/pstypes-names.txt')
mock2.ps_pstype_data_read.side_effect = _ps_pstype_data_read
mock2.ps_pstype_setpoint_limits.return_value = _read_test_file(
    'pwrsupply/pstypes-setpoint-limits.txt')
# ps_mock_web.pu_pstype_setpoint_limits.return_value = _read_test_file(
#     'pwrsupply/putypes-setpoint-limits.txt')

# --- mock objects excdata _web ---
_p = mock.patch.object(excdata, '_web', autospec=True)
mock3 = _p.start()
mock3.magnets_excitation_data_read.side_effect = \
    _magnets_excitation_data_read

# --- mock objects hl_time_search _web ---
_p = mock.patch.object(hl_time_search, '_web', autospec=True)
mock4 = _p.start()
mock4.high_level_events.return_value = _read_test_file(
    'timesys/high-level-events.py')
mock4.high_level_triggers.return_value = _read_test_file(
    'timesys/high-level-triggers.py')

# --- mock objects ll_time_search _web ---
_p = mock.patch.object(ll_time_search, '_web', autospec=True)
mock5 = _p.start()
mock5.timing_devices_mapping.return_value = _read_test_file(
    'timesys/timing-devices-connection.txt')

# --- mock objects bpms_search _web ---
_p = mock.patch.object(bpms_search, '_web', autospec=True)
mock6 = _p.start()
mock6.bpms_data.return_value = _read_test_file(
    'diagnostics/bpms-data.txt')
