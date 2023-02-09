#!/usr/bin/env python-sirius
"""Test webserver implementation module."""
from unittest import TestCase, mock
from urllib.request import URLError

from siriuspy.clientweb import implementation
import siriuspy.util as util

_TIMEOUT = implementation._TIMEOUT
# Dependencies
# _envars.SRVURL_CSCONSTS
# _urllib_request.urlopen
# _urllib_request.urlopen.read


class TestClientWebReadUrl(TestCase):
    """Test read url method."""

    def setUp(self):
        """Common setup for all tests."""
        # Create mocks
        url_patcher = mock.patch.object(
            implementation, '_urllib_request', autospec=True)
        env_patcher = mock.patch.object(
            implementation, '_envars', autospec=True)
        self.addCleanup(url_patcher.stop)
        self.addCleanup(env_patcher.stop)
        self.url_mock = url_patcher.start()
        self.env_mock = env_patcher.start()
        # Configuration parameters
        self.fake_url = "http://FakeBaseURL/"
        # Mocked methods
        self.url_mock.urlopen.return_value.read.return_value = b'FakeResponse'
        # Mock a property from envars
        type(self.env_mock).SRVURL_CSCONSTS = \
            mock.PropertyMock(return_value=self.fake_url)

    def _test_read_url_request(self):
        """Test read_rul makes a request using urlopen."""
        implementation.read_url("FakeURL")
        self.url_mock.urlopen.assert_called_once_with(
            self.fake_url + "FakeURL", timeout=1.0)

    def _test_read_url_response(self):
        """Test read_url."""
        self.assertEqual(implementation.read_url("FakeURL"), "FakeResponse")

    def _test_read_url_exception(self):
        """Test read_url raises exception."""
        self.url_mock.urlopen.side_effect = URLError("FakeError")
        with self.assertRaises(Exception):
            implementation.read_url("FakeURL")


@mock.patch.object(implementation, 'read_url', autospec=True,
                   return_value="FakeResponse")
