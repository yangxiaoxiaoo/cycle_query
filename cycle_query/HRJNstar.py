#!/usr/bin/env python

## Implementation of the HRJN* operator, generalized to handle l-way joins (not only binary)
## We assume that the query is a path from R0 to R(l-1)
## The output is ranked by minimum weight and the top-k answers are returned

## pip install blist
## pip install cython
## pip install treap
import sys
from collections import defaultdict
import operator
import priority_queue
import globalclass

## Inserts new join combinations to the sorted list
def add_results(newResults, joinResults):
	for outTuple in newResults:
		joinResults.add(outTuple)

## If a result is below the threshold, then it is safe to output, so move it from the priority queue to the output buffer
def move_to_out(joinResults, outBuffer, threshold, k, tuple2weight, l):

	while joinResults.size() != 0 and len(outBuffer) < k:
		minWeight = joinResults.min_weight()
		if minWeight > threshold: 
			break
		outTuple = joinResults.pop_min(minWeight)
		## Since outTuple is part of the top-k, we can decrease the maximum size of the data structure holding potential results
		joinResults.decrease_max_size()
		#print "Result " + str(outTuple) + " exceeds threshold and is moved to the output buffer"

		## For a fair comparison, build PEI instances
		t0 = (outTuple[1][0], outTuple[1][1])
		PEI_instance = globalclass.PEI_path(t0, tuple2weight[t0], 0, l)
		for i in range(1, l):
			t_new = (outTuple[1][i], outTuple[1][i + 1])
			PEI_instance.merge(t_new, tuple2weight, tuple2weight)
		outBuffer.append(outTuple)

## Sorts the input relations in ascending order of weight
def sort_relations(relation2tuple, tuple2weight, l):
	## Utility function for sorting
	def sorting_criterion(e):
	  return tuple2weight[e]

	relations = []
	for relationNo in range(l):
		r = list(relation2tuple["R" + str(relationNo)])
		r.sort(key = sorting_criterion)
		relations.append(r)
	return relations

## Inserts a new tuple (leftVal, rightVal) to the hash tables of relation Ri
def update_hash_tables((leftVal, rightVal), hashTables, i, l):
	if i != 0: 
		leftHashTable = hashTables["R" + str(i) + "left"]
		leftHashTable[leftVal].append((leftVal, rightVal))
	if i != l - 1: 
		rightHashTable = hashTables["R" + str(i) + "right"]
		rightHashTable[rightVal].append((leftVal, rightVal))
	return hashTables

## Given a set of partial join results, we expand them using relation j from the left
## The new relation is joined from the left, so the leftmost attribute of the partial result is joined with the right attribute of Rj
def expand_left(partialResults, j, hashTables, tuple2weight):
	hashTable = hashTables["R" + str(j) + "right"]
	newPartialResults = []
	while partialResults:
		(partial_weight, partial_join) = partialResults.pop()
		right = partial_join[0]
		for joinable_tuple in hashTable[right]:
			(left1, right1) = joinable_tuple
			newPartialResults.append((partial_weight + tuple2weight[joinable_tuple], [left1] + partial_join))
	if j > 0: 
		return expand_left(newPartialResults, j - 1, hashTables, tuple2weight)
	else:
		return newPartialResults

## Given a set of partial join results, we expand them using relation j from the right
## The new relation is joined from the right, so the rightmost attribute of the partial result is joined with the left attribute of Rj
def expand_right(partialResults, j, hashTables, tuple2weight, l):
	hashTable = hashTables["R" + str(j) + "left"]
	newPartialResults = []
	while partialResults:
		(partial_weight, partial_join) = partialResults.pop()
		left = partial_join[-1]
		for joinable_tuple in hashTable[left]:
			(left1, right1) = joinable_tuple
			newPartialResults.append((partial_weight + tuple2weight[joinable_tuple], partial_join + [right1]))
	if j < l - 1: 
		return expand_right(newPartialResults, j + 1, hashTables, tuple2weight, l)
	else:
		return newPartialResults

## Heuristically determines the next relation to fetch a tuple from
def next_relation(l, top, bottom, relations, frontier):
	## The virtual score of relation i is top[0]+top[1]+...+bot[i]+...+top[l-2]+top[l-1]
	sum_of_top = sum(top)
	vscore_list = []
	for i in range(l):
		## For each relation Ri, compute its virtual score by substracting top and adding bottom
		if frontier[i] < len(relations[i]) - 1:
			## For each relation Ri, compute its virtual score by substracting top and adding bottom
			virtual_score = sum_of_top - top[i] + bottom[i]
			vscore_list.append((virtual_score, i))
	## Corner case: all relations have been fully explored
	if vscore_list == []:
		return -1
	## Select the relation with the minimum virtual score from the ones in the list
	(min_vscore, min_relationNo) = min(vscore_list, key = operator.itemgetter(0))
	return min_relationNo

