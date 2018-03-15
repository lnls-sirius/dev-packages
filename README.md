[![Build Status](https://travis-ci.org/lnls-sirius/dev-packages.svg?branch=master)](https://travis-ci.org/lnls-sirius/dev-packages)

# Development Packages for Sirius

Useful development packages for Sirius control system.

Packages:

* <code>siriuspy</code>: Sirius control system classes and utility functions used in user and machine applications.
* <code>siriusdm</code>: Sirius extensions of PyDM.

Integration tests:

* To run integration test for <code>siriuspy</code> before pull-requests, issue the following commands: 
  * cd siriuspy/tests
  * python-sirius -m unittest discover
