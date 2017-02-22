import utils as _utils


# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)


scan_period = 0.1 # [second]
magnet_families = (
    'QFA','QDA','QDB1','QFB','QDB2','QDP1','QFP','QDP2','Q1','Q2','Q3','Q4',
    'SFA0','SDA0','SDA1','SFA1','SDA2','SDA3',
)

_etyps = _utils.get_enum_types()

pvdb = {
    'IOC:Version':    {'type':'string', 'value':_utils.ioc_version, 'scan':scan_period},

    'QFA:Reset-Cmd':  {'type':'int', 'value': 0},
    'QFA:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QFA:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QFA:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'QFA:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'QDA:Reset-Cmd':  {'type':'int', 'value': 0},
    'QDA:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QDA:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QDA:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'QDA:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'QDB1:Reset-Cmd':  {'type':'int', 'value': 0},
    'QDB1:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QDB1:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QDB1:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'QDB1:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'QFB:Reset-Cmd':  {'type':'int', 'value': 0},
    'QFB:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QFB:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QFB:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'QFB:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'QDB2:Reset-Cmd':  {'type':'int', 'value': 0},
    'QDB2:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QDB2:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QDB2:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'QDB2:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'QDP1:Reset-Cmd':  {'type':'int', 'value': 0},
    'QDP1:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QDP1:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QDP1:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'QDP1:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'QFP:Reset-Cmd':  {'type':'int', 'value': 0},
    'QFP:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QFP:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QFP:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'QFP:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'QDP2:Reset-Cmd':  {'type':'int', 'value': 0},
    'QDP2:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QDP2:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'QDP2:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'QDP2:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'Q1:Reset-Cmd':  {'type':'int', 'value': 0},
    'Q1:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'Q1:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'Q1:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'Q1:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'Q2:Reset-Cmd':  {'type':'int', 'value': 0},
    'Q2:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'Q2:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'Q2:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'Q2:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'Q3:Reset-Cmd':  {'type':'int', 'value': 0},
    'Q3:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'Q3:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'Q3:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'Q3:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'Q4:Reset-Cmd':  {'type':'int', 'value': 0},
    'Q4:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'Q4:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'Q4:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'Q4:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'SFA0:Reset-Cmd':  {'type':'int', 'value': 0},
    'SFA0:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'SFA0:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'SFA0:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'SFA0:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'SDA0:Reset-Cmd':  {'type':'int', 'value': 0},
    'SDA0:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'SDA0:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'SDA0:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'SDA0:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'SDA1:Reset-Cmd':  {'type':'int', 'value': 0},
    'SDA1:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'SDA1:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'SDA1:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'SDA1:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'SFA1:Reset-Cmd':  {'type':'int', 'value': 0},
    'SFA1:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'SFA1:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'SFA1:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'SFA1:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'SDA2:Reset-Cmd':  {'type':'int', 'value': 0},
    'SDA2:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'SDA2:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'SDA2:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'SDA2:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

    'SDA3:Reset-Cmd':  {'type':'int', 'value': 0},
    'SDA3:State-Sel':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'SDA3:State-Sts':  {'type':'enum', 'enums':_etyps['OffOnTyp'], 'value':1, 'unit': ''},
    'SDA3:Current-RB': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},
    'SDA3:Current-SP': {'type':'float', 'value': 0.0, 'prec': 6, 'unit': 'A'},

}
