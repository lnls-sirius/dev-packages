from pydm.PyQt.QtCore import *
from pydm.PyQt.QtGui import *
from pydm import PyDMApplication
from siriuspy.pwrsupply import psdata
from ..LoadingDlg import LoadingDlg
from .CyclePowerSupplies import CyclePowerSupplies
from .PrepareCycleThread import PrepareCycleThread
#from .PsCycleControlItem import PsCycleControlItem


class PsCycleWindow(QDialog):

    def __init__(self, parent=None):
        super(PsCycleWindow, self).__init__(parent)

        self._selected_devices = set()
        self._selected_ps = list()

        self._ps_cycle = CyclePowerSupplies()

        self._preparing_to_cycle = False
        self._ready_to_cycle = False

        self._setupUi()

    #Actions
    def _prepareToCycle(self):
        ''' Prepare chosen PS to be cycled. '''
        if self._ready_to_cycle:
            #Reset
            self._ready_to_cycle = False
            self.prepareButton.setText("Set to Cycle")
            self.cycleButton.setEnabled(False)
            self._enableCheckBoxes(True)
        else:
            #Set Pwr Supplies to be cycled
            self._ps_cycle.power_supplies = self._getSelectedPowerSupplies()
            #Thread that'll execute the cycling
            t = PrepareCycleThread(self._ps_cycle, self)
            #Dlg with a progress bar
            dlg = LoadingDlg("Preparing to Cycle", len(self._selected_ps), self)
            #Signals/Slots to update progress bar and close it
            t.taskUpdated.connect(dlg.update)
            t.taskFinished.connect(dlg.done)
            #Start thread and open dlg
            t.start()
            ret = dlg.exec_()

            if ret == QDialog.Accepted:
                self._ready_to_cycle = True
                self.cycleButton.setEnabled(True)
                self.prepareButton.setText("Reset")
                self._enableCheckBoxes(False)
            else:
                #SHOW MESSAGE
                pass

    def _cycle(self):
        pass

    #Helpers
    def _enableCheckBoxes(self, state):
        for cb in self.findChildren(QGroupBox):
            cb.setEnabled(state)

    def _getSelectedPowerSupplies(self):
        ''' Gets the power supplies based on the what devices are selected '''
        self._selected_ps = list()
        psdata.clear_filter()
        for sel in self._selected_devices:
            section, sub_section, device = sel
            psdata.add_filter(section, sub_section, 'PS', device)

        self._selected_ps = psdata.get_filtered_names()

        return self._selected_ps

    @pyqtSlot(int)
    def changePsSet(self, state, section, sub_section, device):
        ''' The selected_devices corresponds to the chk boxes chosen '''
        if state:
            self._selected_devices.add((section, sub_section, device))
        else:
            self._selected_devices.remove((section, sub_section, device))

    #Interface setup
    def _setupUi(self):
        self.setWindowTitle("Power Supply Cycling")

        #Anel
        self.siDCkB = QCheckBox("Dipoles")
        self.siDCkB.setObjectName("si_b")
        self.siDCkB.stateChanged.connect(
            lambda state: self.changePsSet(
                state, 'SI', psdata.filters.FAM, psdata.filters.DIPO))
        self.siQCkB = QCheckBox("Quadrupoles")
        self.siQCkB.setObjectName("si_q")
        self.siQCkB.stateChanged.connect(
            lambda state: self.changePsSet(
                state, 'SI', psdata.filters.FAM, psdata.filters.QUAD))
        self.siSCkB = QCheckBox("Sextupoles")
        self.siSCkB.setObjectName("si_s")
        self.siSCkB.stateChanged.connect(
            lambda state: self.changePsSet(
                state, 'SI', psdata.filters.FAM, psdata.filters.SEXT))
        self.siCCkB = QCheckBox("Corretoras")
        self.siCCkB.setObjectName("si_c")
        self.siCCkB.stateChanged.connect(
            lambda state: self.changePsSet(
                state, 'SI', psdata.filters.TRIM, psdata.filters.CORR))
        #Linhas de transpote
        self.ltDCkB = QCheckBox("Dipoles")
        self.ltDCkB.setObjectName("lt_b")
        self.ltDCkB.stateChanged.connect(
            lambda state: self.changePsSet(
                state, 'LT', psdata.filters.FAM, psdata.filters.DIPO))
        self.ltQCkB = QCheckBox("Quadrupoles")
        self.ltQCkB.setObjectName("lt_q")
        self.ltQCkB.stateChanged.connect(
            lambda state: self.changePsSet(
                state, 'LT', psdata.filters.FAM, psdata.filters.QUAD))
        self.ltCCkB = QCheckBox("Corretoras")
        self.ltCCkB.setObjectName("lt_c")
        self.ltCCkB.stateChanged.connect(
            lambda state: self.changePsSet(
                state, 'LT', psdata.filters.TRIM, psdata.filters.CORR))
        #Linac
        self.liQCkB = QCheckBox("Quadrupoles")
        self.liQCkB.setObjectName("li_q")
        self.liQCkB.stateChanged.connect(
            lambda state: self.changePsSet(
                state, 'LI', psdata.filters.FAM, psdata.filters.QUAD))
        self.liCCkb = QCheckBox("Corretoras")
        self.liCCkb.setObjectName("li_c")
        self.liCCkb.stateChanged.connect(
            lambda state: self.changePsSet(
                state, 'LI', psdata.filters.TRIM, psdata.filters.CORR))
        #Create Group Boxes
        siPsBox = self._createCheckBoxGroup("Ring", [self.siDCkB, self.siQCkB, \
                self.siSCkB, self.siCCkB ])
        ltPsBox = self._createCheckBoxGroup("Tansport Lines", [self.ltDCkB, \
                self.ltQCkB, self.ltCCkB ])
        liPsBox = self._createCheckBoxGroup("Linac", [self.liQCkB, self.liCCkb])
        #Create command buttons
        self.prepareButton = QPushButton("Set to Cycle")
        self.prepareButton.clicked.connect(self._prepareToCycle)
        self.cycleButton = QPushButton("Cycle")
        if self._ready_to_cycle:
            self.cycleButton.setEnabled(True)
        else:
            self.cycleButton.setEnabled(False)
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.prepareButton)
        buttonLayout.addWidget(self.cycleButton)
        #Build grid containing the main menu
        menu_grid = QGridLayout()
        menu_grid.addWidget(siPsBox, 0, 0)
        menu_grid.addWidget(ltPsBox, 0, 1)
        menu_grid.addWidget(liPsBox, 1, 0)
        menu_grid.addLayout(buttonLayout, 2, 0, 1, 2)
        '''
        #Create Group boxes with the power stupplies status
        status_grid = QGridLayout()
        status_grid.addWidget(self._createPsGroupBox("Ring - Dipoles", self._getPs('si', 'b')), 0, 0)
        status_grid.addWidget(self._createPsGroupBox("Ring - Quadrupoles", self._getPs('si', 'q')), 0, 1)
        status_grid.addWidget(self._createPsGroupBox("Ring - Sextupoles", self._getPs('si', 's')), 0, 2)
        status_grid.addWidget(self._createPsGroupBox("Ring - Corretoras", self._getPs('si', 'c')), 0, 3, 3, 1)
        status_grid.addWidget(self._createPsGroupBox("Transport Lines - Dipoles", self._getPs('lt', 'b')), 1, 0)
        status_grid.addWidget(self._createPsGroupBox("Transport Lines - Quadrupoles", self._getPs('lt', 'q')), 1, 1)
        status_grid.addWidget(self._createPsGroupBox("Transport Lines - Corretoras", self._getPs('lt', 'c')), 1, 2, 2, 1)
        status_grid.addWidget(self._createPsGroupBox("Linac - Quadrupoles", self._getPs('li', 'q')), 2, 0)
        status_grid.addWidget(self._createPsGroupBox("Linac - Corretoras", self._getPs('li', 'c')), 2, 1)

        #Create frame that'll contain the PS status widgets
        self.moreFrame = QFrame()
        self.moreFrame.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        frameLayout = QVBoxLayout()
        frameLayout.addLayout(status_grid)
        self.moreFrame.setLayout(frameLayout)
        self.moreFrame.setMinimumHeight(800)
        self.moreFrame.setMaximumHeight(800)
        self.moreFrame.setMaximumWidth(1500)
        self.moreFrame.setMinimumWidth(1500)
        self.moreFrame.hide()

        self.moreButton = QPushButton("Show More")
        self.moreButton.setCheckable(True)
        self.moreButton.toggled.connect(self.moreFrame.setVisible)
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.moreButton)
        '''
        #Build main grid and set as dlg layout
        main_grid = QGridLayout()
        #main_grid.addLayout(menuLayout, 0, 0)
        main_grid.addLayout(menu_grid, 0, 0)
        '''main_grid.addWidget(self.moreFrame, 0, 1, 1, 2)
        main_grid.addLayout(buttonLayout, 1, 0)'''
        main_grid.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(main_grid)

    def _createCheckBoxGroup(self, title, elements):
        groupBox = QGroupBox(title)
        #Group box setting
        groupBox.setCheckable(True)
        groupBox.setChecked(False)
        #Add group box elements
        boxLayout = QVBoxLayout()
        for e in elements:
            boxLayout.addWidget(e)
        #boxLayout.addStretch()
        groupBox.setLayout(boxLayout)
        #Create signals
        for e in elements:
            groupBox.toggled.connect(e.setChecked)

        return groupBox

    def _createPsGroupBox(self, title, elements):
        labels = []
        #grid = QGridLayout()
        vBox = QVBoxLayout()
        vBox.setSpacing(0)
        vBox.setContentsMargins(0, 0, 0, 0)
        for idx, ps in enumerate(elements):
            controlItem = PsCycleControlItem(ps, self)
            vBox.addWidget(controlItem)

        groupBox = QGroupBox(title)
        groupBox.setLayout(vBox)
        scroll = QScrollArea()
        scroll.setWidget(groupBox)
        scroll.setMinimumWidth(275)

        return scroll
