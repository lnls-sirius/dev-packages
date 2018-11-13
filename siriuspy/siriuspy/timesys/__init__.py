"""Timesys subpackage."""
from .plot_network import PlotNetwork
from .static_table import create_static_table, read_data_from_google, \
    read_data_from_local_excel_file

del plot_network
del static_table

__all__ = ('time_simul', )
