#!/usr/bin/env python-sirius

"""Tests."""

from siriuspy.bsmp import BSMP
from siriuspy.pwrsupply.bsmp import FBPEntities
from siriuspy.pwrsupply.pru import PRU


SYNC_CYCLE = 0x5c


def create_pru_bsmp(slave_id=1):
    """create_pru_bsmp."""
    # BBB1: 10.0.21.119, slave_ids: 1,2
    # BBB2: 10.0.21.179, slave_ids: 3,4

    fbp_entities = FBPEntities()
    pru = PRU()
    bsmp = BSMP(pru, slave_id, fbp_entities)

    return pru, bsmp


def main():
    """Run."""
    pru, bsmp = create_pru_bsmp(slave_id=1)
    print('pru_sync_status: {}'.format(pru.sync_status))
    pru.sync_start()


if __name__ == "__main__":
    main()
