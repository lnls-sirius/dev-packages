from .BaseMagnetControlWidget import BaseMagnetControlWidget

class SiFamSextupoleControlWidget(BaseMagnetControlWidget):
    def __init__(self, magnet_list, orientation=0, parent=None):
        super(SiFamSextupoleControlWidget, self).__init__(magnet_list, orientation, parent)
        self._setupUi()

    def _getPattern(self):
        return "SI-Fam:MA-S(\w+[0-9]*|[0-9])"

    def _getMetric(self):
        return "SL"

    def _getHeader(self):
        return [None, None, None, "Setpoint [A]", "Readback [A]", "SL [1/m<sup>2</sup>]"]

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return False

    def _getGroups(self):
        return [    ('Focusing Sextupoles', '-SF'),
                    ('Defocusing Sextupoles', '-SD')]

class BoFamSextupoleControlWidget(SiFamSextupoleControlWidget):
    def _getPattern(self):
        return "BO-Fam:MA-S(\w+[0-9]*|[0-9])"
