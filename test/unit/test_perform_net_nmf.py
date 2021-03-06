import numpy as np
import unittest
from unittest import TestCase

import knpackage.toolbox as kn

def synthesize_random_network(network_dim, n_nodes):
    """ symmetric random adjacency matrix from random set of nodes
    Args:
        network_dim: number of rows and columns in the symmetric output matrix
        n_nodes: number of connections (approximate because duplicates are ignored)
    Returns:
        network: a symmetric adjacency matrix (0 or 1 in network_dim x network_dim matrix)
    """
    network = np.zeros((network_dim, network_dim))
    col_0 = np.random.randint(0, network_dim, n_nodes)
    col_1 = np.random.randint(0, network_dim, n_nodes)
    for node in range(0, n_nodes):
        if col_0[node] != col_1[node]:
            network[col_0[node], col_1[node]] = 1
    network = network + network.T
    network[network != 0] = 1

    return network

def get_cluster_indices_list(a_arr):
    """ get the list of sets of positive integers in the input array where a set
        is the index of where equal values occur for all equal values in the array

    Args:
        a_arr: array of positive integers

    Returns:
        cluster_list: list of lists where each list is the indecies of the members
            of that set, and the lists are ordered by the first member of each.
    """
    idx_arr = np.arange(0, a_arr.size)
    a_arr_unique = np.unique(a_arr)
    tmp_list = []
    for v in a_arr_unique:
        tmp_list.append(idx_arr[a_arr == v])

    len_tmp_list = len(tmp_list)
    first_member_array = np.int_(np.zeros(len_tmp_list))
    for m in range(0, len_tmp_list):
        tmp = tmp_list[m]
        first_member_array[m] = int(tmp[0])

    list_order = np.int_(np.argsort(first_member_array))
    cluster_list = []
    for t in list_order:
        cluster_list.append(tmp_list[t])

    return cluster_list

def sets_a_eq_b(a, b):
    """ check that all indices of equal values in a
        are same sets as indices of equal values in b
    Args:
        a: array of cluster assignments
        b: array of cluster assignments - same size or will return false
    Returns:
        True or False: array a indices of equal value
            are the same as array b indices of equal values
    """
    a_u = np.unique(a)
    b_u = np.unique(b)
    if len(a_u) != len(b_u):
        return False
    else:
        a_list = get_cluster_indices_list(a)
        b_list = get_cluster_indices_list(b)
        if len(b) != len(a):
            return False
        else:
            n_here = 0
            for a_set in a_list:
                if (len(a_set) != len(b_list[n_here])):
                    return False
                elif sum(np.int_(a_set != b_list[n_here])) != 0:
                    return False
                else:
                    n_here += 1
    return True

class TestPerform_net_nmf(TestCase):
    def setUp(self):
        self.run_parameters = {
            'nmf_max_invariance': 100,
            'nmf_max_iterations': 1500,
            'nmf_conv_check_freq': 50,
            'number_of_clusters': 3,
            'nmf_penalty_parameter': 1400}

    def tearDown(self):
        del self.run_parameters

    def test_perform_net_nmf(self):
        # assert that net_nmf finds the same clusters as a known cluster set
        # with a basis made from the network
        run_parameters = self.run_parameters
        k = run_parameters['number_of_clusters']
        nrows = 90
        ncols = 30
        H0 = np.random.rand(k, ncols)
        C = np.argmax(H0, axis=0)
        H = np.zeros(H0.shape)
        for row in range(0, max(C) + 1):
            rowdex = C == row
            H[row, rowdex] = 1

        pct_nodes = 0.1
        n_nodes = np.int_(np.round(pct_nodes * nrows ** 2))
        N = synthesize_random_network(nrows, n_nodes)

        W = np.random.rand(nrows, k)
        W = N.dot(W)

        X = W.dot(H)

        lap_dag, lap_val = kn.form_network_laplacian_matrix(N)
        H_b = kn.perform_net_nmf(X, lap_val, lap_dag, run_parameters)

        H_clusters = np.argmax(H, axis=0)
        H_b_clusters = np.argmax(H_b, axis=0)

        sets_R_equal = sets_a_eq_b(H_clusters, H_b_clusters)
        self.assertTrue(sets_R_equal, msg='test net nmf clusters differ')

if __name__ == '__main__':
    unittest.main()
