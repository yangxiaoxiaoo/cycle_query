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
    for l in range(4, 10, 1):
        for n in range(5, 30, 5):
            measure_time_l_path(n, l, True)  # cyclic
            measure_time_l_path(n, l, False)  # cyclic

from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
def plot():
    # TODO: read from pickle and plot.
    any_k_times = []
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
            for i in range(len(time_for_each)):
                time_till_now.append(time_for_each[i] + accumulated_time)
                accumulated_time = time_for_each[i] + accumulated_time
                results_count.append(i+1)
                time_for_all.append(timetuple_full[1])
            plt.plot(results_count, time_till_now, 'r--', results_count, time_for_all, 'b--')
            line_1, = plt.plot(results_count, time_till_now, 'r--', label='line 1')
            line_2, = plt.plot(results_count, time_for_all, 'b--', label='Line 2')
            plt.legend([line_1, line_2], ['any-k', 'full enumeration'])
            if cycle_or_not:
                plt.title('d_max = '+ str(n) + ', l = ' + str(l) + ', cycle')
            else:
                plt.title('d_max = ' + str(n) + ', l = ' + str(l) + ', path')
            plt.show()


    pass

if __name__ == "__main__":
    #measure_time_l_path(80, 7, True)
    #measure_time_grow_n()
    plot()