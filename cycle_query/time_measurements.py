import timeit
import pickle
import semi_join_utils
import numpy as np
import CQ
import BooleanTop1


def lazy_time_l_path(n, l, cycle_or_not, k):
    # add datapoints for lazy sort
    queryType = "Cycle"
    DensityOfEdges = "Full"
    edgeDistribution = "HardCase"
    rel2tuple, tuple2weight = DataGenerator.getDatabase \
        (queryType, n, l, DensityOfEdges, edgeDistribution)

    if not cycle_or_not:  # path case
        t_start = timeit.default_timer()
        tu2down_neis, tu2up_neis = CQ.path_SJ_reduce_l(rel2tuple, l)
        t_end = timeit.default_timer()
        t_preprocess = t_end - t_start  # the time_any to preprocess and build the relation maps.

        print "algo: any-k lazy sort"
        t1 = timeit.default_timer()
        TOP_K, time_for_each = CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak=True, Lazy= True,
                                                         PQmode="Heap", bound=None, debug=False)
        # modes: "Heap", "Btree", "Treap"
        # bound=None | k
        # when debug is True there is prints, otherwise not
        if len(time_for_each) > 0:
            time_for_each[0] += t_preprocess




    else:  # cycle
        t_start = timeit.default_timer()
        tu2down_neis, tu2up_neis = CQ.path_SJ_reduce_l(rel2tuple, l)
        t_end = timeit.default_timer()
        t_preprocess = t_end - t_start  # the time_any to preprocess and build the relation maps.


        print "algo: any-k lazy sort"
        TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=True, Lazy=True,
                                                                  PQmode="Heap", bound=None, debug=False)

        if len(time_for_each) > 0:
            time_for_each[0] += t_preprocess


    if cycle_or_not:
        pickle.dump(time_for_each, open("../time_lazy/" + str(n) + '_' + str(l) + '_cycle', 'wb'))
    else:
        pickle.dump(time_for_each, open("../time_lazy/" + str(n) + '_' + str(l) + '_path', 'wb'))





def get_time_lower4(n, l, cycle_or_not):
    # simplest version, takes n and l. Useful version!

    queryType = "Cycle"
    DensityOfEdges = "Full"
    edgeDistribution = "HardCase"
    rel2tuple, tuple2weight = DataGenerator.getDatabase \
        (queryType, n, l, DensityOfEdges, edgeDistribution)


    k = 1
    if not cycle_or_not:  # path case
        t_start = timeit.default_timer()
        tu2down_neis, tu2up_neis = CQ.path_SJ_reduce_l(rel2tuple, l)
        t_end = timeit.default_timer()
        t_preprocess = t_end - t_start  # the time_any to preprocess and build the relation maps.
        print "any-k sort"
        t1 = timeit.default_timer()
        TOP_K, time_for_each = CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak= True, Lazy=False, PQmode = "Heap", bound = None, debug = False)
        #modes: "Heap", "Btree", "Treap"
        #bound=None | k
        # when debug is True there is prints, otherwise not
        if len(time_for_each) > 0:
            time_for_each[0] += t_preprocess
        TOP_K, time_for_each_old = CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak=False,Lazy=False,
                                                             PQmode="Heap", bound=None, debug=False)
        if len(time_for_each_old) > 0:
            time_for_each_old[0] += t_preprocess

        exist, t_bool = BooleanTop1.l_path_bool(rel2tuple,l)
        Top1, t_top1 = BooleanTop1.l_path_top1(rel2tuple, tuple2weight, tu2down_neis, l)
        t_top1 += t_preprocess


    else:  # cycle
        t_start = timeit.default_timer()
        tu2down_neis, tu2up_neis = CQ.path_SJ_reduce_l(rel2tuple, l)
        t_end = timeit.default_timer()
        t_preprocess = t_end - t_start  # the time_any to preprocess and build the relation maps.

        # TODO: add any-k naive?
        print "algo: any-k split version"
        TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=True, Lazy=False, PQmode= "Heap", bound = None, debug = False)

        if len(time_for_each) > 0:
            time_for_each[0] += t_preprocess

        TOP_K, time_for_each_old = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=False, Lazy=False,
                                                                  PQmode="Heap", bound=None, debug=False)

        if len(time_for_each_old) > 0:
            time_for_each_old[0] += t_preprocess

        exist, t_bool = BooleanTop1.l_cycle_split_bool(rel2tuple, tuple2weight, l)
        Top1, t_top1 = BooleanTop1.l_cycle_split_top1(rel2tuple, tuple2weight, l)

        print ('Time any-k split: ', t_preprocess + sum(time_for_each))


    timetuple_bool = (t_bool, t_top1)
    if cycle_or_not:
        pickle.dump(time_for_each, open("../time_any/" + str(n)+'_'+str(l) + '_cycle', 'wb'))
        pickle.dump(time_for_each_old, open("../time_old/" + str(n) + '_' + str(l) + '_cycle', 'wb'))
        pickle.dump(timetuple_bool, open("../time_bool/" + str(n) + '_' + str(l) + '_cycle', 'wb'))

    else:
        pickle.dump(time_for_each, open("../time_any/" + str(n) + '_' + str(l) + '_path', 'wb'))
        pickle.dump(time_for_each_old, open("../time_old/" + str(n) + '_' + str(l) + '_path', 'wb'))
        pickle.dump(timetuple_bool, open("../time_bool/" + str(n) + '_' + str(l) + '_path', 'wb'))



