
from pcaspy import Severity


pvdb = {
    'SHIFT-TYPE': {
        'type': 'enum',
        'enums': [
            'User Shift',
            'Accelerator Shift',
            'Maintenance Shift',
            'Conditioning Shift'
        ],
        'severity': 4*[Severity.NO_ALARM],
        'value': 0
    },
    'MESSAGE': {
        'type': 'string',
        'value': 'In case of trouble, call Control Room.'
    },
}
