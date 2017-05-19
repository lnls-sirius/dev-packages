import re
from pydm.PyQt.QtCore import Qt
from pydm.PyQt.QtGui import QWidget, QVBoxLayout, QPushButton, QDoubleValidator, \
        QGroupBox, QGridLayout, QLabel, QHBoxLayout, QScrollArea
from pydm.widgets.label import PyDMLabel
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.led import PyDMLed
from pydm.widgets.scrollbar import PyDMScrollBar

class BaseMagnetControlWidget(QWidget):
    SQUARE      = 0
    HORIZONTAL  = 1
    VERTICAL    = 2

    def __init__(self, magnet_list, orientation=0, parent=None):
        super(BaseMagnetControlWidget, self).__init__(parent)
        self._orientation = orientation
        self._magnet_list = magnet_list

    def _setupUi(self):
        if self._orientation == self.SQUARE:
            self.layout = QGridLayout()
        elif self._orientation == self.HORIZONTAL:
            self.layout = QHBoxLayout()
        else:
            self.layout = QVBoxLayout()

        groups = self._getGroups()
        last_section = 0

        #Create group boxes and pop. layout
        for idx, group in enumerate(groups):

            #group[0] = name; group[1] = name pattern
            #Get magnets that belong to group
            magnets = list()
            element_list = self._getElementList()
            pattern = re.compile(group[1])
            for el in element_list:
                if pattern.search(el):
                    magnets.append(el)

            #Loop magnets to create all the widgets of a groupbox
            group_widgets = list()
            for n, ma in enumerate(magnets):
                #Add section label widget for individual magnets
                if self._divideBySection():
                    section = self._getSection(ma)
                    if section != last_section:
                        last_section = section
                        section_label = QLabel("<b>Section {:02d}:</b>".format(section))
                        #Create a new line with a QLabel only
                        group_widgets.append([section_label])
                #Add magnet widgets
                group_widgets.append(self._createGroupWidgets(ma))

            #Create group and scroll area
            group_box = self._createGroupBox(group[0], self._getHeader(), group_widgets)
            if self._hasScrollArea():
                widget = QScrollArea()
                widget.setWidget(group_box)
                widget.setMinimumWidth(800)
            else:
                widget = group_box

            #Add group box or scroll area to grid layout
            if self._orientation == self.SQUARE:
                if idx % 2 == 0:
                    self.layout.addWidget(widget, int(idx), 0)
                else:
                    self.layout.addWidget(widget, int(idx/2), 1)
            else:
                self.layout.addWidget(widget)

        self.setLayout(self.layout)

    def _createGroupWidgets(self, ma):

        magnet_widgets = list()

        #Create magnet widgets
        state_led = PyDMLed(self, "ca://" + ma + ":PwrState-Sts")
        state_led.setObjectName("pwr-state_" + ma)
        magnet_widgets.append(state_led)

        name_label = QPushButton(ma, self)
        name_label.setObjectName("label_" + ma)
        #name_label.setFlat(True) #Trasparent button
        magnet_widgets.append(name_label)

        scroll_bar = PyDMScrollBar(Qt.Horizontal, self, "ca://" + ma + ":Current-SP")
        scroll_bar.setObjectName("current-sp_" + ma)
        scroll_bar.setMinimumWidth(150)
        magnet_widgets.append(scroll_bar)

        current_sp = PyDMLineEdit(self, "ca://" + ma + ":Current-SP")
        current_sp.setObjectName("current-sp_" + ma)
        current_sp.receivePrecision(3) #PyDM BUG!!!!!!!!!!!!!!
        current_sp.setValidator(QDoubleValidator())
        current_sp._useunits = False
        magnet_widgets.append(current_sp)

        current_rb = PyDMLabel(self, "ca://" + ma + ":Current-RB")
        current_rb.setObjectName("current-rb_" + ma)
        current_rb.setPrecision(3)
        magnet_widgets.append(current_rb)

        metric_rb = PyDMLineEdit(self, "ca://" + ma + ":" + self._getMetric() + "-SP")
        metric_rb.setObjectName("metric-sp_" + ma)
        metric_rb.receivePrecision(3)
        metric_rb.setMinimumWidth(80)
        magnet_widgets.append(metric_rb)

        #Create a new line with all the magnet widgets
        return magnet_widgets

    def _createGroupBox(self, title, headers, widget_group):
        group_box = QGroupBox(title)

        grid = QGridLayout()
        for col, header in enumerate(headers):
            if header:
                grid.addWidget(QLabel("<b>"+header+"</b>"), 0, col)
        for line, widgets in enumerate(widget_group):
            for col, widget in enumerate(widgets):
                grid.addWidget(widget, line + 1, col)
        grid.setRowStretch(len(widget_group) + 1, 1)
        grid.setColumnStretch(len(headers), 1)
        group_box.setLayout(grid)

        return group_box

    def _getElementList(self):
        return filter(lambda magnet: re.match(self._getPattern(), magnet), self._magnet_list)

    def _getSection(self, name):
        section = name.split(":")[0].split("-")[1][:2]
        try:
            int(section)
        except:
            return 0

        return int(section)
