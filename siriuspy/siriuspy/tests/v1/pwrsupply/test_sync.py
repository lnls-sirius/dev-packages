#!/usr/bin/env python-sirius

"""Test Sync class."""
import unittest
from unittest import mock

import epics

from siriuspy.pwrsupply.sync import SyncWrite
from siriuspy.epics.computed_pv import ComputedPV
from siriuspy.epics.computed_pv import QueueThread


class SyncWritePutTest(unittest.TestCase):
    """Test sync write behaviour.

    Tests:
        - must put to all values
    """

    @mock.patch.object(epics.PV, "put", autospec=True)
    def test_put(self, mock_put):
        """Test put is called for all pvs."""
        sync = SyncWrite()
        pv = ComputedPV("FakePV", sync, QueueThread(), "fakepv-1", "fakepv-2")

        pv.put(10)

        calls = [mock.call(pv.pvs[0], 10), mock.call(pv.pvs[1], 10)]
        mock_put.assert_has_calls(calls)


class SyncWriteUpdateCmdTest(unittest.TestCase):
    """Test sync write behaviour.

    Test `compute_update` beahaviour when the ComputedPV `value` is None
    Tests:
        - not puts are called
        - callback is called
    """

    @mock.patch.object(ComputedPV, "_issue_callback", autospec=True)
    @mock.patch.object(epics.PV, "put", autospec=True)
    def setUp(self, mock_put, mock_callback):
        """Set up a computed pv with syncing.

        Mocks the put epics methods and the `_set_limits` function in the
        SyncWrite interface.
        """
        # Create Mocks
        self.mock_put = mock_put
        self.mock_callback = mock_callback

        sync = SyncWrite(lock=True)
        self.pv = ComputedPV("FakePV", sync, QueueThread(),
                             "fakepv-1:Reset-Cmd", "fakepv-2:Reset-Cmd")
        # Issue update value
        self.initial_value = 0
        self.update_value = 1

        self.pv.value = self.initial_value
        self.pv.upper_disp_limit = 0  # avoid setting limits
        self.pv._update_value("fakepv-1:Reset-Cmd", self.update_value)

    def test_put_not_issued(self):
        """Test put is not issued."""
        self.mock_put.assert_not_called()

    def test_callback_issued(self):
        """Test update value when pv is of type Cmd."""
        # Callback is issued
        self.mock_callback.assert_called_with(
            self.pv, pvname="FakePV", **{"value": self.update_value})

    def test_value_changed(self):
        """Test value was set."""
        self.assertEqual(self.pv.value, self.update_value)


class SyncWriteUpdateWhenNoneTest(unittest.TestCase):
    """Test sync write behaviour.

    Test `compute_update` beahaviour when the ComputedPV `value` is None
    Tests:
        - calc limit when computed_pv limits are None
        - issue put when computed pv value is None
        - return value when computed pv value is None
    """

    @mock.patch.object(ComputedPV, "_issue_callback", autospec=True)
    @mock.patch.object(SyncWrite, "compute_limits", autospec=True)
    @mock.patch.object(epics.PV, "put", autospec=True)
    def setUp(self, mock_put, mock_limits, mock_callback):
        """Set up a computed pv with syncing.

        Mocks the put epics methods and the `_set_limits` function in the
        SyncWrite interface.
        """
        self.mock_put = mock_put
        self.mock_limits = mock_limits
        self.mock_callback = mock_callback

        sync = SyncWrite(lock=True)
        self.pv = ComputedPV("FakePV", sync, QueueThread(), "fakepv-1", "fakepv-2")
        # Issue update value
        self.update_value = 100
        self.pv._update_value("fakepv-2", self.update_value)

    def test_limits_set(self):
        """Test wether the limits are set when ComputedPV limits are None."""
        self.mock_limits.assert_called_with(self.pv.computer, self.pv)

    def test_puts_issued(self):
        """Test if SyncWrite forces value down when value is None.

        When one of the real pvs changes and the ComputedPV value is None, a
        put must be issued to all pvs.
        """
        calls = [mock.call(self.pv.pvs[0], self.update_value),
                 mock.call(self.pv.pvs[1], self.update_value)]
        self.assertEqual(self.mock_put.call_args_list, calls)

    def test_callback_issued(self):
        """Test a callback is issued.

        When one of the real pvs changes and the ComputedPV value is None, the
        new value must be set and a callback issued.
        """
        # Assert callback is issued
        self.mock_callback.assert_called_with(
            self.pv, pvname="FakePV", **{"value": self.update_value})

    def test_value_changed(self):
        """Test CopmutedPV value was set."""
        # Assert value was set to pv
        self.assertEqual(self.pv.value, self.update_value)


