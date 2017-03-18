from siriuspy.cs_device.enumtypes import enum_types as _enumt

_Off, _On = _enumt.OffOnTyp
_SlowRef, _FastRef, _WfmRef, _SigGen = _enumt.PSOpModeTyp


class ControllerModel:
    """Base Controller class

    This is a simple power supply controller that responds immediatelly
    to setpoints.
    """

    def __init__(self):

        self._current_sp = 0.0
        self._current_DCCT = 0.0
        self._pwrstate = _Off
        self._opmode = _SlowRef

    @property
    def current(self):
        return self._current_DCCT

    @property
    def pwrstate(self):
        return self._pwrstate

    @property
    def opmode(self):
        return self._opmode

    @current.setter
    def current(self, value):
        self._current_sp = value # Should it happen even with PS off?
        if self._pwrstate == _On:
            if self._opmode == _SlowRef:
                self._current_DCCT = self._current_sp

    @pwrstate.setter
    def pwrstate(self, value):
        if value == _Off:
            self._pwrstate = _Off
            self._current_DCCT = 0.0
        elif value == _On:
            self._pwrstate = _On
            if self._opmode == _SlowRef:
                self._current_DCCT = self._current_sp
        else:
            raise Exception('Invalid value!')

    @opmode.setter
    def opmode(self, value):
        if value == _SlowRef:
            self._opmode = value
            if self._pwrstate == _On:
                self._current_DCCT = self._current_sp
        elif value in (_FastRef, _WfmRef, _SigGen):
            self._opmode = value
        else:
            raise Exception('Invalid value!')

    def __str__(self):
        st = ''
        propty = 'pwrstate';     st +=   '{0:<20s}: {1}'.format(propty, self.pwrstate)
        propty = 'opmode';       st += '\n{0:<20s}: {1}'.format(propty, self.opmode)
        propty = 'current-DCCT'; st += '\n{0:<20s}: {1}'.format(propty, self.current)
        propty = 'current-sp';   st += '\n{0:<20s}: {1}'.format(propty, self._current_sp)
        return st
