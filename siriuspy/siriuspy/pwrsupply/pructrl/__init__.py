"""PRU Controller subpackage.

This subpackage contains lower level modules and classes that are responsible
for communicating ultimately with power supplies using BSMP protocol.

Modules:

    pru.py :
        PRU library class that implements UART communication methods.
        It inkokes EthBridgePRUserial485 library methods.

    prucontroller.py :
        Implements PRUController, class used to drive the communication flow
        and store devices state mirrors.

    udc.py :
        Communication methods that apply to all devices controlled by a
        given UDC.

    prucparams.py :
        Classes with PSModel-dependent PRUController parameters, such
        as bsmp variable groups and so on.

    psdevstate.py :
        Implements PSDevState class, whose objects are used as mirrors
        to store device states.

"""
