#!/usr/bin/env python

__author__ = "Rob Knight, Justin Kuczynski"
__copyright__ = "Copyright 2009, the PyCogent Project"
__credits__ = ["Rob Knight", "justin kuczynski"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Justin Kuczynski"
__email__ = "justinak@gmail.com"
__status__ = "Prototype"


"""contains metrics for use with beta_diversity.py
most metrics are from cogent.math.distance_transform.py,
but some need wrappers to look like f(data, taxon_names, tree)-> dist_mtx
"""
from cogent.maths.unifrac.fast_tree import (unifrac, unnormalized_unifrac,
    G, unnormalized_G, weighted_unifrac)
from cogent.maths.unifrac.fast_unifrac import fast_unifrac
from pipe454.parse import make_envs_dict
import numpy

def make_unifrac_metric(weighted, metric, is_symmetric):
    """Make a unifrac-like metric.

    Parameters:
    weighted: bool, if True does the necessary root to tip calcs.
    metric: f(branch_lengths, i, j) -> distance
    is_symmetric: saves calc time if metric is symmetric.
    """
    def result(data, taxon_names, tree):
        """ wraps the fast_unifrac fn to return just a matrix, in correct order"""
        sample_names = [str(i) for i in range(len(data))]
        envs = make_envs_dict(data, sample_names, taxon_names)
        unifrac_res = fast_unifrac(tree, envs, weighted=weighted, metric=metric,
            is_symmetric=is_symmetric, modes=["distance_matrix"])
        dist_mtx = _reorder_unifrac_res(unifrac_res['distance_matrix'],
            sample_names)
        return dist_mtx
    return result

# these should start with dist_ to be discoverable by beta_diversity.py
dist_unweighted_unifrac = make_unifrac_metric(False, unifrac, True)
dist_unweighted_unnormalized_unifrac = make_unifrac_metric(False, 
    unnormalized_unifrac, True)
dist_weighted_unifrac = make_unifrac_metric(True, weighted_unifrac, True)
dist_weighted_normalized_unifrac = make_unifrac_metric('correct',
    weighted_unifrac, True)
dist_G = make_unifrac_metric(False, G, False)
dist_unnormalized_G = make_unifrac_metric(False, unnormalized_G, False)

def _reorder_unifrac_res(unifrac_res, sample_names_in_desired_order):
    sample_names = sample_names_in_desired_order
    unifrac_dist_mtx = unifrac_res[0]
    unifrac_sample_names = unifrac_res[1]
    if unifrac_sample_names == sample_names:
        dist_mtx = unifrac_dist_mtx
    else:
        dist_mtx = numpy.zeros(unifrac_dist_mtx.shape)
        for i, sam_i in enumerate(sample_names):
            unifrac_i = unifrac_sample_names.index(sam_i)
            for j, sam_j in enumerate(sample_names):
                unifrac_j =  unifrac_sample_names.index(sam_j)
                dist_mtx[i,j] = unifrac_dist_mtx[unifrac_i, unifrac_j]

    return dist_mtx
