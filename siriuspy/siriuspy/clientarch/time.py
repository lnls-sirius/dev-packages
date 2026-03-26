"""Time conversion module."""

from calendar import timegm as _timegm
from datetime import datetime as _datetime, timedelta as _timedelta

import numpy as _np


class Time(_datetime):
    """Time class."""

    _DEFAULT_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __new__(cls, *args, **kwargs):  # noqa: D417, C901
        """Create Time object.

        Usage options:

        Time(datetime)
            datetime is a keyword/positional argument of datetime|Time class.
        Time(timestamp)
            timestamp is a float|int keyword/positional argument.

        Time(timestamp_string)
        Time(timestamp_string, timestamp_format='%Y-%m-%d %H:%M:%S.%f')
            `timestamp_string` is a str keyword/positional argument.
            `timestamp_format` is an optional keyword argument for string
                formating. Defaults to '%Y-%m-%d %H:%M:%S.%f' or iso8601.

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

        Any of the above options (apart from the last) can be used with an
        additional keyword argument for `tzinfo`.

        Args:
            datetime (datetime|Time): keyword/positional argument.
            timestamp (float|int): keyword/positional argument.
            timestamp_string (str): keyword/positional argument.
            timestamp_format (str): keyword argument for string formating.
            year (int): keyword/positional argument.
            month (int): keyword/positional argument.
            day (int): keyword/positional argument.
            hour (int): keyword/positional argument.
            minute (int): keyword/positional argument.
            second (int): keyword/positional argument.
            microsecond (int): keyword/positional argument.
            tzinfo (tzinfo): keyword/positional argument. Defaults to None.
        """
        if not args and not kwargs:
            raise TypeError('no arguments found to build Time object')
        if len(args) == 1:
            arg = args[0]
            dic_ = {
                'timestamp': (int, float),
                'timestamp_string': (str,),
                'datetime': (_datetime,),
            }
            if not isinstance(arg, sum(dic_.values(), ())):
                raise TypeError(f'Argument of unexpected type {type(arg)}')

            for key, typ in dic_.items():
                if isinstance(arg, typ) and key not in kwargs:
                    kwargs[key] = arg
                    break
            else:
                raise TypeError(
                    'Conflicting positional and keyword arguments.'
                )

            if not {'timestamp', 'timestamp_string'} - kwargs.keys():
                raise TypeError(
                    'Conflicting positional and keyword arguments.'
                )
        elif len(args) == 8:
            if 'tzinfo' in kwargs:
                raise TypeError(
                    'Conflicting positional and keyword arguments.'
                )
            kwargs['tzinfo'] = args[7]
            args = args[:7]

        tim = None
        if 'datetime' in kwargs:
            tim = Time.fromtimestamp(kwargs['datetime'].timestamp())
        elif 'timestamp' in kwargs:
            tim = Time.fromtimestamp(kwargs['timestamp'])
        elif 'timestamp_string' in kwargs:
            ts_fmt = kwargs.get(
                'timestamp_format', Time._DEFAULT_TIMESTAMP_FORMAT
            )
            ts_str = kwargs['timestamp_string']
            try:
                tim = Time.strptime(ts_str, ts_fmt)
            except ValueError:
                return Time.fromisoformat(ts_str)
        else:
            tim = super().__new__(cls, *args, **kwargs)

        return tim.replace(kwargs.get('tzinfo', tim.tzinfo))

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
