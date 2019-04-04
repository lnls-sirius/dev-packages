#!/usr/bin/env python-sirius

"""Unittest module for device_models.py."""

import unittest
# import re
# from unittest import mock

from siriuspy import util
from ...mock_servweb import MockServConf

mock_flag = True

public_interface = (
    'CallBack',
    'EVGIOC',
    'EVRIOC',
    'EVEIOC',
    'AMCFPGAEVRIOC',
    'FoutIOC',
)


class TestModule(MockServConf):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        from siriuspy.timesys.time_simul import device_models
        valid = util.check_public_interface_namespace(
                device_models,
                public_interface)
        self.assertTrue(valid)


class TestCallBack(MockServConf):
    """Test CallBack class."""

    public_interface = (
        'add_callback',
        'remove_callback',
    )

    def test_public_interface(self):
        """Test class public interface."""
        from siriuspy.timesys.time_simul import device_models
        valid = util.check_public_interface_namespace(
            device_models.CallBack, TestCallBack.public_interface)
        self.assertTrue(valid)

    def test_add_callback(self):
        """Test add_callback."""
        # TODO: implement test!
        pass

    def test_remove_callback(self):
        """Test remove_callback."""
        # TODO: implement test!
        pass


class TestEVGIOC(MockServConf):
    """Test EVGIOC class."""

    public_interface = (
        'get_database',
        'add_pending_devices_callback',
        'remove_pending_devices_callback',
        'add_injection_callback',
        'remove_injection_callback',
        'get_propty',
        'set_propty',
    )

    def test_public_interface(self):
        """Test class public interface."""
        from siriuspy.timesys.time_simul import device_models
        valid = util.check_public_interface_namespace(
            device_models.EVGIOC, TestEVGIOC.public_interface)
        self.assertTrue(valid)

    def test_get_database(self):
        """Test get_database."""
        # TODO: implement test!
        pass

    def test_add_pending_devices_callback(self):
        """Test add_pending_devices_callback."""
        # TODO: implement test!
        pass

    def test_remove_pending_devices_callback(self):
        """Test remove_pending_devices_callback."""
        # TODO: implement test!
        pass

    def test_add_injection_callback(self):
        """Test add_injection_callback."""
        # TODO: implement test!
        pass

    def test_remove_injection_callback(self):
        """Test remove_injection_callback."""
        # TODO: implement test!
        pass

    def test_get_propty(self):
        """Test get_propty."""
        # TODO: implement test!
        pass

    def test_set_propty(self):
        """Test set_propty."""
        # TODO: implement test!
        pass


class TestEVRIOC(MockServConf):
    """Test EVRIOC class."""

    public_interface = (
        'get_database',
        'get_propty',
        'set_propty',
        'receive_events',
    )

    def test_public_interface(self):
        """Test class public interface."""
        from siriuspy.timesys.time_simul import device_models
        valid = util.check_public_interface_namespace(
            device_models.EVRIOC, TestEVRIOC.public_interface)
        self.assertTrue(valid)

    def test_get_database(self):
        """Test get_database."""
        # TODO: implement test!
        pass

    def test_get_propty(self):
        """Test get_propty."""
        # TODO: implement test!
        pass

    def test_set_propty(self):
        """Test set_propty."""
        # TODO: implement test!
        pass

    def test_receive_events(self):
        """Test receive_events."""
        # TODO: implement test!
        pass


class TestEVEIOC(MockServConf):
    """Test EVEIOC class."""

    public_interface = (
        'get_database',
    )

    def test_public_interface(self):
        """Test class public interface."""
        from siriuspy.timesys.time_simul import device_models
        valid = util.check_public_interface_namespace(
            device_models.EVEIOC, TestEVEIOC.public_interface)
        self.assertTrue(valid)

    def test_get_database(self):
        """Test get_database."""
        # TODO: implement test!
        pass


class TestAMCFPGAEVRIOC(MockServConf):
    """Test AMCFPGAEVRIOC class."""

    public_interface = (
        'get_database',
    )

    def test_public_interface(self):
        """Test class public interface."""
        from siriuspy.timesys.time_simul import device_models
        valid = util.check_public_interface_namespace(
            device_models.AMCFPGAEVRIOC, TestAMCFPGAEVRIOC.public_interface)
        self.assertTrue(valid)

    def test_get_database(self):
        """Test get_database."""
        # TODO: implement test!
        pass


class TestFoutIOC(MockServConf):
    """Test FoutIOC class."""

    public_interface = (
        'get_database',
        'receive_events',
    )

    def test_public_interface(self):
        """Test class public interface."""
        from siriuspy.timesys.time_simul import device_models
        valid = util.check_public_interface_namespace(
            device_models.FoutIOC, TestFoutIOC.public_interface)
        self.assertTrue(valid)

    def test_get_database(self):
        """Test get_database."""
        # TODO: implement test!
        pass

    def test_receive_events(self):
        """Test receive_events."""
        # TODO: implement test!
        pass


if __name__ == "__main__":
    unittest.main()
