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
import argparse

def sanitize_times(time_for_each, t_preprocess):
	if time_for_each == []:
		return []
	time_for_each[0] += t_preprocess
	accum = time_for_each[0]
	res = [accum]
	for i in range(1, len(time_for_each)):
		res.append(accum + time_for_each[i])
		accum += time_for_each[i]
	return res

def outFile_name(dataset, impl, pq, query, l, n, delta, max_id):
	if dataset == "Random":
		return impl + "_" + pq + "_" + dataset + "_" + query + "_l" + str(l) + "_n" + str(n) + "_d" + str(delta) + ".out"
	elif dataset == "HardCase":
		return impl + "_" + pq + "_" + dataset + "_" + query + "_l" + str(l) + "_n" + str(n) + ".out"
	elif dataset == "Twitter":
		return impl + "_" + pq + "_" + dataset + "_" + query + "_l" + str(l) + "_m" + str(max_id) + ".out"

## -- Read input
parser = argparse.ArgumentParser(description='Running script')
parser.add_argument('-i', nargs='+', dest="impl_list", choices={"batch_ranking", "anyk_sort", "anyk_sort_unbounded", "anyk_sort_bounded", "anyk_lazy", "anyk_lazy_unbounded", "anyk_lazy_bounded", "anyk_lazysort", "anyk_lazysort_unbounded", "anyk_lazysort_bounded"}, default=["batch"], help="list of implementations to run")
parser.add_argument('-pq', nargs='+', dest="pq_list", choices={"Heap", "Btree", "Treap", "FibHeap", "PairHeap"}, default=["Heap"], help="list of data structures to pair implementations with")
parser.add_argument('-dataset', action="store", dest="dataset", choices={"Random", "HardCase", "Twitter"}, default="Twitter", help="Dataset to run")
parser.add_argument('-query', action="store", dest="query", choices={"Path", "Cycle"}, default="Cycle", help="Run path or cycle query")
parser.add_argument('-l', action="store", dest="l", type=int, default=4, help="Length of query")
parser.add_argument('-n', action="store", dest="n", type=int, default=50, help="Tuples per relation (For Twitter use -mid instead)")
parser.add_argument('-mid', action="store", dest="max_id", type=int, default=50, help="Keep users with ids up to this number (Only use for Twitter)")
parser.add_argument('-delta', action="store", dest="delta", type=int, default=None, help="Maximum duplicity of attribute value per relation (Only use with Random dataset)")

arg_results = parser.parse_args()
impl_list = arg_results.impl_list
pq_list = arg_results.pq_list
dataset = arg_results.dataset
query = arg_results.query
l = arg_results.l
n = arg_results.n
max_id = arg_results.max_id
delta = arg_results.delta

k_limit = sys.maxsize
if delta is None: delta = n

## -- Generate data
if dataset == "Random":
	rel2tuple, tuple2weight = DataGenerator.getDatabase(query, n, l, "Full", delta, 1)
elif dataset == "HardCase":
	rel2tuple, tuple2weight = DataGenerator.getDatabase(query, n, l, "Full", "HardCase", 2)
else:
	rel2tuple, tuple2weight = data_loader.load_twitter("../Experiment_Runtime/", "Twitter_truncated", max_id, l)

## -- Preprocess
if query == "Path":
	t_start = timeit.default_timer()
	tu2down_neis, tu2up_neis = CQ.path_SJ_reduce_l(rel2tuple, l)
	t_end = timeit.default_timer()
	t_preprocess = t_end - t_start
	print "Done with preprocessing  at " + str(t_preprocess) + " sec"    
elif query == "Cycle":
	t_start = timeit.default_timer()
	tu2down_neis, tu2up_neis = CQ.cycle_SJ_reduce_l_light(rel2tuple, l)
	t_end = timeit.default_timer()
	t_preprocess = t_end - t_start
	print "Done with preprocessing  at " + str(t_preprocess) + " sec"

for impl in impl_list:
	if impl == "batch_ranking":
		pq = "Heap"
		t1 = timeit.default_timer()
		if query == "Path":
			sorted_values = CQ.path_enumerate_all(rel2tuple, tuple2weight, tu2down_neis, k_limit, l, debug = False)
		elif query == "Cycle":	
			results, sorted_values = CQ.cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k_limit, l, False, debug= False)
		t2 = timeit.default_timer()
		t_batch  =  t_preprocess + t2 - t1
		f = open("outs/" + outFile_name(dataset, impl, pq, query, l, n, delta, max_id), "w")
		f.write("Time = " + str(t_batch) + "\n")
		num_of_results = len(sorted_values)
		f.write("Results = " + str(num_of_results) + "\n")
		num_of_tuples = len(rel2tuple["R0"])
		f.write("Number of tuples (Twitter edges) = " + str(num_of_tuples))
		f.close()   
	else:
		for pq in pq_list:

			if query == "Path":
				if impl == "anyk_sort" or impl == "anyk_sort_unbounded":
					TOP_K, time_for_each = CQ.priority_search_l_path(k_limit, rel2tuple, tuple2weight, tu2down_neis, l, Deepak= True, Lazy = False, PQmode = pq, bound = None, debug = False)
				elif impl == "anyk_lazy" or impl == "anyk_lazy_unbounded":
					TOP_K, time_for_each = CQ.priority_search_l_path(k_limit, rel2tuple, tuple2weight, tu2down_neis, l, Deepak= False, Lazy = False, PQmode = pq, bound = None, debug = False)
				elif impl == "anyk_lazysort" or impl == "anyk_lazysort_unbounded":
					TOP_K, time_for_each = CQ.priority_search_l_path(k_limit, rel2tuple, tuple2weight, tu2down_neis, l, Deepak= True, Lazy = True, PQmode = pq, bound = None, debug = False)

			elif query == "Cycle":	
				if impl == "anyk_sort" or impl == "anyk_sort_unbounded":
					TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k_limit, l, Deepak=True, Lazy = False, PQmode= pq, bound = None, debug = False)
				elif impl == "anyk_lazy" or impl == "anyk_lazy_unbounded":
					TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k_limit, l, Deepak=False, Lazy = False, PQmode= pq, bound = None, debug = False)
				elif impl == "anyk_lazysort" or impl == "anyk_lazysort_unbounded":
					TOP_K, time_for_each = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k_limit, l, Deepak=True, Lazy = True, PQmode= pq, bound = None, debug = False)

			times = sanitize_times(time_for_each, t_preprocess)
			f = open("outs/" + outFile_name(dataset, impl, pq, query, l, n, delta, max_id), "w")
			for i in range(len(times)):
				f.write("k = " + str(i + 1) + " : " + str(times[i]) + "\n")
			f.close()
	print "Done with " + outFile_name(dataset, impl, pq, query, l, n, delta, max_id)                        
