# International System of Units
# =============================
# ref.: http://en.wikipedia.org/wiki/Si_system

from mathphys.base_units import *
import mathphys.constants as _constants
import math as _math

# Derived units
# =============
newton  = kilogram * meter / second
joule   = newton * meter
watt    = joule / second
coulomb = second * ampere
volt    = watt / ampere
weber   = volt * second
tesla   = weber / meter**2

radian                  = (meter / meter)
(mA,uA)                 = (1e-3,1e-6)
(km,cm,mm,um,nm)        = (1e3,1e-2,1e-3,1e-6,1e-9)
(rad,mrad,urad,nrad)    = (1e0,1e-3,1e-6,1e-9)
(minute,hour,day,year)  = (60,60*60,24*60*60,365.25*24*60*60)

electron_volt           = _constants.elementary_charge * volt
(eV,MeV,GeV)            = (electron_volt,electron_volt*1e6,electron_volt*1e9)

# conversions factors
# ===================
# conversion factors should be defined instead of conversion functions
# whenever possible. The reason is that it is more general since a
# conversion function over iterable would have to be defined, whereas some
# iterables (from numpy, for example) defines multiplication by scalar.

meter_2_mm = (meter / mm)
mm_2_meter = (mm / meter)
mrad_2_rad = (mrad / rad)
rad_2_mrad = (rad / mrad)
joule_2_eV = (joule / electron_volt)
radian_2_degree = (180.0/_math.pi)
degree_2_radian = (_math.pi/180.0)

# conversion functions
# ====================

def kelvin_2_celsius(x): return x - 273.15
def celcius_2_kelvin(x): return x + 273.15
