#!/usr/bin/env python-sirius

"""Unittest module for envars.py."""

from unittest import TestCase
import siriuspy.envars as envars
import siriuspy.util as util

folders = (
    'folder_root',
    'folder_epics_base',
    'folder_lnls_sirius',
    'folder_lnls_fac',
    'folder_lnls_ima',
    'folder_fac_code',
    'folder_fac_data',
    'folder_lnls_sirius_csslnls',
    'folder_lnls_sirius_discs',
    'folder_lnls_sirius_csconstants',
    'folder_lnls_sirius_dev_packages',
    'folder_lnls_sirius_hla',
)
servers = (
    'server_url_rbac_auth',
    'server_url_rbac',
    'server_url_ns',
    'server_url_ccdb',
    'server_url_cables',
    'server_url_consts',
    'server_url_logbook',
    'server_url_configdb',
)
misc = (
    'org_folders',
    'repo_names',
    '__loader__',
    '_os',
    '__doc__',
    '__cached__',
    '__name__',
    '__spec__',
    '__package__',
    '__builtins__',
    '__file__',
)

public_interface = folders + servers + \
                  ('vaca_prefix', 'org_folders', 'repo_names')


class TestEnvars(TestCase):
    """Test envars."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(envars, public_interface)
        self.assertTrue(valid)

    def test_folders(self):
        """Test folder names."""
        for folder in folders:
            self.assertIn(folder, envars.__dict__)
            value = getattr(envars, folder)
            self.assertIsInstance(value, str)

    def test_servers(self):
        """Test server names."""
        for server in servers:
            self.assertIn(server, envars.__dict__)
            value = getattr(envars, server)
            self.assertIsInstance(value, str)

    def test_vaca(self):
        """VACA prefix string."""
        self.assertIn('vaca_prefix', envars.__dict__)
        value = getattr(envars, 'vaca_prefix')
        self.assertIsInstance(value, str)
