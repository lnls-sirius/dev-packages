from .BaseMagnetControlWidget import BaseMagnetControlWidget

class SiSlowCorrectorControlWidget(BaseMagnetControlWidget):
    def __init__(self, magnet_list, orientation=0, parent=None):
        super(SiSlowCorrectorControlWidget, self).__init__(magnet_list, orientation, parent)
        self._setupUi()

    def _getPattern(self):
        return "SI-\w{4}:MA-(CH|CV)(-[1-2])*"

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
        return [    ('Horizontal Slow Correctors', '-CH'),
                    ('Vertical Slow Corretors', '-CV')]

class BoSlowCorrectorControlWidget(SiSlowCorrectorControlWidget):
    def _getPattern(self):
        return "BO-\w{3}:MA-(CH|CV)(-[1-2])*"

    def _divideBySection(self):
        return False

class TBSlowCorrectorControlWidget(SiSlowCorrectorControlWidget):
    def _getPattern(self):
        return "TB-\w{2}:MA-(CH|CV)(-[1-2])*"

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return False

class TSSlowCorrectorControlWidget(SiSlowCorrectorControlWidget):
    def _getPattern(self):
        return "TS-\w{2}:MA-(CH|CV)(-[1-2])*"

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return False
