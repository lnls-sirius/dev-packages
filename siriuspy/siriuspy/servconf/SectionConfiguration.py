import re
from . import db
from ..pwrsupply import psdata

class SectionConfiguration:
    PVS = list()

    def __init__(self, section, name, values):
        self._section = section
        self._name = name
        self._old_name = None

        self._values = {}

        self._dirty_pvs = dict()
        self._renamed = False

        self._connection = db.get_connection()
        if values is None:
            self._load()
            self._isNew = False
        else:
            self._values = values
            self._isNew = True

    @classmethod
    def getConfiguration(configuration, section, name):
        try:
            c = configuration(section, name, None)
            return c
        except FileNotFoundError as e:
            return 0

    @staticmethod
    def getForce(slot):
        if re.match("^[A-Z]{2}-\w{2,4}:PS-B", slot):
            return "Energy"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-Q", slot):
            return "KL"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-S", slot):
            return "SL"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-(C|F)", slot):
            return "Angle"
        else:
            return "???"

    @staticmethod
    def getSectionPvs(section):
        if len(SectionConfiguration.PVS) == 0:
            slots = psdata.get_names()
            for slot in slots:
                pv = slot + ":" + SectionConfiguration.getForce(slot) + "-RB"
                SectionConfiguration.PVS.append(pv)

        return [x for x in SectionConfiguration.PVS if re.match("^" + section + "-\w{2,4}:PS-(B|Q|S|C|F)", x)]

    @staticmethod
    def checkConfiguration(configuration):
        section_pvs = SectionConfiguration.getSectionPvs(configuration.section)

        if len(section_pvs) != len(configuration.values.keys()):
            return False

        for pvname in section_pvs:
            if pvname not in configuration.values.keys():
                return False

        return True

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
    def section(self):
        return self._section

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

    #Actions
    def _load(self):
        values = {}
        with self._connection.cursor() as cursor:
            sql = "SELECT pvname, value FROM section_configuration_values WHERE name=%s AND section=%s"
            result = cursor.execute(sql, (self._name, self._section))
            if not result:
                raise FileNotFoundError
            qry_res = cursor.fetchall()

            for pv in qry_res:
                self._values[pv['pvname']] = pv['value']

        return True

    def save(self):
        if self._renamed:
            self.updateName()
        if self.dirty or self._isNew:
            with self._connection.cursor() as cursor:
                if self._isNew:
                    sql = ( "INSERT INTO section_configuration(name, section) "
                            "VALUES (%s, %s)")
                    cursor.execute(sql, (self._name, self._section))

                    for pvname, value in self._values.items():
                        sql = ( "INSERT INTO section_configuration_values"
                                "(name, section, pvname, value) "
                                "VALUES (%s, %s, %s, %s)")
                        cursor.execute(sql, (self._name, self._section, pvname, value))
                else:
                    for pvname in self._dirty_pvs:
                        sql =   ("UPDATE section_configuration_values SET value=%s "
                                "WHERE name=%s AND section=%s AND pvname=%s")
                        cursor.execute(sql, (self._values[pvname], self._name, self._section, pvname))

                self._connection.commit()
                self._dirty_pvs = dict()
                self._isNew = False

    @staticmethod
    def delete(name, section):
        connection = db.get_connection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM section_configuration WHERE name=%s AND section=%s";
            result = cursor.execute(sql, (name, section))
            if result:
                connection.commit()
                return True

            return False

    def updateName(self):
        with self._connection.cursor() as cursor:
            #Update database
            sql = "UPDATE section_configuration SET name=%s WHERE name=%s and section=%s"
            cursor.execute(sql, (self._name, self._old_name, self._section))
            self._connection.commit()
            self._renamed = False
