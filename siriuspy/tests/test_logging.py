#!/usr/bin/env python-sirius

"""Unittest module for util.py."""

from io import StringIO
import logging
from unittest import mock, TestCase
import numpy as np

import siriuspy.logging as mylog
import siriuspy.util as util


PUB_INTERFACE = (
    'logging',
    'print_ioc_banner',
    'configure_logging',
    )


class TestUtil(TestCase):
    """Test util."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(mylog, PUB_INTERFACE)
        self.assertTrue(valid)

    def test_configure_logging(self):
        """Test configure_log_file."""
        fil = StringIO()
        logging.root.handlers = []
        mylog.configure_logging(stream=fil)
        logging.info('test')
        logging.debug('test')
        text = fil.getvalue()
        self.assertEqual(len(text.splitlines()), 1)

        fil = StringIO()
        logging.root.handlers = []
        mylog.configure_logging(stream=fil, debug=True)
        logging.info('test')
        logging.debug('test')
        text = fil.getvalue()
        self.assertEqual(len(text.splitlines()), 2)
