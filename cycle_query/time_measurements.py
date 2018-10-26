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
    t_preprocess = t_end - t_start  # the time_any to preprocess and build the relation maps.
    k = 9999999
    if not cycle_or_not:  # path case
        print "algo: any-k priotitized search"
        t1 = timeit.default_timer()
        TOP_K, time_for_each = CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l)
        t2 = timeit.default_timer()
        print "algo: enumerate all"
        CQ.path_enumerate_all(rel2tuple, tuple2weight, tu2down_neis, k, l)
        t3 = timeit.default_timer()
        print ('Time any-k: ', t_preprocess + sum(time_for_each))
        t_full  =  t_preprocess + t3 - t2
        print ('Time enumerate: ', t_full)

    else:  # cycle
        # TODO: add any-k naive
        print "algo: any-k split version"
        TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l)
        t1 = timeit.default_timer()
        print "algo: enumerate all"
        CQ.cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, l, True)
        t3 = timeit.default_timer()

        print ('Time any-k split: ', t_preprocess + sum(time_for_each))
        t_full = t_preprocess + t3 - t1
        print ('Time enumerate: ', t_full)
        print t_preprocess

    timetuple_full = (t_preprocess, t_full)
    if cycle_or_not:
        pickle.dump(time_for_each, open("../time_any/" + str(n)+'_'+str(l) + '_cycle', 'wb'))
        pickle.dump(timetuple_full, open("../time_all/" + str(n) + '_' + str(l) + '_cycle', 'wb'))
    else:
        pickle.dump(time_for_each, open("../time_any/" + str(n) + '_' + str(l) + '_path', 'wb'))
        pickle.dump(timetuple_full, open("../time_all/" + str(n) + '_' + str(l) + '_path', 'wb'))


def measure_time_grow_n():
    for l in range(10, 4, -1):
        for n in range(5, 51, 5):
            measure_time_l_path(n, l, True)  # cyclic
            measure_time_l_path(n, l, False)  # cyclic


def plot():
    # TODO: read from pickle and plot.
    pass

if __name__ == "__main__":
    #measure_time_l_path(80, 7, True)
    measure_time_grow_n()