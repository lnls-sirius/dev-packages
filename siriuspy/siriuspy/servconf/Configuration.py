import re
from . import db, ConfigurationPvs
from ..pwrsupply import psdata

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
#         return "ConfigurationValue(name=%s classname=%s, pvname=%s, value=%s)" % (self.name, self.classname, self.pvname, self.value)
#
# class Configuration(Base):
#     __tablename__ = 'configuration'
#
#     name = Column(String(32), primary_key=True)
#     classname = Column(String(32), primary_key=True)
#     values = relationship('ConfigurationValues', foreign_keys=[ConfigurationValues.name, ConfigurationValues.classname], lazy='dynamic')
#
#     def __init__(self, name, classname, values):
#         self.name = name
#         self.classname = classname
#         self.values = values
#
#     def __repr__(self):
#         return "Configuration(name=%s classname=%s)" % (self.name, self.classname)

class Configuration:
    def __init__(self, classname, name, values):
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
        try:
            c = configuration(classname, name, None)
            return c
        except FileNotFoundError as e:
            return 0

    def check(self):
        if len(self._pvs) != len(self.values.keys()):
            return False

        for pvname in self._pvs:
            if pvname not in self.values.keys():
                return False

        return True

    #Actions
    def _load(self):
        values = {}
        connection = db.get_connection()
        with connection.cursor() as cursor:
            sql = "SELECT pvname, typename, value FROM configuration_values WHERE name=%s AND classname=%s"
            result = cursor.execute(sql, (self._name, self._classname))
            if not result:
                raise FileNotFoundError
            qry_res = cursor.fetchall()

            for pv in qry_res:
                value = Configuration.castTo(pv['value'], self._pvs[pv['pvname']])
                self._values[pv['pvname']] = value

        return True

    def save(self):
        if self._renamed:
            self.updateName()
        if self.dirty or self._isNew:
            connection = db.get_connection()
            with connection.cursor() as cursor:
                if self._isNew:
                    sql = ( "INSERT INTO configuration(name, classname) "
                            "VALUES (%s, %s)")
                    cursor.execute(sql, (self._name, self._classname))

                    for pvname, value in self._values.items():
                        sql = ( "INSERT INTO configuration_values"
                                "(name, classname, pvname, typename, value) "
                                "VALUES (%s, %s, %s, %s, %s)")
                        #cast to string
                        str_value = Configuration.castToStr(value)
                        typename = str(type(value))
                        cursor.execute(sql, (self._name, self._classname,
                            pvname, typename, str_value))
                else:
                    for pvname in self._dirty_pvs:
                        sql =   ("UPDATE configuration_values SET value=%s "
                                "WHERE name=%s AND classname=%s AND pvname=%s")
                        cursor.execute(sql, (self._values[pvname], self._name,
                            self._classname, pvname))

            connection.commit()
            self._dirty_pvs = dict()
            self._isNew = False

    @staticmethod
    def delete(name, classname):
        connection = db.get_connection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM configuration WHERE name=%s AND classname=%s";
            result = cursor.execute(sql, (name, classname))
            if result:
                connection.commit()
                return True

            return False

    def updateName(self):
        connection = db.get_connection()
        with connection.cursor() as cursor:
            #Update database
            sql = "UPDATE configuration SET name=%s WHERE name=%s and classname=%s"
            cursor.execute(sql, (self._name, self._old_name, self._classname))
        connection.commit()
        self._renamed = False

    #Helpers
    @staticmethod
    def castTo(value, typename):
        if typename in [int, float, str]:
            return typename(value)
        else:
            raise NotImplementedError

    @staticmethod
    def castToStr(value):
        type_ = type(value)
        if type_ in [int, float, str]:
            return type_(value)
        else:
            raise NotImplementedError


    #Properties
    def getValue(self, pvname):
        return self._values[pvname]

    def setValue(self, pvname, value):
        if value != self._values[pvname]:
            if not self._isNew:
                if pvname in self._dirty_pvs.keys() and value == self._dirty_pvs[pvname]:
                    del self._dirty_pvs[pvname]
                elif pvname not in self._dirty_pvs.keys():
                    self._dirty_pvs[pvname] = self._values[pvname]
            self._values[pvname] = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if not self._renamed and not self._isNew:
            self._old_name = self._name
        self._name = new_name
        self._renamed = True

    @property
    def pvs(self):
        return self._pvs

    @property
    def classname(self):
        return self._classname

    @property
    def old_name(self):
        return self._old_name

    @property
    def values(self):
        return self._values

    @property
    def dirty(self):
        return len(self._dirty_pvs) > 0

    @property
    def renamed(self):
        return self._renamed

    @renamed.setter
    def renamed(self, value):
        self._renamed = value

    @property
    def isNew(self):
        return self._isNew

    def isSaved(self):
        if self.dirty or self._renamed or self._isNew:
            return False

        return True
