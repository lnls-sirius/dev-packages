"""ClientArchiver Exception Classes."""

import asyncio as _asyncio
import urllib as _urllib


class ClientArchError(Exception):
    """ClientArch Abstract Exception."""


class AuthenticationError(ClientArchError):
    """ClientArch Authentication Exception."""


class TimeoutError(ClientArchError, _asyncio.TimeoutError):
    """ClientArch Timeout Exception."""


class RuntimeError(ClientArchError, RuntimeError):
    """ClientArch Runtime Exception."""


class TypeError(ClientArchError, TypeError):
    """ClientArch TypeError Exception."""
    

class IndexError(ClientArchError, IndexError):
    """ClientArch IndexError Exception."""
