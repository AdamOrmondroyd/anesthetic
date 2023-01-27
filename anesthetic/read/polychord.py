"""Read NestedSamples from polychord chains."""
import os
import numpy as np
from anesthetic.read.getdist import read_paramnames
from anesthetic.samples import NestedSamples

def read_cluster_tree(root, cluster_column):
    """Read the cluster tree"""
    cluster_tree_file = root + '_cluster_tree.txt'
    print(cluster_tree_file)
    data = np.loadtxt(cluster_tree_file)
    clusters = np.unique(cluster_column)
    parent = {}
    for cluster_number in np.unique(cluster_column):
        if 0 == cluster_number:
            parent[cluster_number] = None
        parent[cluster_number] = data[cluster_number-1]
    return parent
        

def read_polychord(root, *args, **kwargs):
    """Read ``<root>_dead-birth.txt`` in polychord format."""
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
    # drop cluster column as these are ints
    data = data[:,:-1]

    cluster = np.loadtxt(birth_file, usecols=-1, dtype=int)

    try:
        phys_live_birth_file = root + '_phys_live-birth-cluster.txt'
        _data = np.loadtxt(phys_live_birth_file)
        _data = np.atleast_2d(_data)
        # drop cluster column
        _data = _data[:, :-1]

        _cluster = np.loadtxt(phys_live_birth_file, usecols=-1, dtype=int)

        data = np.concatenate([data, _data]) if _data.size else data
        data, unique_idx = np.unique(data, axis=0, return_index=True)

        cluster = np.concatenate([cluster, _cluster]) if _cluster.size else data
        cluster = cluster[unique_idx]

        sorted_idx = np.argsort(data[:, -2])
        data = data[sorted_idx, :]
        cluster = cluster[sorted_idx]
    except IOError:
        pass
    data, logL, logL_birth = np.split(data, [-2, -1], axis=1)
    params, labels = read_paramnames(root)

    columns = kwargs.pop('columns', params)
    kwargs['label'] = kwargs.get('label', os.path.basename(root))

    ns = NestedSamples(data=data, columns=columns,
                         logL=logL, logL_birth=logL_birth, cluster=cluster,
                         labels=labels, *args, **kwargs)

    parent = read_cluster_tree(root, cluster)
    print(parent)
    
    return ns
