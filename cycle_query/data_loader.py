import os

def findcycle(neighbors, seed):
    seen = {seed}
    Q = [seed]
    while Q:






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







    elif dataset == "Twitter":
        graphfile = os.path.join(dir, dataset + ".csv")
        with open(graphfile) as f:
            lines = f.readlines()
        for line in lines:
            node_fro = int(line.split(',')[0])
            node_to = int(line.split(',')[1])

    else:
        print "what dataset?"

    return relation2tuple, tuple2weight