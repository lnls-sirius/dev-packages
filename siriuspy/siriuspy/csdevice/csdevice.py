from .pwrsupply import PSClasses as _PSClasses


def get_types():
    """Return a name list of all control system devices for which EPICS
    databases are defined.
    """
    return _PSClasses.get_types()

def get_database(csdevice_type):
    """Return a pcaspy-style database dictionary with all properties that apply
    to the power supply type whose name is passed as an argument."""
    db = _PSClasses.get_database(csdevice_type)
    return db
