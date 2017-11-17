"""Defines the Configuration class.

This class is used as an interface with the database.
"""
from . import db, ConfigurationPvs

# class ConfigurationValues(Base):
#     __tablename__ = 'configuration_values'
#
#     name = Column(String(32), primary_key=True)
#     classname = Column(String(32), primary_key=True)
#     pvname = Column(String(32), primary_key=True)
#     typename = Column(String(16), nullable=False)
#     value = Column(String(255), nullable=False)
#
#     __table_args__ = (
#         ForeignKeyConstraint(
#             ['name', 'classname'],
#             ['configuration.name', 'configuration.classname'],
#         ),
#     )
#
#     def __init__(self, name, classname, pvname, typename, value):
#         self.name = name
#         self.classname = classname
#         self.pvname = pvname
#         self.typename = str(typename)
#         self.value = str(value)
#
#     def __repr__(self):
#         return "ConfigurationValue(name=%s classname=%s, pvname=%s, value=%s)
# " % (self.name, self.classname, self.pvname, self.value)
#
# class Configuration(Base):
#     __tablename__ = 'configuration'
#
#     name = Column(String(32), primary_key=True)
#     classname = Column(String(32), primary_key=True)
#     values = relationship('ConfigurationValues',
#                           foreign_keys=[ConfigurationValues.name,
#                            ConfigurationValues.classname], lazy='dynamic')
#
#     def __init__(self, name, classname, values):
#         self.name = name
#         self.classname = classname
#         self.values = values
#
#     def __repr__(self):
#         return "Configuration(
#            name=%s classname=%s)" % (self.name, self.classname)


class Configuration:
    """Class to read and maintain a configuration from the database."""

    def __init__(self, classname, name, values):
        """Class constructor.

        Classname and name are the primary keys to find a configuration in the
        database. Classname must correspond to one of the classes defined in
        ConfigurationPvs that define different group of devices.
        """
        self._classname = classname
        self._name = name
        self._old_name = None

        self._values = {}
        self._pvs = getattr(ConfigurationPvs, classname)().pvs()

        self._dirty_pvs = dict()
        self._renamed = False

        if values is None:
            self._load()
            self._isNew = False
        else:
            self._values = values
            self._isNew = True

    @classmethod
    def getConfiguration(configuration, classname, name):
        """Return a configuration if it exists."""
        try:
            c = configuration(classname, name, None)
            return c
        except FileNotFoundError as e:
            return 0

    def check(self):
        """Check if PVs in this configuration are valid.

        The PVs in the configuraiton must be the same as the ones read from the
        static files. If the elements (in the static file) change the
        configuration will no longer be valid and must be deleted or updated.
        """
        if len(self._pvs) != len(self.values.keys()):
            return False

        for pvname in self._pvs:
            if pvname not in self.values.keys():
                return False

        return True

    # Actions
    def _load(self):
        connection = db.get_connection()
        with connection.cursor() as cursor:
            sql = ("SELECT pvname, typename, value "
                   "FROM configuration_values "
                   "WHERE name=%s AND classname=%s")
            result = cursor.execute(sql, (self._name, self._classname))
            if not result:
                raise FileNotFoundError
            qry_res = cursor.fetchall()

            for pv in qry_res:
                value = Configuration.castTo(
                    pv['value'], self._pvs[pv['pvname']])
                self._values[pv['pvname']] = value

        return True

    def save(self):
        """Persist configuration PV values."""
        if self._renamed:
            self.updateName()
        if self.dirty or self._isNew:
            connection = db.get_connection()
            with connection.cursor() as cursor:
                if self._isNew:
                    sql = ("INSERT INTO configuration(name, classname) "
                           "VALUES (%s, %s)")
                    cursor.execute(sql, (self._name, self._classname))

                    for pvname, value in self._values.items():
                        sql = ("INSERT INTO configuration_values"
                               "(name, classname, pvname, typename, value) "
                               "VALUES (%s, %s, %s, %s, %s)")
                        # cast to string
                        str_value = Configuration.castToStr(value)
                        typename = str(type(value))
                        cursor.execute(sql, (self._name, self._classname,
                                             pvname, typename, str_value))
                else:
                    for pvname in self._dirty_pvs:
                        sql = ("UPDATE configuration_values SET value=%s "
                               "WHERE name=%s AND classname=%s AND pvname=%s")
                        cursor.execute(sql, (self._values[pvname], self._name,
                                             self._classname, pvname))

            connection.commit()
            self._dirty_pvs = dict()
            self._isNew = False

    @staticmethod
    def delete(name, classname):
        """Delete given configuration."""
        connection = db.get_connection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM configuration WHERE name=%s AND classname=%s"
            result = cursor.execute(sql, (name, classname))
            if result:
                connection.commit()
                return True

            return False

    def updateName(self):
        """Persist configuration name."""
        connection = db.get_connection()
        with connection.cursor() as cursor:
            # Update database
            sql = ("UPDATE configuration "
                   "SET name=%s "
                   "WHERE name=%s and classname=%s")
            cursor.execute(sql, (self._name, self._old_name, self._classname))
        connection.commit()
        self._renamed = False

    # Helpers
    @staticmethod
    def castTo(value, typename):
        """Cast value read from db to given typename."""
        if typename in [int, float, str]:
            return typename(value)
        else:
            raise NotImplementedError

    @staticmethod
    def castToStr(value):
        """Cast value to be saved in db to string."""
        type_ = type(value)
        if type_ in [int, float, str]:
            return type_(value)
        else:
            raise NotImplementedError

    # Properties
    def getValue(self, pvname):
        """Return the value of a given PV."""
        return self._values[pvname]

    def setValue(self, pvname, value):
        """Set value of a given PV."""
        if value != self._values[pvname]:
            if not self._isNew:
                if pvname in self._dirty_pvs.keys() and \
                        value == self._dirty_pvs[pvname]:
                    del self._dirty_pvs[pvname]
                elif pvname not in self._dirty_pvs.keys():
                    self._dirty_pvs[pvname] = self._values[pvname]
            self._values[pvname] = value

    @property
    def name(self):
        """Return configuration name."""
        return self._name

    @name.setter
    def name(self, new_name):
        """Set configuration name."""
        if not self._renamed and not self._isNew:
            self._old_name = self._name
        self._name = new_name
        self._renamed = True

    @property
    def pvs(self):
        """Return PVs dict."""
        return self._pvs

    @property
    def classname(self):
        """Return the section elements belong to."""
        return self._classname

    @property
    def old_name(self):
        """Return the configuration name as in the database.

        When the configuration is persisted this name name will be the same
        as self._name.
        """
        return self._old_name

    @property
    def values(self):
        """Return PV values."""
        return self._values

    @property
    def dirty(self):
        """Return wether there is usaved data."""
        return len(self._dirty_pvs) > 0

    @property
    def renamed(self):
        """Return wether the configuration name changed."""
        return self._renamed

    @renamed.setter
    def renamed(self, value):
        """Set renamed."""
        self._renamed = value

    @property
    def isNew(self):
        """Return wether this configuration was loaded from db."""
        return self._isNew

    def isSaved(self):
        """Return wether this configuration is persisted."""
        if self.dirty or self._renamed or self._isNew:
            return False

        return True
