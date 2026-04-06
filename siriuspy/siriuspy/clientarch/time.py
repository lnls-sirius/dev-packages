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
        if len(args) == 2:
            kwargs['tzinfo'] = args[1]
            args = args[:1]
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
        elif len(args) == 8:
            if 'tzinfo' in kwargs:
                raise TypeError(
                    'Conflicting positional and keyword arguments.'
                )
            kwargs['tzinfo'] = args[7]
            args = args[:7]

        if not {'timestamp', 'timestamp_string'} - kwargs.keys():
            raise TypeError('Conflicting positional and keyword arguments.')

        tz = kwargs.get('tzinfo')
        tzl = _datetime.now().astimezone().tzinfo
        if 'datetime' in kwargs:
            dtim = kwargs['datetime']
            tz = tz or dtim.tzinfo or tzl
            obj = super().fromtimestamp(dtim.timestamp(), tz=tz)
        elif 'timestamp' in kwargs:
            obj = super().fromtimestamp(kwargs['timestamp'], tz=tz or tzl)
        elif 'timestamp_string' in kwargs:
            ts_str = kwargs['timestamp_string']
            try:
                ts_fmt = kwargs.get(
                    'timestamp_format', Time._DEFAULT_TIMESTAMP_FORMAT
                )
                obj = (
                    super().strptime(ts_str, ts_fmt).replace(tzinfo=tz or tzl)
                )
            except ValueError:
                import sys as _sys
                if _sys.version_info <= (3, 8):
                    from dateutil import parser as _dateutil_parser
                    tim = _dateutil_parser.parse(ts_str)
                else:
                    tim = super().fromisoformat(ts_str)
                tz = tz or tim.tzinfo
                obj = super().fromtimestamp(tim.timestamp(), tz=tz)
        else:
            kwargs.setdefault('tzinfo', tzl)
            obj = super().__new__(cls, *args, **kwargs)

        # NOTE: This if is necessary for python versions prior to 3.9.
        # in this cases, calling super().fromtimestamp with tzinfo returns
        # an object of datetime class.
        if not isinstance(obj, cls):
            return super().__new__(
                cls,
                obj.year,
                obj.month,
                obj.day,
                obj.hour,
                obj.minute,
                obj.second,
                obj.microsecond,
                tzinfo=obj.tzinfo,
            )
        return obj

    def get_iso8601(self):
        """Get iso8601 format."""
        return self.astimezone(self.tzinfo).isoformat()

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
    time_start: Time,
    time_stop: Time,
    interval: int,
    return_isoformat=False,
    tzinfo=None,
):
    """Break `time_start` to `time_stop` in intervals of `interval` seconds.

    Args:
        time_start (Time): start time.
        time_stop (Time): stop time.
        interval (int|float|None): interval duration in seconds.
            If <= 0 or None, no splitting will be done.
        return_isoformat (bool): return in iso8601 format.
        tzinfo (tzinfo): timezone info. Defaults to None, which means using
            the timezone of `time_start`.

    Returns:
        start_time (Time|str | list[Time|str]): start times.
        stop_time (Time|str | list[Time|str]): stop times.
    """
    tzinfo = tzinfo or time_start.tzinfo
    t_start = time_start.timestamp()
    t_stop = time_stop.timestamp()
    if interval is None or interval <= 0:
        t_start = [t_start]
        t_stop = [t_stop]
    else:
        t_start = _np.arange(t_start, t_stop, int(interval))
        t_stop = _np.r_[t_start[1:], t_stop]
    t_start = [Time(t, tzinfo=tzinfo) for t in t_start]
    t_stop = [Time(t, tzinfo=tzinfo) for t in t_stop]
    if return_isoformat:
        t_start = [t.get_iso8601() for t in t_start]
        t_stop = [t.get_iso8601() for t in t_stop]
    if len(t_start) == 1:
        return t_start[0], t_stop[0]
    return t_start, t_stop
