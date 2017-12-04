# demo implementation for cyclic queries
# utilities functions
import math
import random
import heapq
import globalclass
import copy
import time


def build_data(cyc_len, d):
    # a hard coded function to create t-cycles, each relations is a tuple of two variables
    # each has a cardinality of d[i]

    var2cand = dict() # mapping from variable to its candidates
    max_node = 0
    for variable in range(cyc_len):
        var2cand[variable] = set()
        for i in range(max_node, max_node + d[variable]):
            var2cand[variable].add(i)
        max_node = max_node + d[variable]
    return var2cand


def build_relation(cyc_len, var2cand, weightrange):
    # build non-redundant relations based on the candidates, and randomly assign a weight to them
    # weight is uniformly distributed in (0, weight_range)--can do other distributions later too.
    # there can be multiple ways. I'm doing all to all dense connection now.
    rel2tuple = dict()
    tuple2weight = dict()
    for variable in range(cyc_len - 1):
        key = "R"+str(variable)
        rel2tuple[key] = set()
        for tuple0 in var2cand[variable]:
            for tuple1 in var2cand[variable + 1]:
                # all pair add. Can do other strategies...
                rel2tuple[key].add((tuple0, tuple1))
                tuple2weight[(tuple0, tuple1)] = random.uniform(0, weightrange)
                print key + ": adding tuple" + str([tuple0, tuple1])
        key = "R" + str(cyc_len - 1)
        rel2tuple[key] = set()
        for tuple0 in var2cand[cyc_len - 1]:
            for tuple1 in var2cand[0]:
                # all pair add. Can do other strategies...
                rel2tuple[key].add((tuple0, tuple1))
                tuple2weight[(tuple0, tuple1)] = random.uniform(0, weightrange)
                print key + ": adding tuple" + str([tuple0, tuple1])
    return rel2tuple, tuple2weight


def semi_join(R_start, R_end, rel2tuple):
    tu2down_neis = dict()
    tu2up_neis = dict()
    print "reduce " + R_start + " according to "+R_end + '...'
    # R_start and R_end are both keys in rel2tuple
    get_first_ele = lambda (x0, x1): x0
    checkset = set((get_first_ele(tup) for tup in rel2tuple[R_end]))
    new_set = set()
    for tup in rel2tuple[R_start]:
        tu2down_neis[tup] = set()
        if tup[1] in checkset:
            new_set.add(tup)
            for tup_down in rel2tuple[R_end]:
                if tup_down[0] == tup[1]:
                    # [DESIGN CHOICE]when there are many spurious tuples, this is more efficient than loop earlier
                    tu2down_neis[tup].add(tup_down)
                    if tup_down in tu2up_neis:
                        tu2up_neis[tup_down].add(tup)
                    else:
                        tu2up_neis[tup_down] = {tup}
    rel2tuple[R_start] = new_set
    return tu2down_neis, tu2up_neis


def full_SJ_reduce_4(rel2tuple):
    # contain hard code for 4-cycle and will rewrite later...
    # semi-join reduction for all relations, and return an index from tuple to downstream and upstream neighbors
    # No global consistency: R0 to upstream and R0 to downstream
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
    # [DESIGN CHOICE]Q: shall we omit this and record a hash to max item only?
    # [DESIGN CHOICE]A: No since we will need the hash to neighbors anyway later to expend PEI


def heavy_map(rel2tuple):
    # take a tuple candidate map, return a map to boolean values indicating each relation is heavy or not
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

def real_heavy_map(tu2down_neis, tu2up_neis):
    #take a tuple to neighbors map(up stream and down stream)
    tu2degree = dict()
    tu2is_heavy = dict()
    for tu in tu2down_neis:
        tu2degree[tu] = len(tu2down_neis[tu]) + len(tu2up_neis[tu])
    n = len(tu2down_neis)
    print "n is"
    print n
    print math.sqrt(n)
    for key, value in tu2degree.iteritems():
        if value < math.sqrt(n):
            tu2is_heavy[key] = False
        else:
            tu2is_heavy[key] = True
            print "heavy value:"
            print value
    print tu2is_heavy
    return tu2is_heavy



