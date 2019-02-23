#!/usr/bin/env python

## Implementation of a ranked list which holds items of the form (weight, _)
## Its size can be bound during initialization
## In that case, whenever the min item is popped, the maximum allowed size is reduced by one
## Currently supported data structures:
##		- Prioritry Queue
##		- Btree
##		- Treap

import heapq
import treap
import blist

class ranked_list:
	def __init__(self, data_struct, size = None):
		self.data_struct = data_struct
		self.max_size = size
		self.curr_size = 0
		if (data_struct == "pq"):
			self.l = []
		elif (data_struct == "btree"): 
			self.l = blist.sortedlist([], key = lambda x: x[0])
		elif (data_struct == "treap"):
			self.l = treap.treap()
		else:
			print "Data structure not supported"
			sys.exit(1)

	## Returns the minimum weight of all items stored
	def min_weight(self):
		if (self.data_struct == "pq"): 
			return self.l[0][0]
		elif (self.data_struct == "btree"): 
			return self.l[0][0]
		elif (self.data_struct == "treap"): 
			return self.l.find_min()

	## Removes an item of minimum weight from the list and returns it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def pop_min(self, minWeight = None):
		if (self.data_struct == "pq"): 
			tup = heapq.heappop(self.l)
		elif (self.data_struct == "btree"): 
			tup = self.l.pop(0)
		elif (self.data_struct == "treap"): 
			if minWeight == None: 
				key = self.l.find_min()
			else: 
				key = minWeight
			listOfTuples = self.l[key]
			tup = listOfTuples.pop()
			if listOfTuples == []:
				self.l.remove(key)	

		self.curr_size -= 1
		if (self.max_size != None):
			self.max_size -= 1
		return tup	

	## Adds an item to the ranked list
	## If the list is initialized as bounded, then the item is only stored if its weight is less than the maximum one stored
	def add(self, item):
		if (self.max_size == None or self.curr_size < self.max_size):
			## Simply add in this case
			if (self.data_struct == "pq"): 
				heapq.heappush(self.l, item)
			elif (self.data_struct == "btree"): 
				self.l.add(item)
			elif (self.data_struct == "treap"): 
				if item[0] in self.l:
					self.l[item[0]].append(item)
				else:
					self.l[item[0]] = [item]
			self.curr_size += 1
		else:
			## Add only if its weight is less than the maximum of the list, in which case it discards one of the max items
			if (self.data_struct == "pq"): 
				## Find index of max
				idx = max(range(len(self.l)), key = self.l.__getitem__)
				## If the item in this index is worse than the new one, swap them
				if self.l[idx][0] > item[0]:
					self.l[idx] = item
					heapq.heapify(self.l)
			elif (self.data_struct == "btree"): 
				maxWeight = self.l[-1][0]
				if maxWeight > item[0]:
					self.l.pop()
					self.l.add(item)
			elif (self.data_struct == "treap"): 
				maxWeight = self.l.find_max()
				## If the tuples with the max weight are worse than the new one, swap one of them with it
				if maxWeight > item[0]:
					## Remove
					listOfTuples = self.l[maxWeight]
					listOfTuples.pop()
					if listOfTuples == []:
						self.l.remove(maxWeight)
					## Add
					if item[0] in self.l:
						self.l[item[0]].append(item)
					else:
						self.l[item[0]] = [item]					

	## Returns the number of items stored
	def size(self):
		return self.curr_size
