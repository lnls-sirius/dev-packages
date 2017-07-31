"""Base class for controlling a magnet."""

import re
from pydm.PyQt.QtCore import Qt
from pydm.PyQt.QtGui import QWidget, QVBoxLayout, QPushButton, \
    QDoubleValidator, QGroupBox, QGridLayout, QLabel, QHBoxLayout, \
    QScrollArea, QSizePolicy
from pydm.widgets.label import PyDMLabel
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.led import PyDMLed
from pydm.widgets.scrollbar import PyDMScrollBar


class BaseMagnetControlWidget(QWidget):
    """Base widget class to control magnet."""

    SQUARE = 0
    HORIZONTAL = 1
    VERTICAL = 2

    STYLESHEET = """
    .QPushButton,
    .PyDMLineEdit,
    .PyDMLabel
    {
        margin: 0 5px 0 5px;
    }
    .PyDMLineEdit {
        width: 100px;
    }
    # QWidget {
    #     border: 1px solid red;
    # }
    """

    def __init__(self, magnet_list, orientation=0, parent=None):
        """Class constructor."""
        super(BaseMagnetControlWidget, self).__init__(parent)
        self._orientation = orientation
        self._magnet_list = magnet_list

        self._setupUi()
        self.setStyleSheet(self.STYLESHEET)

    def _setupUi(self):
        self.layout = self._getLayout()

        groups = self._getGroups()
        last_section = 0

        # Create group boxes and pop. layout
        for idx, group in enumerate(groups):

            # group[0] = name; group[1] = name pattern
            # Get magnets that belong to group
            magnets = list()
            element_list = self._getElementList()
            pattern = re.compile(group[1])
            for el in element_list:
                if pattern.search(el):
                    magnets.append(el)

            # Loop magnets to create all the widgets of a groupbox
            group_widgets = list()
            for n, ma in enumerate(magnets):
                # Add section label widget for individual magnets
                if self._divideBySection():
                    section = self._getSection(ma)
                    if section != last_section:
                        last_section = section
                        section_label = QLabel(
                            "Section {:02d}:".format(section))
                        # Create a new line with a QLabel only
                        group_widgets.append(section_label)
                # Add magnet widgets
                group_widgets.append(self._createGroupWidgets(ma))

            # Create group and scroll area
            group_box = self._createGroupBox(
                group[0], self._getHeader(), group_widgets)
            if self._hasScrollArea():
                widget = QScrollArea()
                widget.setWidget(group_box)
                # widget.setMinimumWidth(800)
            else:
                widget = group_box

            # Add group box or scroll area to grid layout
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

        led_width = 30
        name_width = 150
        bar_width = 80
        value_width = 120

        magnet_widget = QWidget()
        magnet_widget.layout = QHBoxLayout()

        # Create magnet widgets
        state_led = PyDMLed(self, "ca://" + ma + ":PwrState-Sts")
        state_led.setObjectName("pwr-state_" + ma)
        state_led.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        state_led.setMinimumSize(led_width, state_led.minimumSize().height())
        magnet_widgets.append(state_led)
        magnet_widget.layout.addWidget(state_led)

        name_label = QPushButton(ma, self)
        name_label.setObjectName("label_" + ma)
        name_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        name_label.setMinimumSize(
            name_width, name_label.minimumSize().height())
        # name_label.setFlat(True) #Trasparent button
        magnet_widgets.append(name_label)
        magnet_widget.layout.addWidget(name_label)

        scroll_bar = PyDMScrollBar(
            self, orientation=Qt.Horizontal,
            init_channel="ca://" + ma + ":Current-SP")
        scroll_bar.setObjectName("current-sp_" + ma)
        scroll_bar.setMinimumSize(bar_width, 15)
        scroll_bar.limitsFromPV = True
        scroll_bar.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        magnet_widgets.append(scroll_bar)
        magnet_widget.layout.addWidget(scroll_bar)

        current_sp = PyDMLineEdit(self, "ca://" + ma + ":Current-SP")
        current_sp.setObjectName("current-sp_" + ma)
        current_sp.setMinimumSize(
            value_width, current_sp.minimumSize().height())
        current_sp.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # current_sp.receivePrecision(3)
        current_sp.setValidator(QDoubleValidator())
        current_sp._useunits = False
        magnet_widgets.append(current_sp)
        magnet_widget.layout.addWidget(current_sp)

        current_rb = PyDMLabel(self, "ca://" + ma + ":Current-Mon")
        current_rb.setObjectName("current-mon_" + ma)
        current_rb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        current_rb.setMinimumSize(
            value_width, current_rb.minimumSize().height())
        current_rb.precFromPV = True
        # current_rb.setPrecision(3)
        magnet_widgets.append(current_rb)
        magnet_widget.layout.addWidget(current_rb)

        metric_rb = PyDMLineEdit(
            self, "ca://" + ma + ":" + self._getMetric() + "-SP")
        metric_rb.setObjectName("metric-sp_" + ma)
        metric_rb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        metric_rb.setMinimumSize(
            value_width, metric_rb.minimumSize().height())
        metric_rb._useunits = False
        # metric_rb.receivePrecision(3)
        # metric_rb.setMinimumWidth(80)
        magnet_widgets.append(metric_rb)
        magnet_widget.layout.addWidget(metric_rb)

        magnet_widget.setLayout(magnet_widget.layout)

        # Create a new line with all the magnet widgets
        # return magnet_widgets
        return magnet_widget

    def _createGroupBox(self, title, headers, widget_group):
        group_box = QGroupBox(title)

        # grid = QGridLayout()
        # for col, header in enumerate(headers):
        #     if header:
        #         grid.addWidget(QLabel(header), 0, col)
        # for line, widgets in enumerate(widget_group):
        #     for col, widget in enumerate(widgets):
        #         grid.addWidget(widget, line + 1, col)
        # grid.setRowStretch(len(widget_group) + 1, 1)
        # grid.setColumnStretch(len(headers), 1)
        # group_box.setLayout(grid)
        group_box.layout = QVBoxLayout()
        header_widget = QWidget()
        header_widget.layout = QHBoxLayout()

        header_size = [30, 150, 80, 120, 120, 120, 50]
        header_policy = [QSizePolicy.Fixed, QSizePolicy.Fixed,
                         QSizePolicy.MinimumExpanding,
                         QSizePolicy.Fixed, QSizePolicy.Fixed,
                         QSizePolicy.Fixed, QSizePolicy.Fixed]

        for col, header in enumerate(headers):
            label = QLabel(header)
            label.setSizePolicy(header_policy[col], QSizePolicy.Fixed)
            label.setMinimumSize(
                header_size[col], label.minimumSize().height())
            header_widget.layout.addWidget(label)
        header_widget.setLayout(header_widget.layout)
        group_box.layout.addWidget(header_widget)
        for line, widget in enumerate(widget_group):
            group_box.layout.addWidget(widget)
        group_box.layout.addStretch()
        group_box.setLayout(group_box.layout)

        return group_box

    def _getElementList(self):
        return filter(lambda magnet: re.match(
            self._getPattern(), magnet), self._magnet_list)

    def _getSection(self, name):
        section = name.split(":")[0].split("-")[1][:2]
        try:
            int(section)
        except Exception:
            return 0

        return int(section)

    def _getLayout(self):
        if self._orientation == self.SQUARE:
            return QGridLayout()
        elif self._orientation == self.HORIZONTAL:
            return QHBoxLayout()
        else:
            return QVBoxLayout()
