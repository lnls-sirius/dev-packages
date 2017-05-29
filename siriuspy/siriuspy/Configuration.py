import re
from . import ConfigurationPvs
from . import db
from ..pwrsupply import psdata
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Column, String, Float, ForeignKeyConstraint
from sqlalchemy.orm import relationship

Base = declarative_base()


class ConfigurationValues(Base):
    __tablename__ = 'configuration_values'

    name = Column(String(32), primary_key=True)
    classname = Column(String(32), primary_key=True)
    pvname = Column(String(32), primary_key=True)
    typename = Column(String(16), nullable=False)
    value = Column(String(255), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['name', 'classname'],
            ['configuration.name', 'configuration.classname'],
        ),
    )

    def __init__(self, name, classname, pvname, typename, value):
        self.name = name
        self.classname = classname
        self.pvname = pvname
        self.typename = str(typename)
        self.value = str(value)

    def __repr__(self):
        return "ConfigurationValue(name=%s classname=%s, pvname=%s, value=%s)" % (self.name, self.classname, self.pvname, self.value)



class Configuration(Base):
    __tablename__ = 'configuration'

    name = Column(String(32), primary_key=True)
    classname = Column(String(32), primary_key=True)
    values = relationship('ConfigurationValues', foreign_keys=[ConfigurationValues.name, ConfigurationValues.classname], lazy='dynamic')

    def __init__(self, name, classname, values):
        self.name = name
        self.classname = classname
        self.values = values

    def __repr__(self):
        return "Configuration(name=%s classname=%s)" % (self.name, self.classname)


# class Configuration:
#     def __init__(self, classname, name, values):
#         self._class = classname
#         self._name = name
#         self._old_name = None
#
#         self._pvs = getattr(ConfigurationPvs, self._class)().pvs()
#
#         self._values = {}
#
#         self._dirty_pvs = dict()
#         self._renamed = False
#
#         #self._connection = None
#         if values is None:
#             self._load()
#             self._isNew = False
#         else:
#             self._values = values
#             self._isNew = True
#
#     @classmethod
#     def getConfiguration(configuration, section, name):
#         try:
#             c = configuration(section, name, None)
#             return c
#         except FileNotFoundError as e:
#             return 0
#
#     def check(self):
#         print(self._values)
#         if len(self._pvs) != len(self._values.keys()):
#             return False
#
#         for pvname in self._pvs:
#             if pvname not in self._values.keys():
#                 return False
#
#         return True
#
#     def getValue(self, pvname):
#         return self._values[pvname]
#
#     def setValue(self, pvname, value):
#         if value != self._values[pvname]:
#             if not self._isNew:
#                 if pvname in self._dirty_pvs.keys() and value == self._dirty_pvs[pvname]:
#                     del self._dirty_pvs[pvname]
#                 elif pvname not in self._dirty_pvs.keys():
#                     self._dirty_pvs[pvname] = self._values[pvname]
#             self._values[pvname] = value
#
#     @property
#     def name(self):
#         return self._name
#
#     @name.setter
#     def name(self, new_name):
#         if not self._renamed and not self._isNew:
#             self._old_name = self._name
#         self._name = new_name
#         self._renamed = True
#
#     @property
#     def section(self):
#         return self._section
#
#     @property
#     def pvs(self):
#         return self._pvs
#
#     @property
#     def old_name(self):
#         return self._old_name
#
#     @property
#     def values(self):
#         return self._values
#
#     @property
#     def dirty(self):
#         return len(self._dirty_pvs) > 0
#
#     @property
#     def renamed(self):
#         return self._renamed
#
#     @renamed.setter
#     def renamed(self, value):
#         self._renamed = value
#
#     @property
#     def isNew(self):
#         return self._isNew
#
#     def isSaved(self):
#         if self.dirty or self._renamed or self._isNew:
#             return False
#
#         return True
#
#     #Actions
#     def _load(self):
#         values = {}
#         connection = db.get_connection()
#         with connection.cursor() as cursor:
#             sql = "SELECT pvname, typename, value FROM configuration_values WHERE name=%s AND classname=%s"
#             result = cursor.execute(sql, (self._name, self._class))
#             if not result:
#                 raise FileNotFoundError
#             qry_res = cursor.fetchall()
#
#             for pv in qry_res:
#                 self._values[pv['pvname']] = pv['value']
#
#         return True
#
#     def save(self):
#         if self._renamed:
#             self.updateName()
#         if self.dirty or self._isNew:
#             connection = db.get_connection()
#             with connection.cursor() as cursor:
#                 if self._isNew:
#                     sql = ( "INSERT INTO configuration(name, classname) "
#                             "VALUES (%s, %s)")
#                     cursor.execute(sql, (self._name, self._class))
#
#                     for pvname, value in self._values.items():
#                         sql = ( "INSERT INTO configuration_values"
#                                 "(name, classname, pvname, value) "
#                                 "VALUES (%s, %s, %s, %s)")
#                         cursor.execute(sql, (self._name, self._class, pvname, value))
#                 else:
#                     for pvname in self._dirty_pvs:
#                         sql =   ("UPDATE configuration_values SET value=%s "
#                                 "WHERE name=%s AND classname=%s AND pvname=%s")
#                         cursor.execute(sql, (self._values[pvname], self._name, self._class, pvname))
#
#                 connection.commit()
#                 self._dirty_pvs = dict()
#                 self._isNew = False
#
#     @staticmethod
#     def delete(name, classname):
#         connection = db.get_connection()
#         with connection.cursor() as cursor:
#             sql = "DELETE FROM configuration WHERE name=%s AND classname=%s"
#             result = cursor.execute(sql, (name, classname))
#             if result:
#                 connection.commit()
#                 return True
#
#             return False
#
#     def updateName(self):
#         connection = db.get_connection()
#         with connection.cursor() as cursor:
#             #Update database
#             sql = "UPDATE configuration SET name=%s WHERE name=%s and classname=%s"
#             cursor.execute(sql, (self._name, self._old_name, self._class))
#             connection.commit()
#             self._renamed = False
#
#     @staticmethod
#     def configurations(classname=None):
#         connection = db.get_connection()
#         with connection.cursor() as cursor:
#             if classname is None:
#                 sql = "SELECT * FROM configuration"
#                 result = cursor.execute(sql)
#                 if result:
#                     return cursor.fetchall()
#
#         return None
#
#     @staticmethod
#     def printConfigurations(classname=None):
#         print("+---------------------------------+---------------------------------+")
#         print("|{:32s} | {:32s}|".format("Name", "Class"))
#         print("+---------------------------------+---------------------------------+")
#         configs = Configuration.configurations(classname)
#         if configs is not None:
#             for config in configs:
#                 print("|{:32s} | {:32s}|".format(config['name'], config['classname']))
#         print("+---------------------------------+---------------------------------+")
