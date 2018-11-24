"""SI Units."""

# International System of Units
# =============================
# ref.: http://en.wikipedia.org/wiki/Si_system

from . import base_units as _u
from . import constants as _constants
import math as _math

# Derived units
# =============
newton = _u.kilogram * _u.meter / _u.second
coulomb = _u.second * _u.ampere
joule = newton * _u.meter
watt = joule / _u.second
volt = watt / _u.ampere
weber = volt * _u.second
tesla = weber / _u.meter**2
pascal = _u.kilogram / (_u.meter * _u.second**2)

radian = (_u.meter / _u.meter)
(mA, uA) = (1e-3, 1e-6)
(km, cm, mm, um, nm) = (1e3, 1e-2, 1e-3, 1e-6, 1e-9)
(rad, mrad, urad, nrad) = (1e0, 1e-3, 1e-6, 1e-9)
(minute, hour, day, year) = (60, 60*60, 24*60*60, 365.25*24*60*60)

electron_volt = _constants.elementary_charge * volt
(eV, MeV, GeV) = (electron_volt, electron_volt*1e6, electron_volt*1e9)

# conversions factors
# ===================
# conversion factors should be defined instead of conversion functions
# whenever possible. The reason is that it is more general since a
# conversion function over iterable would have to be defined, whereas some
# iterables (from numpy, for example) defines multiplication by scalar.

radian_2_degree = (180.0/_math.pi)
degree_2_radian = (_math.pi/180.0)

rad_2_mrad = (rad / mrad)
meter_2_mm = (_u.meter / mm)
joule_2_eV = (joule / electron_volt)
pascal_2_bar = pascal * 1.0e-5
eV_2_GeV = (eV / GeV)
joule_2_GeV = joule_2_eV * eV_2_GeV
ev_2_joule = 1.0 / joule_2_eV
GeV_2_eV = 1.0 / eV_2_GeV
mrad_2_rad = 1.0 / rad_2_mrad
mm_2_meter = 1.0 / meter_2_mm


# conversion functions
# ====================


def kelvin_2_celsius(x):
    """Convert kelvin to celcius."""
    return x - 273.15


def celcius_2_kelvin(x):
    """Convert celcius to kelvin."""
    return x + 273.15