def measure_time_l_path(n, l, cycle_or_not):
    # simplest version, takes n and l. Useful version!

    queryType = "Cycle"
    DensityOfEdges = "Full"
    edgeDistribution = "HardCase"
    rel2tuple, tuple2weight = DataGenerator.getDatabase \
        (queryType, n, l, DensityOfEdges, edgeDistribution)


    k = 9999999999
    if not cycle_or_not:  # path case
        t_start = timeit.default_timer()
        tu2down_neis, tu2up_neis = CQ.path_SJ_reduce_l(rel2tuple, l)
        t_end = timeit.default_timer()
        t_preprocess = t_end - t_start  # the time_any to preprocess and build the relation maps.

        print "algo: any-k priotitized search"
        t1 = timeit.default_timer()
        TOP_K, time_for_each = CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak= True, PQmode = "Heap", bound = None, debug = False)
        #modes: "Heap", "Btree", "Treap"
        #bound=None | k
        # when debug is True there is prints, otherwise not
        if len(time_for_each) > 0:
            time_for_each[0] += t_preprocess

        TOP_K, time_for_each_old = CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak=False,
                                                             PQmode="Heap", bound=None, debug=False)
        if len(time_for_each_old) > 0:
            time_for_each_old[0] += t_preprocess


        t2 = timeit.default_timer()
        print "algo: enumerate all"
        CQ.path_enumerate_all(rel2tuple, tuple2weight, tu2down_neis, k, l, debug = False)
        t3 = timeit.default_timer()

        exist, t_bool = BooleanTop1.l_path_bool(rel2tuple,l)
        Top1, t_top1 = BooleanTop1.l_path_top1(rel2tuple, tuple2weight, tu2down_neis, l)
        t_top1 += t_preprocess

        print ('Time any-k: ', t_preprocess + sum(time_for_each))
        t_full  =  t_preprocess + t3 - t2
        print ('Time enumerate: ', t_full)

    else:  # cycle
        t_start = timeit.default_timer()
        tu2down_neis, tu2up_neis = CQ.path_SJ_reduce_l(rel2tuple, l)
        t_end = timeit.default_timer()
        t_preprocess = t_end - t_start  # the time_any to preprocess and build the relation maps.

        # TODO: add any-k naive?
        print "algo: any-k split version"
        TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=True, PQmode= "Heap", bound = None, debug = False)

        if len(time_for_each) > 0:
            #time_for_each[0] = t_preprocess
            time_for_each[0] += t_preprocess

        TOP_K, time_for_each_old = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=False,
                                                                  PQmode="Heap", bound=None, debug=False)

        if len(time_for_each_old) > 0:
            #time_for_each_old[0] = t_preprocess
            time_for_each_old[0] += t_preprocess


        t1 = timeit.default_timer()
        print "algo: enumerate all"
        CQ.cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, l, False, debug= False)
        t3 = timeit.default_timer()

        exist, t_bool = BooleanTop1.l_cycle_split_bool(rel2tuple, tuple2weight, l)
        Top1, t_top1 = BooleanTop1.l_cycle_split_top1(rel2tuple, tuple2weight, l)

        print ('Time any-k split: ', t_preprocess + sum(time_for_each))
        t_full = t_preprocess + t3 - t1
        print ('Time enumerate: ', t_full)



    timetuple_full = (t_preprocess, t_full)
    timetuple_bool = (t_bool, t_top1)
    if cycle_or_not:
        pickle.dump(time_for_each, open("../time_any/" + str(n)+'_'+str(l) + '_cycle', 'wb'))
        pickle.dump(time_for_each_old, open("../time_old/" + str(n) + '_' + str(l) + '_cycle', 'wb'))
        pickle.dump(timetuple_full, open("../time_all/" + str(n) + '_' + str(l) + '_cycle', 'wb'))
        pickle.dump(timetuple_bool, open("../time_bool/" + str(n) + '_' + str(l) + '_cycle', 'wb'))

    else:
        pickle.dump(time_for_each, open("../time_any/" + str(n) + '_' + str(l) + '_path', 'wb'))
        pickle.dump(time_for_each_old, open("../time_old/" + str(n) + '_' + str(l) + '_path', 'wb'))
        pickle.dump(timetuple_full, open("../time_all/" + str(n) + '_' + str(l) + '_path', 'wb'))
        pickle.dump(timetuple_bool, open("../time_bool/" + str(n) + '_' + str(l) + '_path', 'wb'))

