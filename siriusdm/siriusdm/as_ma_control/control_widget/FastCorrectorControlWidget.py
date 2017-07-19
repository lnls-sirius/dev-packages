from .BaseMagnetControlWidget import BaseMagnetControlWidget

class SiFastCorrectorControlWidget(BaseMagnetControlWidget):

    def _getPattern(self):
        return "SI-\w{3,4}:MA-(FCH|FCV)(-[1-2])*"

    def _getMetric(self):
        return "Kick"

    def _getHeader(self):
        return [None, None, None, "Setpoint [A]", "Cur-Mon [A]", "Kick [mrad]"]

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _divideBySection(self):
        return True

    def _getGroups(self):
        return [    ('Horizontal Fast Correctors', '-FCH'),
                    ('Vertical Fast Corretors', '-FCV')]
