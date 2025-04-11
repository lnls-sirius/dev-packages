"""Define PVs, constants and properties of Filling Pattern SoftIOCs."""

from .. import csdev as _csdev

# --- Const class ---


class Const(_csdev.Const):
    """Const class defining Filling Pattern constants."""

    FP_MAX_ARR_SIZE = 40000
    FP_HARM_NUM = 864
    FP_MAX_UPDT_TIME = 600  # [s]
    DEVNAME = 'SI-Glob:DI-FPMOsc'


_c = Const  # syntactic sugar


# --- Databases ---

def get_si_fpmosc_database():
    """Return SI FPMOsc Soft IOC database."""
    pvs_db = {'Version-Cte': {'type': 'string', 'value': 'UNDEF'}}

    pvs_db['UpdateTime-SP'] = {
        'type': 'int', 'value': 5, 'unit': 's',
        'low': 0, 'high': _c.FP_MAX_UPDT_TIME,
        'lolo': 0, 'hihi': _c.FP_MAX_UPDT_TIME,
        'lolim': 0, 'hilim': _c.FP_MAX_UPDT_TIME,
    }
    pvs_db['UpdateTime-RB'] = {
        'type': 'int', 'value': 5, 'unit': 's',
        'low': 0, 'high': _c.FP_MAX_UPDT_TIME,
        'lolo': 0, 'hihi': _c.FP_MAX_UPDT_TIME,
        'lolim': 0, 'hilim': _c.FP_MAX_UPDT_TIME,
    }
    pvs_db['FiducialOffset-SP'] = {
        'type': 'int', 'value': 0, 'unit': 'bunches',
        'low': -_c.FP_HARM_NUM, 'high': _c.FP_HARM_NUM,
        'lolo': -_c.FP_HARM_NUM, 'hihi': _c.FP_HARM_NUM,
        'lolim': -_c.FP_HARM_NUM, 'hilim': _c.FP_HARM_NUM,
    }
    pvs_db['FiducialOffset-RB'] = {
        'type': 'int', 'value': 0, 'unit': 'bunches',
        'low': -_c.FP_HARM_NUM, 'high': _c.FP_HARM_NUM,
        'lolo': -_c.FP_HARM_NUM, 'hihi': _c.FP_HARM_NUM,
        'lolim': -_c.FP_HARM_NUM, 'hilim': _c.FP_HARM_NUM,
    }
    pvs_db['TimeOffset-Mon'] = {
        'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'ns'
    }
    pvs_db['FillPatternRef-SP'] = {
        'type': 'float', 'prec': 5, 'count': _c.FP_HARM_NUM,
        'value': [0.0, ] * _c.FP_HARM_NUM, 'unit': 'rel'
    }
    pvs_db['FillPatternRef-RB'] = {
        'type': 'float', 'prec': 5, 'count': _c.FP_HARM_NUM,
        'value': [0.0, ] * _c.FP_HARM_NUM, 'unit': 'rel'
    }

    pvs_db['UniFillEqCurrent-Mon'] = {
        'type': 'float', 'value': 0, 'unit': 'mA', 'prec': 2,
    }
    pvs_db['ErrorRelStd-Mon'] = {
        'type': 'float', 'value': 0, 'unit': '%', 'prec': 2,
    }
    pvs_db['ErrorKLDiv-Mon'] = {
        'type': 'float', 'value': 0, 'unit': '', 'prec': 5,
    }
    pvs_db['FillPatternRef-Mon'] = {
        'type': 'float', 'prec': 5, 'count': _c.FP_HARM_NUM,
        'value': [0.0, ] * _c.FP_HARM_NUM, 'unit': 'mA'
    }
    pvs_db['FillPattern-Mon'] = {
        'type': 'float', 'prec': 5, 'count': _c.FP_HARM_NUM,
        'value': [0.0, ] * _c.FP_HARM_NUM, 'unit': 'mA'
    }
    pvs_db['Time-Mon'] = {
        'type': 'float', 'prec': 3, 'count': _c.FP_HARM_NUM,
        'value': [0.0, ] * _c.FP_HARM_NUM, 'unit': 'ns'
    }
    pvs_db['Raw-Mon'] = {
        'type': 'float', 'prec': 3, 'count': _c.FP_MAX_ARR_SIZE,
        'value': [0.0, ] * _c.FP_MAX_ARR_SIZE, 'unit': 'mA'
    }
    pvs_db['RawAmp-Mon'] = {
        'type': 'float', 'prec': 3, 'count': _c.FP_MAX_ARR_SIZE,
        'value': [0.0, ] * _c.FP_MAX_ARR_SIZE, 'unit': 'mA'
    }
    pvs_db['RawTime-Mon'] = {
        'type': 'float', 'prec': 3, 'count': _c.FP_MAX_ARR_SIZE,
        'value': [0.0, ] * _c.FP_MAX_ARR_SIZE, 'unit': 'ns'
    }
    return _csdev.add_pvslist_cte(pvs_db)
