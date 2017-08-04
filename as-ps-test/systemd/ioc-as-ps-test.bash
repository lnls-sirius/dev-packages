#!/bin/bash

# Loads bashrc-sirius
# - to run final IOC the line setting environment variable VACA_PREFIX
#   in bashrc-sirius should be commented out.
# - running this bash script with argument 'print_banner' prints info on IOC

source ~/.bashrc

# args:      print_banner[optional]
./ps-test.py $1
