"""Timesys subpackage."""
from .plot_network import PlotNetwork
from .static_table import create_static_table, read_data_from_google, \
    read_data_from_local_excel_file
from .hl_classes import HLEvent, HLTrigger
from .ll_classes import LLEvent, get_evg_name, get_ll_trigger

del plot_network, static_table, hl_classes, ll_classes

__all__ = ('time_simul', )
