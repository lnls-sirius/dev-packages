# Power Supply Diagnostic IOC
This IOC checks Current SP/Mon difference.

## Installation
sudo ./setup.py install/develop

## Dependencies
dev-packages (DiffPV)

## Running
`sirius-ioc-as-ps.py section sub_section device`
`section`, `sub_section` and `device` are regular expressions.
### Examples
`sirius-ioc-as-ps.py 'TB' '' ''` The IOC will using all power supply of TB section