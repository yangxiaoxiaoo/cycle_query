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
    # [DESIGN CHOICE] to generate heavy/light mixed database instances, randomly pick degrees
    # for each variable.
    rel2tuple = dict()
    tuple2weight = dict()
    for variable in range(cyc_len - 1):
        key = "R"+str(variable)
        rel2tuple[key] = set()
        for tuple0 in var2cand[variable]:
            maxdegree = len(var2cand[variable + 1])
            chosendegree = random.randint(1, maxdegree)
            count = 0
            for tuple1 in var2cand[variable + 1]:
                # bound the degree into chosendegree
                if count >= chosendegree:
                    break
                count += 1
                rel2tuple[key].add((tuple0, tuple1))
                tuple2weight[(tuple0, tuple1)] = random.uniform(0, weightrange)
                # print key + ": adding tuple" + str([tuple0, tuple1])
        key = "R" + str(cyc_len - 1)
        rel2tuple[key] = set()
        for tuple0 in var2cand[cyc_len - 1]:
            maxdegree = len(var2cand[0])
            chosendegree = random.randint(maxdegree/2, maxdegree)
            count = 0
            for tuple1 in var2cand[0]:
                # bound the degree into chosendegree
                if count >= chosendegree:
                    break
                count += 1
                # all pair add. Can do other strategies...
                rel2tuple[key].add((tuple0, tuple1))
                tuple2weight[(tuple0, tuple1)] = random.uniform(0, weightrange)
                # print key + ": adding tuple" + str([tuple0, tuple1])
    return rel2tuple, tuple2weight

def explode_bp(rel2tuple, l):

    bp_set = set()
    temp_set = set()
    for t1 in rel2tuple['R0']:
        temp_set.add(t1[0])
    for tl in rel2tuple['R'+str(l-1)]:
        if tl[1] in temp_set:
            bp_set.add(tl[1])

    rel2tuplebp = dict()
    for bp in bp_set:
        rel2tuplebp[bp] = dict()
        for k in rel2tuple:
            rel2tuplebp[bp][k] = set()
        for tuple in rel2tuple['R0']:
            if tuple[0] == bp:
                rel2tuplebp[bp]['R0'].add(tuple)
        for i in range(1, l-1):
            r = 'R'+ str(i)
            assert type(rel2tuple[r]) == set
            rel2tuplebp[bp][r] = rel2tuple[r]
        r = 'R' + str(l-1)
        for tuple in rel2tuple[r]:
            if tuple[1] == bp:
                rel2tuplebp[bp][r].add(tuple)
    return bp_set, rel2tuplebp


def semi_join_bp(R_start, R_end, rel2tuplebp, bp):
    # rel2tuplebp is mapping a bp to rel2tuple
    rel2tuple = rel2tuplebp[bp]
    tu2down_neis = dict()
    tu2up_neis = dict()


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
    rel2tuplebp[bp] = rel2tuple
    return tu2down_neis, tu2up_neis

def semi_join_reverse_bp(R_start, R_end, rel2tuplebp, bp):
    rel2tuple = rel2tuplebp[bp]
    get_second_ele = lambda (x0, x1): x1
    checkset = set((get_second_ele(tup) for tup in rel2tuple[R_start]))
    new_set = set()
    for tup in rel2tuple[R_end]:
        if tup[0] in checkset:
            new_set.add(tup)
    rel2tuple[R_end] = new_set
    rel2tuplebp = rel2tuple


def semi_join(R_start, R_end, rel2tuple):
    tu2down_neis = dict()
    tu2up_neis = dict()
    # print "reduce " + R_start + " according to "+R_end + '...'
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

def semi_join_reverse(R_start, R_end, rel2tuple):
    get_second_ele = lambda (x0, x1): x1
    checkset = set((get_second_ele(tup) for tup in rel2tuple[R_start]))
    new_set = set()
    for tup in rel2tuple[R_end]:
        if tup[0] in checkset:
            new_set.add(tup)
    rel2tuple[R_end] = new_set

