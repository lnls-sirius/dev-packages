import epics

_slow_props = ['posX', 'posY', 'posQ', 'posS', 'ampA', 'ampB', 'ampC', 'ampD']
_slow_props_def = """
    @property
    def {0:s}(self):
        if self._pvs['{0:s}'].is_connected():
            return self._pvs['{0:s}'].value

    @{0:s}.setter
    def {0:s}(self, value):
        if self._pvs['{0:s}'].is_connected():
            self._pvs['{0:s}'].value = value
"""


class BPM:

    def __init__(self, bpm_name):
        self._pvs['posX'] = epics.PV(bpm_name + ':PosX-Mon')
        self._pvs['posY'] = epics.PV(bpm_name + ':PosY-Mon')
        self._pvs['posQ'] = epics.PV(bpm_name + ':PosQ-Mon')
        self._pvs['posS'] = epics.PV(bpm_name + ':PosS-Mon')
        self._pvs['ampA'] = epics.PV(bpm_name + ':AmpA-Mon')
        self._pvs['ampB'] = epics.PV(bpm_name + ':AmpB-Mon')
        self._pvs['ampC'] = epics.PV(bpm_name + ':AmpC-Mon')
        self._pvs['ampD'] = epics.PV(bpm_name + ':AmpD-Mon')

    for prop in _slow_props:
        exec(_slow_props_def.format(prop))
