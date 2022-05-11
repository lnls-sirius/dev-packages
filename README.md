
[![Test siriuspy](https://github.com/lnls-sirius/dev-packages/actions/workflows/test-siriuspy.yml/badge.svg)](https://github.com/lnls-sirius/dev-packages/actions/workflows/test-siriuspy.yml)

![Latest tag](https://img.shields.io/github/tag/lnls-sirius/dev-packages.svg?style=flat)
[![Latest release](https://img.shields.io/github/release/lnls-sirius/dev-packages.svg?style=flat)](https://github.com/lnls-sirius/dev-packages/releases)
[![PyPI version fury.io](https://badge.fury.io/py/siriuspy.svg)](https://pypi.python.org/pypi/siriuspy/)

# Dev-packages

Python packages useful for the development of the Sirius control system.

| Packages | Description |
| -------- | ----------- |
| `siriuspy` | Sirius control system classes and utility functions used in HLA and IOC applications.

---

## siriuspy

### Subpackages and modules

* ```siriuspy.bsmp``` - BSMP functionalities.
* ```siriuspy.clientarch``` - Retrieve data from epics archiver.
* ```siriuspy.clientconfigdb``` - Client-side library to interact with Sirius configuration server.
* ```siriuspy.servweb``` - Functions to retrieve data from the static table server.
* ```siriuspy.currinfo``` - Classes for Sirius current information.
* ```siriuspy.cycle``` - Classes for magnet cycling.
* ```siriuspy.devices``` - Classes that implement epics devices.
* ```siriuspy.diagbeam``` - Classes for Beam diagnostics
* ```siriuspy.epics``` - Auxiliary classes for epics functionalities.
* ```siriuspy.machshift``` - Machine shift classes.
* ```siriuspy.magnet``` - Classes and structures useful to represent magnet properties.
* ```siriuspy.meas``` - Beam measurements classes.
* ```siriuspy.namesys``` - Functionalities to deal with names for Sirius naming system.
* ```siriuspy.optics``` - Constants, functions and data related to Sirius beam optics.
* ```siriuspy.opticscorr``` - Optical corrections.
* ```siriuspy.posang``` - Position and Angle corrections.
* ```siriuspy.ramp``` - Library used to perform booster ramp operations.
* ```siriuspy.search``` - Search methods for various data structures retrieved from the static tables of the control system constants server.
* ```siriuspy.sofb``` - Classes for Slow Orbit Feedback system. 
* ```siriuspy.timesys``` - Functionalities related to Sirius timing subsystem.
* ```siriuspy.callbacks.py``` - (module) Implementation of general function callback mechanism similar to Epics PV callbacks.
* ```siriuspy.csdev.py``` - (module) General control system device funcstion adn data structures.
* ```siriuspy.envars.py``` - (module) Configuration of environment variables.
* ```siriuspy.thread.py``` - (module) Thread classes.
* ```siriuspy.util.py``` - General useful functions and constants


### Prerequisites

See the repository's  [requirements.txt](siriuspy/requirements.txt) file.

### Installation

``` bash
cd siriuspy
./setup.py install
```

### Unittests

Before making pull-requests to ```master``` branch, unittests can be run.

* To run all integration unittests, issue the following commands
  ``` bash
  cd sirius 
  pytest tests/
  ```

 * To run unittests for specific  subpackages or modules, for example, issue
   ``` bash
   cd siriuspy
   pytest tests/devices/
   pytest tests/pwrsupply/test_csdev.py
   ```

  ---

