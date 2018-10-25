import timeit
import pickle
import semi_join_utils
import CQ

def measure_time_l_path(n, l, cycle_or_not):
    attr_card = []
    for i in range(l):
        attr_card.append(n)
    var2cand = semi_join_utils.build_data(l, attr_card)
    rel2tuple, tuple2weight = semi_join_utils.build_relation(l, var2cand, weightrange=10)
    t_start = timeit.default_timer()
    tu2down_neis, tu2up_neis = CQ.cycle_SJ_reduce_l(rel2tuple, l)
    t_end = timeit.default_timer()
    t_preprocess = t_end - t_start  # the time to preprocess and build the relation maps.
    k = 9999
    if not cycle_or_not:  # path case
        print "algo: any-k priotitized search"
        t1 = timeit.default_timer()
        CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l)
        t2 = timeit.default_timer()
        print "algo: enumerate all"
        CQ.path_enumerate_all(rel2tuple, tuple2weight, tu2down_neis, k, l)
        t3 = timeit.default_timer()
        print ('Time any-k: ', t_preprocess + t2 - t1)
        print ('Time enumerate: ', t_preprocess + t3 - t2)
        return t2 - t1, t3 - t2

    else:  # cycle
        # TODO: add any-k naive
        print "algo: any-k split version"
        TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l)
        t1 = timeit.default_timer()
        print "algo: enumerate all"
        CQ.cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, l, True)
        t3 = timeit.default_timer()

    print ('Time any-k split: ', t_preprocess + sum(time_for_each))
    print ('Time enumerate: ', t_preprocess + t3 - t1)
    print t_preprocess




def measure_time_grow_n():
    # TODO: different l, different N, plot how these grows.
    # TODO: pickle performance numbers for repeated use.

    t_next_list = []

    for n in range(2, 50, 3):
        t_next, t_all = measure_time_l_path(30, 4, True)  # cyclic

    for n in range(2, 50, 3):
        t_next, t_all = measure_time_l_path(30, 4, False)  # acyclic


def plot():
    pass

if __name__ == "__main__":
    measure_time_l_path(80, 7, True)