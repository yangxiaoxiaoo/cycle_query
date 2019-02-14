import os

def load(dir, dataset):
    relation2tuple = dict()
    tuple2weight = dict()

    if dataset in ["Yelp", "Flickr", "Enron", "DBLP"]:
        graphfile = os.path.join(dir, dataset)
        with open(graphfile) as f:
            lines = f.readlines()
        del lines[0]

        for line in lines:
            node_fro = int(line.split()[0])
            node_to = int(line.split()[1])
            type_fro = int(line.split()[2].strip('[').strip(']'))
            type_to = int(line.split()[3].strip('[').strip(']'))
            wgt = float(line.split()[5])





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