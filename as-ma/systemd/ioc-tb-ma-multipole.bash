#!/bin/bash

# Loads bashrc-sirius
# - to run final IOC the line setting environment variable VACA_PREFIX
#   in bashrc-sirius should be commented out.
# - running this bash script with argument 'print_banner' prints info on IOC

source ~/.bashrc

# args:    ioc_type       prefix_section section subsection discipline device    print_banner[optional]
./as-ma.py "Fam:MA-Multi" "TB-"          "TB"    ".*"       "MA"       "(Q|S).*" $1
