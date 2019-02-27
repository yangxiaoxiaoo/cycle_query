import timeit
import pickle
import semi_join_utils
import numpy as np
import CQ

def measure_time_l_path(n, l, cycle_or_not):
    # simplest version, takes n and l. Useful version!

    queryType = "Cycle"
    DensityOfEdges = "Full"
    edgeDistribution = "HardCase"
    rel2tuple, tuple2weight = DataGenerator.getDatabase \
        (queryType, n, l, DensityOfEdges, edgeDistribution, 2)


    k = 9999999999
    if not cycle_or_not:  # path case
        t_start = timeit.default_timer()
        tu2down_neis, tu2up_neis = CQ.path_SJ_reduce_l(rel2tuple, l)
        t_end = timeit.default_timer()
        t_preprocess = t_end - t_start  # the time_any to preprocess and build the relation maps.

        print "algo: any-k priotitized search"
        t1 = timeit.default_timer()
        TOP_K, time_for_each = CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak= True, RLmode = "PQ", bound = None, debug = False)
        #modes: "PQ", "Btree", "Treap"
        #bound=None | k
        # when debug is True there is prints, otherwise not
        if len(time_for_each) > 0:
            time_for_each[0] += t_preprocess

        TOP_K, time_for_each_old = CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak=False,
                                                             RLmode="PQ", bound=None, debug=False)
        if len(time_for_each_old) > 0:
            time_for_each_old[0] += t_preprocess


        t2 = timeit.default_timer()
        print "algo: enumerate all"
        CQ.path_enumerate_all(rel2tuple, tuple2weight, tu2down_neis, k, l, debug = False)
        t3 = timeit.default_timer()
        print ('Time any-k: ', t_preprocess + sum(time_for_each))
        t_full  =  t_preprocess + t3 - t2
        print ('Time enumerate: ', t_full)

    else:  # cycle
        t_start = timeit.default_timer()
        tu2down_neis, tu2up_neis = CQ.cycle_SJ_reduce_l(rel2tuple, l)
        t_end = timeit.default_timer()
        t_preprocess = t_end - t_start  # the time_any to preprocess and build the relation maps.

        # TODO: add any-k naive?
        print "algo: any-k split version"
        TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=True, RLmode= "PQ", bound = k, debug = False, naive=1)

        if len(time_for_each) > 0:
            time_for_each[0] = t_preprocess
            time_for_each[0] += t_preprocess

        TOP_K, time_for_each_old = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=False,
                                                                  RLmode="PQ", bound=k, debug=False, naive=1)

        if len(time_for_each_old) > 0:
            time_for_each_old[0] = t_preprocess
            time_for_each_old[0] += t_preprocess


        t1 = timeit.default_timer()
        print "algo: enumerate all"
        CQ.cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, l, False, debug= False)
        t3 = timeit.default_timer()

        print ('Time any-k split: ', t_preprocess + sum(time_for_each))
        t_full = t_preprocess + t3 - t1
        print ('Time enumerate: ', t_full)



    timetuple_full = (t_preprocess, t_full)
    if cycle_or_not:
        pickle.dump(time_for_each, open("../time_any/" + str(n)+'_'+str(l) + '_cycle', 'wb'))
        pickle.dump(time_for_each_old, open("../time_old/" + str(n) + '_' + str(l) + '_cycle', 'wb'))
        pickle.dump(timetuple_full, open("../time_all/" + str(n) + '_' + str(l) + '_cycle', 'wb'))
    else:
        pickle.dump(time_for_each, open("../time_any/" + str(n) + '_' + str(l) + '_path', 'wb'))
        pickle.dump(time_for_each_old, open("../time_old/" + str(n) + '_' + str(l) + '_path', 'wb'))
        pickle.dump(timetuple_full, open("../time_all/" + str(n) + '_' + str(l) + '_path', 'wb'))

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
            (queryType, n, l, DensityOfEdges, edgeDistribution, 1)

        t_start = timeit.default_timer()
        tu2down_neis, tu2up_neis = CQ.cycle_SJ_reduce_l(rel2tuple, l)
        t_end = timeit.default_timer()
        t_preprocess = t_end - t_start  # the time_any to preprocess and build the relation maps.
        k = 9999999999
        
        if not cycle_or_not:  # path case
            print "algo: any-k priotitized search"

            t_start = timeit.default_timer()
            tu2down_neis, tu2up_neis = CQ.path_SJ_reduce_l(rel2tuple, l)
            t_end = timeit.default_timer()
            t_preprocess = t_end - t_start

            TOP_K, time_for_each = CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak=True, RLmode= "PQ", bound = k, debug = False)
            if len(time_for_each) > 0:
                time_for_each[0] += t_preprocess

            TOP_K, time_for_each_old = CQ.priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak=False, RLmode= "PQ", bound = k, debug = False)
            if len(time_for_each_old) > 0:
                time_for_each_old[0] += t_preprocess

            t1 = timeit.default_timer()
            print "algo: enumerate all"
            CQ.path_enumerate_all(rel2tuple, tuple2weight, tu2down_neis, k, l)
            t3 = timeit.default_timer()
            print ('Time any-k: ', t_preprocess + sum(time_for_each))
            t_full  =  t_preprocess + t3 - t1
            print ('Time enumerate: ', t_full)

        else:  # cycle
            # TODO: add any-k naive
            print "algo: any-k split version"
            TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=True, debug=False)
            if len(time_for_each) > 0:
                time_for_each[0] += t_preprocess
            TOP_K, time_for_each_old = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=False, debug=False)
            if len(time_for_each_old) > 0:
                time_for_each_old[0] += t_preprocess
            t1 = timeit.default_timer()
            print "algo: enumerate all"
            CQ.cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, l, False)
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
    n_log = np.logspace(1, 3, 10, endpoint=True)
    n_line =  range(3, 50, 3)
    for n in n_line:
        print int(n)
        measure_time_l_path(int(n), l, True)  # cyclic
        #measure_time_l_path(int(n), l, False)  # acyclic
    for n in n_log:
        print int(n)
        measure_time_l_path(int(n), l, True)  # cyclic
        #measure_time_l_path(int(n), l, False)  # acyclic

