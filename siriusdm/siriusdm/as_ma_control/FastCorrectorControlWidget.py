from .BaseMagnetControlWidget import BaseMagnetControlWidget

class SiFastCorrectorControlWidget(BaseMagnetControlWidget):
    def __init__(self, magnet_list, orientation=0, parent=None):
        super(SiFastCorrectorControlWidget, self).__init__(magnet_list, orientation, parent)
        self._setupUi()

    def _getPattern(self):
        return "SI-\w{3,4}:MA-(FCH|FCV)(-[1-2])*"

    def _getMetric(self):
        return "Angle"

    def _getHeader(self):
        return [None, None, None, "Setpoint [A]", "Readback [A]", "Angle [mrad]"]

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _divideBySection(self):
        return True

    def _getGroups(self):
        return [    ('Horizontal Fast Correctors', '-FCH'),
                    ('Vertical Fast Corretors', '-FCV')]
