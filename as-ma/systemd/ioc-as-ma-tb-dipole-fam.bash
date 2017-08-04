#!/bin/bash

# Loads bashrc-sirius
# To run final IOC the line setting environment variable VACA_PREFIX
# in bashrc-sirius should be commented out.

source ~/.bashrc
#source /usr/local/etc/bashrc-sirius
./as-ma.py "TB-" "TB" "Fam" "MA" "B.*"
