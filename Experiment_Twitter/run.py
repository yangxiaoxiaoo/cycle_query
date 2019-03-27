#!/usr/bin/env python

import sys 
import os
sys.path.append(os.path.abspath("../cycle_query"))
import HRJNstar
import timeit
import pickle
import semi_join_utils
import CQ
import data_loader
import DataGenerator

def sanitize_times(time_for_each, t_preprocess):
    time_for_each[0] += t_preprocess
    accum = time_for_each[0]
    res = [accum]
    for i in range(1, len(time_for_each)):
        res.append(accum + time_for_each[i])
        accum += time_for_each[i]
    return res

## Fixed
max_id = 700
l = 5
k_limit = sys.maxsize

## Input relations
#rel2tuple, tuple2weight = data_loader.load_twitter("../Experiment_Twitter/", "Twitter_truncated", max_id, l)
#DataGenerator.printRelations(rel2tuple)
n = 500
rel2tuple, tuple2weight = DataGenerator.getDatabase("Cycle", n, l, "Full", 20, 1)

## Preprocess
t_start = timeit.default_timer()
tu2down_neis, tu2up_neis = CQ.cycle_SJ_reduce_l_light(rel2tuple, l)
t_end = timeit.default_timer()
t_preprocess = t_end - t_start
print "Done with preprocessing  at " + str(t_preprocess) + " sec"

## First run batch ranking
t1 = timeit.default_timer()
results, sorted_values = CQ.cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k_limit, l, False, debug= False)
t2 = timeit.default_timer()
t_batch  =  t_preprocess + t2 - t1
f = open("outs/batch_ranking.out", "w")
f.write("Time = " + str(t_batch) + "\n")
num_of_results = len(sorted_values)
f.write("Results = " + str(num_of_results) + "\n")
num_of_tuples = len(rel2tuple["R0"])
f.write("Number of tuples (Twitter edges) = " + str(num_of_tuples))
f.close()
print "Done with batch ranking"

## Run anyk-max unbounded

data_structure_list = ["Heap", "Btree"]
for ds in data_structure_list:
    TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k_limit, l, Deepak=False, PQmode= "Heap", bound = None, debug = False)
    times = sanitize_times(time_for_each, t_preprocess)
    f = open("outs/anyk_max_" + ds + "_unbounded.out", "w")
    for i in range(len(times)):
        f.write("k = " + str(i + 1) + " : " + str(times[i]) + "\n")
    f.close()
    print "Done with anyk_max_" + ds + "_unbounded"


## Run anyk-sort unbounded
data_structure_list = ["Heap", "Btree"]
for ds in data_structure_list:
    TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k_limit, l, Deepak=True, PQmode= ds, bound = None, debug = False)
    times = sanitize_times(time_for_each, t_preprocess)
    f = open("outs/anyk_sort_" + ds + "_unbounded.out", "w")
    for i in range(len(times)):
        f.write("k = " + str(i + 1) + " : " + str(times[i]) + "\n")
    f.close()
    print "Done with anyk_sort_" + ds + "_unbounded"


## Run Boolean
'''
exist, time_bool = l_path_bool(rel2tuple, l)
f = open("outs/boolean.out", "w")
f.write("Time = " + str(time_bool) + "\n")
f.close()
print "Done with boolean"

Top1, time_top1 = l_path_top1(rel2tuple, tuple2weight, tu2down_neis, l)
f = open("outs/top1.out", "w")
f.write("Time = " + str(t_preprocess + time_top1) + "\n")
f.close()
print "Done with top1"
'''