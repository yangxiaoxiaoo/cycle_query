#!/usr/bin/env python

## Implementation of a ranked list which holds items of the tuple form (weight, _)
## Its size can be bound during initialization
## In that case, whenever the min item is popped, the maximum allowed size is reduced by one
## Currently supported data structures:
##		- Prioritry Queue
##		- Btree
##		- Treap

import abc
import heapq
import treap
import blist

class ranked_list_abstract():
	__metaclass__ = abc.ABCMeta
 
	def __init__(self, size = None):
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

	## Adds an item to the ranked list
	## If the list is initialized as bounded, then the item is only stored if its weight is less than the maximum one stored
	@abc.abstractmethod
	def add(self, item):
		pass

	## Returns the number of items stored
	def size(self):
		return self.curr_size

class ranked_list_pq(ranked_list_abstract):

	def __init__(self, size = None):
		super(ranked_list_pq, self).__init__(size)
		self.l = []

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
		if (self.max_size != None):
			self.max_size -= 1
		return tup

	## Adds an item to the ranked list
	## If the list is initialized as bounded, then the item is only stored if its weight is less than the maximum one stored
	def add(self, item):
		if (self.max_size == None or self.curr_size < self.max_size):
			## Simply add in this case
			heapq.heappush(self.l, item)
			self.curr_size += 1
		else:
			## Add only if its weight is less than the maximum of the list, in which case it discards one of the max items
			## Find index of max
			idx = max(range(len(self.l)), key = self.l.__getitem__)
			## If the item in this index is worse than the new one, swap them
			if self.l[idx][0] > item[0]:
				self.l[idx] = item
				heapq.heapify(self.l)


class ranked_list_btree(ranked_list_abstract):
	
	def __init__(self, size = None):
		super(ranked_list_btree, self).__init__(size)
		self.l = blist.sortedlist([], key = lambda x: x[0])

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
		if (self.max_size != None):
			self.max_size -= 1
		return tup

	## Adds an item to the ranked list
	## If the list is initialized as bounded, then the item is only stored if its weight is less than the maximum one stored
	def add(self, item):
		if (self.max_size == None or self.curr_size < self.max_size):
			## Simply add in this case
			self.l.add(item)
			self.curr_size += 1
		else:
			## Add only if its weight is less than the maximum of the list, in which case it discards one of the max items
			maxWeight = self.l[-1][0]
			if maxWeight > item[0]:
				self.l.pop()
				self.l.add(item)
		
class ranked_list_treap(ranked_list_abstract):
	
	def __init__(self, size = None):
		super(ranked_list_treap, self).__init__(size)
		self.l = treap.treap()

	## Returns the minimum weight of all items stored
	def min_weight(self):
		return self.l.find_min()

	## Returns an item of minimum weight without removing it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def peek_min(self, minWeight = None):
		if minWeight == None: 
			key = self.l.find_min()
		else: 
			key = minWeight
		listOfTuples = self.l[key]
		tup = listOfTuples[0]
		return tup

	## Removes an item of minimum weight from the list and returns it
	## If the minimum weight in the queue is known, it can be passed as an argument for better performance
	def pop_min(self, minWeight = None):
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
			if item[0] in self.l:
				self.l[item[0]].append(item)
			else:
				self.l[item[0]] = [item]
			self.curr_size += 1
		else:
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