class SyncWriteUpdateValueChangedTest(unittest.TestCase):
    """Test sync write update behaviour when value changed.

    Tests:
        - put ComputedPV value to all pvs
        - do not issue callback
        - do not set ComputedPV value
    """

    @mock.patch.object(ComputedPV, "_issue_callback", autospec=True)
    @mock.patch.object(SyncWrite, "compute_limits", autospec=True)
    @mock.patch.object(epics.PV, "put", autospec=True)
    def setUp(self, mock_put, mock_limits, mock_callback):
        """Set up a computed pv with syncing.

        Mocks the put epics methods and the `_set_limits` function in the
        SyncWrite interface.
        """
        self.mock_put = mock_put
        self.mock_limits = mock_limits
        self.mock_callback = mock_callback

        sync = SyncWrite(lock=True)
        self.pv = ComputedPV("FakePV", sync, QueueThread(), "fakepv-1", "fakepv-2")
        # Issue update value
        self.initial_value = 99
        self.update_value = 100

        self.pv.value = self.initial_value
        self.pv.upper_disp_limit = 200
        self.pv._update_value("fakepv-2", self.update_value)

    def test_limits_not_set(self):
        """Test limits not called when it is already set."""
        self.mock_limits.assert_not_called()

    def test_puts_issued(self):
        """Test if SyncWrite forces value down when value is None.

        When one of the real pvs changes and the ComputedPV value is None, a
        put must be issued to all pvs with the current ComputedPV value.
        """
        calls = [mock.call(self.pv.pvs[0], self.initial_value),
                 mock.call(self.pv.pvs[1], self.initial_value)]
        self.assertEqual(self.mock_put.call_args_list, calls)

    def test_callback_issued(self):
        """Test a callback is issued.

        When one of the real pvs changes and the ComputedPV value is None, the
        new value must be set and a callback issued.
        """
        # Assert callback is issued
        self.mock_callback.assert_not_called()

    def test_value_not_changed(self):
        """Test value remains the same afted update value was called."""
        # Assert value was not set to pv
        self.assertEqual(self.pv.value, self.initial_value)


class SyncWriteUpdateValueNotChangedTest(unittest.TestCase):
    """Test sync write update behaviour when value did not changed.

    Tests:
        - do not put to any pv
        - do not issue callback
        - do not set ComputedPV value
    """

    @mock.patch.object(ComputedPV, "_issue_callback", autospec=True)
    @mock.patch.object(SyncWrite, "compute_limits", autospec=True)
    @mock.patch.object(epics.PV, "put", autospec=True)
    def setUp(self, mock_put, mock_limits, mock_callback):
        """Set up a computed pv with syncing.

        Mocks the put epics methods and the `_set_limits` function in the
        SyncWrite interface.
        """
        self.mock_put = mock_put
        self.mock_limits = mock_limits
        self.mock_callback = mock_callback

        sync = SyncWrite(lock=True)
        self.pv = ComputedPV("FakePV", sync, QueueThread(), "fakepv-1", "fakepv-2")
        # Issue update value
        self.initial_value = 99
        self.update_value = 100

        self.pv.value = self.initial_value
        self.pv.upper_disp_limit = 200
        self.pv._update_value("fakepv-2", self.update_value)

    def test_limits_not_set(self):
        """Test limits not called when it is already set."""
        self.mock_limits.assert_not_called()

    def test_puts_issued(self):
        """Test if SyncWrite forces value down when value is None.

        When one of the real pvs changes and the ComputedPV value is None, a
        put must be issued to all pvs with the current ComputedPV value.
        """
        calls = [mock.call(self.pv.pvs[0], self.initial_value),
                 mock.call(self.pv.pvs[1], self.initial_value)]
        self.assertEqual(self.mock_put.call_args_list, calls)

    def test_callback_issued(self):
        """Test a callback is issued.

        When one of the real pvs changes and the ComputedPV value is None, the
        new value must be set and a callback issued.
        """
        # Assert callback is issued
        self.mock_callback.assert_not_called()

    def test_value_not_changed(self):
        """Test value remains the same afted update value was called."""
        # Assert value was not set to pv
        self.assertEqual(self.pv.value, self.initial_value)


if __name__ == "__main__":
    unittest.main()
