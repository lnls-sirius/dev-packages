import re
from pydm.PyQt.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from pydm.PyQt.QtGui import QItemDelegate, QColor, QDoubleSpinBox, QItemDelegate
from siriuspy.servconf import db, ConfigurationPvs
from siriuspy.servconf.Configuration import Configuration


class ConfigDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(ConfigDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        col = index.column()
        pvname = index.model()._vertical_header[index.row()]['name']
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
    """Model for the configuration table."""

    TUNE, CHROMATICITY = range(2)
    UNDO_MEMORY = 75

    def __init__(self, config_type, parent=None):
        """Class constructor."""
        super(ConfigModel, self).__init__(parent)

        self._config_type = config_type
        self._setVerticalHeader()
        self._types = set()
        self._configurations = list()
        self._undo = list()
        self._redo = list()

    @property
    def configurations(self):
        """Return list of open configurations."""
        return self._configurations

    # QAbstractTableModel Overriden functions
    def rowCount(self, index=QModelIndex()):
        """Return the number of PVs for this configuration type."""
        return len(self._vertical_header)

    def columnCount(self, index=QModelIndex()):
        """Return the number of configurations currently open."""
        return len(self._configurations)

    def data(self, index, role=Qt.DisplayRole):
        """Set data of the table (override)."""
        if role == Qt.DisplayRole:
            pvname = self._vertical_header[index.row()]['name']
            pvtype = self._vertical_header[index.row()]['type']
            if pvtype == float:
                return QVariant("{:8.5f}".format(
                    self._configurations[index.column()].values[pvname]))
            else:
                raise NotImplementedError

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Set headers of the table (override)."""
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
                pvname = self._vertical_header[section]['name']
                # element = ':'.join(pvname.split(":")[:2])
                # vheader = "{:02d} - {}".format(section + 1, element)
                vheader = "{}".format(pvname)
                return QVariant(vheader)

        return QVariant(int(section + 1))

    def flags(self, index):
        """Override to make cells editable."""
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)

    def setData(self, index, value, role=Qt.EditRole):
        """Set cell data."""
        row = index.row()
        col = index.column()
        if index.isValid() and 0 <= row < len(self._vertical_header):
            pvname = self._vertical_header[row]['name']
            pvtype = self._vertical_header[row]['type']
            cast_val = Configuration.castTo(value, pvtype)
            # Record action for UNDO
            config_name = self._configurations[col].name
            old_value = self._configurations[col].values[pvname]
            cast_old_val = Configuration.castTo(old_value, pvtype)
            if len(self._undo) > self.UNDO_MEMORY:
                self._undo.pop(0)
            self._undo.append(
                (config_name,
                 lambda: self.setDataAlt(
                    row, config_name, cast_val, cast_old_val)))
            # Update Value
            self._configurations[col].setValue(pvname, cast_val)
            # Update view
            self.headerDataChanged.emit(Qt.Horizontal, col, col)
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertColumn(self, column, index=QModelIndex()):
        """Update table widget telling it a new column was inserted."""
        self.beginInsertColumns(index, column, column)
        self.endInsertColumns()

        return True

    def removeColumns(self, column, count=1, index=QModelIndex()):
        """Update table widget telling it a column was removed."""
        self.beginRemoveColumns(index, column, column + count - 1)
        self.endRemoveColumns()

        return True

    # Private members
    def _setVerticalHeader(self):
        # Used to sort section elements dict
        def subSection(elem):
            if re.search('-Fam', elem):
                return 0
            else:
                return 1

        def elem(elem):
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

        self._vertical_header = list()
        pvs = getattr(ConfigurationPvs, self._config_type)().pvs()
        for name, type_ in pvs.items():
            self._vertical_header.append({'name': name, 'type': type_})
        self._vertical_header.sort(
            key=lambda x: elem(x['name']) + subSection(x['name']))

    def _addConfiguration(self, config_name, column, values):
        """Add new configuration to table."""
        # Create new configuration
        if values is None:
            new_configuration = \
                Configuration.getConfiguration(self._config_type, config_name)
            if not new_configuration:
                raise FileNotFoundError(
                    "Configuration {} not found".format(config_name))
            if not new_configuration.check():
                raise KeyError(
                    "Configuration {} corrupted".format(config_name))
        else:
            new_configuration = \
                Configuration(self._config_type, config_name, values)
        # Add to model in case it was successfully created
        if column >= self.columnCount():
            self._configurations.append(new_configuration)
        else:
            self._configurations.insert(column, new_configuration)
        # Call insertColumns to update table widget
        self.insertColumn(column)

    # Interface functions view - model
    def getConfigurationColumn(self, config_name):
        """Return column number of the given configuration."""
        for configuration in self._configurations:
            if config_name in (configuration.name, configuration.old_name):
                return self._configurations.index(configuration)

        return -1

    def getConfigurations(self):
        """Return name of saved configurations."""
        connection = db.get_connection()
        with connection.cursor() as cursor:
            sql = "SELECT name FROM configuration WHERE classname=%s"
            # r = cursor.execute(sql, (self._config_type))
            cursor.execute(sql, (self._config_type))
            qry_res = cursor.fetchall()

        configurations = [x['name'] for x in qry_res]
        return configurations

    def getTuneMatrix(self):
        """Get tune matrix from db."""
        conn = db.get_connection()
        with conn.cursor() as cursor:
            sql = ("SELECT `line`, `column`, value "
                   "FROM parameter_values "
                   "WHERE name='standard_matrix' AND type='tune' "
                   "ORDER BY `line`, `column`")
            # ret = cursor.execute(sql)
            cursor.execute(sql)
            qry = cursor.fetchall()

        new_line = list()
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

    # Actions
    def saveConfiguration(self, column):
        """Save configuration if it is dirty."""
        if not self._configurations[column].isSaved():
            self._configurations[column].save()
        # Isuue a change in the table and header
        idx1 = self.index(0, column)
        idx2 = self.index(self.rowCount() - 1, column)
        self.dataChanged.emit(idx1, idx2)
        self.headerDataChanged.emit(Qt.Horizontal, column, column)

    def renameConfiguration(self, column, new_name):
        """Change configuration name."""
        self._configurations[column].name = new_name

    def deriveConfiguration(self, config_name, base_column, func, parameters):
        """Create new configuration from existing one TUNE or CHROMATICITY."""
        # Derives new configuration
        new_configuration = dict()
        for pv in self._vertical_header:
            pvname = pv['name']
            # pvtype = pv['type']
            value = self._configurations[base_column].values[pvname]
            if func == self.TUNE:  # Applied to quadrupoles
                if re.search("-QD", pvname):
                    new_value = value + parameters[0]
                elif re.search("QF", pvname):
                    new_value = value + parameters[1]
                else:
                    new_value = value
            elif func == self.CHROMATICITY:
                new_value = value
            else:
                new_value = value
            new_configuration[pvname] = new_value
        # Add configuration to table as a new column
        self._addConfiguration(config_name, base_column+1, new_configuration)

    def closeConfiguration(self, column):
        """Close a configuration."""
        self._configurations.remove(self._configurations[column])
        self.removeColumns(column)

    def interpolateConfiguration(self, config_name, column1, column2):
        """Linear interpolation of 2 configurations."""
        for type_ in self._getTypes():
            if type_ not in [int, float]:
                raise ValueError("Cannot interpolate non-numeric values")

        new_configuration = dict()
        for pv in self._vertical_header:
            pvname = pv['name']
            value1 = self._configurations[column1].values[pvname]
            value2 = self._configurations[column2].values[pvname]
            new_configuration[pvname] = (value1 + value2)/2
        # Choose where to place new column
        new_column = column1 if column1 > column2 else column2
        self._addConfiguration(config_name, new_column + 1, new_configuration)

    def loadConfiguration(self, name, values=None):
        """Load configuration from database."""
        self._addConfiguration(name, self.columnCount(), values)

    def deleteConfiguration(self, config):
        """Delete configuration from database."""
        col = self.getConfigurationColumn(config)
        if col >= 0:
            self.closeConfiguration(col)
        return Configuration.delete(config, self._config_type)

    # Implements undo/redo
    def setDataAlt(self, row, config_name, value, old_value, redo=True):
        """Called by the undo/redo methods to change data on table."""
        pvname = self._vertical_header[row]['name']
        # pvtype = self._vertical_header[row]['type']
        column = self.getConfigurationColumn(config_name)
        index = self.index(row, column)
        self._configurations[column].setValue(pvname, old_value)
        if redo:
            if len(self._redo) > self.UNDO_MEMORY:
                self._redo.pop(0)
            self._redo.append(
                (config_name,
                 lambda: self.setDataAlt(
                    row, config_name, old_value, value, False)))
        else:
            if len(self._undo) > self.UNDO_MEMORY:
                self._undo.pop(0)
            self._undo.append(
                (config_name,
                 lambda: self.setDataAlt(
                    row, config_name, old_value, value, True)))
        # Update view
        self.headerDataChanged.emit(
            Qt.Horizontal, index.column(), index.column())
        self.dataChanged.emit(index, index)

    def cleanUndo(self, column):
        """Clean undo/redo actions for given column."""
        config_name = self._configurations[column].name
        for i, action in enumerate(self._undo):
            if action[0] == config_name:
                self._undo.pop(i)

        for i, action in enumerate(self._redo):
            if action[0] == config_name:
                self._redo.pop(i)

    def _getTypes(self):
        if not self._types:
            for pv in self._vertical_header:
                self._types.add(pv['type'])
        return self._types
