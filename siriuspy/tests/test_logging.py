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
    'get_logger',
    'configure_logging',
    'LogMonHandler',
    )


class TestLogging(TestCase):
    """Test logging."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(mylog, PUB_INTERFACE)
        self.assertTrue(valid)

    def test_configure_logging(self):
        """Test configure_logging."""
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