def full_SJ_reduce_4(rel2tuple):
    #TODO: correct it, add bottom-up swipe for baselines use

    # contain hard code for 4-cycle and will rewrite later...
    # semi-join reduction for all relations, and return an index from tuple to downstream and upstream neighbors
    # No global consistency: R0 to upstream and R0 to downstream
    '''
    print "before"
    print rel2tuple
    semi_join_reverse('R3', 'R0', rel2tuple)
    semi_join_reverse('R2', 'R3', rel2tuple)
    semi_join_reverse('R1', 'R2', rel2tuple)
    semi_join_reverse('R0', 'R1', rel2tuple)
    semi_join_reverse('R3', 'R0', rel2tuple)
    print "after"
    print rel2tuple
    '''
    tu2down_neis, tu2up_neis = semi_join('R0', 'R1', rel2tuple)
    tu2down_neis1, tu2up_neis1 = semi_join('R1', 'R2', rel2tuple)
    tu2up_neis.update(tu2up_neis1)
    tu2down_neis.update(tu2down_neis1)
    tu2down_neis1, tu2up_neis1 = semi_join('R2', 'R3', rel2tuple)
    tu2up_neis.update(tu2up_neis1)
    tu2down_neis.update(tu2down_neis1)
    tu2down_neis1, tu2up_neis1 = semi_join('R3', 'R0', rel2tuple)
    tu2up_neis.update(tu2up_neis1)
    tu2down_neis.update(tu2down_neis1)
   # tu2down_neis1, tu2up_neis1 = semi_join('R0', 'R1', rel2tuple)

    # print tu2down_neis
    return tu2down_neis, tu2up_neis
    # [DESIGN CHOICE]Q: shall we omit this and record a hash to max item only?
    # [DESIGN CHOICE]A: No since we will need the hash to neighbors anyway later to expend PEI

def join(R_start, R_end):
    # [DESIGN CHOICE] be careful about the 3-variable tuple order
    # this function takes R_start(x0, x1) join with (x1, x2) output (x0, x1, x2)
    result = set()
    var2tu_end = dict()
    for tu in R_end:
        if tu[0] not in var2tu_end:
            var2tu_end[tu[0]] = {tu}
        else:
            var2tu_end[tu[0]].add(tu)
    for tu in R_start:
        if tu[-1] in var2tu_end:
            for tu_end in var2tu_end[tu[-1]]:
                result.add(tu[:-1] + tu_end)
    return result

def semi_join_pos(R_start, R_end, pos_1, pos_2):
    # return a new set of R_start such that pos_1 in R_start is in pos_2 in R_end
    result = set()
    get_ele = lambda tup: tup[pos_2]
    checkset = set((get_ele(tup) for tup in R_end))
    for tup in R_start:
        if tup[pos_1] in checkset:
            result.add(tup)
    return result

