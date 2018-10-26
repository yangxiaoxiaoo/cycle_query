# this file contains some quick utilities, may require other files' presence
# therefore is not guaranteed to stay usable in time_any

import networkx as nx
import copy
graph = "../../enron_graph.wgt.norm"

class Partial:

    def __init__(self, node):
        self.len = 1
        self.nodes = {node}
        self.frontier = node

    def check_contains(self, node):
        return node in self.nodes

    def append(self, new_node):
        self.len += 1
        self.nodes.add(new_node)
        self.frontier = new_node


#copied from auto_querygen
def load_graph_struct(graphfile):
    node2type = dict()
    with open(graphfile) as f:
        lines = f.readlines()
    del lines[0]

    myList = []
    for line in lines:
        node_fro = int(line.split()[0])
        node_to = int(line.split()[1])
        type_fro = int(line.split()[2].strip('[').strip(']'))
        type_to = int(line.split()[3].strip('[').strip(']'))
        myList.append([node_fro, node_to])
        if node_fro not in node2type:
            node2type[node_fro] = type_fro
        if node_to not in node2type:
            node2type[node_to] = type_to

    g = nx.Graph()
    g.add_edges_from(myList)
    print len(g.nodes())
    return g, node2type

def count_k_cycles_homo(g, node2type, seed, k, type_list):
    #count the amount of k cycles passing seed for asymmetric typelist ending at seed.
    partial_cycles = [Partial(seed)]
    for i in range(k-1):
        print "i = "
        print i
        print "size of partial cycles"
        print len(partial_cycles)
        new_list = []
        # expand the partial cycles for k-1 times, then delete those with non-seed fronter
        for pc in partial_cycles:
            neibors = g.neighbors(pc.frontier)
            #add type filter here
            for nei in neibors:
                if node2type[nei] == type_list[i]:
                    new_pc = copy.deepcopy(pc)
                    new_pc.append(nei)
                    new_list.append(new_pc)
        partial_cycles = new_list
    #check if the past frontier is seed:
    count = 0
    for pc in partial_cycles:
        if pc.frontier in g.neighbors(seed):
            count += 1
    return count



def count_k_cycles_iso(g, node2type, seed, k, type_list):
    #count the amount of k simple cycles iso, not highly optimized
    partial_cycles = [Partial(seed)]
    for i in range(k - 1):
        print "i = "
        print i
        print "size of partial cycles"
        print len(partial_cycles)
        new_list = []
        # expand the partial cycles for k-1 times, then delete those with non-seed fronter
        for pc in partial_cycles:
            neibors = g.neighbors(pc.frontier)
            # add type filter here
            for nei in neibors:
                if node2type[nei] == type_list[i] and (nei not in pc.nodes):
                    new_pc = copy.deepcopy(pc)
                    new_pc.append(nei)
                    new_list.append(new_pc)
        partial_cycles = new_list
    # check if the past frontier is seed:
    count = 0
    for pc in partial_cycles:
        if pc.frontier in g.neighbors(seed):
            count += 1
    return count


g, dictype = load_graph_struct(graph)
print len(dictype)

count =  count_k_cycles_homo(g, dictype, 10388, 4,  [1, 2, 3, 2])
print "homo count is "
print count

count =  count_k_cycles_iso(g, dictype, 10388, 4,  [1, 2, 3, 2])
print "iso count is "
print count