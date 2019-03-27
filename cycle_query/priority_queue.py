#!/usr/bin/env python

## Implementation of a priority queue which holds items of the tuple form (weight, _)
## Its size can be bound during initialization
## In that case, whenever the min item is popped, the maximum allowed size is reduced by one
## Currently supported data structures:
##		- Heap
##		- Btree
##		- Treap
##		- Fibonacci Heap

import abc
import heapq
#import treap
import blist
import fib_heap
#import pairing_heap
import sys

def initialize_priority_queue(PQmode, bound = None, initialize_with = []):
    if PQmode == "Heap": return priority_queue_heap(bound, initialize_with)
    elif PQmode == "Btree": return priority_queue_btree(bound, initialize_with)
    elif PQmode == "Treap": return priority_queue_treap(bound, initialize_with)
    elif PQmode == "FibHeap": return priority_queue_FibHeap(bound, initialize_with)
    elif PQmode == "PairHeap": return priority_queue_PairHeap(bound, initialize_with)
    else:
        print "PQ data structure not supported!"
        sys.exit(1)        


class priority_queue_abstract():
	__metaclass__ = abc.ABCMeta
 
	def __init__(self, size, initialize_with):
		self.max_size = size
		self.curr_size = 0
	
	## Returns the minimum weight of all items stored
	@abc.abstractmethod
	def min_weight(self):
		pass

	## Returns an item of minimum weight without removing it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	@abc.abstractmethod
	def peek_min(self, minWeight = None):
		pass

	## Removes an item of minimum weight from the list and returns it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	@abc.abstractmethod
	def pop_min(self, minWeight = None):
		pass

	## Adds an item to the priority queue
	## If the list is initialized as bounded, then the item is only stored if its weight is less than the maximum one stored
	@abc.abstractmethod
	def add(self, item):
		pass

	## Returns the number of items stored
	def size(self):
		return self.curr_size

	## Decreases the maximum allowed number of items by one
	## Works only if initialized with a maximum size
	def decrease_max_size(self):
		if (self.max_size is not None):
			self.max_size -= 1

class priority_queue_heap(priority_queue_abstract):

	def __init__(self, size, initialize_with):
		super(priority_queue_heap, self).__init__(size, initialize_with)
		if initialize_with == []:
			self.l = []
		else:
			self.l = initialize_with
			heapq.heapify(self.l)

	## Returns the minimum weight of all items stored
	def min_weight(self):
		return self.l[0][0]

	## Returns an item of minimum weight without removing it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def peek_min(self, minWeight = None):
		return self.l[0]

	## Removes an item of minimum weight from the list and returns it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def pop_min(self, minWeight = None):
		tup = heapq.heappop(self.l)
		self.curr_size -= 1
		return tup

	## Adds an item to the priority queue
	## If the list is initialized as bounded, then the item is only stored if its weight is less than the maximum one stored
	def add(self, item):
		if (self.max_size is None or self.curr_size < self.max_size):
			## Simply add in this case
			heapq.heappush(self.l, item)
			self.curr_size += 1
		elif (self.curr_size != 0):
			## Add only if its weight is less than the maximum of the list, in which case it discards one of the max items
			## Find index of max
			idx = max(range(len(self.l)), key = self.l.__getitem__)
			## If the item in this index is worse than the new one, swap them
			if self.l[idx][0] > item[0]:
				self.l[idx] = item
				heapq.heapify(self.l)


class priority_queue_FibHeap(priority_queue_abstract):

	def __init__(self, size, initialize_with):
		if size != None:
			print "Bounded Fibonacci Heap currently unsupported!"
			sys.exit(1)
		super(priority_queue_FibHeap, self).__init__(size, initialize_with)
		self.l = fib_heap.FibonacciHeap()
		for item in initialize_with:
			self.add(item)

	## Returns the minimum weight of all items stored
	def min_weight(self):
		return self.l.find_min().key

	## Returns an item of minimum weight without removing it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def peek_min(self, minWeight = None):
		minNode = self.l.find_min()
		tup = (minNode.key, minNode.value)
		return tup
		
	## Removes an item of minimum weight from the list and returns it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def pop_min(self, minWeight = None):
		minNode = self.l.extract_min()
		tup = (minNode.key, minNode.value)
		self.curr_size -= 1
		return tup

	## Adds an item to the priority queue
	## If the list is initialized as bounded, then the item is only stored if its weight is less than the maximum one stored
	def add(self, item):
		(weight, value) = item
		self.l.insert(weight, value)
		self.curr_size += 1