def SJ_split_heuristic_4(rel2tuple, split_rel2tuple, tuple2weight):
    # reduce into triple I1 and then I2 for different instances
    # Q1: I11, I12; Q2: I21, I22; Q3: I31, I32
    # create a map from breakpairs to (a list of Ix1 tuples, min weight of such Ix1 tuples)
    # breakpoints is (x2, x0) for I11, (x0, x2) for I21, (x1, x3) for I31
    intermid2tuple = {'I11': set(), 'I12': set(), 'I21': set(), 'I22': set(), 'I31': set(), 'I32': set()}
    intertuple2weight = dict()  # mapping an instance of Ix1 or Ix2 to its weight
    breakpair2tuples = dict()
    breakpair2minweight = dict()
    rel2tuple.update(split_rel2tuple)

    # create I11
    intermid2tuple['I11'] = join(rel2tuple['R0H'], rel2tuple['R1'])
    for (x0, x1, x2) in intermid2tuple['I11']:
        cur_wgt = tuple2weight[(x0, x1)] + tuple2weight[(x1, x2)]
        intertuple2weight[(x0, x1, x2)] = cur_wgt
        if (x2, x0) not in breakpair2tuples:
            breakpair2tuples[(x2, x0)] = {(x0, x1, x2)}
            breakpair2minweight[(x2, x0)] = cur_wgt
        else:
            breakpair2tuples[(x2, x0)].add((x0, x1, x2))
            breakpair2minweight[(x2, x0)] = min(breakpair2minweight[(x2, x0)], cur_wgt)
    # create I21
    intermid2tuple['I21'] = join(rel2tuple['R2H'], rel2tuple['R3'])
    for (x2, x3, x0) in intermid2tuple['I21']:
        cur_wgt = tuple2weight[(x2, x3)] + tuple2weight[(x3, x0)]
        intertuple2weight[(x2, x3, x0)] = cur_wgt
        if (x0, x2) not in breakpair2tuples:
            breakpair2tuples[(x0, x2)] = {(x2, x3, x0)}
            breakpair2minweight[(x0, x2)] = cur_wgt
        else:
            breakpair2tuples[(x0, x2)].add((x2, x3, x0))
            breakpair2minweight[(x0, x2)] = min(breakpair2minweight[(x0, x2)], cur_wgt)
    # create I31
    intermid2tuple['I31'] = join(rel2tuple['R3'], rel2tuple['R0L'])
    for (x3, x0, x1) in intermid2tuple['I31']:
        cur_wgt = tuple2weight[(x3, x0)] + tuple2weight[(x0, x1)]
        intertuple2weight[(x3, x0, x1)] = cur_wgt
        if (x1, x3) not in breakpair2tuples:
            breakpair2tuples[(x1, x3)] = {(x3, x0, x1)}
            breakpair2minweight[(x1, x3)] = cur_wgt
        else:
            breakpair2tuples[(x1, x3)].add((x3, x0, x1))
            breakpair2minweight[(x1, x3)] = min(breakpair2minweight[(x1, x3)], cur_wgt)
    # create I12
    R31 = semi_join_pos(rel2tuple['R3'], intermid2tuple['I11'], 1, 0)
    R21 = semi_join_pos(rel2tuple['R2'], intermid2tuple['I11'], 0, 2)
    intermid2tuple['I12'] = join(R21, R31)
    for tu in intermid2tuple['I12']:
        intertuple2weight[tu] = tuple2weight[(tu[0], tu[1])] + tuple2weight[(tu[1], tu[2])]
    # create I22
    R01 = semi_join_pos(rel2tuple['R0'], intermid2tuple['I21'], 0, 2)
    R11 = semi_join_pos(rel2tuple['R1'], intermid2tuple['I21'], 1, 0)
    intermid2tuple['I22'] = join(R01, R11)
    for tu in intermid2tuple['I22']:
        intertuple2weight[tu] = tuple2weight[(tu[0], tu[1])] + tuple2weight[(tu[1], tu[2])]
    # create I32
    R11 = semi_join_pos(rel2tuple['R1'], intermid2tuple['I31'], 0, 2)
    R21 = semi_join_pos(rel2tuple['R2'], intermid2tuple['I31'], 1, 0)
    intermid2tuple['I32'] = join(R11, R21)
    for tu in intermid2tuple['I32']:
        intertuple2weight[tu] = tuple2weight[(tu[0], tu[1])] + tuple2weight[(tu[1], tu[2])]

    return intermid2tuple, intertuple2weight, breakpair2tuples, breakpair2minweight


def p_search_decom_tree(K, intermid2tuple, intertuple2weight, breakpair2tuples, breakpair2minweight):
    # prioritized search on decompsed trees. In this case from
    PQ = []
    TOP_K = []
    for I12 in intermid2tuple['I12']:
        # print intertuple2weight
        heapq.heappush(PQ, globalclass.PE_tree(I12, intertuple2weight[I12], 1, breakpair2minweight))
    for I22 in intermid2tuple['I22']:
        heapq.heappush(PQ, globalclass.PE_tree(I22, intertuple2weight[I22], 2, breakpair2minweight))
    for I32 in intermid2tuple['I32']:
        heapq.heappush(PQ, globalclass.PE_tree(I32, intertuple2weight[I32], 3, breakpair2minweight))
    while len(PQ) != 0:
        cur_PET = heapq.heappop(PQ)
        if cur_PET.completion:
            TOP_K.append(cur_PET)
            if len(TOP_K) == K:
                break
        else:
            if cur_PET.query_type == 1:
                breakpair = (cur_PET.x2, cur_PET.x0)
            elif cur_PET.query_type == 2:
                breakpair = (cur_PET.x0, cur_PET.x2)
            else:
                assert cur_PET.query_type == 3
                breakpair = (cur_PET.x1, cur_PET.x3)
            for Ix1 in breakpair2tuples[breakpair]:
                new_PET = copy.deepcopy(cur_PET)
                new_PET.merge(Ix1, intertuple2weight[Ix1])
                heapq.heappush(PQ, new_PET)
    print "TOP K results are"
 #   for PET in TOP_K:
  #      print PET.wgt
    return TOP_K


