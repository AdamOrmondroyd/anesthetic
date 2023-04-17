"""Data-processing utility functions."""
import numpy as np
from scipy.interpolate import interp1d
import contextlib


def channel_capacity(w):
    r"""Channel capacity (effective sample size).

    .. math::

        H = \sum_i p_i \ln p_i

        p_i = \frac{w_i}{\sum_j w_j}

        N = e^{-H}
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        W = np.array(w)/sum(w)
        H = np.nansum(np.log(W)*W)
        return np.exp(-H)


def compress_weights(w, u=None, ncompress=True):
    """Compresses weights to their approximate channel capacity."""
    if u is None:
        u = np.random.rand(len(w))

    if w is None:
        w = np.ones_like(u)

    if ncompress is True:
        ncompress = channel_capacity(w)
    elif ncompress is False:
        return w

    if ncompress <= 0:
        W = w/w.max()
    else:
        W = w * ncompress / w.sum()

    fraction, integer = np.modf(W)
    extra = (u < fraction).astype(int)
    return (integer + extra).astype(int)


def quantile(a, q, w=None, interpolation='linear'):
    """Compute the weighted quantile for a one dimensional array."""
    if w is None:
        w = np.ones_like(a)
    a = np.array(list(a))  # Necessary to convert pandas arrays
    w = np.array(list(w))  # Necessary to convert pandas arrays
    i = np.argsort(a)
    c = np.cumsum(w[i[1:]]+w[i[:-1]])
    c = c / c[-1]
    c = np.concatenate(([0.], c))
    icdf = interp1d(c, a[i], kind=interpolation)
    quant = icdf(q)
    if isinstance(q, float):
        quant = float(quant)
    return quant
