#!/usr/bin/env python-sirius

"""Test the configuration client class."""
from unittest import mock, TestCase
import json
from urllib.error import URLError

from siriuspy.clientconfigdb import ConfigDBClient, ConfigDBDocument, \
    ConfigDBException
import siriuspy.util as util


class TestConfigDBClient(TestCase):
    """Test update and delete config meets requirements."""

    api = {
        'config_type',
        "url",
        "connected",
        "get_dbsize",
        "get_nrconfigs",
        "get_config_types",
        "find_configs",
        "get_config_value",
        "get_config_info",
        "rename_config",
        "insert_config",
        "delete_config",
        "retrieve_config",
        "get_value_template",
        'check_valid_value',
        "get_config_types_from_templates",
        'check_valid_configname',
        "conv_timestamp_txt_2_flt",
        "conv_timestamp_flt_2_txt",
    }

    def test_api(self):
        """Test api."""
        valid = util.check_public_interface_namespace(
            ConfigDBClient, TestConfigDBClient.api)
        self.assertTrue(valid)

    # def test_exceptions(self):
    #     cdb = ConfigDBClient(url='http://nonexistent:80')
    #     self.assertRaises(ConfigDBException, cdb.get_config_types)
    #     self.assertRaises(ConfigDBException, cdb.get_dbsize)
    #     self.assertRaises(ConfigDBException, cdb.get_nrconfigs)
    #     self.assertRaises(
    #         ConfigDBException, cdb.find_configs, config_type='bla')


class TestConfigDBDocument(TestCase):
    """Test update and delete config meets requirements."""

    api = {
        'configdbclient',
        'url',
        'config_type',
        'connected',
        'name',
        'name',
        'info',
        'created',
        'modified',
        'modified_count',
        'discarded',
        'value',
        'value',
        'synchronized',
        'exist',
        'load',
        'save',
        'delete',
        'check_valid_value',
        'get_value_template',
        'generate_config_name',
    }

    def test_api(self):
        """Test api."""
        valid = util.check_public_interface_namespace(
            ConfigDBDocument, TestConfigDBDocument.api)
        self.assertTrue(valid)


class TestConfigServiceConTimestamp(TestCase):
    """Test response error handling."""

    def _test_conv_timestamp(self):
        """Test timestamp conversion."""
        # TODO: NOT WORKING ON TRAVIS
        samples = {
            ("Dec 11, 2017", 1512957600.0),
            ("12/11/2017", 1512957600.0),
            ("2017/12/11", 1512957600.0),
            ("2017-12-11", 1512957600.0),
            ("Dec 11 2017 14:00:00", 1513008000.0),
            ("12/11/2017 14:00:00", 1513008000.0),
            ("2017/12/11 14:00:00", 1513008000.0),
            ("2017-12-11 14:00:00", 1513008000.0),
            ("2017-12-11T14:00:00", 1513008000.0),
            ("2017-12-11 14:00:00+01:00", 1512997200.0),
            ("2017-12-11T14:00:00+01:00", 1512997200.0),
            ("2017-12-11T14:00:00.45", 1513008000.45),
        }

        for sample in samples:
            date_string = sample[0]
            timestamp = sample[1]
            self.assertEqual(
                ConfigDBClient.conv_timestamp_txt_2_flt(date_string),
                timestamp)
