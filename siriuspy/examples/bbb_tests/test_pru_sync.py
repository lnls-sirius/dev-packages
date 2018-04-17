#!/usr/bin/env python-sirius

"""Tests."""

from siriuspy.bsmp import BSMP
from siriuspy.pwrsupply.bsmp import FBPEntities
from siriuspy.pwrsupply.pru import PRU

slave_id = 1
fbp_entities = FBPEntities()
pru = PRU()
bsmp = BSMP(pru, slave_id, fbp_entities)
