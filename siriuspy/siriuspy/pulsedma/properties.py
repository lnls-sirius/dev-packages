"""Pulsed magnet field names."""
from siriuspy.pulsedps.properties import PulsedPowerSupplyAttrs

StrengthSP = "Kick-SP"
StrengthRB = "Kick-RB"
StrengthRefMon = "KickRef-Mon"
StrengthMon = "Kick-Mon"

PulsedMagnetAttrs = PulsedPowerSupplyAttrs + \
    [StrengthSP, StrengthRB, StrengthRefMon, StrengthMon]
