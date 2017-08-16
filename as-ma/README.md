# AS-MA Soft IOC

Software IOCs for magnet power supplies.

This IOC is supposed to be a middle-layer server that implements more stringent power supply limits that the low-level power supply IOCs and also converts current values to corresponding physics values, depending on the type of
magnet the power supply is connected. (kicks, energy, strengths)

installation:

 sudo ./setup.py develop
 cd systemd; sudo make install-services

 dependencies:

  siriuspy
  pyepics
