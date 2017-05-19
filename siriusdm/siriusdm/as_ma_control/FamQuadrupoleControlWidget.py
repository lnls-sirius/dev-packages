from pydm.PyQt.QtGui import QPushButton
from .BaseMagnetControlWidget import BaseMagnetControlWidget

class SiFamQuadrupoleControlWidget(BaseMagnetControlWidget):
    def __init__(self, magnet_list, orientation=0, parent=None):
        super(SiFamQuadrupoleControlWidget, self).__init__(magnet_list, orientation, parent)
        self._setupUi()

    def _getPattern(self):
        return "SI-Fam:MA-Q(\w+[0-9]*|[0-9])"

    def _getMetric(self):
        return "KL"

    def _getHeader(self):
        return [None, None, None, "Setpoint [A]", "Readback [A]", "KL [1/m]", "Trim"]

    def _hasTrimButton(self):
        return True

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return False

    def _getGroups(self):
        return [    ('Focusing Quadrupoles', "-QF"),
                    ('Defocusing Quadrupoles', "-QD"),
                    ('Dispersive Quadrupoles', "-Q[0-9]")]

    def _createGroupWidgets(self, ma):
        magnet_widgets = super()._createGroupWidgets(ma)

        trim_btn = QPushButton(">", self)
        trim_btn.setObjectName("trim_" + ma)
        trim_btn.setMaximumWidth(40)

        magnet_widgets.append(trim_btn)

        return magnet_widgets

class BoFamQuadrupoleControlWidget(SiFamQuadrupoleControlWidget):

    def _getPattern(self):
        return "BO-Fam:MA-Q(\w+[0-9]*|[0-9])"

    def _getGroups(self):
        return [    ('Focusing Quadrupoles', "-QF"),
                    ('Defocusing Quadrupoles', "-QD")]