def update_threshold(l, top, bottom):
	## T = min{bot[0]+top[1]+...+top[l-1], top[0]+bot[1]+...+top[l-1], top[0]+top[1]+...+bot[l-1]}
	## Avoid l^2 computation
	sum_of_top = sum(top)
	vscore_list = []
	for i in range(l):
		## For each relation Ri, compute its virtual score by substracting top and adding bottom
		virtual_score = sum_of_top - top[i] + bottom[i]
		vscore_list.append(virtual_score)
	## Return the minimum virtual score
	return min(vscore_list)

def hrjn_main(relation2tuple, tuple2weight, k, l, data_struct, bound, verify = False):
	## First sort relations by weight
	relations = sort_relations(relation2tuple, tuple2weight, l)
	'''
	print "Sorted Relations:"
	for i in range(l):
		print "Relation " + str(i)
		r = relations[i]
		for entry in r:
			print str(entry) + "   weight=" + str(tuple2weight[entry]) 
	'''

	## Initialize data structures
	## 1. Priority queue for results, when a join result exceeds the threshold it is moved to the outBuffer
	## Results are in the form of (weight, list) where list is a list of values from R0 to R(l-1)
	if bound:
		joinResults = priority_queue.initialize_priority_queue(data_struct, k)
	else:
		joinResults = priority_queue.initialize_priority_queue(data_struct, None)
	outBuffer = []

	## 2. Hash tables
	## For each middle relation, both attributes serve as keys so we create 2 hash tables
	## The first relation R(0) only needs a right hash table and the last relation R(l-1) only needs a left one
	hashTables = {}
	for relationNo in range(l):
		r = relations[relationNo]
		## Build hash table for left attribute value
		if relationNo != 0: 
			hashTables["R" + str(relationNo) + "left"] = defaultdict(list)
		## Build hash table for right attribute value
		if relationNo != l - 1: 
			hashTables["R" + str(relationNo) + "right"] = defaultdict(list)

	## 3. Indexes to store frontier of explored relations
	## e.g. if frontier[2]=3, we have already explored 4 tuples from R2
	frontier = []
	for relationNo in range(l):
		frontier.append(-1)

	## 4. Top and bottom values for computing threshold
	## e.g. if top[2]=3 and bottom[2]=100, the top tuple from R2 has weight 3 and the last explored from R2 (at index frontier[2]) has weight 100
	top = []
	bottom = []
	for relationNo in range(l):
		top.append(-1)
		bottom.append(-1)
	threshold = 0

	#iterations = 0
	while True:
		#iterations += 1
		#print "=============  Iteration " + str(iterations) + "  =============="

		## Decide the relation Ri to fetch a tuple from
		i = next_relation(l, top, bottom, relations, frontier)
		#print "Fetching tuple from relation " + str(i)

		## If i is returned as -1, then we have depleted all tuples from all relations - all join results have been produced
		## Either k is very high or our threshold is very loose
		## Ignore the threshold and output the results that have been computed
		if i == -1: 
			#print "\n==[All join combinations have been produced]=="
			move_to_out(joinResults, outBuffer, float('inf'), k, tuple2weight, l)   
			break
		r = relations[i]

		## Fetch the next tuple from the frontier of Ri
		frontier[i] += 1
		tup = r[frontier[i]]
		#print "Frontier = " + str(frontier)

		## Update top, bottom and threshold
		if frontier[i] == 0: top[i] = tuple2weight[tup]
		bottom[i] = tuple2weight[tup]
		threshold = update_threshold(l, top, bottom)
		#print "Threshold = " + str(threshold)

		## Update the hash tables of Ri
		hashTables = update_hash_tables(tup, hashTables, i, l)

		## Compute the join results that can be produced with the current tuple and all the other ones seen so far
		(leftVal, rightVal) = tup
		newResults = [(tuple2weight[tup], [leftVal, rightVal])]
		## Join from preceding relations
		if i != 0:
			newResults = expand_left(newResults, i - 1, hashTables, tuple2weight)
		## Join from following relations
		if i != l - 1:
			newResults = expand_right(newResults, i + 1, hashTables, tuple2weight, l)
		## Insert the new results to the priority queue
		#print "New results produced: " + str(newResults)
		add_results(newResults, joinResults)

		## Move join results to the output buffer and check for termination
		move_to_out(joinResults, outBuffer, threshold, k, tuple2weight, l)
		if len(outBuffer) == k:
			break

	#print "Size of pq: " + str(len(joinResults))

	## The top-k results are now contained in outBuffer
	if not verify:
		return outBuffer
	else:
		## Perform checks
		## TEST1: Verify that the output is sorted
		w = -1
		for (next_w, _) in outBuffer:
			if (next_w < w): print "Error: Output is not sorted"
			w = next_w

		## TEST2: Compare the result with naive full enumeration by NLJ
		fe_output = []
		for (l0, r0) in relation2tuple["R0"]:
			fe_output.append((tuple2weight[(l0, r0)], [l0, r0]))

		def expand_naive_fe(partialResults, j, relation2tuple, tuple2weight, l):
			r = relation2tuple["R" + str(j)]
			newPartialResults = []
			for (partial_weight, tup1) in partialResults:
				for tup2 in r:
					leftVal = tup1[-1]
					rightVal = tup2[0]
					if leftVal == rightVal:
						newPartialResults.append((partial_weight + tuple2weight[tup2], tup1 + [tup2[1]]))
			if j != l - 1:
				return expand_naive_fe(newPartialResults, j + 1, relation2tuple, tuple2weight, l)
			else:
				return newPartialResults

		fe_output = expand_naive_fe(fe_output, 1, relation2tuple, tuple2weight, l)
		sorted_fe_output = sorted(fe_output, key=lambda x: x[0])
		fe_topk = sorted_fe_output[:k]
		print "--Topk results by naive full enumeration--"
		print fe_topk
		for i in range(len(fe_topk)):
			(_, tup1) = outBuffer[i]
			(_, tup2) = fe_topk[i]
			if (tup1 != tup2):
				print "Warning: Naive full enumeration produced different results for the top-k!"
				break

		## TEST3: Verify the hash tables we constructed earlier
		fe_output2 = []
		for (l0, r0) in relation2tuple["R0"]:
			fe_output2.append((tuple2weight[(l0, r0)], [l0, r0]))
		fe_output2 = expand_right(fe_output2, 1, hashTables, tuple2weight, l)
		sorted_fe_output2 = sorted(fe_output2, key=lambda x: x[0])
		fe_topk2 = sorted_fe_output2[:k]
		print "\n--Topk results by enumeration with constructed hash tables--"
		print fe_topk2
		for i in range(len(fe_topk)):
			(_, tup1) = outBuffer[i]
			(_, tup2) = fe_topk2[i]
			if (tup1 != tup2):
				print "Warning: Enumeration with constructed hash tables produced different results for the top-k!"
				break
		print ""
		## End of tests
		return outBuffer



