"""Define Slit device high level PVs database.

This is not a primary source database. Primary sources can be found in:
 - Pos. Difference Control IOC: https://github.com/lnls-dig/diff-ctrl-epics-ioc
 - Motors IOC: https://github.com/lnls-dig/galil-dmc30017-epics-ioc
"""


def get_slit_database():
    """Return Slit device database."""
    pvs_database = {
        # Low level devides prefixes
        'NegativeMotionCtrl-Cte': {'type': 'string'},
        'PositiveMotionCtrl-Cte': {'type': 'string'},

        # PVs to control slit edges positions
        'NegativeEdgePos-SP': {'type': 'float', 'unit': 'mm', 'prec': 5,
                               'hihi': 1000000, 'high': 1000000,
                               'hilim': 1000000, 'lolim': -1000000,
                               'low': -1000000, 'lolo': -1000000},
        'NegativeEdgePos-RB': {'type': 'float', 'unit': 'mm', 'prec': 5,
                               'hihi': 1000000, 'high': 1000000,
                               'hilim': 1000000, 'lolim': -1000000,
                               'low': -1000000, 'lolo': -1000000},
        'PositiveEdgePos-SP': {'type': 'float', 'unit': 'mm', 'prec': 5,
                               'hihi': 1000000, 'high': 1000000,
                               'hilim': 1000000, 'lolim': -1000000,
                               'low': -1000000, 'lolo': -1000000},
        'PositiveEdgePos-RB': {'type': 'float', 'unit': 'mm', 'prec': 5,
                               'hihi': 1000000, 'high': 1000000,
                               'hilim': 1000000, 'lolim': -1000000,
                               'low': -1000000, 'lolo': -1000000},

        # Helper PVs to perform step increments in slit edges positions
        'NegativeEdgeStep-SP': {'type': 'float', 'unit': 'mm', 'prec': 5,
                                'value': 1, 'hihi': 1000000, 'high': 1000000,
                                'hilim': 1000000, 'lolim': -1000000,
                                'low': -1000000, 'lolo': -1000000},
        'NegativeEdgeStep-RB': {'type': 'float', 'unit': 'mm', 'prec': 5,
                                'value': 1, 'hihi': 1000000, 'high': 1000000,
                                'hilim': 1000000, 'lolim': -1000000,
                                'low': -1000000, 'lolo': -1000000},
        'IncNegativeEdge-Cmd': {'type': 'int', 'value': 0},
        'DecNegativeEdge-Cmd': {'type': 'int', 'value': 0},
        'PositiveEdgeStep-SP': {'type': 'float', 'unit': 'mm', 'prec': 5,
                                'value': 1, 'hihi': 1000000, 'high': 1000000,
                                'hilim': 1000000, 'lolim': -1000000,
                                'low': -1000000, 'lolo': -1000000},
        'PositiveEdgeStep-RB': {'type': 'float', 'unit': 'mm', 'prec': 5,
                                'value': 1, 'hihi': 1000000, 'high': 1000000,
                                'hilim': 1000000, 'lolim': -1000000,
                                'low': -1000000, 'lolo': -1000000},
        'IncPositiveEdge-Cmd': {'type': 'int', 'value': 0},
        'DecPositiveEdge-Cmd': {'type': 'int', 'value': 0},

        # Alternative PVs to control slit center and width
        'Center-SP': {'type': 'float', 'unit': 'mm', 'prec': 5},
        'Center-RB': {'type': 'float', 'unit': 'mm', 'prec': 5},
        'Width-SP':  {'type': 'float', 'unit': 'mm', 'prec': 5,
                      'hihi': 500, 'high': 500, 'hilim': 500,
                      'lolim': 0, 'low': 0, 'lolo': 0},
        'Width-RB':  {'type': 'float', 'unit': 'mm', 'prec': 5,
                      'hihi': 500, 'high': 500, 'hilim': 500,
                      'lolim': 0, 'low': 0, 'lolo': 0},

        # Helper PVs to perform step increments in slit center and width
        'CenterStep-SP': {'type': 'float', 'unit': 'mm', 'prec': 5,
                          'value': 1, 'hihi': 1000000, 'high': 1000000,
                          'hilim': 1000000, 'lolim': -1000000,
                          'low': -1000000, 'lolo': -1000000},
        'CenterStep-RB': {'type': 'float', 'unit': 'mm', 'prec': 5,
                          'value': 1, 'hihi': 1000000, 'high': 1000000,
                          'hilim': 1000000, 'lolim': -1000000,
                          'low': -1000000, 'lolo': -1000000},
        'IncCenter-Cmd': {'type': 'int', 'value': 0},
        'DecCenter-Cmd': {'type': 'int', 'value': 0},
        'WidthStep-SP':  {'type': 'float', 'unit': 'mm', 'prec': 5,
                          'value': 1, 'hihi': 1000000, 'high': 1000000,
                          'hilim': 1000000, 'lolim': -1000000,
                          'low': -1000000, 'lolo': -1000000},
        'WidthStep-RB':  {'type': 'float', 'unit': 'mm', 'prec': 5,
                          'value': 1, 'hihi': 1000000, 'high': 1000000,
                          'hilim': 1000000, 'lolim': -1000000,
                          'low': -1000000, 'lolo': -1000000},
        'IncWidth-Cmd':  {'type': 'int', 'value': 0},
        'DecWidth-Cmd':  {'type': 'int', 'value': 0},

        # Command to edges motors return to Home position
        'Home-Cmd': {'type': 'int', 'value': 0},

        # PVs indicating movement status of slit edges motors
        'NegativeDoneMov-Mon': {'type': 'int', 'value': 1},
        'PositiveDoneMov-Mon': {'type': 'int', 'value': 1},

        # PVs to perform commands to force slit edges positioning
        'ForceNegativeEdgePos-Cmd': {'type': 'float', 'value': 0},
        'ForcePositiveEdgePos-Cmd': {'type': 'float', 'value': 0},
        'ForceComplete-Mon':        {'type': 'int', 'value': 1},

        # Slit edges position limits PVs
        'LowOuterLim-SP':  {'type': 'float', 'unit': 'mm', 'prec': 5,
                            'value': -1000, 'hihi': 1000000, 'high': 1000000,
                            'hilim': 1000000, 'lolim': -1000000,
                            'low': -1000000, 'lolo': -1000000},
        'LowOuterLim-RB':  {'type': 'float', 'unit': 'mm', 'prec': 5,
                            'value': -1000, 'hihi': 1000000, 'high': 1000000,
                            'hilim': 1000000, 'lolim': -1000000,
                            'low': -1000000, 'lolo': -1000000},
        'HighOuterLim-SP': {'type': 'float', 'unit': 'mm', 'prec': 5,
                            'value': 1000, 'hihi': 1000000, 'high': 1000000,
                            'hilim': 1000000, 'lolim': -1000000,
                            'low': -1000000, 'lolo': -1000000},
        'HighOuterLim-RB': {'type': 'float', 'unit': 'mm', 'prec': 5,
                            'value': 1000, 'hihi': 1000000, 'high': 1000000,
                            'hilim': 1000000, 'lolim': -1000000,
                            'low': -1000000, 'lolo': -1000000}
    }
    return pvs_database
