from siriuspy.pwrsupply import PowerSupplySim as _PowerSupplySim
from siriuspy import envars as _envars
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.csdevice.enumtypes import EnumTypes as _et

_prefix = _envars.vaca_prefix


ps_devices = None


try:
    with open('VERSION','r') as _f:
        __version__ = _f.read().strip()
except:
    __version__ = 'not defined'


class PS:

    def __init__(self, psname):
        self._callback    = None
        self.psname = psname
        self.pstype = _PSSearch.conv_psname_2_pstype(self.psname)
        self.opmode_sel   = 0
        self.pwrstate_sel = 0
        self.current_sp   = 0

    @property
    def opmode_sel(self):
        return self._opmode_sel

    @opmode_sel.setter
    def opmode_sel(self, value):
        self._opmode_sel = value
        self._mycallback('OpMode-Sel',value)

    @property
    def pwrstate_sel(self):
        return self._pwrstate_sel

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        self._pwrstate_sel = value
        self._mycallback('PwrState-Sel',value)

    @property
    def current_sp(self):
        return self._current_sp

    @current_sp.setter
    def current_sp(self, value):
        self._current_sp = value
        self._mycallback('Current-SP',value)

    @property
    def opmode_sts(self):
        return self.opmode_sel

    @property
    def pwrstate_sts(self):
        return self.pwrstate_sel

    @property
    def current_rb(self):
        return self.current_sp

    @property
    def currentref_mon(self):
        return self.current_rb

    @property
    def current_mon(self):
        return self.currentref_mon

    @property
    def database(self):
        db = {
            'PwrState-Sel'       : {'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':self.pwrstate_sel},
            'PwrState-Sts'       : {'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':self.pwrstate_sts},
            'OpMode-Sel'         : {'type':'enum',   'enums':_et.enums('PSOpModeTyp'), 'value':self.opmode_sel},
            'OpMode-Sts'         : {'type':'enum',   'enums':_et.enums('PSOpModeTyp'), 'value':self.opmode_sts},
            'Current-SP'         : {'type':'float',  'value':self.current_sp, 'prec':4, },
            'Current-RB'         : {'type':'float',  'value':self.current_rb, 'prec':4},
            'CurrentRef-Mon'     : {'type':'float',  'value':self.currentref_mon, 'prec':4},
            'Current-Mon'        : {'type':'float',  'value':self.current_mon, 'prec':4},
        }
        pstype = self.pstype

        label='lolo';  db['Current-SP'][label] = _PSSearch.get_splim(pstype,label)
        label='low';   db['Current-SP'][label] = _PSSearch.get_splim(pstype,label)
        label='lolim'; db['Current-SP'][label] = _PSSearch.get_splim(pstype,label)
        label='hilim'; db['Current-SP'][label] = _PSSearch.get_splim(pstype,label)
        label='high';  db['Current-SP'][label] = _PSSearch.get_splim(pstype,label)
        label='hihi';  db['Current-SP'][label] = _PSSearch.get_splim(pstype,label)

        return db

    def add_callback(self, callback, index=None):
        self._callback = callback

    def _mycallback(self, pvname, value, **kwargs):
        if callable(self._callback):
            if 'Current-SP' in pvname:
                self._callback(self.psname + ':Current-RB', self.current_rb)
                self._callback(self.psname + ':CurrentRef-Mon', self.currentref_mon)
                self._callback(self.psname + ':Current-Mon', self.current_mon)
            elif 'OpMode-Sel' in pvname:
                self._callback(self.psname + ':OpMode-Sts', self.opmode_sts)
            elif 'PwrState-Sel' in pvname:
                self._callback(self.psname + ':PwrState-Sts', self.pwrstate_sts)


def get_ps_devices():
    ''' Create/Returns PowerSupplyMA objects for each magnet. '''
    global ps_devices
    if ps_devices is None:
        ps_devices = {}
        #Create filter, only getting Fam Quads
        filters = []
        #Get magnets
        pwr_supplies = _PSSearch.get_psnames()
        #Create objects that'll handle the magnets
        for ps in pwr_supplies:
            if 'Fam:PS-QDA' in ps or 'B1B2' in ps:
                #ps_devices[ps] = _PowerSupplySim(psname=ps)
                ps_devices[ps] = PS(psname=ps)

    return ps_devices

def get_database():

    #global ps_devices

    ps_devices = get_ps_devices()

    db = {}
    for psname in ps_devices:
        ps_db = ps_devices[psname].database
        props = list(ps_db.keys())
        for i in range(len(props)):
            db[psname + ':' + props[i]] = ps_db[props[i]]
    return {_prefix:db}
