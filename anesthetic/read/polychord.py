"""Read NestedSamples from PolyChord chains."""
import os
import numpy as np
from anesthetic.read.getdist import read_paramnames
from anesthetic.samples import NestedSamples, ClusteredSamples


def read_cluster_tree(root, cluster_column):
    """Read the cluster tree."""
    cluster_tree_file = root + '_cluster_tree.txt'
    print(cluster_tree_file)
    data = np.loadtxt(cluster_tree_file)
    print(data)
    clusters = np.unique(cluster_column)
    parent = {}
    split_fractions = data[:, 1]
    for cluster_number in clusters:
        if 0 == cluster_number:
            parent[cluster_number] = None
        parent[cluster_number] = int(data[cluster_number-1, 0])
    return parent, split_fractions


def read_polychord(root, *args, **kwargs):
    """Read PolyChord chain files.

    Parameters
    ----------
    root : str
        root name for reading files in PolyChord format, i.e. the files
        ``<root>_dead-birth.txt`` and ``<root>_phys_live-birth.txt``.

    """
    birth_file = root + '_dead-birth.txt'
    birth_file
    data = np.loadtxt(birth_file)
    try:
        phys_live_birth_file = root + '_phys_live-birth.txt'
        _data = np.loadtxt(phys_live_birth_file)
        _data = np.atleast_2d(_data)
        data = np.concatenate([data, _data]) if _data.size else data
        data = np.unique(data, axis=0)
        i = np.argsort(data[:, -2])
        data = data[i, :]
    except IOError:
        pass
    data, logL, logL_birth = np.split(data, [-2, -1], axis=1)
    columns, labels = read_paramnames(root)

    columns = kwargs.pop('columns', columns)
    labels = kwargs.pop('labels', labels)
    kwargs['label'] = kwargs.get('label', os.path.basename(root))

    return NestedSamples(data=data, columns=columns,
                         logL=logL, logL_birth=logL_birth,
                         labels=labels, *args, **kwargs)


def read_polychord_cluster(root, *args, **kwargs):
    """Read ``<root>_dead-birth-cluster.txt`` in polychord format."""
    birth_file = root + '_dead-birth-cluster.txt'
    birth_file
    data = np.loadtxt(birth_file)

    try:
        phys_live_birth_file = root + '_phys_live-birth-cluster.txt'
        _data = np.loadtxt(phys_live_birth_file)
        _data = np.atleast_2d(_data)

        data = np.concatenate([data, _data]) if _data.size else data
        data = np.unique(data, axis=0)

        sorted_idx = np.argsort(data[:, -3])
        data = data[sorted_idx, :]
    except IOError:
        pass
    data, logL, logL_birth, cluster = np.split(data, [-3, -2, -1], axis=1)
    cluster = cluster.astype(int)
    params, labels = read_paramnames(root)

    columns = kwargs.pop('columns', params)
    labels = kwargs.pop('labels', labels)
    kwargs['label'] = kwargs.get('label', os.path.basename(root))

    cluster_tree, cluster_fractions = read_cluster_tree(root, cluster)

    cs = ClusteredSamples(data=data, columns=columns,
                          logL=logL, logL_birth=logL_birth,
                          cluster=cluster,
                          labels=labels, *args, **kwargs)
    cs.cluster_tree = cluster_tree
    cs.cluster_fractions = cluster_fractions

    print(cluster_tree)

    return cs
