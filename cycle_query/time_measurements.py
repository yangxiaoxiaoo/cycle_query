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
        CQ.cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, l, False)
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

import DataGenerator
def measure_time_n_v2(n_start, n_end, l, cycle_or_not):
    # for the same query, plot how the running times changes as database density changes.
    # this requires the database generation procedure for every value of n...
    # not needed apart from v1 if same d_max generation method.

    for n in range(n_start, n_end, (n_end - n_start)/15):

        # attr_card = []
        # for i in range(l):
        #     attr_card.append(n)
        # var2cand = semi_join_utils.build_data(l, attr_card)
        # rel2tuple, tuple2weight = semi_join_utils.build_relation(l, var2cand, weightrange=10)

        if cycle_or_not:
            queryType = "Cycle"
        else:
            queryType = "Path"
        DensityOfEdges = "Full"
        edgeDistribution = "HardCase"
        rel2tuple, tuple2weight = DataGenerator.getDatabase\
            (queryType, n, l, DensityOfEdges, edgeDistribution, 1)

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
            CQ.cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, l, False)
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
    for l in range(4, 10, 1):
        for n in range(5, 30, 5):
            measure_time_l_path(n, l, True)  # cyclic
            measure_time_l_path(n, l, False)  # cyclic

# single database, multiple queries.
def measure_time_grow_v2():
    for n in range(5, 30, 5):
        measure_time_l_v2(n, 4, 8, True) # cyclic
        measure_time_l_v2(n, 4, 8, False)  # acyclic



from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
def plot(mode, target):
    # mode = 1: plot for fixed n, l, any-k time pattern.
    # mode = 2: plot for fixed n (same database), both time changes with l. specify a target N
    l2_any_k_time_cycle = []
    l2_any_k_average_time_cycle = []
    l2_full_time_cycle = []
    l2_any_k_time_path = []
    l2_any_k_average_time_path = []
    l2_full_time_path = []
    l_values_cycle = []
    l_values_path = []
    for f in listdir('../time_any'):
        if isfile(join('../time_any', f)) and isfile(join('../time_all', f)):
            time_for_each = pickle.load(open(join('../time_any', f),'rb'))
            timetuple_full = pickle.load(open(join('../time_all', f), 'rb'))
            n = int(f.split('_')[0])
            l = int(f.split('_')[1])
            cycle_or_not =  f.split('_')[2] == 'cycle'
            time_for_all = []
            results_count = []
            time_till_now = []
            accumulated_time = 0

            if len(time_for_each) == 0:
                print "no result for this query"
                continue

            for i in range(len(time_for_each)):
                time_till_now.append(time_for_each[i] + accumulated_time)
                accumulated_time = time_for_each[i] + accumulated_time
                results_count.append(i+1)
                time_for_all.append(timetuple_full[1])
            if n == target:
                if cycle_or_not:
                    l2_any_k_time_cycle.append(accumulated_time)
                    l2_any_k_average_time_cycle.append(accumulated_time/len(time_for_each))
                    l2_full_time_cycle.append(timetuple_full[1])
                    l_values_cycle.append(l)
                else:
                    l2_any_k_time_path.append(accumulated_time)
                    l2_any_k_average_time_path.append(accumulated_time/len(time_for_each))
                    l2_full_time_path.append(timetuple_full[1])
                    l_values_path.append(l)

            if mode == 1:
                plt.plot(results_count, time_till_now, 'r--', results_count, time_for_all, 'b--')
                line_1, = plt.plot(results_count, time_till_now, 'r--', label='line 1')
                line_2, = plt.plot(results_count, time_for_all, 'b--', label='Line 2')
                plt.legend([line_1, line_2], ['any-k', 'full enumeration'])
                if cycle_or_not:
                    plt.title('N = '+ str(n) + ', l = ' + str(l) + ', cycle')
                else:
                    plt.title('N = ' + str(n) + ', l = ' + str(l) + ', path')
                plt.xlabel('k')
                plt.ylabel('Time/Sec')
                plt.show()
    if mode == 2:
        # plot how computational time for different l changes on the same database:
        plt.xlabel('l')
        plt.ylabel('time/seconds')
        line_1, = plt.plot(l_values_cycle, l2_any_k_time_cycle, 'o', label='line 1')
        line_2, = plt.plot(l_values_cycle, l2_full_time_cycle, 'o', label='Line 2')
        plt.legend([line_1, line_2], ['any-k', 'full enumeration'])
        plt.title('l-cycle any-k total vs. full enumeration')
        plt.show()
        plt.xlabel('l')
        plt.ylabel('time/seconds')
        line_1, = plt.plot(l_values_cycle, l2_any_k_average_time_cycle, 'o', label='line 1')
        line_2, = plt.plot(l_values_cycle, l2_full_time_cycle, 'o', label='Line 2')
        plt.legend([line_1, line_2], ['any-k', 'full enumeration'])
        plt.title('l-cycle any-k next vs. full enumeration')
        plt.show()
        plt.xlabel('l')
        plt.ylabel('time/seconds')
        line_1, = plt.plot(l_values_path, l2_any_k_time_path, 'o', label='line 1')
        line_2, = plt.plot(l_values_path, l2_full_time_path, 'o', label='Line 2')
        plt.legend([line_1, line_2], ['any-k', 'full enumeration'])
        plt.title('l-path any-k total vs. full enumeration')
        plt.show()
        plt.xlabel('l')
        plt.ylabel('time/seconds')
        line_1, = plt.plot(l_values_path, l2_any_k_average_time_path, 'o', label='line 1')
        line_2, = plt.plot(l_values_path, l2_full_time_path, 'o', label='Line 2')
        plt.legend([line_1, line_2], ['any-k', 'full enumeration'])
        plt.title('l-path any-k next vs. full enumeration')
        plt.show()


if __name__ == "__main__":
    #measure_time_l_path(80, 7, True)
    #measure_time_grow_n()
    #plot(2, 15)
    #measure_time_grow_v2()

    #measure_time_n_v2(3, 50, 5, True) #3-cycle
    #measure_time_n_v2(3, 50, 5, False) #4-path
    plot(1, 30)