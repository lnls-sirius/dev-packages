"""Utils."""

import gzip as _gzip
import pickle as _pickle

# TODO: these functions should be moved to another place in the
# lnls-fac/mathphys original package. after that this module in
# siriuspy/mathphys can be deleted!


def flatten(l):
    """."""
    try:
        l[0]
        r = []
        for e in l:
            r.extend(flatten(e))
        return r
    except TypeError:
        return [l]


def save_pickle(filename, **kwargs):
    """Save variables in gzip compressed pickle format as a dictionary.

    Inputs
    ------
      filename : path to and name (with or without extension) of the file to
                 save
      kwargs   : variables to save:

    Examples
    --------
        >>> a = dict({'casa':[1,2], 'bla':3.4})
        >>> b = ['fla',3.42,True]
        >>>save_pickle('teste',a=a,b=b)
        >>>save_pickle('teste2',var1=a,var2=b)

    """
    if not filename.endswith('.pickle'):
        filename += '.pickle'

    with _gzip.open(filename, 'wb') as fi:
        _pickle.dump(kwargs, fi, _pickle.HIGHEST_PROTOCOL)


def load_pickle(filename):
    """Load gzip compressed files in pickle format.

    Inputs
    ------
        filename : path to and name (with or without extension) of the file

    Outputs
    -------
        dictionary with the variables of the file.

    Examples
    --------
        >>> a = dict({'casa':[1,2], 'bla':3.4})
        >>> b = ['fla',3.42,True]
        >>>save_pickle('teste',a=a,b=b)
        >>>save_pickle('teste2',var1=a,var2=b)
        >>>vars = load_pickle('teste2.pickle')
        >>> vars['var1']
        {'casa':[1,2], 'bla':3.4}
        >>>vars['var2']
        ['fla',3.42,True]
        >>> load_pickle('teste')
        {'a':{'casa':[1,2], 'bla':3.4},'b':['fla',3.42,True]}

    """
    if not filename.endswith('.pickle'):
        filename += '.pickle'

    with _gzip.open(filename, 'rb') as f1:
        data = _pickle.load(f1)
    return data
