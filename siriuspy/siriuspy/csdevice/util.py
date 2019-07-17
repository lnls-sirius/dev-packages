"""Control system Device Util Module."""

import copy as _copy
from siriuspy import util as _util
from siriuspy.clientweb import beaglebone_ip_list as _bbb_ip_list
from siriuspy.search.ps_search import PSSearch as _PSSearch


_device_2_ioc_ip_dict = None


class ETypes:
    """Enumerate types."""

    DSBL_ENBL = ('Dsbl', 'Enbl')
    DSBLD_ENBLD = ('Dsbld', 'Enbld')
    OFF_ON = ('Off', 'On')
    CLOSE_OPEN = ('Closed', 'Open')
    DISCONN_CONN = ('Disconnected', 'Connected')
    FIXED_INCR = ('Incr', 'Fixed')
    NORM_INV = ('Normal', 'Inverse')
    UNLINK_LINK = ('Unlink', 'Link')


_et = ETypes  # syntactic sugar


class Const:
    """Const class defining power supply constants."""

    DsblEnbl = _util.get_namedtuple('DsblEnbl', _et.DSBL_ENBL)
    OffOn = _util.get_namedtuple('OffOn', _et.OFF_ON)
    CloseOpen = _util.get_namedtuple('CloseOpen', _et.CLOSE_OPEN)
    DisconnConn = _util.get_namedtuple('DisconnConn', _et.DISCONN_CONN)

    @staticmethod
    def register(name, field_names, values=None):
        """Register namedtuple."""
        return _util.get_namedtuple(name, field_names, values)


def add_pvslist_cte(database, prefix=''):
    """Add Properties-Cte."""
    pvslist_cte_name = prefix + 'Properties-Cte'
    keys = list(database.keys())
    keys.append(pvslist_cte_name)
    val = ' '.join(sorted(keys))
    database[pvslist_cte_name] = {
        'type': 'char',
        'count': len(val),
        'value': val,
    }
    return database


def get_device_2_ioc_ip(reload=False):
    """Return a dict of ioc IP numbers for csdevices."""
    if _device_2_ioc_ip_dict is None or reload is True:
        _reload_device_2_ioc_ip()
    return _copy.deepcopy(_device_2_ioc_ip_dict)


def _reload_device_2_ioc_ip():
    global _device_2_ioc_ip_dict
    _device_2_ioc_ip_dict = dict()

    # beaglebone IPs
    text, _ = _util.read_text_data(_bbb_ip_list())
    for item in text:
        if len(item) == 2:
            bbbname, ip = item
            _device_2_ioc_ip_dict[bbbname] = ip

    # power supplies
    dic = dict()
    for bbbname, ip in _device_2_ioc_ip_dict.items():
        bsmps = _PSSearch.conv_bbbname_2_bsmps(bbbname)
        for bsmp in bsmps:
            psname, _ = bsmp
            dic[psname] = ip
    _device_2_ioc_ip_dict.update(dic)