class TestClientWeb(TestCase):
    """Test ClientWeb."""

    public_interface = {
        'read_url',
        'server_online',
        'magnets_model_data',
        'magnets_excitation_data_read',
        'magnets_excitation_ps_read',
        'ps_pstypes_names_read',
        'ps_pstype_data_read',
        'ps_pstype_setpoint_limits',
        'pu_pstype_setpoint_limits',
        'ps_siggen_configuration_read',
        'ps_psmodels_read',
        'pu_psmodels_read',
        'beaglebone_freq_mapping',
        'beaglebone_ip_list',
        'bbb_udc_mapping',
        'udc_ps_mapping',
        'crates_mapping',
        'bpms_data',
        'timing_devices_mapping',
        'high_level_triggers',
        'high_level_events',
        'bsmp_dclink_mapping',
        'mac_schedule_read',
        'doc_services_read',
    }

    def test_public_interface(self, mock_read):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            implementation, TestClientWeb.public_interface)
        self.assertTrue(valid)

    def test_server_online(self, mock_read):
        """Test server_online return True when no exception is issued."""
        self.assertTrue(implementation.server_online())

    def test_server_online_exception(self, mock_read):
        """Test server_online return True when no exception is issued."""
        mock_read.side_effect = Exception()
        self.assertFalse(implementation.server_online())

    # def _test_bpms_data(self, mock_read):
    #     """Test bpms_data."""
    #     url = implementation._magnet_folder + 'magnets-model-data.txt'
    #     # Call with different parameters
    #     resp = implementation.bpms_data()
    #     self.assertEqual(resp, "FakeResponse")
    #     resp = implementation.bpms_data(timeout=2.0)
    #     self.assertEqual(resp, "FakeResponse")
    #     # Assert read_url was called correctly
    #     mock_read.assert_has_calls([
    #         mock.call(url, timeout=1.0),
    #         mock.call(url, timeout=2.0)])

    def test_magnets_excitation_data_read(self, mock_read):
        """Test magnets_excitation_data_read."""
        filename = "fakefile"
        folder = implementation._EXCDAT_FOLDER
        # Call two times
        resp = implementation.magnets_excitation_data_read(filename)
        self.assertEqual(resp, "FakeResponse")
        resp = implementation.magnets_excitation_data_read(
            filename, timeout=2*_TIMEOUT)
        self.assertEqual(resp, "FakeResponse")
        # Assert read was called correctly
        mock_read.assert_has_calls([
            mock.call(folder + filename, timeout=_TIMEOUT),
            mock.call(folder + filename, timeout=2*_TIMEOUT)])

    def test_magnets_excitation_ps_read(self, mock_read):
        """Test magnets_excitation_ps_read."""
        url = implementation._MAGNET_FOLDER + 'magnet-excitation-ps.txt'
        # Call with different parameters
        resp = implementation.magnets_excitation_ps_read()
        self.assertEqual(resp, "FakeResponse")
        resp = implementation.magnets_excitation_ps_read(timeout=2*_TIMEOUT)
        self.assertEqual(resp, "FakeResponse")
        # Assert read_url was called correctly
        mock_read.assert_has_calls([
            mock.call(url, timeout=_TIMEOUT),
            mock.call(url, timeout=2*_TIMEOUT)])

    def test_ps_pstypes_names_read(self, mock_read):
        """Test ps_pstypes_names_read."""
        url = implementation._PS_FOLDER + 'pstypes-names.txt'
        # Call with different parameters
        resp = implementation.ps_pstypes_names_read()
        self.assertEqual(resp, "FakeResponse")
        resp = implementation.ps_pstypes_names_read(timeout=2*_TIMEOUT)
        self.assertEqual(resp, "FakeResponse")
        # Assert read_url was called correctly
        mock_read.assert_has_calls([
            mock.call(url, timeout=_TIMEOUT),
            mock.call(url, timeout=2*_TIMEOUT)])

    def test_ps_pstype_data_read(self, mock_read):
        """Test ps_pstype_data_read."""
        filename = "fakefilename"
        url = implementation._PSTYPES_DATA_FOLDER + filename
        # Call with different parameters
        resp = implementation.ps_pstype_data_read(filename)
        self.assertEqual(resp, "FakeResponse")
        resp = implementation.ps_pstype_data_read(filename, timeout=2*_TIMEOUT)
        self.assertEqual(resp, "FakeResponse")
        # Assert read_url was called correctly
        mock_read.assert_has_calls([
            mock.call(url, timeout=_TIMEOUT),
            mock.call(url, timeout=2*_TIMEOUT)])

    def test_ps_siggen_configuration_read(self, mock_read):
        """Test ps_siggen_configuration_read."""
        url = implementation._PS_FOLDER + 'siggen-configuration.txt'
        # Call with different parameters
        resp = implementation.ps_siggen_configuration_read()
        self.assertEqual(resp, "FakeResponse")
        resp = implementation.ps_siggen_configuration_read(timeout=2*_TIMEOUT)
        self.assertEqual(resp, "FakeResponse")
        # Assert read_url was called correctly
        mock_read.assert_has_calls([
            mock.call(url, timeout=_TIMEOUT),
            mock.call(url, timeout=2*_TIMEOUT)])

    def test_ps_pstype_setpoint_limits(self, mock_read):
        """Test ps_pstype_setpoint_limits."""
        url = implementation._PS_FOLDER + 'pstypes-setpoint-limits.txt'
        # Call with different parameters
        resp = implementation.ps_pstype_setpoint_limits()
        self.assertEqual(resp, "FakeResponse")
        resp = implementation.ps_pstype_setpoint_limits(timeout=2*_TIMEOUT)
        self.assertEqual(resp, "FakeResponse")
        # Assert read_url was called correctly
        mock_read.assert_has_calls([
            mock.call(url, timeout=_TIMEOUT),
            mock.call(url, timeout=2*_TIMEOUT)])

    def test_pu_pstype_setpoint_limits(self, mock_read):
        """Test pu_pstype_setpoint_limits."""
        url = implementation._PS_FOLDER + 'putypes-setpoint-limits.txt'
        # Call with different parameters
        resp = implementation.pu_pstype_setpoint_limits()
        self.assertEqual(resp, "FakeResponse")
        resp = implementation.pu_pstype_setpoint_limits(timeout=2*_TIMEOUT)
        self.assertEqual(resp, "FakeResponse")
        # Assert read_url was called correctly
        mock_read.assert_has_calls([
            mock.call(url, timeout=_TIMEOUT),
            mock.call(url, timeout=2*_TIMEOUT)])

    def test_beaglebone_freq_mapping(self, mock_read):
        """Test beaglebone_freqs_mapping."""
        # TODO: implement!
        pass

    def test_beaglebone_ip_list(self, mock_read):
        """Test beaglebone_ip_list."""
        # TODO: implement!
        pass

    def test_crates_mapping(self, mock_read):
        """Test crate_to_bpm_mapping."""
        url = (
            implementation._DIAG_FOLDER + 'microTCA-vs-BPMs-mapping/')
        # Call with different parameters
        resp = implementation.crates_mapping()
        self.assertEqual(resp, "")
        resp = implementation.crates_mapping(timeout=2*_TIMEOUT)
        self.assertEqual(resp, "")
        # Assert read_url was called correctly
        mock_read.assert_has_calls([
            mock.call(url, timeout=_TIMEOUT),
            mock.call(url, timeout=2*_TIMEOUT)])

    def test_bpms_data(self, mock_read):
        """Test bpms_data."""
        url = implementation._DIAG_FOLDER + 'bpms-data.txt'
        # Call with different parameters
        resp = implementation.bpms_data()
        self.assertEqual(resp, "FakeResponse")
        resp = implementation.bpms_data(timeout=2*_TIMEOUT)
        self.assertEqual(resp, "FakeResponse")
        # Assert read_url was called correctly
        mock_read.assert_has_calls([
            mock.call(url, timeout=_TIMEOUT),
            mock.call(url, timeout=2*_TIMEOUT)])

    def test_timing_devices_mapping(self, mock_read):
        """Test timing_devices_mapping."""
        url = implementation._TIMESYS_FOLDER + 'timing-devices-connection.txt'
        # Call with different parameters
        resp = implementation.timing_devices_mapping()
        self.assertEqual(resp, "FakeResponse")
        resp = implementation.timing_devices_mapping(timeout=2*_TIMEOUT)
        self.assertEqual(resp, "FakeResponse")
        # Assert read_url was called correctly
        mock_read.assert_has_calls([
            mock.call(url, timeout=_TIMEOUT),
            mock.call(url, timeout=2*_TIMEOUT)])

    def test_high_level_triggers(self, mock_read):
        """Test high_level_triggers."""
        url = implementation._TIMESYS_FOLDER + 'high-level-triggers.py'
        # Call with different parameters
        resp = implementation.high_level_triggers()
        self.assertEqual(resp, "FakeResponse")
        resp = implementation.high_level_triggers(timeout=2*_TIMEOUT)
        self.assertEqual(resp, "FakeResponse")
        # Assert read_url was called correctly
        mock_read.assert_has_calls([
            mock.call(url, timeout=_TIMEOUT),
            mock.call(url, timeout=2*_TIMEOUT)])

    def test_high_level_events(self, mock_read):
        """Test high_level_events."""
        url = implementation._TIMESYS_FOLDER + 'high-level-events.py'
        # Call with different parameters
        resp = implementation.high_level_events()
        self.assertEqual(resp, "FakeResponse")
        resp = implementation.high_level_events(timeout=2*_TIMEOUT)
        self.assertEqual(resp, "FakeResponse")
        # Assert read_url was called correctly
        mock_read.assert_has_calls([
            mock.call(url, timeout=_TIMEOUT),
            mock.call(url, timeout=2*_TIMEOUT)])
