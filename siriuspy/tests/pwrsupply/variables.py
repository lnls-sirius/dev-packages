"""Test values to test read_all_variables methods.

Used by test in controller and model modulesself.
"""
# TODO: change string format return from serial
values = [
    8579, 6.7230000495910645, 6.7230000495910645,
    [b'V', b'0', b'.', b'0', b'7', b' ', b'2', b'0', b'1', b'8', b'-', b'0', b'3',
     b'-', b'2', b'6', b'V', b'0', b'.', b'0', b'7', b' ', b'2', b'0', b'1', b'8', b'-', b'0',
     b'3', b'-', b'2', b'6'], 5, 8617, 0, 2, 1, 0.0, 0.0, 1.0, 0.0,
    [1.0, 1.0, 1.0, 0.0], 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0, 0, 0,
    6.722831726074219, 1.23291015625, 5.029296875, 53.0]

bsmp_values = [
    '\x00', '\x13', '\x00', 'ô', '\x83', '!', 'Ñ', '"', '×', '@', 'Ñ', '"',
    '×', '@', 'V', '0', '.', '0', '7', ' ', '2', '0', '1', '8', '-', '0', '3',
    '-', '2', '6', 'V', '0', '.', '0', '7', ' ', '2', '0', '1', '8', '-', '0',
    '3', '-', '2', '6', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x05',
    '\x00', '\x00', '\x00', '©', '!', '\x00', '\x00', '\x00', '\x00', '\x02',
    '\x00', '\x01', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x80', '?', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x80', '?', '\x00', '\x00', '\x80', '?',
    '\x00', '\x00', '\x80', '?', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
    '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', 'p', '!', '×', '@',
    '\x00', 'Ð', '\x9d', '?', '\x00', 'ð', '\xa0', '@', '\x00', '\x00', 'T',
    'B', 'c']

# Missing entries
dict_values = {
    'PwrState-Sts': 1,
    'OpMode-Sts': 0,
    'CtrlLoop-Sel': 0,
    'CtrlMode-Sts': 0,
    'Current-RB': 6.7230000495910645,
    'CurrentRef-Mon': 6.7230000495910645,
    'Version-Cte': 'V0.07 2018-03-26V0.07 2018-03-26',
    'CycleEnbl-Mon': 0,
    'CycleType-Sts': 2,
    'CycleNrCycles-RB': 1,
    'CycleIndex-Mon': 0.0,
    'CycleFreq-RB': 0.0,
    'CycleAmpl-RB': 1.0,
    'CycleOffset-RB': 0.0,
    'CycleAuxParam-RB': [1.0, 1.0, 1.0, 0.0],
    'IntlkSoft-Mon': 0,
    'IntlkHard-Mon': 0,
    'Current-Mon': 6.722831726074219,
    'WfmOffset-RB': 0.0,
    'WfmData-RB': list(range(4000))}
