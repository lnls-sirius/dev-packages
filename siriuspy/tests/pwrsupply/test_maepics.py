#!/usr/bin/env python-sirius
"""Test public API of PowerSupply/Magnet class."""

from unittest import mock, TestCase

from siriuspy.bsmp import SerialError
from siriuspy.pwrsupply import maepics
from siriuspy.csdevice.pwrsupply import get_ps_propty_database
from siriuspy.util import check_public_interface_namespace


mock_read = [
    8579, 6.7230000495910645, 6.7230000495910645,
    [b'S', b'i', b'm', b'u'], 5, 8617, 0, 2, 1, 0.0, 0.0, 1.0, 0.0,
    [1.0, 1.0, 1.0, 0.0], 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0, 0, 0,
    6.722831726074219, 1.23291015625, 5.029296875, 53.0]


def mock_splims(pstype, label):
    """Return limits value."""
    if label in ('lolo', 'low', 'lolim'):
        return 0.0
    else:
        return 165.0


public_interface = (
    'PSCommInterface',
    'PSEpics',
    'MAEpics',
)


class TestModule(TestCase):
    """Test Module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = check_public_interface_namespace(maepics, public_interface)
        self.assertTrue(valid)
