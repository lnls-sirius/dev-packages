# Power Supply Diagnostic IOC
This IOC checks Current SP/Mon difference.

## Installation
`sudo ./setup.py install`
`sudo ./setup.py develop`

## Dependencies
dev-packages (DiffPV)

## Running
`sirius-ioc-as-ps-diagnostic.py section sub_section device`
`section`, `sub_section` and `device` are regular expressions.
### Examples
`sirius-ioc-as-ps-diagnostic.py 'TB' '' ''` The IOC will using all power supply of TB section