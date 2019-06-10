"""Timestamp module."""


import datetime as _datetime


class TimeStamp(_datetime):
    """TimeStamp class."""

    pass
    # @property
    # def timestamp(self):
    #     """Return timestamp string."""
    #     return self._get_timestamp()
    #
    # def _get_timestamp(self):
    #     fmt = '{:04d}-{:02d}-{:02d}T{:02d}%3A{:02d}%3A{:06.3f}Z'
    #     ts = fmt.format(
    #         str(self._year), str(self._month), str(self._day),
    #         str(self._hour), str(self._minute), str(self._second),
    #     )
    #     return ts
