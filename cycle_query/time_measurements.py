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
    tu2down_neis, tu2up_neis = CQ.cycle_SJ_reduce_l(rel2tuple, l)
    k = 500000
    if not cycle_or_not:  # path case
        print "algo: any-k priotitized search"
        t1 = timeit.default_timer()
        CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l)
        t2 = timeit.default_timer()
        print "algo: enumerate all"
        CQ.path_enumerate_all(rel2tuple, tuple2weight, tu2down_neis, k, l)
        t3 = timeit.default_timer()
    else:  # cycle
        print "algo: enumerate all"
        t1 = timeit.default_timer()
        CQ.cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, l, False)
        t2 = timeit.default_timer()
        print "algo: any-k naive version"
        # TODO: separate the part from l-cycle-split.
        t3 = timeit.default_timer()

    print ('Time any-k: ', t2 - t1)
    print ('Time enumerate: ', t3 - t2)
    return t2 - t1, t3 - t2



def measure_time_grow_n():
    t_next_list = []

    for n in range(2, 50, 3):
        t_next, t_all = measure_time_l_path(30, 4, True)  # cyclic

    for n in range(2, 50, 3):
        t_next, t_all = measure_time_l_path(30, 4, False)  # acyclic


def plot():
    pass

if __name__ == "__main__":
    measure_time_l_path(30, 5, False)