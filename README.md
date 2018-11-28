
[![Build Status](https://travis-ci.org/lnls-sirius/dev-packages.svg?branch=master)](https://travis-ci.org/lnls-sirius/dev-packages)

# Dev-packages

Python packages useful for the development of the Sirius control system.

| Packages | Description |
| -------- | ----------- |
| `siriuspy` | Sirius control system classes and utility functions used in HLA and IOC applications.
| `siriusdm` | Sirius extensions of PyDM. |

---

## siriuspy

### Subpackages and modules

* ```siriuspy.bsmp``` - Implementation of BSMP functionalities.
* ```siriuspy.csdevice``` - Property database definitions for devices of the control system.
* ```siriuspy.diagnostics``` - Data structure corresponding to diagnostics elements.devices of the control system.
* ```siriuspy.epics``` - Auxiliary classes for epics functionalities.
* ```siriuspy.magnet``` - Classes and structures useful to represent magnet properties.
* ```siriuspy.mathphys``` - Mathematical and physics constants and calculations.
* ```siriuspy.namesys``` - Functionalities to deal with names for Sirius naming system.
* ```siriuspy.optics``` - Constants, functions and data related to Sirius beam optics.
* ```siriuspy.pwrsupply``` - Modules implementing representation of magnet power supplies.
* ```siriuspy.ramp``` - Library used to perform booster ramp operations.
* ```siriuspy.search``` - Search methods for various data structures retrieved  from the static tables server.
* ```siriuspy.servconf``` - Client-side library to interact with Sirius configuration server.static tables server.
* ```siriuspy.servweb``` - Functions to retrieve data from the static table server.configuration server.static tables server.
* ```siriuspy.timesys``` - Functionalities related to Sirius timing subsystem.
* ```siriuspy.envars.py``` - (module) Configuration of environment variables.
* ```siriuspy.util.py``` - (module) General useful functions and constants
* ```siriuspy.factory.py``` - (module) Factories for various types of class objects.
* ```siriuspy.callbacks.py``` - (module) Implementation of general function callback mechanism similar to Epics PV callbacks.


### Prerequisites

See the repository's  [requirements.txt](requirements.txt) file.

### Installation

``` bash
cd siriuspy
./setup.py install
```

### Unittests

Before making pull-requests to ```master``` branch, unittests can be run.

* To run all integration unittests, issue the following commands
  ``` bash
  cd siriuspy
  ./setup.py test
  ```

 * To run unittests for specific  subpackages or modules, for example, issue
   ``` bash
   cd siriuspy
   ./setup.py test -s tests.csdevice
   ./setup.py test -s tests.csdevice.test_pwrsupply
   ```

  ---

## siriusdm

### Prerequisites

### Installation

### Unittests
