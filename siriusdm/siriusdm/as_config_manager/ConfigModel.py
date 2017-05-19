import re
from pydm.PyQt.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from pydm.PyQt.QtGui import QItemDelegate, QColor, QDoubleSpinBox, QItemDelegate
from siriuspy.servconf import db
from siriuspy.servconf import SectionConfiguration


class ConfigDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(ConfigDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        col = index.column()
        pvname = index.model()._vertical_header[index.row()]
        if pvname in index.model().configurations[col]._dirty_pvs.keys():
            color = QColor(200, 0, 0)
            painter.fillRect(option.rect, color)
            QItemDelegate.paint(self, painter, option, index)
        elif not index.model().configurations[col].isSaved():
            color = QColor(230, 230, 230)
            painter.fillRect(option.rect, color)
            QItemDelegate.paint(self, painter, option, index)
        else:
            QItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(5)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        editor.setValue(float(value.value()))

class ConfigModel(QAbstractTableModel):

    TUNE, CHROMATICITY = range(2)
    UNDO_MEMORY = 75

    def __init__(self, section, parent=None):
        super(ConfigModel, self).__init__(parent)

        self._section = section
        self._vertical_header = list()
        self._configurations = list()
        self._undo = list()
        self._redo = list()
        self._buildAreaElementsDict()

    @property
    def configurations(self):
        return self._configurations

    #QAbstractTableModel Overriden functions
    def rowCount(self, index=QModelIndex()):
        return len(self._vertical_header)

    def columnCount(self, index=QModelIndex()):
        return len(self._configurations)

    def data(self, index, role=Qt.DisplayRole):
        ''' (override) Sets data of the table '''
        if role == Qt.DisplayRole:
            pvname = self._vertical_header[index.row()]
            return QVariant("{:8.5f}".format(self._configurations[index.column()].values[pvname]))

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        ''' (override) Sets headers of the table '''
        if role == Qt.TextAlignmentRole:
            pass
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if self._configurations[section].isSaved():
                return QVariant(self._configurations[section].name)
            else:
                return QVariant(self._configurations[section].name + "*")
        elif orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                element = ':'.join(self._vertical_header[section].split(":")[:2])
                #vheader = "{:02d} - {}".format(section + 1, element)
                vheader = "{}".format(element)
                return QVariant(vheader)

        return QVariant(int(section + 1))

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|Qt.ItemIsEditable)

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self._vertical_header):
            pvname = self._vertical_header[index.row()]

            config_name = self._configurations[index.column()].name
            old_value = self._configurations[index.column()].values[pvname]
            if len(self._undo) > self.UNDO_MEMORY:
                self._undo.pop(0)
            self._undo.append((config_name, lambda: self.setDataAlt(pvname, config_name, value, old_value)))

            self._configurations[index.column()].setValue(pvname, value)
            self.headerDataChanged.emit(Qt.Horizontal, index.column(), index.column())
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertColumn(self, column, index=QModelIndex()):
        ''' Updates table widget telling it a new column was inserted (override)'''
        self.beginInsertColumns(index, column, column)
        self.endInsertColumns()

        return True

    def removeColumns(self, column, count=1, index=QModelIndex()):
        self.beginRemoveColumns(index, column, column + count - 1)
        self.endRemoveColumns()

        return True

    #Used to sort section elements dict
    def _subSection(self, elem):
        if re.search('-Fam', elem):
            return 0
        else:
            return 1

    def _elem(self, elem):
        name = elem
        if re.search('-B', name):
            return 0
        elif re.search('-QF', name):
            return 2
        elif re.search('-QD', name):
            return 4
        elif re.search('-Q[0-9]', name):
            return 6
        elif re.search('-SF', name):
            return 8
        elif re.search('-SD', name):
            return 10
        elif re.search('-CH', name):
            return 12
        elif re.search('-CV', name):
            return 14
        elif re.search('-FCH', name):
            return 16
        elif re.search('-FCV', name):
            return 18
        else:
            return 20

    #Private members
    def _buildAreaElementsDict(self):
        for pv in SectionConfiguration.getSectionPvs(self._section):
            self._vertical_header.append(pv)
        self._vertical_header.sort(key=lambda x: self._elem(x) + self._subSection(x))

    def _addConfiguration(self, config_name, column, values):
        ''' Adds new configuration to table '''
        #Create new configuration
        if values is None:
            new_configuration = SectionConfiguration.getConfiguration(self._section, config_name)
            if not new_configuration:
                raise FileNotFoundError("Configuration {} not found".format(config_name))
            if not SectionConfiguration.checkConfiguration(new_configuration):
                raise KeyError("Configuration {} corrupted".format(config_name))
        else:
            new_configuration = SectionConfiguration(self._section, config_name, values)
        #Add to model in case it was successfully created
        if column >= self.columnCount():
            self._configurations.append(new_configuration)
        else:
            self._configurations.insert(column, new_configuration)
        #Call insertColumns to update table widget
        self.insertColumn(column)

    #Interface functions view - model
    def getConfigurationColumn(self, config_name):
        for configuration in self._configurations:
            if config_name in (configuration.name, configuration.old_name):
                return self._configurations.index(configuration)

        return -1

    def getConfigurations(self):
        ''' Returns name of saved configurations '''
        connection = db.get_connection()
        with connection.cursor() as cursor:
            sql = "SELECT name FROM section_configuration WHERE section=%s";
            r = cursor.execute(sql, (self._section))
            qry_res = cursor.fetchall()

        return [x['name'] for x in qry_res]

    def getTuneMatrix(self):
        conn = db.get_connection()

        with conn.cursor() as cursor:
            sql = "SELECT `line`, `column`, value FROM parameter_values WHERE name='standard_matrix' AND type='tune' ORDER BY `line`, `column`";
            ret = cursor.execute(sql)
            qry = cursor.fetchall()

        last_line = -1
        result = list()
        for row in qry:
            line = row['line']
            if line != last_line:
                if last_line > -1:
                    result.append(new_line)
                last_line = line
                new_line = list()

            if row['column'] == len(new_line):
                new_line.append(row['value'])
            else:
                return 0
        result.append(new_line)

        if len(result) > 1:
            return result
        else:
            return result[0]

    #Actions
    def saveConfiguration(self, column):
        if not self._configurations[column].isSaved():
            self._configurations[column].save()
        #Isuue a change in the table and header
        idx1 = self.index(0, column)
        idx2 = self.index(self.rowCount() - 1, column)
        self.dataChanged.emit(idx1, idx2)
        self.headerDataChanged.emit(Qt.Horizontal, column, column)

    def renameConfiguration(self, column, new_name):
        self._configurations[column].name = new_name

    def deriveConfiguration(self, config_name, base_column, func, parameters):
        ''' Create new configuration from existing one '''
        #Derives new configuration
        new_configuration = dict()
        for pvname in self._vertical_header:
            value = self._configurations[base_column].values[pvname]
            if func == self.TUNE:
                if re.search("-QD", pvname):
                    new_value = value + parameters[0]
                elif re.search("QF", pvname):
                    new_value = value + parameters[1]
                else:
                    new_value = value
            else:
                new_value = value
            new_configuration[pvname] = new_value
        #Add configuration to table as a new column
        self._addConfiguration(config_name, base_column+1, new_configuration)

    def closeConfiguration(self, column):
        self._configurations.remove(self._configurations[column])
        self.removeColumns(column)

    def interpolateConfiguration(self, config_name, column1, column2):
        ''' Linear interpolation of 2 configurations '''
        new_configuration = dict()
        for pvname in self._vertical_header:
            value1 = self._configurations[column1].values[pvname]
            value2 = self._configurations[column2].values[pvname]
            new_configuration[pvname] = (value1 + value2)/2
        #Choose where to place new column
        new_column = column1 if column1 > column2 else column2
        self._addConfiguration(config_name, new_column + 1, new_configuration)

    def loadConfiguration(self, config):
        ''' Loads configuration from database '''
        self._addConfiguration(config, self.columnCount(), None)

    def deleteConfiguration(self, config):
        col = self.getConfigurationColumn(config)
        if col >= 0:
            self.closeConfiguration(col)
        return SectionConfiguration.delete(config, self._section)

    def loadCurrentConfiguration(self, name, config):
        ''' Loads current state of booster element '''
        #Add new configuration
        self._addConfiguration(name, self.columnCount(), config)

    #Implements undo/redo
    def setDataAlt(self, pvname, config_name, value, old_value, redo=True):
        column = self.getConfigurationColumn(config_name)
        row = self._vertical_header.index(pvname)
        index = self.index(row, column)
        self._configurations[column].setValue(pvname, old_value)

        if redo:
            if len(self._redo) > self.UNDO_MEMORY:
                self._redo.pop(0)
            self._redo.append((config_name, lambda: self.setDataAlt(pvname, config_name, old_value, value, False)))
        else:
            if len(self._undo) > self.UNDO_MEMORY:
                self._undo.pop(0)
            self._undo.append((config_name, lambda: self.setDataAlt(pvname, config_name, old_value, value, True)))

        self.headerDataChanged.emit(Qt.Horizontal, index.column(), index.column())
        self.dataChanged.emit(index, index)

    def cleanUndo(self, column):
        config_name = self._configurations[column].name
        for i, action in enumerate(self._undo):
            if action[0] == config_name:
                self._undo.pop(i)

        for i, action in enumerate(self._redo):
            if action[0] == config_name:
                self._redo.pop(i)