if __name__ == "__main__":
	## Parse the command line
	import argparse
	import DataGenerator

	parser = argparse.ArgumentParser(description='Implementation of a generalized HRJN* operator for path queries')

	parser.add_argument('-b', action="store_true", dest="bound", default=False, help="Bound the size of the data structure holding the results in ranked order")
	parser.add_argument('-ds', action="store", dest="data_struct", default="Heap", help="Data structure to jold ranked results")
	parser.add_argument('-k', action="store", dest="k", default=1, type=int, help="Number of top results to produce")
	parser.add_argument('-n', action="store", dest="n", default=5, type=int, help="Maximum cardinality of relations")
	parser.add_argument('-l', action="store", dest="length", default=4, type=int, help="Length of Path or Cycle")
	parser.add_argument('-d', action="store", dest="DensityOfEdges", choices={"Full", "Random"}, default="Full", help="\"Full\"=Maximum possible cardinality for relations|\"Random\"=Random cardinality for each relation")
	parser.add_argument('-ed', action="store", dest="edgeDistribution", choices={"HardCase", "Random"}, default="Random", help="\"HardCase\"=Fanout:1->max->1->...|\"Random\"=Edges are distributed randomly")
	parser.add_argument('-u', action="store", dest="unionOfDatabases", default=1, type=int, help="By setting this option, the result will be the union of that many sub-databases (Useful for the Hard Case where it will alternate the fanout across databases)")
	parser.add_argument('--c', action="store_true", dest='check', default=False, help="Perform checks to verify result")

	arg_results = parser.parse_args()
	bound = arg_results.bound
	data_struct = arg_results.data_struct
	k = arg_results.k
	n = arg_results.n
	length = arg_results.length
	DensityOfEdges = arg_results.DensityOfEdges
	edgeDistribution = arg_results.edgeDistribution
	databasesNo = arg_results.unionOfDatabases
	check = arg_results.check

	relation2tuple, tuple2weight = DataGenerator.getDatabase("Path", n, length, DensityOfEdges, edgeDistribution, databasesNo)
	result = hrjn_main(relation2tuple, tuple2weight, k, length, data_struct, bound, check)
	print "--Ranked Output--"
	print result

'''
SMALL EXAMPLE

relation2tuple = {}
relation2tuple["R0"] = [(1,2), (5,6), (9,10)]
relation2tuple["R1"] = [(6,7), (10,3), (2,3)]
relation2tuple["R2"] = [(7,8), (3,11), (3,4)]

tuple2weight = {}
tuple2weight[(1,2)] = 1.0
tuple2weight[(5,6)] = 2.0
tuple2weight[(9,10)] = 3.0
tuple2weight[(6,7)] = 10.0
tuple2weight[(10,3)] = 20.0
tuple2weight[(2,3)] = 30.0
tuple2weight[(7,8)] = 5.0
tuple2weight[(3,11)] = 6.0
tuple2weight[(3,4)] = 7.0
'''