"""Pulsed magnet field names."""
from siriuspy.pulsedps.properties import PulsedPowerSupplyAttrs

StrengthSP = "Strength-SP"
StrengthRB = "Strength-RB"
StrengthRefMon = "StrengthRef-Mon"
StrengthMon = "Strength-Mon"

PulsedMagnetAttrs = PulsedPowerSupplyAttrs + \
    [StrengthSP, StrengthRB, StrengthRefMon, StrengthMon]