'''
def measure_time_l_v2(n, l_start, l_end, cycle_or_not):
    attr_card = []
    for i in range(l_end):
        attr_card.append(n)
    var2cand = semi_join_utils.build_data(l_end, attr_card)
    rel2tuple, tuple2weight = semi_join_utils.build_relation(l_end, var2cand, weightrange=10)
    t_start = timeit.default_timer()
    tu2down_neis, tu2up_neis = CQ.cycle_SJ_reduce_l(rel2tuple, l_end)
    t_end = timeit.default_timer()
    t_preprocess = t_end - t_start  # the time_any to preprocess and build the relation maps.
    k = 9999999
    for l in range(l_start, l_end):
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

'''

import DataGenerator
def measure_time_n_v2(n_start, n_end, l, cycle_or_not):
    # for the same query, plot how the running times changes as database density changes.
    # this requires the database generation procedure for every value of n...
    # not needed apart from v1 if same d_max generation method.

    for n in range(n_start, n_end, (n_end - n_start)/15):

        #run cycle and path query on the same input dataset. also: generator mode has been verified for cycle
        queryType = "Cycle"
        DensityOfEdges = "Full"
        edgeDistribution = "HardCase"
        rel2tuple, tuple2weight = DataGenerator.getDatabase\
            (queryType, n, l, DensityOfEdges, edgeDistribution)

        t_start = timeit.default_timer()
        tu2down_neis, tu2up_neis = CQ.cycle_SJ_reduce_l_light(rel2tuple, l)
        t_end = timeit.default_timer()
        t_preprocess = t_end - t_start  # the time_any to preprocess and build the relation maps.
        k = 9999999999
        
        if not cycle_or_not:  # path case
            print "algo: any-k priotitized search"

            t_start = timeit.default_timer()
            tu2down_neis, tu2up_neis = CQ.path_SJ_reduce_l(rel2tuple, l)
            t_end = timeit.default_timer()
            t_preprocess = t_end - t_start

            TOP_K, time_for_each = CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak=True, PQmode= "Heap", bound = k, debug = False)
            if len(time_for_each) > 0:
                time_for_each[0] += t_preprocess

            TOP_K, time_for_each_old = CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak=False, PQmode= "Heap", bound = k, debug = False)
            if len(time_for_each_old) > 0:
                time_for_each_old[0] += t_preprocess

            t1 = timeit.default_timer()
            print "algo: enumerate all"
            CQ.path_enumerate_all(rel2tuple, tuple2weight, tu2down_neis, k, l, False)
            t3 = timeit.default_timer()
            print ('Time any-k: ', t_preprocess + sum(time_for_each))
            t_full  =  t_preprocess + t3 - t1
            print ('Time enumerate: ', t_full)

        else:  # cycle
            # TODO: add any-k naive
            print "algo: any-k split version"
            TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=True, PQmode= "Heap", bound = k, debug = False)
            if len(time_for_each) > 0:
                time_for_each[0] += t_preprocess
            TOP_K, time_for_each_old = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=False, PQmode= "Heap", bound = k, debug = False)
            if len(time_for_each_old) > 0:
                time_for_each_old[0] += t_preprocess
            t1 = timeit.default_timer()
            print "algo: enumerate all"
            CQ.cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, l, False, False)
            t3 = timeit.default_timer()

            print ('Time any-k split: ', t_preprocess + sum(time_for_each))
            t_full = t_preprocess + t3 - t1
            print ('Time enumerate: ', t_full)



        timetuple_full = (t_preprocess, t_full)
        if cycle_or_not:
            pickle.dump(time_for_each, open("../time_any/" + str(n)+'_'+str(l) + '_cycle', 'wb'))
            pickle.dump(timetuple_full, open("../time_all/" + str(n) + '_' + str(l) + '_cycle', 'wb'))
            pickle.dump(time_for_each_old, open("../time_old/" + str(n) + '_' + str(l) + '_cycle', 'wb'))

        else:
            print len(time_for_each)
            pickle.dump(time_for_each, open("../time_any/" + str(n) + '_' + str(l) + '_path', 'wb'))
            pickle.dump(timetuple_full, open("../time_all/" + str(n) + '_' + str(l) + '_path', 'wb'))
            pickle.dump(time_for_each_old, open("../time_old/" + str(n) + '_' + str(l) + '_path', 'wb'))




