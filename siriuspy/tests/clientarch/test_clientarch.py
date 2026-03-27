#!/usr/bin/env python-sirius

"""Test the archiver client class."""
import datetime
from unittest import TestCase

from siriuspy.clientarch.time import get_time_intervals, Time


class TestClientArchTime(TestCase):
    """Test update and delete config meets requirements."""

    def test_constructor(self):
        """Test api."""
        tz_local = datetime.datetime.now().astimezone().tzinfo
        tim_dt = datetime.datetime(2025, 1, 8, 10, 13, 14, 4587, tz_local)
        tim_dt_naive = datetime.datetime(2025, 1, 8, 10, 13, 14, 4587)
        try:

            tim_naive = Time(2025, 1, 8)
            tim_naive = Time(2025, 1, 8, 10)
            tim_naive = Time(2025, 1, 8, 10, 13)
            tim_naive = Time(2025, 1, 8, 10, 13, 14)
            tim_naive = Time(2025, 1, 8, 10, 13, 14, 4587)

            tim_ts1 = Time(tim_naive.timestamp())
            tim_ts2 = Time(tim_naive.strftime(
                tim_naive._DEFAULT_TIMESTAMP_FORMAT)
            )
            tim_ts3 = Time(tim_naive.get_iso8601())
            tim_ts4 = Time(tim_dt_naive)
            tim_ts5 = Time(tim_dt)
        except Exception as err:
            self.fail(err)

        self.assertEqual(tim_ts1, tim_naive)
        self.assertEqual(tim_ts2, tim_naive)
        self.assertNotEqual(tim_ts3, tim_naive)
        self.assertEqual(tim_ts4, tim_naive)
        self.assertNotEqual(tim_ts5, tim_naive)

        tz_info = datetime.timezone(datetime.timedelta(seconds=-3600))
        try:
            tim = Time(2025, 1, 8, 10, 13, 14, 4587, tz_info)
            tim = Time(2025, 1, 8, tzinfo=tz_info)
            tim = Time(2025, 1, 8, 10, tzinfo=tz_info)
            tim = Time(2025, 1, 8, 10, 13, tzinfo=tz_info)
            tim = Time(2025, 1, 8, 10, 13, 14, tzinfo=tz_info)
            tim = Time(2025, 1, 8, 10, 13, 14, 4587, tzinfo=tz_info)

            tim_ts1 = Time(tim_naive.timestamp(), tzinfo=tz_info)
            tim_ts2 = Time(
                tim_naive.strftime(tim_naive._DEFAULT_TIMESTAMP_FORMAT),
                tzinfo=tz_info
            )
            tim_ts3 = Time(tim_naive.get_iso8601(), tzinfo=tz_info)
            tim_ts4 = Time(tim_dt)
            tim_ts5 = Time(tim_dt, tzinfo=tz_info)
        except Exception as err:
            self.fail(err)

        self.assertNotEqual(tim, tim_naive)
        self.assertEqual(tim_ts1, tim)
        self.assertEqual(tim_ts2, tim)
        self.assertEqual(tim_ts3, tim)
        self.assertNotEqual(tim_ts4, tim)
        self.assertEqual(tim_ts5, tim)

        with self.assertRaises(ValueError):
            Time('2025-01-ladieno')
        with self.assertRaises(TypeError):
            Time((tim, ))
        ts_int = tim.timestamp()
        ts_str = tim.get_iso8601()
        with self.assertRaises(TypeError):
            Time(ts_int, timestamp=ts_int)
        with self.assertRaises(TypeError):
            Time(ts_str, timestamp=ts_str)
        with self.assertRaises(TypeError):
            Time(ts_int, timestamp_string=ts_int)
        with self.assertRaises(TypeError):
            Time(ts_str, timestamp=ts_int)
        with self.assertRaises(TypeError):
            Time(timestamp=ts_int, timestamp_string=ts_str)
        with self.assertRaises(TypeError):
            Time(timestamp_string=ts_int)
        with self.assertRaises(TypeError):
            Time(timestamp=ts_str)

    def test_get_time_intervals(self):
        """Test get_time_intervals."""
        time_start = Time(2026, 1, 13, 0, 0, 0, 345)
        time_stop = time_start + 24*3600
        interval = 3600*10

        tst_corr = [
            '2026-01-13T00:00:00.000345-03:00',
            '2026-01-13T10:00:00.000345-03:00',
            '2026-01-13T20:00:00.000345-03:00'
        ]
        tsp_corr = [
            '2026-01-13T10:00:00.000345-03:00',
            '2026-01-13T20:00:00.000345-03:00',
            '2026-01-14T00:00:00.000345-03:00'
        ]
        tst, tsp = get_time_intervals(
            time_start, time_stop, interval, return_isoformat=True
        )
        self.assertEqual(tst, tst_corr)
        self.assertEqual(tsp, tsp_corr)

        tst_corr = [Time(t) for t in tst_corr]
        tsp_corr = [Time(t) for t in tsp_corr]
        tst, tsp = get_time_intervals(
            time_start, time_stop, interval, return_isoformat=False
        )
        self.assertEqual(tst, tst_corr)
        self.assertEqual(tsp, tsp_corr)

        time_stop = time_start + 4*3600
        tst, tsp = get_time_intervals(
            time_start, time_stop, interval, return_isoformat=False
        )
        self.assertEqual(tst, time_start)
        self.assertEqual(tsp, time_stop)
