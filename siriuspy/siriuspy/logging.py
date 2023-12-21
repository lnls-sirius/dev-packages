import sys as _sys
import logging
import inspect as _inspect


def get_logger(obj=None):
    """Get the appropriate logger for object 'obj'."""
    if isinstance(obj, str):
        return logging.getLogger(obj)
    elif obj is None:
        return logging.getLogger()

    mod = _inspect.getmodule(obj)
    if mod is not None:
        return logging.getLogger(mod.__name__)

    get_logger(get_logger).warning(
        'Could not resolve logger name. Returning root logger.'
    )
    return logging.getLogger()


def configure_logging(stream=None, filename=None, debug=False):
    """Configure logging messages for the IOCs."""
    if filename is not None:
        hand = logging.FileHandler(filename=filename, mode='w')
    else:
        stream = stream or _sys.stdout
        hand = logging.StreamHandler(stream)

    level = logging.DEBUG if debug else logging.INFO
    fmt = ('%(levelname)7s | %(asctime)s | ' +
           '%(module)15s.%(funcName)-20s[%(lineno)4d] ::: %(message)s')

    hand.setLevel(level)
    hand.setFormatter(logging.Formatter(fmt=fmt, datefmt='%F %T'))
    root = logging.getLogger()
    root.addHandler(hand)
    root.setLevel(level)


class LogMonHandler(logging.Handler):
    """Class intented to run callback to update 'Log-Mon' PVs."""

    def __init__(self, callback, level=logging.INFO):
        """Object that calls 'callback' to update 'Log-Mon'PVs."""
        self.callback = callback
        super().__init__(level)
        self.addFilter(self._filter_only_ioc)

    def emit(self, record):
        """."""
        msg = self.format(record)
        if record.levelno >= logging.ERROR:
            msgs = ['ERR:'+msg[i:i+35] for i in range(0, len(msg), 35)]
        elif record.levelno >= logging.WARNING:
            msgs = ['WARN:'+msg[i:i+34] for i in range(0, len(msg), 34)]
        else:
            msgs = [msg[i:i+39] for i in range(0, len(msg), 39)]
        for msg in msgs:
            self.callback(msg)

    @staticmethod
    def _filter_only_ioc(record):
        """Do not show in PV log messages destined only to IOC logs."""
        extra = 'ioc_only'
        return not (hasattr(record, extra) and bool(getattr(record, extra)))
