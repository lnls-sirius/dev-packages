import re
from pymysql.err import IntegrityError, InternalError, OperationalError
from pydm.PyQt.QtCore import Qt, QPoint, pyqtSlot
from pydm.PyQt.QtGui import QVBoxLayout, QPushButton, QMainWindow, QTableView,  \
        QWidget, QHBoxLayout, QInputDialog, QMenu, QAction, QMessageBox,        \
        QKeySequence, QAbstractItemView
from ..LoadingDlg import LoadingDlg
from .ConfigModel import ConfigModel
from .ConfigModel import ConfigDelegate
from .TuneDlg import TuneDlg
from .LoadingThread import LoadingThread


class ConfigManagerWindow(QMainWindow):
    NEW_CONFIGURATION = 0

    def __init__(self, config_type, parent=None):
        super(ConfigManagerWindow, self).__init__(parent)

        self._config_type = config_type
        self._model = ConfigModel(self._config_type)
        self._delegate = ConfigDelegate()

        self._setupUi()

        self.ld_cur_state_btn.clicked.connect(self._loadCurrentConfiguration)
        self.ld_config_btn.clicked.connect(self._addConfiguration)
        self.delete_config_btn.clicked.connect(self._removeConfiguration)

        self.setGeometry(100, 100, 1600, 900)
        self.setWindowTitle("Configuration Manager")
        self.show()

    def _setupUi(self):
        self.central_widget = QWidget()
        self.central_widget.layout = QHBoxLayout()

        self.button_box = QVBoxLayout()
        self.ld_cur_state_btn = QPushButton("Load Current State")
        self.ld_config_btn = QPushButton("Load Configuration")
        self.ld_config_btn.setShortcut(QKeySequence.New)
        self.delete_config_btn = QPushButton("Delete Configuration")
        self.button_box.addWidget(self.delete_config_btn)
        self.button_box.addWidget(self.ld_config_btn)
        self.button_box.addWidget(self.ld_cur_state_btn)
        self.button_box.addStretch()

        # TableView
        self.table = QTableView(self)
        self.table.setModel(self._model)
        self.table.setItemDelegate(self._delegate)
        # self.table.setSelectionBehavior(QAbstractItemView.SelectColumns)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._showHeaderMenu)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        # TableView Headers
        self.headers = self.table.horizontalHeader()
        self.headers.setContextMenuPolicy(Qt.CustomContextMenu)
        self.headers.customContextMenuRequested.connect(self._showHeaderMenu)

        self.central_widget.layout.addLayout(self.button_box)
        self.central_widget.layout.addWidget(self.table)
        self.central_widget.setLayout(self.central_widget.layout)

        # Set widget
        self.setCentralWidget(self.central_widget)

    def closeEvent(self, event):
        columns = list(range(len(self._model.configurations)))
        columns.sort(reverse=True)
        if not self._closeConfigurations(columns):
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S:
            self._saveChanges()
            return
        if event.key() == Qt.Key_W:
            self._closeConfigurationOnFocus()
            return
        if event.key() == Qt.Key_F2:
            self._renameOnFocus()
            return
        if event.key() == Qt.Key_Z:
            print(self._model._undo)
            if len(self._model._undo) > 0:
                self._model._undo.pop()[1]()
            return
        if event.key() == Qt.Key_R:
            if len(self._model._redo) > 0:
                self._model._redo.pop()[1]()
            return

    @pyqtSlot(QPoint)
    def _showHeaderMenu(self, point):
        column = self.headers.logicalIndexAt(point.x())
        if column == -1:
            return
        menu = QMenu(self)
        # Actions
        cols = self.table.selectionModel().selectedColumns()
        if len(cols) != 2 or column not in [col.column() for col in cols]:
            self.table.selectColumn(column)
            menu.aboutToHide.connect(lambda: self.table.clearSelection())

            save = QAction("Save", menu)
            save.triggered.connect(lambda: self._saveConfiguration(column))
            save_all = QAction("Save all", menu)
            save_all.triggered.connect(lambda: self._saveChanges())
            save_all.setShortcut(QKeySequence.Save)
            rename = QAction("Rename", menu)
            rename.triggered.connect(lambda: self._renameConfiguration(column))
            close = QAction("Close", menu)
            close.triggered.connect(lambda: self._closeConfiguration(column))
            close.setShortcut(QKeySequence.Close)
            close_right = QAction("Close to the right", menu)
            close_right.triggered.connect(lambda: self._closeConfigurationsToTheRight(column))
            close_others = QAction("Close other", menu)
            close_others.triggered.connect(lambda: self._closeOtherConfigurations(column))
            close_all = QAction("Close all", menu)
            close_all.triggered.connect(lambda: self._closeAllConfigurations())
            tune = QAction("Tune", menu)
            tune.triggered.connect(lambda: self._tuneConfiguration(column))

            menu.addActions([save, save_all])
            menu.addSeparator()
            menu.addActions([rename])
            menu.addSeparator()
            menu.addActions([close, close_right, close_others, close_all])
            menu.addSeparator()
            menu.addActions([tune])
        else:
            bar = QAction("Interpolate", menu)
            bar.triggered.connect(lambda: self._barConfiguration(cols))

            menu.addAction(bar)

        vheader_offset = self.table.verticalHeader().width()
        point.setX(point.x() + vheader_offset)
        menu.popup(self.mapToGlobal(point))

    # ContextMenu Actions
    @pyqtSlot(int)
    def _saveConfiguration(self, column):
        try:
            self._model.saveConfiguration(column)
            return True
        except (IntegrityError, InternalError):
            QMessageBox(QMessageBox.Warning, "Couldn't save",
                "Name already exists!").exec_()
        except OperationalError as e:
            self._showWarningBox("Unable to connect to database")
        except Exception as e:
            QMessageBox(QMessageBox.Warning, "Couldn't save",
                "Exception {} of type {} was caught".format(e, type(e))).exec_()

        return False

    @pyqtSlot(int)
    def _renameConfiguration(self, column):
        ''' Renames a configuration '''
        new_name, ok = QInputDialog.getText(self, "New name", "Rename to:")
        if ok and new_name:
            return self._model.renameConfiguration(column, new_name)

    @pyqtSlot(int)
    def _closeConfiguration(self, column):
        self._closeConfigurations([column])

    @pyqtSlot(int)
    def _closeConfigurationsToTheRight(self, column):
        columns = list()
        i = len(self._model.configurations) - 1
        while i > column:
            columns.append(i)
            i -= 1

        self._closeConfigurations(columns)

    @pyqtSlot(int)
    def _closeOtherConfigurations(self, column):
        columns = list()
        i = len(self._model.configurations) - 1
        while i >= 0:
            if i == column:
                i -= 1
                continue
            columns.append(i)
            i -= 1

        self._closeConfigurations(columns)

    @pyqtSlot()
    def _closeAllConfigurations(self):
        columns = list()
        i = len(self._model.configurations) - 1
        while i >= 0:
            columns.append(i)
            i -= 1

        self._closeConfigurations(columns)

    def _closeConfigurations(self, columns):
        save = self._maybeSaveChanges(columns)

        if save == QMessageBox.Discard:
            for column in columns:
                self._model.cleanUndo(column)
                self._model.closeConfiguration(column)
            return True
        elif save == QMessageBox.Save:
            for column in columns:
                if self._saveConfiguration(column):
                    self._model.cleanUndo(column)
                    self._model.closeConfiguration(column)
                else:
                    return False
            return True
        else:
            return False

    @pyqtSlot(int)
    def _tuneConfiguration(self, column):
        '''value, ok1 = QInputDialog.getDouble(self, "Select value", "\u0394\u03bd<sub>x</sub>:")'''
        dlg = TuneDlg(self)
        ok1 = dlg.exec_()
        if ok1:
            #Get Matrix Calculate deltaK and show to user
            tune = [dlg.tune_x.value(), dlg.tune_y.value()]
            inv_matrix = self._model.getTuneMatrix()
            if not inv_matrix:
                self._showWarningBox("Tune Matrix corrupted")
            delta_f = tune[0]*inv_matrix[0][0] + tune[1]*inv_matrix[0][1]
            delta_d = tune[0]*inv_matrix[1][0] + tune[1]*inv_matrix[1][1]
            #config_name, ok2 = QInputDialog.getText(self, "Select value", "New Configuration Name:")
            #if ok2:
            #    if not config_name:
            proceed = QMessageBox(QMessageBox.Question, "Delta K",
                "\u0394K<sub>d</sub> = {:1.3f}<br>\u0394K<sub>f</sub> = {:1.3f}<br>Proceed?".format(delta_d, delta_f),
                QMessageBox.Ok|QMessageBox.Cancel, self).exec_()
            if proceed == QMessageBox.Ok:
                config_name = self._getNextName()
                self._model.deriveConfiguration(config_name, column, ConfigModel.TUNE, [delta_d, delta_f])

    @pyqtSlot(int)
    def _barConfiguration(self, cols):
        if len(cols) != 2:
            raise SystemError("Must interpolate 2 columns")
        new_name, ok = QInputDialog.getText(self, "New name", "Rename to:")
        if ok:
            if not new_name:
                new_name = self._getNextName()

            self._model.interpolateConfiguration(new_name, cols[0].column(),
                    cols[1].column())

    #Window menu slots
    @pyqtSlot()
    def _addConfiguration(self):
        try:
            configs = self._model.getConfigurations()
            if configs:
                config, ok = QInputDialog.getItem(self, "Available Configurations",
                        "Select a configuration:", configs, 0, False)
                if ok and config:
                    if not self._isConfigurationLoaded(config):
                        self._model.loadConfiguration(config)
                    else:
                        QMessageBox(
                            QMessageBox.Information,
                            "Configuration already loaded",
                            "Configuration is already loaded. Close it or save the changes."
                        ).exec_()
                    #Highlight new column; or the one that is already loaded
                    col = self._model.getConfigurationColumn(config)
                    self.table.selectColumn(col)

            pass
        except FileNotFoundError as e:
            self._showWarningBox(e)
        except KeyError as e:
            message = ( "Configuration corrupted<br><br>"
                        "This configuration no longer represents<br>"
                        "the actual configuaration of elements in the<br>"
                        "Ring/Booster. It should be either deleted or updated")
            self._showWarningBox(message)
        except OperationalError as e:
            self._showWarningBox("Unable to connect to database")

        return

    @pyqtSlot()
    def _removeConfiguration(self):
        try:
            configs = self._model.getConfigurations()
            if configs:
                #Show configs available
                config, ok = QInputDialog.getItem(self, "Available Configurations",
                        "Select a configuration:", configs, 0, False)
                if ok and config:
                    if self._isConfigurationLoaded(config):
                        msg = "Configuration is currenty loaded; Delete it anyway?"
                    else:
                        msg = ( "This will permanently delete configuration {}."
                                "Proceed?").format(config)

                    if self._showDialogBox(msg) == QMessageBox.Cancel:
                        return

                    if self._model.deleteConfiguration(config):
                        msg = "Configuration {} was deleted.".format(config)
                    else:
                        msg = "Failed to delete configuration {}.".format(config)
                    self._showMessageBox(msg)
        except OperationalError as e:
            self._showWarningBox("Unable to connect to database")

    @pyqtSlot()
    def _loadCurrentConfiguration(self):
        #TODO: Loading box
        t = LoadingThread(self._getNextName(), self._model._vertical_header, self)
        dlg = LoadingDlg("Loading", len(self._model._vertical_header), self)
        t.taskUpdated.connect(dlg.update)
        t.taskFinished.connect(dlg.done)
        t.start()
        dlg.exec_()

    #Actions binded with keys
    def _saveChanges(self):
        for column in range(len(self._model.configurations)):
            self._saveConfiguration(column)

    def _closeConfigurationOnFocus(self):
        cols = self.table.selectionModel().selectedColumns()
        columns = list()
        for col in cols:
            columns.append(col.column())
        columns.sort(reverse=True)
        self._closeConfigurations(columns)

    def _renameOnFocus(self):
        cols = self.table.selectionModel().selectedColumns()
        if len(cols) == 1:
            self._renameConfiguration(cols[0].column())

    #Helpers
    def _isConfigurationLoaded(self, config_name):
        ret = self._model.getConfigurationColumn(config_name)

        if ret == -1:
            return False

        return True

    def _getNextName(self):
        #Treat if there already exist saved configuration with this name
        configs = self._model.getConfigurations()
        new_name = 'config-{}'.format(self.NEW_CONFIGURATION)
        while new_name in configs:
            self.NEW_CONFIGURATION += 1
            new_name = 'config-{}'.format(self.NEW_CONFIGURATION)
        return new_name

    def _maybeSaveChanges(self, columns):
        ask_to_save = False
        for column in columns:
            if not self._model.configurations[column].isSaved():
                ask_to_save = True
                break
        #If nothing to save, will close all columns
        if not ask_to_save:
            return QMessageBox.Discard
        #Ask if user wants to save changes
        msg_box = QMessageBox(
                QMessageBox.Question,
                "There are unsaved changes",
                "Keep changes?",
                QMessageBox.Save|QMessageBox.Cancel|QMessageBox.Discard,
                self)

        return msg_box.exec_()

    def _showWarningBox(self, message, title="Warning"):
        QMessageBox(QMessageBox.Warning, title, '{}'.format(message)).exec_()

    def _showMessageBox(self, message, title="Message"):
        return QMessageBox(QMessageBox.Information, title, message).exec_()

    def _showDialogBox(self, message, title="Dialog"):
        return QMessageBox(QMessageBox.Information, title, message,
                QMessageBox.Ok|QMessageBox.Cancel).exec_()
