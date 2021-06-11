INSTALL - siriuspy
==================

This package can be installed using setuptools (>=16.0).
There is no automatic dependency checking, so read the list below and ensure necessary dependencies are available.
Developed and tested with Python 3 (3.4).


REQUIREMENTS
============


TESTS
=====

To run the unittest suite:
 ```command
   cd siriuspy
   ./setup.py test
```
To run a specific unittest subpacke:
```command
   cd siriuspy
   ./setup.py test -s tests.search
```

INSTALLATION
============

To install to a default Python directory, run
```command
    <python> setup.py install
```
Use the appropriate command in <python>. Depending on permissions, it may be
necessary to run the command with sudo or as superuser.

To install a development version, with a link to the local package files in the
default Python directory, run
```command
    <python> setup.py develop
```

Details and further options can be found in setuptools documentation.
