#!/usr/bin/env python

import sys 
import os
sys.path.append(os.path.abspath("../cycle_query"))
import pickle
import data_loader
import DataGenerator
import argparse

def outFile_name(dataset, query, l, n, delta, max_id):
	if dataset == "Random":
		return dataset + "_" + query + "_l" + str(l) + "_n" + str(n) + "_d" + str(delta) + ".out"
	elif dataset == "HardCase":
		return dataset + "_" + query + "_l" + str(l) + "_n" + str(n) + ".out"
	elif dataset == "Twitter":
		return dataset + "_" + query + "_l" + str(l) + "_m" + str(max_id) + ".out"

## -- Read input
parser = argparse.ArgumentParser(description='Running script')
parser.add_argument('-dataset', action="store", dest="dataset", choices={"Random", "HardCase", "Twitter"}, default="Twitter", help="Dataset to generate")
parser.add_argument('-query', action="store", dest="query", choices={"Path", "Cycle"}, default="Cycle", help="Run path or cycle query")
parser.add_argument('-l', action="store", dest="l", type=int, default=4, help="Length of query")
parser.add_argument('-n', action="store", dest="n", type=int, default=50, help="Tuples per relation (For Twitter use -mid instead)")
parser.add_argument('-mid', action="store", dest="max_id", type=int, default=50, help="Keep users with ids up to this number (Only use for Twitter)")
parser.add_argument('-delta', action="store", dest="delta", type=int, default=None, help="Maximum duplicity of attribute value per relation (Only use with Random dataset)")

arg_results = parser.parse_args()
dataset = arg_results.dataset
query = arg_results.query
l = arg_results.l
n = arg_results.n
max_id = arg_results.max_id
delta = arg_results.delta

if delta is None: delta = n

## -- Generate data
if dataset == "Random":
	rel2tuple, tuple2weight = DataGenerator.getDatabase(query, n, l, "Full", delta)
elif dataset == "HardCase":
	rel2tuple, tuple2weight = DataGenerator.getDatabase(query, n, l, "Full", "HardCase")
else:
	rel2tuple, tuple2weight = data_loader.load_twitter("../Experiment_Runtime/", "Twitter_truncated", max_id, l)

DataGenerator.save_to_file("ins/" + outFile_name(dataset, query, l, n, delta, max_id), rel2tuple, tuple2weight)
