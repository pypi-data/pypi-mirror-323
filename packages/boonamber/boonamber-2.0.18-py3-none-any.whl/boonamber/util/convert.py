import itertools
from numbers import Number
from typing import Iterable

import numpy as np


def validate_dims(data):
    """Validate that data is non-empty and one of the following:
    scalar value, list-like or list-of-lists-like where all
    sublists have equal length. Return 0, 1 or 2 as inferred
    number of array dimensions
    """

    # not-iterable data is a single scalar data point
    if not _isiterable(data):
        return 0

    # iterable and unnested data is a 1-d array
    if not any(_isiterable(d) for d in data):
        if len(list(data)) == 0:
            raise ValueError("empty")
        return 1

    # iterable and nested data is 2-d array
    if not all(_isiterable(d) for d in data):
        raise ValueError("cannot mix nested scalars and iterables")

    sublengths = [len(list(d)) for d in data]
    if len(set(sublengths)) > 1:
        raise ValueError("nested sublists must have equal length")

    flattened_2d = list(itertools.chain.from_iterable(data))

    if any(isinstance(i, Iterable) for i in flattened_2d):
        raise ValueError("cannot be nested deeper than list-of-lists")

    if sublengths[0] == 0:
        raise ValueError("empty")

    return 2


def _isiterable(x):
    # consider strings non-iterable for shape validation purposes,
    # that way they are printed out whole when caught as nonnumeric
    if isinstance(x, str):
        return False

    # collections.abc docs: "The only reliable way to determine
    # whether an object is iterable is to call iter(obj)."
    try:
        iter(x)
    except TypeError:
        return False

    return True


def float_list_to_csv_string(float_list):
    # Note: as in the Boon Nano SDK, there is no check that data dimensions
    # align with number of features and streaming window size.
    ndim = validate_dims(float_list)

    if ndim == 0:
        data_flat = [float_list]
    elif ndim == 1:
        data_flat = list(float_list)
    elif ndim == 2:
        data_flat = list(itertools.chain.from_iterable(float_list))
    else:
        raise ValueError("float_list is not in known format")

    for d in data_flat:
        if not isinstance(d, Number) or np.isnan(d):
            raise ValueError("contained {} which is not numeric".format(d.__repr__()))
    return ",".join([str(float(d)) for d in data_flat]), len(data_flat)
