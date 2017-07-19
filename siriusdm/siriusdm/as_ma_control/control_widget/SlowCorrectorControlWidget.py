from .BaseMagnetControlWidget import BaseMagnetControlWidget


class SiSlowCorrectorControlWidget(BaseMagnetControlWidget):

    def _getPattern(self):
        return "SI-\w{4}:MA-(CH|CV)(-[1-2])*"

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
        return [('Horizontal Slow Correctors', '-CH'),
                ('Vertical Slow Corretors', '-CV')]


class BoSlowCorrectorControlWidget(SiSlowCorrectorControlWidget):
    def _getPattern(self):
        return "BO-\w{3}:MA-(CH|CV)(-[1-2])*"

    def _divideBySection(self):
        return False


class TBSlowCorrectorControlWidget(SiSlowCorrectorControlWidget):
    def _getPattern(self):
        return "TB-\d{2}:MA-(CH|CV).*"

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return True


class TSSlowCorrectorControlWidget(SiSlowCorrectorControlWidget):
    def _getPattern(self):
        return "TS-\w{2}:MA-(CH|CV)(-[1-2])*"

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return True
