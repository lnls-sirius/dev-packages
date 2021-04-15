"""Time conversion module."""

from datetime import datetime as _datetime, timedelta as _timedelta


class Time(_datetime):
    """Time conversion class."""

    def __new__(cls, year=None, month=None, day=None,
                hour=None, minute=0, second=0, microsecond=0,
                timestamp=None,
                timestamp_string=None, timestamp_format=None):
        """New."""
        if timestamp:
            if not isinstance(timestamp, float):
                raise TypeError("Expected an argument of type 'float'.")
            return Time.fromtimestamp(timestamp)
        if timestamp_string:
            if not isinstance(timestamp_string, str):
                raise TypeError("Expected an argument of type 'str'.")
            return Time.strptime(
                timestamp_string, '%Y-%m-%d %H:%M:%S.%f'
                if timestamp_format is None else timestamp_format)
        return super().__new__(
            cls, year, month, day, hour, minute, second, microsecond)

    def get_iso8601(self):
        """Get iso8601 format."""
        return self.astimezone().isoformat()

    def __add__(self, other):
        """Addition."""
        if isinstance(other, _datetime):
            add = super().__add__(other)
            return add
        if isinstance(other, (float, int)):
            add = super().__add__(_timedelta(seconds=other))
        else:
            add = super().__add__(other)
        return Time(timestamp=add.timestamp())

    def __sub__(self, other):
        """Subtraction."""
        if isinstance(other, _datetime):
            sub = super().__sub__(other)
            return sub
        if isinstance(other, (float, int)):
            sub = super().__sub__(_timedelta(seconds=other))
        else:
            sub = super().__sub__(other)
        return Time(timestamp=sub.timestamp())