def heuristic_build_4(tuple2weight, rel2tuple, tu2down_neis):
    # build a dictionary from (tuple, breakpoint) down to the remaining weight not including tuple
    # assumption: no tuple appear in different relations
    # later should change it into a while loop for any n...
    tuple2rem = dict()
    breakpoints = set()
    for tu in rel2tuple['R3']:
        breakpoints.add(tu[1]) # a set of all break variables for later loop over

    # a = R3[1], compared later when starting from R0[0]
    for tu in rel2tuple['R2']:
        for tu_down in tu2down_neis[tu]:
            new_val = tuple2weight[tu_down]
            if (tu, tu_down[1]) in tuple2rem:
                tuple2rem[(tu, tu_down[1])] = min(tuple2rem[(tu, tu_down[1])], new_val)
            else:
                tuple2rem[(tu, tu_down[1])] = new_val
    for tu in rel2tuple['R1']:
        for tu_down in tu2down_neis[tu]:
            new_val = tuple2weight[tu_down]
            for bp in breakpoints:
                if (tu, bp) in tuple2rem:
                    tuple2rem[(tu, bp)] = min(tuple2rem[(tu, bp)], tuple2rem[(tu_down, bp)] + new_val)
                    # the same breakpoint
                else:
                    tuple2rem[(tu, bp)] = tuple2rem[(tu_down, bp)] + new_val
    for tu in rel2tuple['R0']:
        for tu_down in tu2down_neis[tu]:
            new_val = tuple2weight[tu_down]
            for bp in breakpoints:
                if (tu, bp) in tuple2rem:
                    tuple2rem[(tu, bp)] = min(tuple2rem[(tu, bp)], tuple2rem[(tu_down, bp)] + new_val)
                    # the same breakpoint
                else:
                    tuple2rem[(tu, bp)] = tuple2rem[(tu_down, bp)] + new_val
    print "(tuple, breakpoint) to remaining heuristic value mapping:"
    print tuple2rem
    return tuple2rem


def fake_heuristic_4(tuple2weight, rel2tuple):
    tuple2rem = dict()
    breakpoints = set()
    for tu in rel2tuple['R3']:
        breakpoints.add(tu[1])

    for tu in tuple2weight:
        for bp in breakpoints:
            tuple2rem[(tu, bp)] = 0
    return tuple2rem


def priority_search_4(K, rel2tuple, tuple2weight, tu2down_neis):
    # push PEIs into a priority queue, pop k heaviest full items
    # [DESIGN CHOICE] pop the lightest element as consistent with heapq native
    TOP_K = []
    PQ = []
    tuple2rem = heuristic_build_4(tuple2weight, rel2tuple, tu2down_neis)
    # for fair time measurement sake, tuple2rem should be part of prioritized search.
    for tu in rel2tuple['R0']:
        heapq.heappush(PQ, globalclass.PEI(tu, tuple2weight[tu], tuple2rem[(tu, tu[0])]))
        print "PQpush"
    while len(PQ) != 0:
        # defult: without termination, enumerate till PQ is empty
        cur_PEI = heapq.heappop(PQ)
        if cur_PEI.instance.completion:
            TOP_K.append(cur_PEI)
            if len(TOP_K) == K:
                break
        elif cur_PEI.instance.length != 3: # not completed, there is frontier, no need to check breakpoint
            frontier = cur_PEI.instance.frontier()
            for neighbor in tu2down_neis[frontier]:
                new_PEI = copy.deepcopy(cur_PEI)
                new_PEI.merge(neighbor, tuple2weight, rel2tuple, tuple2rem)
                heapq.heappush(PQ, new_PEI)
                # [DESIGN CHOICE] shall we keep the top 1 unpushed (outside always)?
                # slightly more wordy to implement so I will defer this dicision later
        else:  # length == 3, check breakpoint
            frontier = cur_PEI.instance.frontier()
            for neighbor in tu2down_neis[frontier]:
                if neighbor[1] == cur_PEI.breakpoint:
                    new_PEI = copy.deepcopy(cur_PEI)
                    new_PEI.merge(neighbor, tuple2weight, rel2tuple, tuple2rem)
                    heapq.heappush(PQ, new_PEI)
                    # [DESIGN CHOICE] for more readable logic, no additional break here (extra push in heapQ)

    print "TOP K results are"
    for PEI in TOP_K:
        print PEI.wgt
    assert len(TOP_K) == K or len(PQ) == 0
    return TOP_K