def heavy_map_v1(tu2down_neis, tu2up_neis):
    #take a tuple to neighbors map(up stream and down stream)
    tu2degree = dict()
    tu2is_heavy = dict()
    for tu in tu2down_neis:
        tu2degree[tu] = len(tu2down_neis[tu]) + len(tu2up_neis[tu])
    n = len(tu2down_neis)
    # print "n is"
    # print n
    # print math.sqrt(n)
    for key, value in tu2degree.iteritems():
        if value < math.sqrt(n):
            tu2is_heavy[key] = False
        else:
            tu2is_heavy[key] = True
            # print "heavy value:"
            # print value
    # print tu2is_heavy
    return tu2is_heavy


def split_by_heavy_4(rel2tuple, n):
    # take a relation to tuple mapping, group R0 on x0's heaviness, then group R2 on x2's heaviness
    # put the R0 tuple in R0H if x0 is heavy in R0(x0, x1), R0L elsewhere.
    # Put the R2 tuple in R2H if x2 is heavy in R2(x2, x3), R2L elsewhere.
    additional_dict = {'R0H': set(), 'R0L': set(), 'R2H': set(), 'R2L': set()}
    x02count = dict()
    x22count = dict()
    for tu in rel2tuple['R0']:
        if tu[0] in x02count:
            x02count[tu[0]] += 1
        else:
            x02count[tu[0]] = 1
    for tu in rel2tuple['R2']:
        if tu[0] in x02count:
            x22count[tu[0]] += 1
        else:
            x22count[tu[0]] = 1

    for tu in rel2tuple['R0']:
        if x02count[tu[0]] > math.sqrt(n):
            additional_dict['R0H'].add(tu)
        else:
            additional_dict['R0L'].add(tu)
    for tu in rel2tuple['R2']:
        if x22count[tu[0]] > math.sqrt(n):
            additional_dict['R2H'].add(tu)
        else:
            additional_dict['R2L'].add(tu)
    return additional_dict


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
                    if (tu_down, bp) in tuple2rem:
                        tuple2rem[(tu, bp)] = min(tuple2rem[(tu, bp)], tuple2rem[(tu_down, bp)] + new_val)
                    # else: do no updates on tuple2rem
                    # check to make sure it is the same breakpoint
                else:
                    if (tu_down, bp) in tuple2rem:  # 1/2/18: can't assume tu_down is always in
                        tuple2rem[(tu, bp)] = tuple2rem[(tu_down, bp)] + new_val
    for tu in rel2tuple['R0']:
        for tu_down in tu2down_neis[tu]:
            new_val = tuple2weight[tu_down]
            for bp in breakpoints:
                if (tu, bp) in tuple2rem:
                    if (tu_down, bp) in tuple2rem:
                        tuple2rem[(tu, bp)] = min(tuple2rem[(tu, bp)], tuple2rem[(tu_down, bp)] + new_val)
                    # the same breakpoint
                else:
                    if (tu_down, bp) in tuple2rem:
                        tuple2rem[(tu, bp)] = tuple2rem[(tu_down, bp)] + new_val
    # print "(tuple, breakpoint) to remaining heuristic value mapping:"
    # print tuple2rem
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
    # for fair time_any measurement sake, tuple2rem should be part of prioritized search.
    for tu in rel2tuple['R0']:
        if (tu, tu[0]) in tuple2rem:
            heapq.heappush(PQ, globalclass.PEI(tu, tuple2weight[tu], tuple2rem[(tu, tu[0])]))
            # print "PQpush"
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
                if cur_PEI.mergable(neighbor, tuple2rem):
                    new_PEI = copy.deepcopy(cur_PEI)
                    new_PEI.merge(neighbor, tuple2weight, tuple2rem)
                    heapq.heappush(PQ, new_PEI)
                    # [DESIGN CHOICE] shall we keep the top 1 unpushed (outside always)?
                    # slightly more wordy to implement so I will defer this dicision later
        else:  # length == 3, check breakpoint
            frontier = cur_PEI.instance.frontier()
            for neighbor in tu2down_neis[frontier]:
                if neighbor[1] == cur_PEI.breakpoint:
                    new_PEI = copy.deepcopy(cur_PEI)
                    new_PEI.merge(neighbor, tuple2weight, tuple2rem)
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
            if ((Inter_res.instance.length == 3 and neighbor[1] == Inter_res.breakpoint) \
                    or Inter_res.instance.length < 3) \
                    and Inter_res.mergable(neighbor, fake_tuple2rem):
                new_PEI = copy.deepcopy(Inter_res)
                new_PEI.merge(neighbor, tuple2weight, fake_tuple2rem)
                if new_PEI.instance.completion:
                    TOP_K.append(new_PEI)
                    if len(TOP_K) == K:
                        break
                else:
                    Interm_results.append(new_PEI)

    TOP_K.sort()
    # print "TOP K results are"
    # for PEI in TOP_K:
        # print PEI.wgt
    assert len(TOP_K) == K or len(Interm_results) == 0
    return TOP_K[:K], len(TOP_K)


