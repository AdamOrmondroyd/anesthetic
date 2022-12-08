"""Read NestedSamples from polychord chains."""
import os
import numpy as np
from anesthetic.read.getdist import read_paramnames
from anesthetic.samples import NestedSamples

def get_parents(cluster_label):
    """list of parent clusters of cluster_label, including cluster_label"""
    parents = [cluster_label]
    left_step_back = False
    while cluster_label > 1:
        print(cluster_label)
        if 0==cluster_label%2:
            left_step_back = True
        cluster_label //= 2
        print(left_step_back)
        if left_step_back: parents.append(cluster_label)
        left_step_back = False

    return parents

def get_clusters(cluster_labels):
    """Identify cluster labels from samples"""
    cluster_labels = set(cluster_labels)
    parents = {}
    for cluster_label in cluster_labels:
        parents[cluster_label]
    ## Unfinished
        

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
    params, labels = read_paramnames(root)

    columns = kwargs.pop('columns', params)
    kwargs['label'] = kwargs.get('label', os.path.basename(root))

    return NestedSamples(data=data, columns=columns,
                         logL=logL, logL_birth=logL_birth,
                         labels=labels, root=root, *args, **kwargs)


def read_polychord_cluster(root, *args, **kwargs):
    """Read ``<root>_dead-birth-cluster.txt`` in polychord format."""
    birth_file = root + '_dead-birth-cluster.txt'
    birth_file
    data = np.loadtxt(birth_file)
    # drop cluster as these are ints
    # data = data[:,:-1]
    try:
        phys_live_birth_file = root + '_phys_live-birth-cluster.txt'
        _data = np.loadtxt(phys_live_birth_file)
        _data = np.atleast_2d(_data)
        data = np.concatenate([data, _data]) if _data.size else data
        data = np.unique(data, axis=0)
        i = np.argsort(data[:, -2])
        data = data[i, :]
    except IOError:
        pass
    data, logL, logL_birth, cluster = np.split(data, [-3, -2, -1], axis=1)
    cluster = cluster.astype(int)
    print(cluster)
    print(len(cluster))
    params, labels = read_paramnames(root)

    columns = kwargs.pop('columns', params)
    kwargs['label'] = kwargs.get('label', os.path.basename(root))

    return NestedSamples(data=data, columns=columns,
                         logL=logL, logL_birth=logL_birth, cluster=cluster,
                         labels=labels, root=root, *args, **kwargs)