class priority_queue_PairHeap(priority_queue_abstract):

	def __init__(self, size, initialize_with):
		if size != None:
			print "Bounded Pairing Heap currently unsupported!"
			sys.exit(1)
		super(priority_queue_PairHeap, self).__init__(size, initialize_with)
		self.l = pairing_heap.Heap()
		for item in initialize_with:
			self.add(item)

	## Returns the minimum weight of all items stored
	def min_weight(self):
		return self.l.top[0]

	## Returns an item of minimum weight without removing it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def peek_min(self, minWeight = None):
		return self.l.top
		
	## Removes an item of minimum weight from the list and returns it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def pop_min(self, minWeight = None):
		return self.l.pop()

	## Adds an item to the priority queue
	## If the list is initialized as bounded, then the item is only stored if its weight is less than the maximum one stored
	def add(self, item):
		self.l.push(item)
		self.curr_size += 1


class priority_queue_btree(priority_queue_abstract):
	
	def __init__(self, size, initialize_with):
		super(priority_queue_btree, self).__init__(size, initialize_with)
		self.l = blist.sortedlist([], key = lambda x: x[0])
		for item in initialize_with:
			self.add(item)

	## Returns the minimum weight of all items stored
	def min_weight(self):
		return self.l[0][0]

	## Returns an item of minimum weight without removing it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def peek_min(self, minWeight = None):
		return self.l[0]

	## Removes an item of minimum weight from the list and returns it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def pop_min(self, minWeight = None):
		tup = self.l.pop(0)
		self.curr_size -= 1
		return tup

	## Adds an item to the priority queue list
	## If the list is initialized as bounded, then the item is only stored if its weight is less than the maximum one stored
	def add(self, item):
		if (self.max_size is None or self.curr_size < self.max_size):
			## Simply add in this case
			self.l.add(item)
			self.curr_size += 1
		elif (self.curr_size != 0):
			## Add only if its weight is less than the maximum of the list, in which case it discards one of the max items
			maxWeight = self.l[-1][0]
			if maxWeight > item[0]:
				self.l.pop()
				self.l.add(item)
		

class priority_queue_treap(priority_queue_abstract):
	
	def __init__(self, size, initialize_with):
		super(priority_queue_treap, self).__init__(size, initialize_with)
		self.l = treap.treap()
		for item in initialize_with:
			self.add(item)

	## Returns the minimum weight of all items stored
	def min_weight(self):
		return self.l.find_min()

	## Returns an item of minimum weight without removing it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def peek_min(self, minWeight = None):
		if minWeight is None: 
			key = self.l.find_min()
		else: 
			key = minWeight
		listOfTuples = self.l[key]
		tup = listOfTuples[0]
		return tup

	## Removes an item of minimum weight from the list and returns it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def pop_min(self, minWeight = None):
		if minWeight is None: 
			key = self.l.find_min()
		else: 
			key = minWeight
		listOfTuples = self.l[key]
		tup = listOfTuples.pop()
		if listOfTuples == []:
			self.l.remove(key)	
		self.curr_size -= 1
		return tup

	## Adds an item to the priority queue list
	## If the list is initialized as bounded, then the item is only stored if its weight is less than the maximum one stored
	def add(self, item):
		if (self.max_size is None or self.curr_size < self.max_size):
			## Simply add in this case
			if item[0] in self.l:
				self.l[item[0]].append(item)
			else:
				self.l[item[0]] = [item]
			self.curr_size += 1
		elif (self.curr_size != 0):
			## Add only if its weight is less than the maximum of the list, in which case it discards one of the max items
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