import os
import cPickle as pickle
import random

def load(dir, dataset):
	relation2tuple = dict()
	tuple2weight = dict()

	if dataset in ["Yelp", "Flickr", "Enron", "DBLP"]:
		graphfile = os.path.join(dir, dataset)
		with open(graphfile) as f:
			lines = f.readlines()
		del lines[0]

		relationTypes = set()
		type2tuples = dict()


		for line in lines:
			node_fro = int(line.split()[0])
			node_to = int(line.split()[1])
			type_fro = int(line.split()[2].strip('[').strip(']'))
			type_to = int(line.split()[3].strip('[').strip(']'))
			wgt = float(line.split()[5])

			type = (type_fro, type_to)
			if type not in type2tuples:
				relationTypes.add(type)
				type2tuples[type] = {(node_fro, node_to)}
			else:
				type2tuples[type].add((node_fro, node_to))
			tuple2weight[(node_fro, node_to)] = wgt

		# DFS on set of relations to find path and cycle in schema.
		neighbors = dict()

		seed = 0
		for type in relationTypes:
			if type[0] not in neighbors:
				neighbors[type[0]] = {type[1]}
			else:
				neighbors[type[0]].add(type[1])

			seed = type[0]  # randomly..

		cycle = findcycle(neighbors, seed)







	elif dataset == "Twitter" or dataset == "Twitter_truncated":

		max_id = 1000
		length = 4
		weightrange = 100.0
		list_of_tuples = []

		## Read the file and keep only ids lower than max_id
		graphfile = os.path.join(dir, dataset + ".csv")
		with open(graphfile) as f:
			lines = f.readlines()
		for line in lines:
			node_fro = int(line.split(',')[0])
			node_to = int(line.split(',')[1])
			if node_fro < max_id and node_to < max_id:
				list_of_tuples.append((node_fro, node_to))

		## Use an offset when replicating the same relation to avoid having duplicate tuples
		offset = [0, 0]
		for i in range(length - 1):
			offset.append(i * max_id)   
			offset.append((i + 1) * max_id)     
		offset[-1] = 0  ## to close the cycle

		## Build length relations
		for i in range(length):
			new_relation = set()
			for (usr1, usr2) in list_of_tuples:
				new_tuple = (usr1 + offset[2 * i], usr2 + offset[2 * i + 1])
				new_relation.add(new_tuple)
				tuple2weight[new_tuple] = random.uniform(0, weightrange)
			relation2tuple["R" + str(i)] = new_relation

		# -- Output dictionaries
		outFile1 = open(os.path.join(dir, "Twitter_tuples.pkl"), "wb")
		pickle.dump(relation2tuple, outFile1)
		outFile1.close()

		outFile2 = open(os.path.join(dir, "Twitter_weights.pkl"), "wb")
		pickle.dump(tuple2weight, outFile2)
		outFile2.close()

	else:
		print "what dataset?"

	return relation2tuple, tuple2weight


def truncate_data(dir, dataset, max_id):
		## Read the file and keep only ids lower than max_id
		graphfile = os.path.join(dir, dataset + ".csv")
		f_out = open(os.path.join(dir, dataset + "_truncated.csv"), "w")
		with open(graphfile) as f:
			lines = f.readlines()
		for line in lines:
			node_fro = int(line.split(',')[0])
			node_to = int(line.split(',')[1])
			if node_fro < max_id and node_to < max_id:
				f_out.write(line)
		f_out.close()

if __name__ == "__main__":
	#truncate_data("../Experiment_Twitter/", "Twitter", 10000)
	load("../Experiment_Twitter/", "Twitter_truncated")


'''

'''