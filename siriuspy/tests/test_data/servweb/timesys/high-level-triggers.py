# This is a python3 file:
#     - The object defined here is a python3 dictionary.
#     - It can be imported into python3 code with the code:
#         `return_dict = ast.literal_eval('/pathto/high-level-triggers.py')`
#     where `ast` is a python3 module available in `pip3`
#
# This file define the triggers used in Sirius operation system and
# maps them with several important properties.
{
    'SI-Glob:TI-Corrs': {
        'database': {
            'Src': {'value': 0, 'enums': ('MigSI', 'OrbSI', 'Cycle', 'Study')},
            'Delay': {'value': 0.0, 'hilim': 1.0, 'high': 1.0, 'hihi': 1.0},
            'RFDelayType': {'value': 1, 'states': (2, 0)},
            'NrPulses': {
                'value': 3920, 'hilim': 4001, 'high': 4001, 'hihi': 4001},
            'Duration': {'value': 2000},
            'State': {'value': 0},
            'Polarity': {'value': 1, 'states': (1, 0)},
            },
        'channels': (
            'SI-01M1:PS-CH:RS485', 'SI-01M2:PS-CH:RS485',
            'SI-02M1:PS-CH:RS485', 'SI-02M2:PS-CH:RS485',
            'SI-03M1:PS-CH:RS485',
        ),
        },
 }
