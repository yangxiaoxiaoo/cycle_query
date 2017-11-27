#demo implementation for cyclic queries
#utilities functions
import math
import random
import heapq
import globalclass

def build_data(cyc_len, d):
    #a hard coded function to create t-cycles, each relations is a tuple of two variables
    #each has a cardinality of d[i]

    var2cand = dict() #mapping from variable to its candidates
    max_node = 0
    for variable in range(cyc_len):
        var2cand[variable] = set()
        for i in range(max_node, max_node + d[variable]):
            var2cand[variable].add(i)
        max_node = max_node + d[variable]
    return var2cand

def build_relation(cyc_len, var2cand, weightrange):
    #build non-redundent relations based on the candidates, and randomly assign a weight to them
    #weight is uniformly distributed in (0, weightrange)--can do other distributions later too.
    #there can be multiple ways. I'm doing all to all dense connection now.
    rel2tuple = dict()
    tuple2weight = dict()
    for variable in range(cyc_len - 1):
        key = "R"+str(variable)
        rel2tuple[key] = set()
        for tuple0 in var2cand[variable]:
            for tuple1 in var2cand[variable + 1]:
                #all pair add. Can do other stratergies...
                rel2tuple[key].add((tuple0, tuple1))
                tuple2weight[(tuple0, tuple1)] = random.uniform(0, weightrange)
                print key + ": adding tuple" + str([tuple0, tuple1])
        key = "R" + str(cyc_len - 1)
        rel2tuple[key] = set()
        for tuple0 in var2cand[cyc_len - 1]:
            for tuple1 in var2cand[0]:
                # all pair add. Can do other stratergies...
                rel2tuple[key].add((tuple0, tuple1))
                tuple2weight[(tuple0, tuple1)] = random.uniform(0, weightrange)
                print key + ": adding tuple" + str([tuple0, tuple1])
    return rel2tuple, tuple2weight

def semi_join(R_start, R_end, rel2tuple):
    print "reduce " + R_start + " according to "+R_end + '...'
    #R_start and R_end are both keys in rel2tuple
    get_first_ele = lambda (x0, x1): x0
    checkset = set((get_first_ele(tup) for tup in rel2tuple[R_end]))
    new_set = set()
    for tup in rel2tuple[R_start]:
        if tup[1] in checkset:
            new_set.add(tup)
    rel2tuple[R_start] = new_set

def heavy_map(rel2tuple):
    #take a tuple candidate map, return a map to boolean values indicating each relation is heavy or not
    n = 0
    result = dict()
    for k, v in rel2tuple.iteritems():
        n += len(v)
    for k, v in rel2tuple.iteritems():
        if len(v) < math.sqrt(n):
            result[k] = False
        else:
            result[k] = True
    return result

#def priority_search():



degrees = [1, 1, 3, 1]
n = sum(degrees)
var2cand = build_data(4, degrees)
min_relations, tuple2weight = build_relation(4, var2cand, weightrange=10)
min_relations['R1'].add((1, 10)) #adding a spurious tuple
print "size before semi join reduction: "+str(len(min_relations['R1']))
semi_join('R1', 'R2', min_relations)
print "size after semi join reduction: "+str(len(min_relations['R1']))
print heavy_map(min_relations)
print "test message again"
