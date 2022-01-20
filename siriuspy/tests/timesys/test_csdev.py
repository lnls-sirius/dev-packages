#!/usr/bin/env python-sirius

"""Unittest module for ll_database.py."""

from unittest import TestCase

from siriuspy import util
from siriuspy.timesys import csdev


PUB_INTERFACE = (
    'get_otp_database',
    'get_out_database',
    'get_afc_out_database',
    'get_evr_database',
    'get_eve_database',
    'get_afc_database',
    'get_fout_database',
    'get_event_database',
    'get_clock_database',
    'get_evg_database',
    'get_hl_trigger_database',
    'Const',
    'ETypes',
    )


class TestModule(TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(csdev, PUB_INTERFACE)
        self.assertTrue(valid)

    def test_get_otp_database(self):
        """Test get_otp_database."""
        # TODO: implement test!

    def test_get_out_database(self):
        """Test get_out_database."""
        # TODO: implement test!

    def test_get_afc_out_database(self):
        """Test get_afc_out_database."""
        # TODO: implement test!

    def test_get_evr_database(self):
        """Test get_evr_database."""
        # TODO: implement test!

    def test_get_eve_database(self):
        """Test get_eve_database."""
        # TODO: implement test!

    def test_get_afc_database(self):
        """Test get_afc_database."""
        # TODO: implement test!

    def test_get_fout_database(self):
        """Test get_fout_database."""
        # TODO: implement test!

    def test_get_event_database(self):
        """Test get_event_database."""
        # TODO: implement test!

    def test_get_clock_database(self):
        """Test get_clock_database."""
        # TODO: implement test!

    def test_get_evg_database(self):
        """Test get_evg_database."""
        # TODO: implement test!

    def test_get_hl_clock_database(self):
        """Test get_hl_clock_database."""
        # TODO: implement test!

    def test_get_hl_event_database(self):
        """Test get_hl_event_database."""
        # TODO: implement test!

    def test_get_hl_evg_database(self):
        """Test get_hl_evg_database."""
        # TODO: implement test!

    def test_get_hl_trigger_database(self):
        """Test get_hl_trigger_database."""
        # TODO: implement test!

    def test_events_hl2ll_map(self):
        """Test HL2LL_MAP."""
        # TODO: implement test!

    def test_events_ll2hl_map(self):
        """Test LL2HL_MAP."""
        # TODO: implement test!

    def test_events_ll_tmp(self):
        """Test LL_TMP."""
        # TODO: implement test!

    def test_events_hl_pref(self):
        """Test HL_PREF."""
        # TODO: implement test!

    def test_events_ll_codes(self):
        """Test LL_CODES."""
        # TODO: implement test!

    def test_events_ll_names(self):
        """Test LL_EVENTS."""
        # TODO: implement test!

    def test_events_modes(self):
        """Test MODES."""
        # TODO: implement test!

    def test_events_delay_types(self):
        """Test DELAY_TYPES."""
        # TODO: implement test!

    def test_clocks_states(self):
        """Test STATES."""
        # TODO: implement test!

    def test_clocks_ll_tmp(self):
        """Test LL_TMP."""
        # TODO: implement test!

    def test_clocks_hl_tmp(self):
        """Test HL_TMP."""
        # TODO: implement test!

    def test_clocks_hl_pref(self):
        """Test HL_PREF."""
        # TODO: implement test!

    def test_clocks_hl2ll_map(self):
        """Test HL2LL_MAP."""
        # TODO: implement test!

    def test_clocks_ll2hl_map(self):
        """Test LL2HL_MAP."""
        # TODO: implement test!

    def test_triggers_states(self):
        """Test STATES."""
        # TODO: implement test!

    def test_triggers_intlk(self):
        """Test INTLK."""
        # TODO: implement test!

    def test_triggers_polarities(self):
        """Test POLARITIES."""
        # TODO: implement test!

    def test_triggers_delay_types(self):
        """Test DELAY_TYPES."""
        # TODO: implement test!

    def test_triggers_src_ll(self):
        """Test SRC_LL."""
        # TODO: implement test!


class TestConst(TestCase):
    """Test Const class."""

    PUB_INTERFACE = (
        'AC_FREQUENCY',
        'RF_DIVISION',
        'RF_FREQUENCY',
        'BASE_FREQUENCY',
        'RF_PERIOD',
        'BASE_DELAY',
        'RF_DELAY',
        'FINE_DELAY',
        'EvtModes',
        'EvtDlyTyp',
        'ClockStates',
        'TrigStates',
        'TrigPol',
        'LowLvlLock',
        'TrigDlyTyp',
        'InInjTab',
        'TrigSrcLL',
        'EvtHL2LLMap',
        'EvtLL2HLMap',
        'EvtLL',
        'ClkHL2LLMap',
        'ClkLL2HLMap',
        'ClkLL',
        'HLTrigStatusLabels',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            csdev.Const, TestConst.PUB_INTERFACE)
        self.assertTrue(valid)