def measure_time_grow_nl():
    for l in range(4, 10, 1):
        for n in range(5, 30, 5):
            measure_time_l_path(n, l, True)  # cyclic
            measure_time_l_path(n, l, False)  # acyclic

def measure_time_n(l):
    n_log = np.logspace(1, 2.5, 15, endpoint=True)
    #n_line =  range(3, 50, 3)
    #for n in n_line:
    #    print int(n)
    #    measure_time_l_path(int(n), l, True)  # cyclic
        #measure_time_l_path(int(n), l, False)  # acyclic
    for n in n_log:
        print int(n)
        measure_time_l_path(int(n), l, True)  # cyclic
        measure_time_l_path(int(n), l, False)  # acyclic

def measure_time_l(n):
    for l in range(3, 17):
        measure_time_l_path(n, l, True)  # cyclic
        measure_time_l_path(n, l, False)  # acyclic

def add_lazy_l(n, k):
    for l in range(3, 17):
        lazy_time_l_path(n, l, True, k)  # cyclic
        lazy_time_l_path(n, l, False, k)  # acyclic


def measure_lower4(n):
    for l in range(3, 17):
        get_time_lower4(n, l, True)
        get_time_lower4(n, l, True)
        lazy_time_l_path(n, l, True, k=1)  # cyclic
        lazy_time_l_path(n, l, False, k=1)  # acyclic

'''
# single database, multiple queries.
def measure_time_grow_v2():
    for n in range(5, 30, 5):
        measure_time_l_v2(n, 4, 8, True) # cyclic
        measure_time_l_v2(n, 4, 8, False)  # acyclic
'''


