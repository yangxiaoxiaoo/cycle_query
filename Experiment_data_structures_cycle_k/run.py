#!/usr/bin/env python

import sys 
import os
sys.path.append(os.path.abspath("../cycle_query"))
import DataGenerator
import HRJNstar
import timeit
import pickle
import semi_join_utils
import CQ

def sanitize_times(time_for_each, t_preprocess):
    time_for_each[0] += t_preprocess
    accum = time_for_each[0]
    res = [accum]
    for i in range(1, len(time_for_each)):
        res.append(accum + time_for_each[i])
        accum += time_for_each[i]
    return res

## Fixed
n = 200
l = 5
k_limit = 999999999

rel2tuple, tuple2weight = DataGenerator.getDatabase("Cycle", n, l, "Full", "HardCase", 2)
## Output dictionaries
outFile1 = open("input_tuples.pkl", "wb")
pickle.dump(rel2tuple, outFile1)
outFile1.close()
outFile2 = open("input_weights.pkl", "wb")
pickle.dump(tuple2weight, outFile2)
outFile2.close()

## Preprocess
t_start = timeit.default_timer()
tu2down_neis, tu2up_neis = CQ.cycle_SJ_reduce_l(rel2tuple, l)
t_end = timeit.default_timer()
t_preprocess = t_end - t_start

## First run batch ranking
t1 = timeit.default_timer()
results, sorted_values = CQ.cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k_limit, l, False, debug= False)
t2 = timeit.default_timer()
t_batch  =  t_preprocess + t2 - t1
f = open("outs/batch_ranking", "w")
f.write("Time = " + str(t_batch))
f.close()
num_of_results = len(sorted_values)
print "Done with batch ranking"

## Run anyk-max unbounded
data_structure_list = ["PQ", "Btree", "Treap"]
for ds in data_structure_list:
    TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k_limit, l, Deepak=False, RLmode= ds, bound = None, debug = False)
    times = sanitize_times(time_for_each, t_preprocess)
    f = open("outs/anyk_max_" + ds + "_unbounded", "w")
    for i in range(len(times)):
        f.write("k = " + str(i + 1) + " : " + str(times[i]) + "\n")
    f.close()
    print "Done with anyk_max_" + ds + "_unbounded"

## Run anyk-sort unbounded
data_structure_list = ["PQ", "Btree", "Treap"]
for ds in data_structure_list:
    TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k_limit, l, Deepak=True, RLmode= ds, bound = None, debug = False)
    times = sanitize_times(time_for_each, t_preprocess)
    f = open("outs/anyk_sort_" + ds + "_unbounded", "w")
    for i in range(len(times)):
        f.write("k = " + str(i + 1) + " : " + str(times[i]) + "\n")
    f.close()
    print "Done with anyk_sort_" + ds + "_unbounded"


k_list = range(1, num_of_results + 1, 1000)

## Run anyk-max bounded
data_structure_list = ["Btree", "Treap"]
for ds in data_structure_list:
    times = []
    for k in k_list:
        t1 = timeit.default_timer()
        TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=False, RLmode= ds, bound = k, debug = False)
        t2 = timeit.default_timer()
        times.append(t2 - t1 + t_preprocess)
    f = open("outs/anyk_max_" + ds + "_bounded", "w")
    for i in range(len(times)):
        f.write("k = " + str(k_list[i]) + " : " + str(times[i]) + "\n")
    f.close()
    print "Done with anyk_max_" + ds + "_bounded"

## Run anyk-sort bounded
data_structure_list = ["Btree", "Treap"]
for ds in data_structure_list:
    times = []
    for k in k_list:
        t1 = timeit.default_timer()
        TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=True, RLmode= ds, bound = k, debug = False)
        t2 = timeit.default_timer()
        times.append(t2 - t1 + t_preprocess)
    f = open("outs/anyk_sort_" + ds + "_bounded", "w")
    for i in range(len(times)):
        f.write("k = " + str(k_list[i]) + " : " + str(times[i]) + "\n")
    f.close()
    print "Done with anyk_sort_" + ds + "_bounded"
