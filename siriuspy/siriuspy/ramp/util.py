"""Ramp utility module."""

DEFAULT_RAMP_DURATION = 490.0  # [ms]

BO_INJECTION_ENERGY = 0.150  # [GeV]
BO_EJECTION_ENERGY = 3.0  # [GeV]

# nominal strength values
NOMINAL_STRENGTHS = {
    'SI-Fam:MA-B1B2': BO_EJECTION_ENERGY,  # [Energy: GeV]
    'SI-Fam:MA-QFA': +0.7146305692912001,  # [KL: 1/m]
    'SI-Fam:MA-QDA': -0.2270152048045000,  # [KL: 1/m]
    'SI-Fam:MA-QFB': +1.2344424683922000,  # [KL: 1/m]
    'SI-Fam:MA-QDB2': -0.4782973132726601,  # [KL: 1/m]
    'SI-Fam:MA-QDB1': -0.2808906119138000,  # [KL: 1/m]
    'SI-Fam:MA-QFP': +1.2344424683922000,  # [KL: 1/m]
    'SI-Fam:MA-QDP2': -0.4782973132726601,  # [KL: 1/m]
    'SI-Fam:MA-QDP1': -0.2808906119138000,  # [KL: 1/m]
    'SI-Fam:MA-Q1': +0.5631612043340000,  # [KL: 1/m]
    'SI-Fam:MA-Q2': +0.8684629376249999,  # [KL: 1/m]
    'SI-Fam:MA-Q3': +0.6471254242426001,  # [KL: 1/m]
    'SI-Fam:MA-Q4': +0.7867827142062001,  # [KL: 1/m]
    'SI-Fam:MA-SDA0': -12.1250549999999979,  # [SL: 1/m^2]
    'SI-Fam:MA-SDB0': -09.7413299999999996,  # [SL: 1/m^2]
    'SI-Fam:MA-SDP0': -09.7413299999999996,  # [SL: 1/m^2]
    'SI-Fam:MA-SDA1': -24.4479749999999996,  # [SL: 1/m^2]
    'SI-Fam:MA-SDB1': -21.2453849999999989,  # [SL: 1/m^2]
    'SI-Fam:MA-SDP1': -21.3459000000000003,  # [SL: 1/m^2]
    'SI-Fam:MA-SDA2': -13.3280999999999992,  # [SL: 1/m^2]
    'SI-Fam:MA-SDB2': -18.3342150000000004,  # [SL: 1/m^2]
    'SI-Fam:MA-SDP2': -18.3421500000000002,  # [SL: 1/m^2]
    'SI-Fam:MA-SDA3': -20.9911199999999987,  # [SL: 1/m^2]
    'SI-Fam:MA-SDB3': -26.0718599999999974,  # [SL: 1/m^2]
    'SI-Fam:MA-SDP3': -26.1236099999999993,  # [SL: 1/m^2]
    'SI-Fam:MA-SFA0': +7.8854400000000000,  # [SL: 1/m^2]
    'SI-Fam:MA-SFB0': +11.0610149999999994,  # [SL: 1/m^2]
    'SI-Fam:MA-SFP0': +11.0610149999999994,  # [SL: 1/m^2]
    'SI-Fam:MA-SFA1': +28.7742599999999982,  # [SL: 1/m^2]
    'SI-Fam:MA-SFB1': +34.1821950000000001,  # [SL: 1/m^2]
    'SI-Fam:MA-SFP1': +34.3873949999999979,  # [SL: 1/m^2]
    'SI-Fam:MA-SFA2': +22.6153800000000018,  # [SL: 1/m^2]
    'SI-Fam:MA-SFB2': +29.6730900000000020,  # [SL: 1/m^2]
    'SI-Fam:MA-SFP2': +29.7755099999999970,  # [SL: 1/m^2]
    'BO-Fam:MA-B': BO_INJECTION_ENERGY,  # [Energy: GeV]
    'BO-Fam:MA-QD': +0.0011197961538728,  # [KL: 1/m]
    'BO-Fam:MA-QF': +0.3770999232791374,  # [KL: 1/m]
    'BO-Fam:MA-SD': +0.5258382119529604,  # [SL: 1/m^2]
    'BO-Fam:MA-SF': +1.1898514030258744,  # [SL: 1/m^2]
}


def update_nominal_strengths(dic):
    """Update dictionary with nominal values."""
    for k, v in NOMINAL_STRENGTHS.items():
        if k in dic:
            dic[k] = v
