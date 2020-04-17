"""Power Supply Controller subpackage.

This subpackage contains higher level modules and classes that are responsible
for communicating power supplies.

Modules:

    pscontrollers.py :
        Power supply classes that convert epics properties to PRUController
        method calls.

    psmodel.py :
        Auxiliary classes that help creation of power controllers by
        storing psmodel-specific constants and structures.

    pscreaders.py :
        PSController reader classes, reciped to convert epics read properties
        to PRUCrontroller method calls.

    pscwriters.py :
        PSController reader classes, reciped to convert epics write properties
        to PRUCrontroller method calls.

    pscstatus.py :
        Auxiliary class to help convert PS_STATUS bsmp variable into
        PwrState and OpMode epics properties, and vice-versa.

"""
