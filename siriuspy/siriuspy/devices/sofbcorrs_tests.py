"""."""
import time

from siriuspy.devices import SOFBCorrectors


def sofbcorrectors_test1(device):
    """."""
    test_label = 'sofbcorrectors_test1'
    fmt = '{:<45s}: {:012.6f} ms'

    label = test_label + '_constructor'
    time0 = time.time()
    sofbcorr = SOFBCorrectors(device)
    print(fmt.format(label, 1000*(time.time() - time0)))

    label = test_label + '_current_setter'
    time0 = time.time()
    sofbcorr.current = [i for i in range(sofbcorr.nr_correctors)]
    print(fmt.format(label, 1000*(time.time() - time0)))

    label = test_label + '_current_getter'
    time0 = time.time()
    curr = sofbcorr.current
    print(fmt.format(label, 1000*(time.time() - time0)))

    label = test_label + '_current_setter_none'
    time0 = time.time()
    curr[10] = None
    sofbcorr.current = curr
    print(fmt.format(label, 1000*(time.time() - time0)))


for i in range(5):
    sofbcorrectors_test1(SOFBCorrectors.DEVICES.SI)
    print()
