"""Time conversion module."""

from datetime import datetime as _datetime, timedelta as _timedelta


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
    _DATETIME_ARGS = {'year', 'month', 'day', 'hour', 'minute',
                      'second', 'microsecond', 'tzinfo'}

    def __new__(cls, *args, **kwargs):
        """New object."""
        if not args and not kwargs:
            raise TypeError('no arguments found to build Time object')
        if len(args) == 1:
            if isinstance(args[0], (float, int)):
                return Time.fromtimestamp(args[0])
            if isinstance(args[0], str):
                timestamp_format = \
                    kwargs['timestamp_format'] if 'timestamp_format'\
                    in kwargs else Time._DEFAULT_TIMESTAMP_FORMAT
                return Time.strptime(args[0], timestamp_format)
            raise TypeError(f'argument of unexpected type {type(args[0])}')
        if len(kwargs) == 1:
            if 'timestamp' in kwargs:
                return Time.fromtimestamp(kwargs['timestamp'])
            if 'timestamp_string' in kwargs:
                return Time.strptime(
                    kwargs['timestamp_string'], Time._DEFAULT_TIMESTAMP_FORMAT)
            if set(kwargs.keys()) & Time._DATETIME_ARGS:
                raise TypeError(
                    'missing input arguments, verify usage options.')
            raise TypeError(f'unexpected key argument {kwargs}')
        if len(kwargs) == 2:
            if set(kwargs.keys()) == {'timestamp_string', 'timestamp_format'}:
                return Time.strptime(
                    kwargs['timestamp_string'], kwargs['timestamp_format'])
            if set(kwargs.keys()) & Time._DATETIME_ARGS:
                raise TypeError(
                    'missing input arguments, verify usage options.')
            raise TypeError(f'unexpected key arguments {list(kwargs.keys())}')
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


def get_time_intervals(
        time_start, time_stop, interval, return_isoformat=False):
    """Return intervals of 'interval' duration from time_start to time_stop."""
    if time_start + interval >= time_stop:
        timestamp_start = time_start.get_iso8601() \
            if return_isoformat else time_start
        timestamp_stop = time_stop.get_iso8601() \
            if return_isoformat else time_stop
    else:
        t_start = time_start
        t_stop = t_start + interval
        timestamp_start = [t_start, ]
        timestamp_stop = [t_stop, ]
        while t_stop < time_stop:
            t_start += interval
            t_stop = t_stop + interval
            if t_stop + interval > time_stop:
                t_stop = time_stop
            timestamp_start.append(t_start)
            timestamp_stop.append(t_stop)
        if return_isoformat:
            timestamp_start = [t.get_iso8601() for t in timestamp_start]
            timestamp_stop = [t.get_iso8601() for t in timestamp_stop]
    return timestamp_start, timestamp_stop