from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
def plot(mode, target, target_l):
    # mode = 1: plot for fixed n, l, any-k time pattern.
    # mode = 2: plot for fixed n (same database), both time changes with l. specify a target N
    l2_any_k_time_cycle = []
    l2_any_k_TTF_cycle = []
    l2_any_k_average_time_cycle = []
    l2_full_time_cycle = []
    l2_any_k_time_path = []
    l2_any_k_TTF_path = []
    l2_any_k_average_time_path = []
    l2_full_time_path = []

    l2_any_k_time_cycle_old = []
    l2_any_k_TTF_cycle_old = []
    l2_any_k_time_path_old = []
    l2_any_k_TTF_path_old = []

    l2_any_k_time_cycle_lazy = []
    l2_any_k_TTF_cycle_lazy = []
    l2_any_k_time_path_lazy = []
    l2_any_k_TTF_path_lazy = []

    l2_boolean_path = []
    l2_boolean_cycle = []
    l2_top1_path = []
    l2_top1_cycle = []

    l_values_cycle = []
    l_values_path = []


    n2_any_k_time_cycle = []
    n2_any_k_TTF_cycle = []
    n2_any_k_average_time_cycle = []
    n2_full_time_cycle = []
    n2_any_k_time_path = []
    n2_any_k_TTF_path = []
    n2_any_k_average_time_path = []
    n2_full_time_path = []

    n2_any_k_time_cycle_old = []
    n2_any_k_TTF_cycle_old = []
    n2_any_k_time_path_old = []
    n2_any_k_TTF_path_old = []

    n2_any_k_time_cycle_lazy = []
    n2_any_k_TTF_cycle_lazy = []
    n2_any_k_time_path_lazy = []
    n2_any_k_TTF_path_lazy = []

    n2_boolean_path = []
    n2_boolean_cycle = []
    n2_top1_path = []
    n2_top1_cycle = []

    n_values_cycle = []
    n_values_path = []
    for f in sorted(listdir('../time_any')):
        if isfile(join('../time_any', f)) and isfile(join('../time_all', f)) and isfile(join('../time_bool', f)):
            time_for_each = pickle.load(open(join('../time_any', f),'rb'))
            time_for_each_old = pickle.load(open(join('../time_old', f),'rb'))
            time_for_each_lazy = pickle.load(open(join('../time_lazy', f), 'rb'))
            timetuple_full = pickle.load(open(join('../time_all', f), 'rb'))
            timetuple_bool = pickle.load(open(join('../time_bool', f), 'rb'))
            n = int(f.split('_')[0])
            l = int(f.split('_')[1])
            cycle_or_not =  f.split('_')[2] == 'cycle'
            time_for_all = []
            time_bool = []
            time_top1 = []
            results_count = []
            time_till_now = []
            time_till_now_old = []
            time_till_now_lazy = []
            accumulated_time = 0
            accumulated_time_old = 0 # not deepak improved
            accumulated_time_lazy = 0
            if n == 5 and mode != 2:
                print "another measurment "
                continue
            if len(time_for_each) == 0:
                print "no result for this query"
                continue

            for i in range(len(time_for_each)):
                time_till_now.append(time_for_each[i] + accumulated_time)
                time_till_now_old.append(time_for_each_old[i] + accumulated_time_old)
                time_till_now_lazy.append(time_for_each_lazy[i] + accumulated_time_lazy)

                accumulated_time = time_for_each[i] + accumulated_time
                accumulated_time_old = time_for_each_old[i] + accumulated_time_old
                accumulated_time_lazy = time_for_each_lazy[i] + accumulated_time_lazy

                results_count.append(i+1)
                time_for_all.append(timetuple_full[1])
                time_bool.append(timetuple_bool[0])
                time_top1.append(timetuple_bool[1])

            if n == target:
                if cycle_or_not:
                    l2_any_k_TTF_cycle_lazy.append(time_for_each_lazy[0])
                    l2_any_k_time_cycle_lazy.append(accumulated_time_lazy)
                    l2_any_k_TTF_cycle.append(time_for_each[0])
                    l2_any_k_time_cycle.append(accumulated_time)
                    l2_any_k_TTF_cycle_old.append(time_for_each_old[0])
                    l2_any_k_time_cycle_old.append(accumulated_time_old)
                    l2_any_k_average_time_cycle.append(accumulated_time/len(time_for_each))
                    l2_full_time_cycle.append(timetuple_full[1])
                    l2_boolean_cycle.append(timetuple_bool[0])
                    l2_top1_cycle.append(timetuple_bool[1])
                    l_values_cycle.append(l)
                else:
                    l2_any_k_TTF_path_lazy.append(time_for_each_lazy[0])
                    l2_any_k_time_path_lazy.append(accumulated_time_lazy)
                    l2_any_k_TTF_path.append(time_for_each[0])
                    l2_any_k_time_path.append(accumulated_time)
                    l2_any_k_TTF_path_old.append(time_for_each_old[0])
                    l2_any_k_time_path_old.append(accumulated_time_old)
                    l2_any_k_average_time_path.append(accumulated_time/len(time_for_each))
                    l2_full_time_path.append(timetuple_full[1])
                    l2_boolean_path.append(timetuple_bool[0])
                    l2_top1_path.append(timetuple_bool[1])
                    l_values_path.append(l)

            if l == target_l:
                if cycle_or_not:
                    n2_any_k_TTF_cycle_lazy.append(time_for_each_lazy[0])
                    n2_any_k_time_cycle_lazy.append(accumulated_time_lazy)
                    n2_any_k_TTF_cycle.append(time_for_each[0])
                    n2_any_k_time_cycle.append(accumulated_time)
                    n2_any_k_TTF_cycle_old.append(time_for_each_old[0])
                    n2_any_k_time_cycle_old.append(accumulated_time_old)
                    n2_any_k_average_time_cycle.append(accumulated_time/len(time_for_each))
                    n2_full_time_cycle.append(timetuple_full[1])
                    n2_boolean_cycle.append(timetuple_bool[0])
                    n2_top1_cycle.append(timetuple_bool[1])
                    n_values_cycle.append(n)
                else:
                    n2_any_k_TTF_path_lazy.append(time_for_each_lazy[0])
                    n2_any_k_time_path_lazy.append(accumulated_time_lazy)
                    n2_any_k_TTF_path.append(time_for_each[0])
                    n2_any_k_time_path.append(accumulated_time)
                    n2_any_k_TTF_path_old.append(time_for_each_old[0])
                    n2_any_k_time_path_old.append(accumulated_time_old)
                    n2_any_k_average_time_path.append(accumulated_time/len(time_for_each))
                    n2_full_time_path.append(timetuple_full[1])
                    n2_boolean_path.append(timetuple_bool[0])
                    n2_top1_path.append(timetuple_bool[1])
                    n_values_path.append(n)


            if mode == 1:
                #plt.plot(time_till_now, results_count, 'r--', time_till_now, results_count, 'b--')
                results_count_k = np.true_divide(results_count, 1000)
                line_1, = plt.plot(time_till_now, results_count_k, 'r', label='line 1')
                line_2, = plt.plot(time_for_all, results_count_k, 'b', label='Line 2')
                line_3, = plt.plot(time_till_now_old, results_count_k, 'g', label='Line 3')

                plt.legend([line_1, line_2, line_3], ['any-k sort', 'full ranking', 'any-k max'])
                if cycle_or_not:
                    plt.title('N = '+ str(n) + ', l = ' + str(l) + ', cycle')
                else:
                    plt.title('N = ' + str(n) + ', l = ' + str(l) + ', path')
                plt.ylabel('number of results (Thousands)')
                plt.xlabel('time (seconds)')
                plt.show()

    if mode == 2:
        # plot how computational time for different l changes on the same database:
        plt.xlabel('query length')
        plt.ylabel('time (seconds)')
        plt.yscale('log')
        line_1, = plt.plot(l_values_cycle, l2_any_k_time_cycle, 'x',color='b', label='line 1')
        line_1_, = plt.plot(l_values_cycle, l2_any_k_TTF_cycle, '^', color='g',label='line 1_')
        line_2, = plt.plot(l_values_cycle, l2_full_time_cycle, 'o', color='r',label='Line 2')
        line_3, = plt.plot(l_values_cycle, l2_any_k_time_cycle_old, 's', color='c',label='line 3')
        line_3_, = plt.plot(l_values_cycle, l2_any_k_TTF_cycle_old, '+', color='m',label='line 3_')
        if target == 5:
            compare1 = np.power(1.89, l_values_cycle)
        else:
            compare1 = np.power(2.55, l_values_path)
        compare1 = np.true_divide(compare1, 50000)
        compare1 = [x for _, x in sorted(zip(l_values_cycle, compare1))]
        compare2 = l_values_cycle
        compare2 = np.true_divide(compare2, 20000) - 10/20000
        compare2 = [x for _, x in sorted(zip(l_values_cycle, compare2))]

        line_4, = plt.plot(sorted(l_values_cycle), compare1,color='y', label='line 4')
        line_5, = plt.plot(sorted(l_values_cycle), compare2, '--', color='gold',label='line 5')

        line_6, = plt.plot(l_values_cycle, l2_boolean_cycle, 'D', color='lime',label='line 6')
        line_7, = plt.plot(l_values_cycle, l2_top1_cycle, 'p',color='brown', label='line 7')

        line_8, = plt.plot(l_values_cycle, l2_any_k_time_cycle_lazy, 'h', color='darkgray', label='line 8')
        line_9, = plt.plot(l_values_cycle, l2_any_k_TTF_cycle_lazy, '<', color='steelblue', label='line 9')

        labels = [line_8, line_1, line_3, line_4, line_2, line_3_, line_1_, line_9, line_7, line_5, line_6]
        handles = ['any-k lazy TTL','any-k sort TTL', 'any-k max TTL', 'n^(l/2)', 'full ranking', 'any-k max TTF', 'any-k sort TTF', 'any-k lazy TTF',
                   "top-1", "l", "boolean"]

        plt.legend(labels, handles)
        #plt.legend([line_1, line_1_, line_2, line_3, line_3_, line_4, line_5, line_6, line_7], ['any-k sort TTL', 'any-k sort TTF', 'full ranking TTF/TTL', 'any-k max TTL', 'any-k max TTF', 'n^(l/2)', "l", "boolean", "top-1"])
        plt.title('Cycle')
        plt.show()
        #plt.xlabel('l')
       # plt.ylabel('time (seconds)')
        #plt.yscale('log')
        #line_1, = plt.plot(l_values_cycle, l2_any_k_TTF_cycle, 'o', label='line 1')
        #line_2, = plt.plot(l_values_cycle, l2_full_time_cycle, 'o', label='Line 2')
        #line_3, = plt.plot(l_values_cycle, l2_any_k_TTF_cycle_old, 'o', label='line 3')
        #plt.legend([line_1, line_2, line_3], ['any-k sort', 'full ranking', 'any-k max'])
        #plt.title('Cycle TTF')
        #plt.show()

        plt.xlabel('query length')
        plt.ylabel('time (seconds)')
        plt.yscale('log')
        if target == 5:
            compare1 = np.power(1.89, l_values_path)
        else:
            compare1 = np.power(2.55, l_values_path)

        compare1 = np.true_divide(compare1, 8000)
        compare1 = [x for _, x in sorted(zip(l_values_path, compare1))]
        compare2 = l_values_path
        compare2 = np.true_divide(compare2, 20000)- 10/2000
        compare2 = [x for _, x in sorted(zip(l_values_path, compare2))]


        line_1, = plt.plot(l_values_path, l2_any_k_time_path, 'x',color='b', label='line 1')
        line_1_, = plt.plot(l_values_path, l2_any_k_TTF_path, '^', color='g',label='line 1_')
        line_2, = plt.plot(l_values_path, l2_full_time_path, 'o',color='r', label='Line 2')
        line_3, = plt.plot(l_values_path, l2_any_k_time_path_old, 's', color='c',label='line 3')
        line_3_, = plt.plot(l_values_path, l2_any_k_TTF_path_old, '+',color='m', label='line 3_')


        line_4, = plt.plot(sorted(l_values_path), compare1, color='y',label='line 4')
        line_5, = plt.plot(sorted(l_values_path),  compare2, '--',color='gold', label='line 5')
        line_6, = plt.plot(l_values_path, l2_boolean_path, 'D', color='lime',label='line 6')
        line_7, = plt.plot(l_values_path, l2_top1_path, 'p',color='brown', label='line 7')

        line_8, = plt.plot(l_values_path, l2_any_k_time_path_lazy, 'h',color='darkgray', label='line 8')
        line_9, = plt.plot(l_values_path, l2_any_k_TTF_path_lazy, '<', color='steelblue', label='line 9')



        #labels = [line_1, line_1_, line_2, line_3, line_3_, line_4, line_5, line_6, line_7]
        #handles = ['any-k sort TTL', 'any-k sort TTF', 'full ranking', 'any-k max TTL', 'any-k max TTF', 'n^(l/2)', "l",
        # "boolean", "top-1"]

        labels = [line_8, line_1, line_3, line_4, line_2, line_3_, line_1_,line_9, line_7, line_5, line_6]
        handles = ['any-k lazy TTL', 'any-k sort TTL', 'any-k max TTL',  'n^(l/2)', 'full ranking',  'any-k max TTF', 'any-k sort TTF', 'any-k lazy TTF',
                   "top-1",  "l", "boolean"]
        #labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
        plt.legend(labels, handles)
        plt.title('Path')
        plt.show()

        #plt.xlabel('l')
        #plt.ylabel('time (seconds)')
        #plt.yscale('log')
        #line_1, = plt.plot(l_values_path, l2_any_k_TTF_path, 'o', label='line 1')
        #line_2, = plt.plot(l_values_path, l2_full_time_path, 'o', label='Line 2')
        #line_3, = plt.plot(l_values_path, l2_any_k_TTF_path_old, 'o', label='line 3')

        #plt.legend([line_1, line_2, line_3], ['any-k sort', 'full ranking', 'any-k max'])
        #plt.title('Path TTF')
        #plt.show()

    if mode == 3:
        # plot how computation time for diffrent n on the same query (same l)
        plt.xlabel('n')
        plt.ylabel('time (seconds)')
        plt.yscale('log')
        plt.xscale('log')

        exp = 2
        if target_l == 4:
            exp = 1.5


        line_1, = plt.plot(n_values_cycle, n2_any_k_time_cycle, 'x', color='b',label='line 1')
        line_1_, = plt.plot(n_values_cycle, n2_any_k_TTF_cycle, '^', color='g', label='line 1_')
        line_2, = plt.plot(n_values_cycle, n2_full_time_cycle, 'o', color='r',label='Line 2')
        line_3, = plt.plot(n_values_cycle, n2_any_k_time_cycle_old, 's', color='c',label='line 3')
        line_3_, = plt.plot(n_values_cycle, n2_any_k_TTF_cycle_old, '+', color='m', label='line 3_')

        compare1 = np.power(n_values_cycle, exp)
        compare1 = np.true_divide(compare1, 10)
        compare1 = np.multiply(compare1, np.log(compare1))
        compare1 = [x for _, x in sorted(zip(n_values_cycle, compare1))]
        compare1 = np.true_divide(compare1, 40000)
        compare2 = np.power(n_values_cycle, 2)
        compare2 = np.true_divide(compare2, 10)
        compare2 = np.multiply(compare2, np.log(compare2))
        compare2 = np.true_divide(compare2, 50000)

        compare2 = [x for _, x in sorted(zip(n_values_cycle, compare2))]

        line_4, = plt.plot(sorted(n_values_cycle), compare1 , color='y',label='line 4')
        line_5, = plt.plot(sorted(n_values_cycle), compare2, '--', color='gold',label='line 5')

        line_6, = plt.plot(n_values_cycle, n2_boolean_cycle, 'D', color='lime', label='line 6')
        line_7, = plt.plot(n_values_cycle, n2_top1_cycle, 'p', color='brown',label='line 7')
        plt.legend([line_1, line_1_, line_2, line_3, line_3_, line_4, line_5, line_6, line_7],
                   ['any-k sort TTL', 'any-k sort TTF', 'full ranking TTF/TTL', 'any-k max TTL', 'any-k max TTF', 'n^'+ str(exp)+' log n' , 'n^2 log n',"boolean", "top-1"])
        plt.title('4-Cycle')
        plt.show()
        plt.xlabel('n')
        plt.ylabel('time (seconds)')
        plt.yscale('log')
        plt.xscale('log')

        #line_1, = plt.plot(n_values_cycle, n2_any_k_TTF_cycle, 'o', label='line 1')
        #line_2, = plt.plot(n_values_cycle, n2_full_time_cycle, 'o', label='Line 2')
        #line_3, = plt.plot(n_values_cycle, n2_any_k_TTF_cycle_old, 'o', label='line 3')
        #line_4, = plt.plot(n_values_cycle, np.power(n_values_cycle, exp), label='line 4')
        #line_5, = plt.plot(n_values_cycle, np.power(n_values_cycle, 2), label='line 5')
        #plt.legend([line_1, line_2, line_3, line_4, line_5],
        #           ['any-k sort', 'full ranking', 'any-k max', 'n^' + str(exp), 'n^2'])
        #plt.title('Cycle TTF')
        #plt.show()
        #plt.xlabel('n')
        #plt.ylabel('time (seconds)')
        #plt.yscale('log')
        #plt.xscale('log')

        exp = 3  # 4-path...
        line_1, = plt.plot(n_values_path, n2_any_k_time_path, 'x', label='line 1')
        line_1_, = plt.plot(n_values_path, n2_any_k_TTF_path, '^', label='line 1_')
        line_2, = plt.plot(n_values_path, n2_full_time_path, 'o', label='Line 2')
        line_3, = plt.plot(n_values_path, n2_any_k_time_path_old, 's', label='line 3')
        line_3_, = plt.plot(n_values_path, n2_any_k_TTF_path_old, '+', label='Line 3_')

        compare1 = np.power(n_values_path, exp)
        #compare1 = np.true_divide(compare1, 0.001)
        #compare1 = np.multiply(compare1, np.log(compare1))
        compare1 = [x for _, x in sorted(zip(n_values_path, compare1))]
        compare1 = np.true_divide(compare1, 500000)

        compare2 = np.power(n_values_path, 1)
        compare2 = np.true_divide(compare2, 5)
        compare2 = np.multiply(compare2, np.log(compare2))
        compare2 = [x for _, x in sorted(zip(n_values_path, compare2))]
        compare2 = np.true_divide(compare2, 5000)
        line_4, = plt.plot(sorted(n_values_path), compare1, label='line 4')
        line_5, = plt.plot(sorted(n_values_path), compare2, '--', label='line 5')

        line_6, = plt.plot(n_values_path, n2_boolean_path, 'D', label='line 6')
        line_7, = plt.plot(n_values_path, n2_top1_path, 'p', label='line 7')

        plt.legend([line_1, line_1_, line_2, line_3, line_3_, line_4, line_5, line_6, line_7],
                   ['any-k sort TTL', 'any-k sort TTF', 'full ranking TTF/TTL', 'any-k max TTL', 'any-k max TTF', 'n^' + str(exp) + ' log n', 'n log n',"boolean", "top-1"])
        plt.title('4-Path')
        plt.show()


def plot_lower4():
    pass
#TODO: add plot for lower 4


if __name__ == "__main__":
    #measure_time_l_path(80, 7, True)
    #measure_time_grow_nl()
    #plot(2, 15)
    #measure_time_grow_v2()

    #measure_time_n_v2(3, 50, 4, True) #4-cycle
    #measure_time_n_v2(3, 50, 4, False) #4-path
    #plot(1, 0, 0) # any-k property.

    n = 10
    #measure_time_l(n)
    #add_lazy_l(n, k=999999999)
    plot(2, n, 0) # l-scalability

    #l = 4
    #measure_time_n(l)
    #plot(3, 0, l)  # n-scalability