def test_priority_search():
    # For now, without a heavy/light method, we just always assume R0 is heavy, without loss of generality.
    degrees = [4, 2, 2, 4]
    var2cand = build_data(4, degrees)
    min_relations, tuple2weight = build_relation(4, var2cand, weightrange=10)
    min_relations['R1'].add((1, 10)) # adding a spurious tuple
    # print "size before semi join reduction: "+str(len(min_relations['R1']))
    tu2down_neis0, tu2up_neis0 = semi_join('R1', 'R2', min_relations)


    tu2down_neis, tu2up_neis = full_SJ_reduce_4(min_relations)
#    heavy_map_v1(tu2down_neis, tu2up_neis)
    tuple2rem = heuristic_build_4(tuple2weight, min_relations, tu2down_neis)
    TOP_K_PQ = priority_search_4(5, min_relations, tuple2weight, tu2down_neis)
    TOP_K_enu, total = enumerate_all_4(5, min_relations, tuple2weight, tu2down_neis)
    print len(TOP_K_enu)
    print len(TOP_K_PQ)
    # assert TOP_K_enu == TOP_K_PQ
    assert (TOP_K_enu[0].wgt - TOP_K_PQ[0].wgt) < 0.0000001
    #TODO: write a correct semi-join for the two baselines

    split_rel2tuple = split_by_heavy_4(rel2tuple=min_relations, n=2)
    intermid2tuple, intertuple2weight, breakpair2tuples, breakpair2minweight = \
        SJ_split_heuristic_4(min_relations, split_rel2tuple, tuple2weight)
    TOP_K_select = p_search_decom_tree(5, intermid2tuple, intertuple2weight, breakpair2tuples, breakpair2minweight)
#    print TOP_K_enu[0].wgt
    print TOP_K_select[0].wgt
    assert (TOP_K_enu[0].wgt - TOP_K_select[0].wgt) < 0.0000001


def time_measurements(degrees, K):
    # return a pair of running time_any of prioritized search and enumerate all
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
    print "=====running time===="
    print time_PQ
    print time_enu
    return time_PQ, time_enu


def test_split_plan():
    degrees = [1, 2, 2, 1]
    var2cand = build_data(4, degrees)
    rel2tuple, tuple2weight = build_relation(4, var2cand, weightrange=10)
    split_rel2tuple = split_by_heavy_4(rel2tuple, n=2)


if __name__ == "__main__":
    test_priority_search()
    # time_measurements([20, 4, 7, 10], 100)
    # time_measurements([20, 4, 7, 10], 10000)