def measure_time_l(n):
    for l in range(3, 20):
        measure_time_l_path(n, l, True)  # cyclic
        measure_time_l_path(n, l, False)  # acyclic



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

    n_values_cycle = []
    n_values_path = []
    for f in listdir('../time_any'):
        if isfile(join('../time_any', f)) and isfile(join('../time_all', f)):
            time_for_each = pickle.load(open(join('../time_any', f),'rb'))
            time_for_each_old = pickle.load(open(join('../time_old', f),'rb'))
            timetuple_full = pickle.load(open(join('../time_all', f), 'rb'))
            n = int(f.split('_')[0])
            l = int(f.split('_')[1])
            cycle_or_not =  f.split('_')[2] == 'cycle'
            time_for_all = []
            results_count = []
            time_till_now = []
            time_till_now_old = []
            accumulated_time = 0
            accumulated_time_old = 0 # not deepak improved

            if len(time_for_each) == 0:
                print "no result for this query"
                continue

            for i in range(len(time_for_each)):
                time_till_now.append(time_for_each[i] + accumulated_time)

                time_till_now_old.append(time_for_each_old[i] + accumulated_time_old)

                accumulated_time = time_for_each[i] + accumulated_time

                accumulated_time_old = time_for_each_old[i] + accumulated_time_old
                results_count.append(i+1)
                time_for_all.append(timetuple_full[1])
            if n == target:
                if cycle_or_not:
                    l2_any_k_TTF_cycle.append(time_for_each[0])
                    l2_any_k_time_cycle.append(accumulated_time)
                    l2_any_k_TTF_cycle_old.append(time_for_each_old[0])
                    l2_any_k_time_cycle_old.append(accumulated_time_old)
                    l2_any_k_average_time_cycle.append(accumulated_time/len(time_for_each))
                    l2_full_time_cycle.append(timetuple_full[1])
                    l_values_cycle.append(l)
                else:
                    l2_any_k_TTF_path.append(time_for_each[0])
                    l2_any_k_time_path.append(accumulated_time)
                    l2_any_k_TTF_path_old.append(time_for_each_old[0])
                    l2_any_k_time_path_old.append(accumulated_time_old)
                    l2_any_k_average_time_path.append(accumulated_time/len(time_for_each))
                    l2_full_time_path.append(timetuple_full[1])
                    l_values_path.append(l)

            if l == target_l:
                if cycle_or_not:
                    n2_any_k_TTF_cycle.append(time_for_each[0])
                    n2_any_k_time_cycle.append(accumulated_time)
                    n2_any_k_TTF_cycle_old.append(time_for_each_old[0])
                    n2_any_k_time_cycle_old.append(accumulated_time_old)
                    n2_any_k_average_time_cycle.append(accumulated_time/len(time_for_each))
                    n2_full_time_cycle.append(timetuple_full[1])
                    n_values_cycle.append(n)
                else:
                    n2_any_k_TTF_path.append(time_for_each[0])
                    n2_any_k_time_path.append(accumulated_time)
                    n2_any_k_TTF_path_old.append(time_for_each_old[0])
                    n2_any_k_time_path_old.append(accumulated_time_old)
                    n2_any_k_average_time_path.append(accumulated_time/len(time_for_each))
                    n2_full_time_path.append(timetuple_full[1])
                    n_values_path.append(n)


            if mode == 1:
                #plt.plot(time_till_now, results_count, 'r--', time_till_now, results_count, 'b--')
                line_1, = plt.plot(time_till_now, results_count, 'r--', label='line 1')
                line_2, = plt.plot(time_for_all, results_count, 'b--', label='Line 2')
                line_3, = plt.plot(time_till_now_old, results_count, 'g--', label='Line 3')

                plt.legend([line_1, line_2, line_3], ['any-k sort', 'full ranking', 'any-k max'])
                if cycle_or_not:
                    plt.title('N = '+ str(n) + ', l = ' + str(l) + ', cycle')
                else:
                    plt.title('N = ' + str(n) + ', l = ' + str(l) + ', path')
                plt.ylabel('k')
                plt.xlabel('Time/Sec')
                plt.show()

    if mode == 2:
        # plot how computational time for different l changes on the same database:
        plt.xlabel('l')
        plt.ylabel('time (seconds)')
        plt.yscale('log')
        line_1, = plt.plot(l_values_cycle, l2_any_k_time_cycle, 'o', label='line 1')
        line_1_, = plt.plot(l_values_cycle, l2_any_k_TTF_cycle, 'o', label='line 1_')
        line_2, = plt.plot(l_values_cycle, l2_full_time_cycle, 'o', label='Line 2')
        line_3, = plt.plot(l_values_cycle, l2_any_k_time_cycle_old, 'o', label='line 3')
        line_3_, = plt.plot(l_values_cycle, l2_any_k_TTF_cycle_old, 'o', label='line 3_')

        compare1 = np.power(2, l_values_cycle)
        compare1 = np.true_divide(compare1, 50000)
        compare2 = l_values_cycle
        compare2 = np.true_divide(compare2, 50000)
        line_4, = plt.plot(l_values_cycle, compare1, label='line 4')
        line_5, = plt.plot(l_values_cycle, compare2, label='line 5')

        plt.legend([line_1, line_1_, line_2, line_3, line_3_, line_4, line_5], ['any-k sort TTL', 'any-k sort TTF', 'full ranking TTF/TTL', 'any-k max TTL', 'any-k max TTF', 'n^(l/2)', "l"])
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

        plt.xlabel('l')
        plt.ylabel('time (seconds)')
        plt.yscale('log')
        line_1, = plt.plot(l_values_path, l2_any_k_time_path, 'o', label='line 1')
        line_1_, = plt.plot(l_values_path, l2_any_k_TTF_path, 'o', label='line 1_')

        line_2, = plt.plot(l_values_path, l2_full_time_path, 'o', label='Line 2')
        line_3, = plt.plot(l_values_path, l2_any_k_time_path_old, 'o', label='line 3')
        line_3_, = plt.plot(l_values_path, l2_any_k_TTF_path_old, 'o', label='line 3_')

        compare1 = np.power(2, l_values_cycle)
        compare1 = np.true_divide(compare1, 50000)
        compare2 = l_values_cycle
        compare2 = np.true_divide(compare2, 50000)
        line_4, = plt.plot(l_values_cycle, compare1, label='line 4')
        line_5, = plt.plot(l_values_cycle, compare2, label='line 5')

        plt.legend([line_1, line_1_, line_2, line_3, line_3_, line_4, line_5], ['any-k sort TTL', 'any-k sort TTF', 'full ranking', 'any-k max TTL', 'any-k max TTF', 'n^(l -1 )', "l"])
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


        line_1, = plt.plot(n_values_cycle, n2_any_k_time_cycle, 'o', label='line 1')
        line_1_, = plt.plot(n_values_cycle, n2_any_k_TTF_cycle, 'o', label='line 1_')
        line_2, = plt.plot(n_values_cycle, n2_full_time_cycle, 'o', label='Line 2')
        line_3, = plt.plot(n_values_cycle, n2_any_k_time_cycle_old, 'o', label='line 3')
        line_3_, = plt.plot(n_values_cycle, n2_any_k_TTF_cycle_old, 'o', label='line 3_')

        compare1 = np.power(n_values_cycle, exp)
        compare1 = np.multiply(compare1, np.log(compare1))
        compare1 = np.true_divide(compare1, 500000)
        compare2 = np.power(n_values_cycle, 2)

        compare2 = np.multiply(compare2, np.log(compare2))
        compare2 = np.true_divide(compare2, 500000)
        line_4, = plt.plot(n_values_cycle, compare1 , label='line 4')
        line_5, = plt.plot(n_values_cycle, compare2, label='line 5')
        plt.legend([line_1, line_1_, line_2, line_3, line_3_, line_4, line_5],
                   ['any-k sort TTL', 'any-k sort TTF', 'full ranking TTF/TTL', 'any-k max TTL', 'any-k max TTF', 'n^'+ str(exp)+' log n' , 'n^2 log n'])
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
        line_1, = plt.plot(n_values_path, n2_any_k_time_path, 'o', label='line 1')
        line_1_, = plt.plot(n_values_path, n2_any_k_TTF_path, 'o', label='line 1_')
        line_2, = plt.plot(n_values_path, n2_full_time_path, 'o', label='Line 2')
        line_3, = plt.plot(n_values_path, n2_any_k_time_path_old, 'o', label='line 3')
        line_3_, = plt.plot(n_values_path, n2_any_k_TTF_path_old, 'o', label='Line 3_')

        compare1 = np.power(n_values_cycle, exp)
        compare1 = np.multiply(compare1, np.log(compare1))
        compare1 = np.true_divide(compare1, 500000)
        compare2 = np.power(n_values_cycle, 1)

        compare2 = np.multiply(compare2, np.log(compare2))
        compare2 = np.true_divide(compare2, 50000)
        line_4, = plt.plot(n_values_cycle, compare1, label='line 4')
        line_5, = plt.plot(n_values_cycle, compare2, label='line 5')

        plt.legend([line_1, line_1_, line_2, line_3, line_3_, line_4, line_5],
                   ['any-k sort TTL', 'any-k sort TTF', 'full ranking TTF/TTL', 'any-k max TTL', 'any-k max TTF', 'n^' + str(exp) + ' log n', 'n log n'])
        plt.title('4-Path')
        plt.show()

        #plt.xlabel('n')
        #plt.ylabel('time (seconds)')
        #plt.yscale('log')
        #plt.xscale('log')

        #line_1, = plt.plot(n_values_path, n2_any_k_TTF_path, 'o', label='line 1')
        #line_2, = plt.plot(n_values_path, n2_full_time_path, 'o', label='Line 2')
        #line_3, = plt.plot(n_values_path, n2_any_k_TTF_path_old, 'o', label='Line 3')
        #line_4, = plt.plot(n_values_path, np.power(n_values_path, exp), label='line 4')
        #line_5, = plt.plot(n_values_path, np.power(n_values_path, 1), label='line 5')
        #plt.legend([line_1, line_2, line_3, line_4, line_5],
        #           ['any-k sort', 'full ranking', 'any-k max', 'n^' + str(exp), 'n'])
        #plt.title('Path TTF')
        #plt.show()


if __name__ == "__main__":
    #measure_time_l_path(80, 7, True)
    #measure_time_grow_nl()
    #plot(2, 15)
    #measure_time_grow_v2()

    #measure_time_n_v2(3, 50, 5, True) #5-cycle
    #measure_time_n_v2(3, 50, 5, False) #5-path
    #plot(1, 0, 0) # any-k property.

    n = 5
    measure_time_l(n)
    plot(2, n, 0) # l-scalability

    #l = 4
    #measure_time_n(l)
    #plot(3, 0, l)