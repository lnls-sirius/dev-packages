"""Time conversion module."""

from calendar import timegm as _timegm
from datetime import datetime as _datetime, timedelta as _timedelta

import numpy as _np

from .exceptions import TypeError as _TypeError


class Time(_datetime):
    """Time conversion class.

    Usage options:
        Time(timestamp)
            timestamp is a float/int keyword/positional argument.

        Time(timestamp_string)
        Time(timestamp_string, timestamp_format='%Y-%m-%d %H:%M:%S.%f')
            timestamp_string is a str keyword/positional argument.
            timestamp_format is an optional keyword argument for string
                formating. Defaults to '%Y-%m-%d %H:%M:%S.%f'.

        Time(year, month, day)
        Time(year, month, day, hour)
        Time(year, month, day, hour, minute)
        Time(year, month, day, hour, minute, second)
        Time(year, month, day, hour, minute, second, microsecond)
        Time(year, month, day, hour, minute, second, microsecond, tzinfo)
            year, month, day, hour, minute, second, microsecond
                are integer keyword/positional arguments.
            tzinfo must be None or of a tzinfo subclass keyword/positional
                argument.
    """

    _DEFAULT_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
    _DATETIME_ARGS = {
        'year',
        'month',
        'day',
        'hour',
        'minute',
        'second',
        'microsecond',
        'tzinfo',
    }

    def __new__(cls, *args, **kwargs):
        """New object."""
        if not args and not kwargs:
            raise _TypeError(
                'no arguments found to build Time object'
            )
        if len(args) == 1:
            if isinstance(args[0], (float, int)):
                return Time.fromtimestamp(args[0])
            if isinstance(args[0], str):
                timestamp_format = (
                    kwargs['timestamp_format']
                    if 'timestamp_format' in kwargs
                    else Time._DEFAULT_TIMESTAMP_FORMAT
                )
                return Time.strptime(args[0], timestamp_format)
            raise _TypeError(
                f'argument of unexpected type {type(args[0])}'
            )

        if len(kwargs) == 1:
            if 'timestamp' in kwargs:
                return Time.fromtimestamp(kwargs['timestamp'])
            if 'timestamp_string' in kwargs:
                return Time.strptime(
                    kwargs['timestamp_string'], Time._DEFAULT_TIMESTAMP_FORMAT
                )
            if set(kwargs.keys()) & Time._DATETIME_ARGS:
                raise _TypeError(
                    'missing input arguments, verify usage options.'
                )
            raise _TypeError(f'unexpected key argument {kwargs}')

        if len(kwargs) == 2:
            if set(kwargs.keys()) == {'timestamp_string', 'timestamp_format'}:
                return Time.strptime(
                    kwargs['timestamp_string'], kwargs['timestamp_format']
                )
            if set(kwargs.keys()) & Time._DATETIME_ARGS:
                raise _TypeError(
                    'missing input arguments, verify usage options.'
                )
            raise _TypeError(
                f'unexpected key arguments {list(kwargs.keys())}'
            )
        return super().__new__(cls, *args, **kwargs)

    def get_iso8601(self):
        """Get iso8601 format."""
        return self.astimezone().isoformat()

    def __add__(self, other):
        """Addition."""
        if isinstance(other, _datetime):
            return super().__add__(other)
        if isinstance(other, (float, int)):
            add = super().__add__(_timedelta(seconds=other))
        else:
            add = super().__add__(other)
        return Time(timestamp=add.timestamp())

    def __sub__(self, other):
        """Subtraction."""
        if isinstance(other, _datetime):
            return super().__sub__(other)
        if isinstance(other, (float, int)):
            sub = super().__sub__(_timedelta(seconds=other))
        else:
            sub = super().__sub__(other)
        return Time(timestamp=sub.timestamp())

    @staticmethod
    def conv_to_epoch(time, datetime_format):
        """Get epoch from datetime."""
        utc_time = _datetime.strptime(time, datetime_format)
        epoch_time = _timegm(utc_time.timetuple())
        return epoch_time


def get_time_intervals(
    time_start: Time, time_stop: Time, interval: int, return_isoformat=False
):
    """Break `time_start` to `time_stop` in intervals of `interval` seconds.

    Args:
        time_start (Time): start time.
        time_stop (Time): stop time.
        interval (int): interval duration in seconds.
        return_isoformat (bool): return in iso8601 format.

    Returns:
        start_time (Time|str | list[Time|str]): start times.
        stop_time (Time|str | list[Time|str]): stop times.
    """
    t_start = time_start.timestamp()
    t_stop = time_stop.timestamp()
    t_start = _np.arange(t_start, t_stop, interval)
    t_stop = _np.r_[t_start[1:], t_stop]
    t_start = [Time(t) for t in t_start]
    t_stop = [Time(t) for t in t_stop]
    if return_isoformat:
        t_start = [t.get_iso8601() for t in t_start]
        t_stop = [t.get_iso8601() for t in t_stop]
    if len(t_start) == 1:
        return t_start[0], t_stop[0]
    return t_start, t_stop
