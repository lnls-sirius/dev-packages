#!/usr/bin/env python-sirius

"""Unittest module for envars.py."""

from unittest import TestCase
import siriuspy.envars as envars
import siriuspy.util as util

DIRS = (
    'DIR_ROOT',
    'DIR_EPICS_BASE',
    'DIR_SIRIUS',
    'DIR_FACS',
    'DIR_IMAS',
    'DIR_SIRIUS_CODE',
    'DIR_FACS_CODE',
    'DIR_SIRIUS_CODE_CSCNSTS',
    'DIR_SIRIUS_CODE_SIRIUSPY',
    'DIR_SIRIUS_CODE_HLA')
SRVURLS = (
    'SRVURL_RBACAUTH',
    'SRVURL_RBAC',
    'SRVURL_NS',
    'SRVURL_CCDB',
    'SRVURL_CABLES',
    'SRVURL_CSCONSTS',
    'SRVURL_CSCONSTS_2',
    'SRVURL_LOGBOOK',
    'SRVURL_CONFIGDB',
    'SRVURL_CONFIGDB_2',
    'SRVURL_ARCHIVER')
PUB_INTERFACE = DIRS + SRVURLS + ('VACA_PREFIX', )


class TestEnvars(TestCase):
    """Test envars."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(envars, PUB_INTERFACE)
        self.assertTrue(valid)

    def test_dirs(self):
        """Test folder names."""
        for folder in DIRS:
            self.assertIn(folder, envars.__dict__)
            value = getattr(envars, folder)
            self.assertIsInstance(value, str)

    def test_srvurls(self):
        """Test server names."""
        for server in SRVURLS:
            self.assertIn(server, envars.__dict__)
            value = getattr(envars, server)
            self.assertIsInstance(value, str)

    def test_vaca(self):
        """VACA prefix string."""
        self.assertIn('VACA_PREFIX', envars.__dict__)
        value = getattr(envars, 'VACA_PREFIX')
        self.assertIsInstance(value, str)
