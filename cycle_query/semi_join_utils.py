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
    tu2down_neis = dict()
    tu2up_neis = dict()
    print "reduce " + R_start + " according to "+R_end + '...'
    #R_start and R_end are both keys in rel2tuple
    get_first_ele = lambda (x0, x1): x0
    checkset = set((get_first_ele(tup) for tup in rel2tuple[R_end]))
    new_set = set()
    for tup in rel2tuple[R_start]:
        tu2down_neis[tup] = set()
        if tup[1] in checkset:
            new_set.add(tup)
            for tup_down in rel2tuple[R_end]:
                if tup_down[0] == tup[1]:
                #[DESIGN CHOICE]when there are many spurious tuples, this is more efficient than loop earlier
                    tu2down_neis[tup].add(tup_down)
                    if tup_down in tu2up_neis:
                        tu2up_neis[tup_down].add(tup)
                    else:
                        tu2up_neis[tup_down] = {tup}
    rel2tuple[R_start] = new_set
    return tu2down_neis, tu2up_neis

def full_SJ_reduce_4(rel2tuple):
    #contain hard code for 4-cycle and will rewrite later...
    #semi-join reduction for all relations, and return an index from tuple to downstream and upstream neighbors
    #No global consistency: R0 to upstream and R0 to downstream
    tu2down_neis, tu2up_neis = semi_join('R0', 'R1', rel2tuple)
    tu2down_neis1, tu2up_neis1 = semi_join('R1', 'R2', rel2tuple)
    tu2up_neis.update(tu2up_neis1)
    tu2down_neis.update(tu2down_neis1)
    tu2down_neis1, tu2up_neis1 = semi_join('R2', 'R3', rel2tuple)
    tu2up_neis.update(tu2up_neis1)
    tu2down_neis.update(tu2down_neis1)
    tu2down_neis1, tu2up_neis1 = semi_join('R3', 'R0', rel2tuple)
    print tu2down_neis1
    tu2up_neis.update(tu2up_neis1)
    tu2down_neis.update(tu2down_neis1)

    print tu2down_neis
    return tu2down_neis, tu2up_neis
    #[DESIGN CHOICE]Q: shall we omit this and record a hash to max item only?
    #[DESIGN CHOICE]A: No since we will need the hash to neighbors anyway later to expend PEI


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

def huristic_build_4(tuple2weight, rel2tuple, tu2down_neis):
    #build a dictionary from (tuple, breakpoint) down to the remaining weight not including tuple
    #assumption: no tuple appear in different relations
    #later should change it into a while loop for any n...
    tuple2rem = dict()
    breakpoints = set()
    for tu in rel2tuple['R3']:
        breakpoints.add(tu[1]) #a set of all break variables for later loop over

    #a = R3[1], compared later when starting from R0[0]
    for tu in rel2tuple['R2']:
        for tu_down in tu2down_neis[tu]:
            new_val = tuple2weight[tu_down]
            if (tu, tu_down[1]) in tuple2rem:
                tuple2rem[(tu, tu_down[1])] = max(tuple2rem[(tu, tu_down[1])], new_val)
            else:
                tuple2rem[(tu, tu_down[1])] = new_val
    for tu in rel2tuple['R1']:
        for tu_down in tu2down_neis[tu]:
            new_val = tuple2weight[tu_down]
            for bp in breakpoints:
                if (tu, bp) in tuple2rem:
                    tuple2rem[(tu, bp)] = max(tuple2rem[(tu, bp)], tuple2rem[(tu_down, bp)] + new_val)
                    #the same breakpoint
                else:
                    tuple2rem[(tu, bp)] = tuple2rem[(tu_down, bp)] + new_val
    for tu in rel2tuple['R0']:
        for tu_down in tu2down_neis[tu]:
            new_val = tuple2weight[tu_down]
            for bp in breakpoints:
                if (tu, bp) in tuple2rem:
                    tuple2rem[(tu, bp)] = max(tuple2rem[(tu, bp)], tuple2rem[(tu_down, bp)] + new_val)
                    # the same breakpoint
                else:
                    tuple2rem[(tu, bp)] = tuple2rem[(tu_down, bp)] + new_val
    print "(tuple, breakpoint) to remaining heuristic value mapping:"
    print tuple2rem
    return tuple2rem



#TODO: def priority_search(k):
    #push PEIs into a priority queue, pop k heaviest full items




degrees = [1, 1, 3, 1]
n = sum(degrees)
var2cand = build_data(4, degrees)
min_relations, tuple2weight = build_relation(4, var2cand, weightrange=10)
min_relations['R1'].add((1, 10)) #adding a spurious tuple
print "size before semi join reduction: "+str(len(min_relations['R1']))
tu2down_neis0, tu2up_neis0 = semi_join('R1', 'R2', min_relations)
print "size after semi join reduction: "+str(len(min_relations['R1']))
print heavy_map(min_relations)
print "test message again"

tu2down_neis, tu2up_neis = full_SJ_reduce_4(min_relations)
tuple2rem = huristic_build_4(tuple2weight, min_relations, tu2down_neis)