def enumerate_all_4(K, rel2tuple, tuple2weight, tu2down_neis):
    # the enumeration baseline to compare with, implemented by regular join.
    # also return a total count
    TOP_K = []
    Interm_results = []
    fake_tuple2rem = fake_heuristic_4(tuple2weight, rel2tuple)
    for tu in rel2tuple['R0']:
        Interm_results.append(globalclass.PEI(tu, tuple2weight[tu], 0))
        # all instances have 0 heuristics, therefore if there is a comparison is by wgt only.
        # ALSO, Comp is not needed.
    while len(Interm_results) != 0:
        Inter_res = Interm_results.pop()
        frontier = Inter_res.instance.frontier()
        for neighbor in tu2down_neis[frontier]:
            if (Inter_res.instance.length == 3 and neighbor[1] == Inter_res.breakpoint) \
                    or Inter_res.instance.length < 3:
                new_PEI = copy.deepcopy(Inter_res)
                new_PEI.merge(neighbor, tuple2weight, rel2tuple, fake_tuple2rem)
                if new_PEI.instance.completion:
                    TOP_K.append(new_PEI)
                    if len(TOP_K) == K:
                        break
                else:
                    Interm_results.append(new_PEI)

    TOP_K.sort()
    print "TOP K results are"
    for PEI in TOP_K:
        print PEI.wgt
    assert len(TOP_K) == K or len(Interm_results) == 0
    return TOP_K[:K], len(TOP_K)


def test_priority_search():
    # For now, without a heavy/light method, we just always assume R0 is heavy, without loss of generality.
    degrees = [1, 2, 2, 1]
    var2cand = build_data(4, degrees)
    min_relations, tuple2weight = build_relation(4, var2cand, weightrange=10)
    min_relations['R1'].add((1, 10)) # adding a spurious tuple
    print "size before semi join reduction: "+str(len(min_relations['R1']))
    tu2down_neis0, tu2up_neis0 = semi_join('R1', 'R2', min_relations)
    print "size after semi join reduction: "+str(len(min_relations['R1']))
    print heavy_map(min_relations)
    print "test message again"

    tu2down_neis, tu2up_neis = full_SJ_reduce_4(min_relations)
    real_heavy_map(tu2down_neis, tu2up_neis)
    tuple2rem = heuristic_build_4(tuple2weight, min_relations, tu2down_neis)
    TOP_K_PQ = priority_search_4(5, min_relations, tuple2weight, tu2down_neis)
    TOP_K_enu, total = enumerate_all_4(5, min_relations, tuple2weight, tu2down_neis)
    assert TOP_K_enu == TOP_K_PQ


def time_measurements(degrees, K):
    # return a pair of running time of prioritized search and enumerate all
    var2cand = build_data(4, degrees)
    min_relations, tuple2weight = build_relation(4, var2cand, weightrange=10)
    tu2down_neis, tu2up_neis = full_SJ_reduce_4(min_relations)

    start = time.time()
    TOP_K_PQ = priority_search_4(K, min_relations, tuple2weight, tu2down_neis)
    end = time.time()
    TOP_K_enu, total = enumerate_all_4(K, min_relations, tuple2weight, tu2down_neis)
    end2 = time.time()
    time_PQ = end - start
    time_enu = end2 - end

    assert TOP_K_enu == TOP_K_PQ
    print "===total count is==="
    print total
    print "=====running time=="
    print time_PQ
    print time_enu
    return time_PQ, time_enu


if __name__ == "__main__":
    test_priority_search()
    # time_measurements([20, 4, 7, 10], 100)
    # time_measurements([20, 4, 7, 10], 10000)
