import math
import random
import priority_queue
import globalclass
import copy
import timeit
import semi_join_utils
import sys
import heapq

def path_SJ_reduce_l_old(rel2tuple, l):
    #path semi-join bottom-up, build dictionary to connected tuples.

    tu2down_neis, tu2up_neis = semi_join_utils.semi_join('R0', 'R1', rel2tuple)
    for relation_index in range(1, l-1):
        tu2down_neis1, tu2up_neis1 = semi_join_utils.semi_join('R'+str(relation_index), 'R'+str(relation_index + 1), rel2tuple)
        tu2up_neis.update(tu2up_neis1)
        tu2down_neis.update(tu2down_neis1)


    return tu2down_neis, tu2up_neis


def path_SJ_reduce_l(rel2tuple, l):
    #path semi-join bottom-up, build dictionary to connected tuples.

    tu2down_neis, tu2up_neis = semi_join_utils.semi_join('R' + str(l-2), 'R' + str(l-1), rel2tuple)
    for relation_index in range(l-3, -1, -1):
        tu2down_neis1, tu2up_neis1 = semi_join_utils.semi_join('R'+str(relation_index), 'R'+str(relation_index + 1), rel2tuple)
        tu2up_neis.update(tu2up_neis1)
        tu2down_neis.update(tu2down_neis1)


    return tu2down_neis, tu2up_neis


def cycle_SJ_reduce_l(rel2tuple, l):
    #cycle SJ build dictionary to neighbors. Add closing one R(l-1) to R0

    n = 0
    for rel in rel2tuple:
        n = max(n, len(rel2tuple[rel]))
    delta = math.pow(n, 0.5)

    bp_set, rel2tuplebp = semi_join_utils.explode_bp(rel2tuple, l)

    bp_tu2down_neis = dict()
    bp_tu2up_neis = dict()
    for bp in bp_set:

        tu2down_neis, tu2up_neis = semi_join_utils.semi_join_bp('R' + str(l - 1), 'R0', rel2tuplebp, bp)
        if n > 20:
            assert len(tu2down_neis) <= delta * n * 1.001

        for relation_index in range(l-2, 0, -1):
            tu2down_neis1, tu2up_neis1 = semi_join_utils.semi_join('R'+str(relation_index), 'R'+str(relation_index + 1), rel2tuple)
            if n > 20:
                assert len(tu2down_neis1) <= delta * n * 1.001
            tu2up_neis.update(tu2up_neis1)
            tu2down_neis.update(tu2down_neis1)
        tu2down_neis1, tu2up_neis1 = semi_join_utils.semi_join('R0', 'R1', rel2tuple)
        if n > 20:
            assert len(tu2down_neis1) <= delta * n * 1.001
        tu2up_neis.update(tu2up_neis1)
        tu2down_neis.update(tu2down_neis1)

        bp_tu2down_neis[bp] = tu2down_neis
        bp_tu2up_neis[bp] = tu2up_neis

    return bp_set, bp_tu2down_neis, bp_tu2up_neis


def cycle_SJ_reduce_l_light(rel2tuple, l):
    # called by the all light case only.

    n = 0
    for rel in rel2tuple:
        n = max(n, len(rel2tuple[rel]))
    delta = math.pow(n, 0.5)

    bp_set, rel2tuplebp = semi_join_utils.explode_bp(rel2tuple, l)

    bp_tu2down_neis = dict()
    bp_tu2up_neis = dict()


    tu2down_neis, tu2up_neis = semi_join_utils.semi_join('R' + str(l - 1), 'R0', rel2tuple)
    if n > 20:
        assert len(tu2down_neis) <= delta * n * 1.001

    for relation_index in range(l - 2, 0, -1):
        tu2down_neis1, tu2up_neis1 = semi_join_utils.semi_join('R' + str(relation_index),
                                                               'R' + str(relation_index + 1), rel2tuple)
        if n > 20:
            assert len(tu2down_neis1) <= delta * n * 1.001
        tu2up_neis.update(tu2up_neis1)
        tu2down_neis.update(tu2down_neis1)
    tu2down_neis1, tu2up_neis1 = semi_join_utils.semi_join('R0', 'R1', rel2tuple)
    if n > 20:
        assert len(tu2down_neis1) <= delta * n * 1.001
    tu2up_neis.update(tu2up_neis1)
    tu2down_neis.update(tu2down_neis1)

    return tu2down_neis, tu2up_neis


'''
def priority_search_l_cycle_naive(K, rel2tuple, tuple2weight, tu2down_neis, l):

    TOP_K = []
    PQ = priority_queue.initialize_priority_queue()
    tuple2rem = heuristic_build_l_cycle(tuple2weight, rel2tuple, tu2down_neis, l)
    for tu in rel2tuple['R0']:
        if (tu, tu[0]) in tuple2rem:
            PQ.add((globalclass.PEI_cycle(tu, tuple2weight[tu], tuple2rem[(tu, tu[0])], l), None))

    while PQ.size() != 0:
        (cur_PEI_cycle, _) = PQ.pop_min()
        ## Decrease PQ size???
        if cur_PEI_cycle.instance.completion:
            TOP_K.append(cur_PEI_cycle)
            if len(TOP_K) == K:
                break
        elif cur_PEI_cycle.instance.length != l-1: # not completed, there is frontier, no need to check breakpoint
            frontier = cur_PEI_cycle.instance.frontier()
            for neighbor in tu2down_neis[frontier]:
                if cur_PEI_cycle.mergable(neighbor, tuple2rem):
                    new_PEI = copy.deepcopy(cur_PEI_cycle)
                    new_PEI.merge(neighbor, tuple2weight, tuple2rem)
                    PQ.add((new_PEI, None))

        else:  # length == l, check breakpoint
            frontier = cur_PEI_cycle.instance.frontier()
            for neighbor in tu2down_neis[frontier]:
                if neighbor[1] == cur_PEI_cycle.breakpoint:
                    new_PEI = copy.deepcopy(cur_PEI_cycle)
                    new_PEI.merge(neighbor, tuple2weight, tuple2rem)
                    PQ.add((new_PEI, None))
    print "TOP K results are"
    for PEI_cycle in TOP_K:
        print PEI_cycle.wgt
    assert len(TOP_K) == K or PQ.size() == 0
    return TOP_K
'''


def priority_search_l_cycle_naive_init(rel2tuple, tuple2weight, bp_set, bptu2down_neis, l, Deepak, Lazy, PQmode, bound):
    #used by a global PQ_global.
    PQ = priority_queue.initialize_priority_queue(PQmode, bound)
    tuple2rem = heuristic_build_l_cycle(tuple2weight, rel2tuple, bp_set,bptu2down_neis, l)

    if Deepak:
        if Lazy:
            prev2sortedmap, prev2heap = Deepak_sort_cycle_lazy(tuple2rem, bp_set, tuple2weight, rel2tuple, l)
        else:
            prev2sortedmap = Deepak_sort_cycle(tuple2rem, bp_set, tuple2weight, rel2tuple, l)
            prev2heap = None

        for k in prev2sortedmap:
            if k[0] == 0:
                tu = prev2sortedmap[k]['#']  # first
                if (tu, tu[0]) in tuple2rem:
                    PQ.add((globalclass.PEI_cycle(tu, tuple2weight[tu], tuple2rem[(tu, tu[0])], l), None))
        return prev2sortedmap, prev2heap, tuple2rem, PQ

    else:
        for tu in rel2tuple['R0']:
            if (tu, tu[0]) in tuple2rem:
                PQ.add((globalclass.PEI_cycle(tu, tuple2weight[tu], tuple2rem[(tu, tu[0])], l), None))
        return tuple2rem, PQ

def priority_search_l_cycle_naive_next(tuple2weight, bptu2down_neis, l, PQ, tuple2rem, prev2sortedmap, prev2heap, Deepak, Lazy):
    #used by a gobal PQ_global.
    #takes a PQ for this sub-database, return the next
    #PQ pass by ref, can be changed.

    while PQ.size() != 0:
        (cur_PEI_cycle, _) = PQ.pop_min()

        if Deepak:
            ## Decrease PQ's maximum size (works for any-k sort)
            #PQ.decrease_max_size()

            if Lazy:
                successor_PEI_cycle = cur_PEI_cycle.lazy_successor(prev2sortedmap, prev2heap, tuple2weight, tuple2rem)
            else:
                successor_PEI_cycle = cur_PEI_cycle.successor(prev2sortedmap, tuple2weight, tuple2rem)
            if successor_PEI_cycle is not None:
                PQ.add((successor_PEI_cycle, None))
                assert successor_PEI_cycle > cur_PEI_cycle
            while not cur_PEI_cycle.instance.completion:
                #print cur_PEI_cycle.instance.length
                state = cur_PEI_cycle.expand(prev2sortedmap, tuple2weight, tuple2rem)
                if state == 1:
                    print "type error! debug only"
                    break
                #print cur_PEI_cycle.instance.length
                if Lazy:
                    successor_PEI_cycle = cur_PEI_cycle.lazy_successor(prev2sortedmap, prev2heap, tuple2weight,
                                                                       tuple2rem)
                else:
                    successor_PEI_cycle = cur_PEI_cycle.successor(prev2sortedmap, tuple2weight, tuple2rem)

                if successor_PEI_cycle is not None:
                    PQ.add((successor_PEI_cycle, None))
                    assert successor_PEI_cycle > cur_PEI_cycle

            assert cur_PEI_cycle.instance.completion
            return cur_PEI_cycle


        else:
            if cur_PEI_cycle.instance.completion:
                return cur_PEI_cycle
            elif cur_PEI_cycle.instance.length != l-1: # not completed, there is frontier, no need to check breakpoint
                frontier = cur_PEI_cycle.instance.frontier()
                bp = cur_PEI_cycle.breakpoint
                tu2down_neis = bptu2down_neis[bp]
                #if frontier in tu2down_neis: # now with diffrent bp, this can be out of dict.
                for neighbor in tu2down_neis[frontier]:
                    if cur_PEI_cycle.mergable(neighbor, tuple2rem):
                        new_PEI = copy.deepcopy(cur_PEI_cycle)
                        new_PEI.merge(neighbor, tuple2weight, tuple2rem)
                        PQ.add((new_PEI, None))

            else:  # length == l, check breakpoint
                frontier = cur_PEI_cycle.instance.frontier()
                bp = cur_PEI_cycle.breakpoint
                tu2down_neis = bptu2down_neis[bp]
                #if frontier in tu2down_neis:  # now with diffrent bp, this can be out of dict.
                for neighbor in tu2down_neis[frontier]:
                    if neighbor[1] == cur_PEI_cycle.breakpoint:
                        new_PEI = copy.deepcopy(cur_PEI_cycle)
                        new_PEI.merge(neighbor, tuple2weight, tuple2rem)
                        PQ.add((new_PEI, None))



def simple_join(rel2tuple, tuple2weight, tu2down_neis, start, end):
    # used by all light case to compute a dictionary from I1_list to weight

    list2wgt = dict()
    for start_tuple in rel2tuple['R' + str(start)]:
        # print start_tuple
        start_list = tuple([start_tuple])
        # print start_list
        list2wgt[start_list] = tuple2weight[start_tuple]
        # print list2wgt

    for index in range(start+1, end):
        new_dict = dict()
        for key in list2wgt:
            assert type(key) == tuple
            if len(key) != 0 and list(key)[-1] in tu2down_neis:
                for neighbor in tu2down_neis[key[-1]]:
                    new_key = copy.deepcopy(list(key))
                    new_key.append(neighbor)
                    new_dict[tuple(new_key)] = list2wgt[key] + tuple2weight[neighbor]
        list2wgt = new_dict
    return list2wgt


def priority_search_l_cycle_light_init(rel2tuple, tuple2weight, tu2down_neis, l, Deepak, Lazy, PQmode, bound):
    #print rel2tuple
    # compute a set of I1_list, a set of I2_list
    # for each I1_list, the max I2_list weight for it, a list of all matching I2_list
    PQ = priority_queue.initialize_priority_queue(PQmode, bound)

    # simple join l/2 first relations
    # to get a set of I1_list to wgt:
    I1_list2wgt = simple_join(rel2tuple, tuple2weight, tu2down_neis, 0, int(l/2))
    I2_list2wgt = simple_join(rel2tuple, tuple2weight, tu2down_neis, int(l/2), l)
    # print I2_list2wgt
    # print I1_list2wgt

    breakpoints2hrtc = dict()
    breakpoints2I2 = dict()
    for I2_list in I2_list2wgt:
        if (I2_list[-1][1], I2_list[0][0]) not in breakpoints2I2:
            breakpoints2I2[(I2_list[-1][1], I2_list[0][0])] = {I2_list}
            breakpoints2hrtc[(I2_list[-1][1], I2_list[0][0])] = I2_list2wgt[I2_list]
        else:
            breakpoints2I2[(I2_list[-1][1], I2_list[0][0])].add(I2_list)
            breakpoints2hrtc[(I2_list[-1][1], I2_list[0][0])] = min(I2_list2wgt[I2_list], breakpoints2hrtc[(I2_list[-1][1], I2_list[0][0])])
    for I1_list in I1_list2wgt:
        cur_breakpoints = (I1_list[0][0], I1_list[-1][1])
        if cur_breakpoints in breakpoints2I2:
            curPEI = globalclass.PEI_lightcycle(I1_list[0], 0, 0, l)
            curPEI.biginit(I1_list, I1_list2wgt[I1_list], breakpoints2hrtc[cur_breakpoints], l)
            PQ.add((curPEI, None))
    # print breakpoints2I2
    # print PQ
    if not Deepak:
        bp2sortedmap = dict()
        return bp2sortedmap, breakpoints2I2, I2_list2wgt, PQ
    else:
        key2list = dict()
        bp2sortedmap = dict()
        for bp in breakpoints2I2:
            key2list[bp] = []
            for i2 in breakpoints2I2[bp]:
                key2list[bp].append((I2_list2wgt[i2], i2))
        for k in key2list:
            localdict = dict()
            list = key2list[k]
            if Lazy:
                heapq.heapify(list)
            else:
                list.sort()
            if len(list) != 0:
                localdict['#'] = list[0][1]
                if not Lazy:
                    for i in range(len(list) - 1):
                        localdict[list[i][1]] = list[i + 1][1]
            bp2sortedmap[k] = localdict
        return bp2sortedmap, key2list, breakpoints2I2, I2_list2wgt, PQ



def priority_search_l_cycle_light_next(breakpoints2I2, I2_list2wgt, PQ, bp2sortedmap, bp2heap, Deepak, Lazy):
    while PQ.size() != 0:
        (cur_PEI_cycle, _) = PQ.pop_min()
        if Deepak:
            ## Decrease PQ's maximum size (works for any-k sort)
            #PQ.decrease_max_size()

            #successor_PEI_cycle = cur_PEI_cycle.bigsucc(breakpoints2I2, I2_list2wgt, bp2sortedmap)
            #if successor_PEI_cycle != None:
            #    heapq.heappush(PQ, successor_PEI_cycle)
            if cur_PEI_cycle.instance.completion:
                if Lazy:
                    successor_PEI_cycle = cur_PEI_cycle.bigsucc_lazy(breakpoints2I2, I2_list2wgt, bp2sortedmap, bp2heap)
                else:
                    successor_PEI_cycle = cur_PEI_cycle.bigsucc(breakpoints2I2, I2_list2wgt, bp2sortedmap)
                if successor_PEI_cycle is not None:
                    PQ.add((successor_PEI_cycle, None))
                return cur_PEI_cycle
            cur_PEI_cycle.bigexpand(breakpoints2I2, I2_list2wgt, bp2sortedmap)
            if not cur_PEI_cycle:
                continue
            assert cur_PEI_cycle.instance.completion
            if Lazy:
                successor_PEI_cycle = cur_PEI_cycle.bigsucc_lazy(breakpoints2I2, I2_list2wgt, bp2sortedmap, bp2heap)
            else:
                successor_PEI_cycle = cur_PEI_cycle.bigsucc(breakpoints2I2, I2_list2wgt, bp2sortedmap)
            if successor_PEI_cycle is not None:
                PQ.add((successor_PEI_cycle, None))
            return cur_PEI_cycle

        else:
            if cur_PEI_cycle.instance.completion:
                return cur_PEI_cycle
            else:
                for I2_list in breakpoints2I2[cur_PEI_cycle.breakpointpair]:
                    new_PEI = copy.deepcopy(cur_PEI_cycle)
                    new_PEI.bigmerge(I2_list, I2_list2wgt[tuple(I2_list)])
                    PQ.add((new_PEI, None))




def heuristic_build_l_cycle(tuple2weight, rel2tuple, breakpoints, bptu2down_neis, l):
    # build a dictionary from tuple down to the remaining weight not including tuple
    # assumption: no tuple appear in different relations

    tuple2rem = dict()
    #breakpoints = set()
    for tu in rel2tuple['R'+ str(l-1)]:
        #breakpoints.add(tu[1])
        tuple2rem[(tu, tu[1])] = 0

    for bp in breakpoints:

        for tu in rel2tuple['R'+ str(l-2)]:
            for tu_down in bptu2down_neis[bp][tu]:
                if tu_down[1] == bp and (tu_down, tu_down[1]) in tuple2rem:
                    new_val = tuple2weight[tu_down] + tuple2rem[tu_down, tu_down[1]]
                    if (tu, bp) in tuple2rem:
                        tuple2rem[(tu, bp)] = min(tuple2rem[(tu, bp)], new_val)
                    else:
                        tuple2rem[(tu, bp)] = new_val

        for which_relation in range(l-3, -1, -1): # when l = 4, which_relation will be 1, 0
            this_relation_name = 'R'+str(which_relation)
            for tu in rel2tuple[this_relation_name]:
                for tu_down in bptu2down_neis[bp][tu]:
                    new_val = tuple2weight[tu_down]

                    if (tu, bp) in tuple2rem:
                        if (tu_down, bp) in tuple2rem:
                            tuple2rem[(tu, bp)] = min(tuple2rem[(tu, bp)], tuple2rem[(tu_down, bp)] + new_val)
                        # the same breakpoint
                    else:
                        if (tu_down, bp) in tuple2rem:
                            tuple2rem[(tu, bp)] = tuple2rem[(tu_down, bp)] + new_val

    return tuple2rem

def Deepak_sort_cycle(tuple2rem, breakpoints, tuple2weight, rel2tuple, l):
    # l is the goal length, build sorted subtree weights for R0, R1...Rl-1
    key2list = dict() # first map all keys in the output dictionary into a list of (subtree-weight, tuple)

    for bp in breakpoints:
        for i in range(l-1, -1, -1):

            relation = 'R' + str(i)
            #if i == l-1:
            #    for t in rel2tuple[relation]:
            #        if t[1] == bp:
            #            if (i, t[0], t[1]) in key2list:
            #                key2list[i, t[0], t[1]].append((tuple2weight[t], t))
            #            else:
            #                key2list[i, t[0], t[1]] = [(tuple2weight[t], t)]

            if True:
                for t in rel2tuple[relation]:

                    if (t, bp) in tuple2rem:
                        if (i, t[0], bp) in key2list:
                            key2list[i, t[0], bp].append((tuple2weight[t] + tuple2rem[t, bp], t))
                        else:
                            key2list[i, t[0], bp] = [(tuple2weight[t] + tuple2rem[t, bp], t)]

    res = dict()
    for k in key2list:
        localdict = dict()
        list = key2list[k]
        list.sort()
        # print list
        if len(list)!= 0:
            localdict['#'] = list[0][1]
            for i in range(len(list) - 1):
                localdict[list[i][1]] = list[i+1][1]
        res[k] = localdict
    #print "sorted cycle list is "
    #print res
    return res


def Deepak_sort_cycle_lazy(tuple2rem, breakpoints, tuple2weight, rel2tuple, l):
    # lazy sort: return a heap and a dictionary: the dictionary is originally empty; the caller of it will keep modifying it.
    # the heap keeps all content
    # caller check if key is in dictionary: if so, find and use; if not, pop from heap and put into dict, use.

    # l is the goal length, build sorted subtree weights for R0, R1...Rl-1
    key2list = dict() # first map all keys in the output dictionary into a list of (subtree-weight, tuple)

    for bp in breakpoints:
        for i in range(l-1, -1, -1):

            relation = 'R' + str(i)

            if True:
                for t in rel2tuple[relation]:

                    if (t, bp) in tuple2rem:
                        if (i, t[0], bp) in key2list:
                            key2list[i, t[0], bp].append((tuple2weight[t] + tuple2rem[t, bp], t))
                        else:
                            key2list[i, t[0], bp] = [(tuple2weight[t] + tuple2rem[t, bp], t)]

    res = dict()
    for k in key2list:
        localdict = dict()
        list = key2list[k]
        heapq.heapify(list)
        #heapify in O(n), instead of list.sort()

        if len(list)!= 0:
            localdict['#'] = list[0][1]
            heapq.heappop(list)

        res[k] = localdict

    # key2list maps a join key to a heap that you can heappop from.
    #for key in res:
    #    assert key in key2list

    return res, key2list



def heuristic_build_l_path(tuple2weight, rel2tuple, tu2down_neis, l):
    # build a dictionary from tuple down to the remaining weight not including tuple
    # assumption: no tuple appear in different relations
    #assert l >= 4
    tuple2rem = dict()

    for tu in rel2tuple['R' + str(l-1)]:
        tuple2rem[tu] = 0

    for which_relation in range(l-2, -1, -1): # when l = 4, which_relation will be 2, 1, 0
        this_relation_name = 'R'+str(which_relation)
        for tu in rel2tuple[this_relation_name]:
            for tu_down in tu2down_neis[tu]:
                if tu_down in tuple2rem:
                    new_val = tuple2weight[tu_down] + tuple2rem[tu_down]
                    if tu in tuple2rem:
                        tuple2rem[tu] = min(tuple2rem[tu], new_val)
                    else:
                        tuple2rem[tu] = new_val


    return tuple2rem

def Deepak_sort_path(tuple2rem, tuple2weight, rel2tuple, l):
    # l is the goal length, build sorted subtree weights for R0, R1...Rl-1
    key2list = dict() # first map all keys in the output dictionary into a list of (subtree-weight, tuple)

    for i in range(0, l):

        relation = 'R' + str(i)
        if i == l-1:
            for t in rel2tuple[relation]:
                if (i, t[0]) in key2list:
                    key2list[i, t[0]].append((tuple2weight[t], t))
                else:
                    key2list[i, t[0]] = [(tuple2weight[t], t)]

        else:
            for t in rel2tuple[relation]:
                if t in tuple2rem:
                    if (i, t[0]) in key2list:
                        key2list[i, t[0]].append((tuple2weight[t] + tuple2rem[t], t))
                    else:
                        key2list[i, t[0]] = [(tuple2weight[t] + tuple2rem[t], t)]

    res = dict()
    for k in key2list:
        localdict = dict()
        list = key2list[k]
        list.sort()
        # print list
        if len(list)!= 0:
            localdict['#'] = list[0][1]
            for i in range(len(list) - 1):
                localdict[list[i][1]] = list[i+1][1]
        res[k] = localdict
    # print res
    return res

def Deepak_sort_path_lazy(tuple2rem, tuple2weight, rel2tuple, l):
    # l is the goal length, build sorted subtree weights for R0, R1...Rl-1
    key2list = dict() # first map all keys in the output dictionary into a list of (subtree-weight, tuple)

    for i in range(0, l):

        relation = 'R' + str(i)
        if i == l-1:
            for t in rel2tuple[relation]:
                if (i, t[0]) in key2list:
                    key2list[i, t[0]].append((tuple2weight[t], t))
                else:
                    key2list[i, t[0]] = [(tuple2weight[t], t)]

        else:
            for t in rel2tuple[relation]:
                if t in tuple2rem:
                    if (i, t[0]) in key2list:
                        key2list[i, t[0]].append((tuple2weight[t] + tuple2rem[t], t))
                    else:
                        key2list[i, t[0]] = [(tuple2weight[t] + tuple2rem[t], t)]

    res = dict()
    for k in key2list:
        localdict = dict()
        list = key2list[k]
        heapq.heapify(list)

        if len(list)!= 0:
            localdict['#'] = list[0][1]
            heapq.heappop(list)

        res[k] = localdict

    # key2list maps a join key to a heap that you can heappop from.
    return res, key2list


def priority_search_l_path(K, rel2tuple, tuple2weight, tu2down_neis, l, Deepak, Lazy, PQmode, bound, debug):

    #Deepak = True: only push sorted successors.
    if debug:
        assert l >= 4
    # push PEIs into a priority queue, pop k heaviest full items
    # [DESIGN CHOICE] pop the lightest element as consistent with heapq native! If paper is about heaviest, can modify later.
    TOP_K = []
    time_for_each = []
    start_time = timeit.default_timer()
    PQ = priority_queue.initialize_priority_queue(PQmode, bound)
    tuple2rem = heuristic_build_l_path(tuple2weight, rel2tuple, tu2down_neis, l)

    if Deepak:  #push only "null pointed first heads"
        if Lazy:
            prev2sortedmap, prev2heap = Deepak_sort_path_lazy(tuple2rem, tuple2weight, rel2tuple, l)
        else:
            prev2sortedmap = Deepak_sort_path(tuple2rem, tuple2weight, rel2tuple, l)

        for k in prev2sortedmap:
            if k[0] == 0:
                tu = prev2sortedmap[k]['#'] # first
                PQ.add((globalclass.PEI_path(tu, tuple2weight[tu], tuple2rem[tu], l), None))

    else:
        for tu in rel2tuple['R0']:
            if tu in tuple2rem:
                PQ.add((globalclass.PEI_path(tu, tuple2weight[tu], tuple2rem[tu], l), None))

    while PQ.size() != 0:
        (cur_PEI_path, _) = PQ.pop_min()

        if Deepak:
            if Lazy:
                successor_PEI_path = cur_PEI_path.lazy_successor(prev2sortedmap, prev2heap, tuple2weight, tuple2rem)
            else:
                successor_PEI_path = cur_PEI_path.successor(prev2sortedmap, tuple2weight, tuple2rem)

            if successor_PEI_path is not None:
                if not cur_PEI_path < successor_PEI_path:
                    print "lazy sort debug"
                    print cur_PEI_path.wgt
                    print successor_PEI_path.wgt

                assert cur_PEI_path < successor_PEI_path
                PQ.add((successor_PEI_path, None))

            while not cur_PEI_path.instance.completion:
                cur_PEI_path.expand(prev2sortedmap, tuple2weight, tuple2rem)
                if Lazy:
                    successor_PEI_path = cur_PEI_path.lazy_successor(prev2sortedmap, prev2heap, tuple2weight, tuple2rem)
                else:
                    successor_PEI_path = cur_PEI_path.successor(prev2sortedmap, tuple2weight, tuple2rem)
                if successor_PEI_path is not None:
                    if not cur_PEI_path < successor_PEI_path:
                        print "lazy sort debug"
                        print cur_PEI_path.wgt
                        print successor_PEI_path.wgt
                    assert cur_PEI_path < successor_PEI_path
                    PQ.add((successor_PEI_path, None))
            if debug:
                assert  cur_PEI_path.instance.completion
            TOP_K.append(cur_PEI_path)
            ## Decrease PQ's maximum size (works only for any-k sort for now)
            PQ.decrease_max_size()

            end_time = timeit.default_timer()
            time_for_each.append(end_time - start_time)

            start_time = end_time
            if len(TOP_K) == K:
                break

        else:  # push all into PQ
            if cur_PEI_path.instance.completion:
                TOP_K.append(cur_PEI_path)
                ## Decrease PQ's maximum size (works only for any-k sort for now)
                PQ.decrease_max_size()
                end_time = timeit.default_timer()
                time_for_each.append(end_time - start_time)
                start_time = end_time
                if len(TOP_K) == K:
                    break
            else:
                if cur_PEI_path.instance.length != l-1: # not completed, there is frontier, no need to check breakpoint
                    frontier = cur_PEI_path.instance.frontier()
                    for neighbor in tu2down_neis[frontier]:
                        if cur_PEI_path.mergable(neighbor, tuple2rem):
                            new_PEI_path = copy.deepcopy(cur_PEI_path)
                            new_PEI_path.merge(neighbor, tuple2weight, tuple2rem)
                            PQ.add((new_PEI_path, None))

                else:  # length == l-1, last growth.
                    frontier = cur_PEI_path.instance.frontier()
                    for neighbor in tu2down_neis[frontier]:
                        new_PEI_path = copy.deepcopy(cur_PEI_path)
                        new_PEI_path.merge(neighbor, tuple2weight, tuple2rem)
                        PQ.add((new_PEI_path, None))
    if debug:
        print "TOP K results are"
        for PEI_path in TOP_K:
            print PEI_path.wgt
        assert len(TOP_K) == K or PQ.size() == 0
    return TOP_K, time_for_each

def cycle_rotate(relation2tuple, pos, l):
    # take the original database relation2tuple dictionary, rotate it by pos downwards in a l-length cycle.
    # so that the we break at R0[0]
    new_database = dict()
    for relation in relation2tuple:
        original_i = int(relation[1:])
        new_i = (original_i + (l - pos)) % l
        # pos = 2, l = 4, 0 -> 2, 1 -> 3, 2->0, 3-> 1
        # pos = 1, l = 4: R1-> R0, R2-> R1. R3-> R2, R0 -> R3
        new_database['R'+str(new_i)] = relation2tuple[relation]
    return new_database

import math
def l_cycle_database_partition(relation2tuple, l):
    # split the database, return a list of (l+1) new databases. last one is all light one.
    partitions = []
    N = 0
    for key, value in relation2tuple.iteritems():
        N = max(N, len(value))
    delta = math.pow(N, 1/ (math.ceil(l/2)))
    if l == 4:
        assert delta * delta < N * 1.001 and delta * delta > N * 0.999

    heavy_tables = []
    light_tables = [] # list of l light table sets. use later to construct partitions.

    # split each relation into heavy and light components.
    for relation_index in range(0, l):
        relation_name = 'R'+str(relation_index)
        current_relation_tuples = relation2tuple[relation_name]
        heavy_tuples = set()
        heavy_values = set()
        light_tuples = set()
        degree_count = dict()
        for tu in current_relation_tuples:
            if tu[0] not in degree_count:
                degree_count[tu[0]] = 1
            else:
                degree_count[tu[0]] += 1
        for tu in current_relation_tuples:
            if degree_count[tu[0]] <= delta:
                light_tuples.add(tu)
            else:
                heavy_tuples.add(tu)
                heavy_values.add(tu[0])
        # current partition is made of current relation light tuples, combined with remaining relation.
        if delta > 5:
            assert len(heavy_values) <= delta * 1.001
        heavy_tables.append(heavy_tuples)
        light_tables.append(light_tuples)

    # use the split components to construct partitions. First l regular partitions, last one "all light" partition.
    for partition_index in range(0, l):
        new_partition = dict()
        for table_index in range(0, partition_index):
            new_partition['R'+str(table_index)] = light_tables[table_index]
        new_partition['R' + str(partition_index)] = heavy_tables[partition_index]
        for table_index in range(partition_index+1, l):
            new_partition['R' + str(table_index)] = relation2tuple['R'+str(table_index)]

        partitions.append(new_partition)

    #construct the all light one:
    new_partition = dict()
    for table_index in range(0, l):
        new_partition['R' + str(table_index)] = light_tables[table_index]
    partitions.append(new_partition)

    return partitions

def path_enumerate_all(rel2tuple, tuple2weight, tu2down_neis,k, l, debug):
    # after the semi-join reduction, Yannakakis output simple join
    list2weight = simple_join(rel2tuple, tuple2weight, tu2down_neis, 0, l)
    sorted_weight = sorted(list2weight.values())
    if debug:
        for i in range(min(len(sorted_weight), k)):
            print sorted_weight[i]
    return sorted_weight

def l_path_sim(l, k, PQmode, bound):
    # simple simulation on l_simple path. Tested and can be referred to in experiments.
    attr_card = [3, 2, 3, 4, 5]
    var2cand = semi_join_utils.build_data(l, attr_card)
    rel2tuple, tuple2weight = semi_join_utils.build_relation(l, var2cand, weightrange=10)
    tu2down_neis, tu2up_neis = path_SJ_reduce_l(rel2tuple, l)
    print "algo: any-k priotitized search WWW"
    TOP_K_max, time_for_each = priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, False, False, PQmode, bound, debug=True)
    print "algo: any-k priotitized search Deepak"
    TOP_K_sort, time_for_each = priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, True, False, PQmode, bound, debug=True)
    print "algo: any-k priotitized search Lazy sort"
    TOP_K_sort, time_for_each = priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, True, True, PQmode,
                                                       bound, debug=True)
    # assert TOP_K_PQ2 == TOP_K_PQ1 -- observed only rounding numerical errors, ignore.
    print "algo: enumerate all"
    path_enumerate_all(rel2tuple, tuple2weight, tu2down_neis, k, l, debug=True)

def cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, l, recurse_or_not, debug):
    # NPRR recursive join. May use Yannakakis as a subroutine
    results = []
    results2wgt = dict()
    if recurse_or_not:
        l_part_2weight = cycle_path_recursive(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, 1, l - 2)
    else:
        l_part_2weight = simple_join(rel2tuple, tuple2weight, tu2down_neis, 1, l-2)

    if l == 3:
        close_relation = rel2tuple['R2']
        x_r1count = dict()
        x_r1 = dict()
        x_r0count = dict()
        x_r0 = dict()
        for t in rel2tuple['R1']:
            if t[0] not in x_r1count:
                x_r1count[t[0]] = 1
                x_r1[t[0]] = {t}
            else:
                x_r1count[t[0]] += 1
                x_r1[t[0]].add(t)
        for t in rel2tuple['R0']:
            if t[1] not in x_r0count:
                x_r0count[t[1]] = 1
                x_r0[t[1]] = {t}
            else:
                x_r0count[t[1]] += 1
                x_r0[t[1]].add(t)

        for x in x_r0count:
            if x in x_r1count:
                path_count = x_r0count[x] * x_r1count[x]
                path_list = []
                if path_count < len(close_relation):
                    for tr0 in x_r0[x]:
                        for tr1 in x_r1[x]:
                            path = [tr0, tr1]
                            path_list.append(path)
                            if (path[-1][1], path[0][0]) in tuple2weight:
                                results2wgt[tuple(path)] = tuple2weight[tr0] + tuple2weight[tr1] + tuple2weight[(path[-1][1], path[0][0])]
                    for path in path_list:
                        if (path[-1][1], path[0][0]) in close_relation:
                            results.append(path)
                else:
                    for close_tu in close_relation:
                        if (close_tu[1], x) in rel2tuple['R0'] and (x, close_tu[0]) in rel2tuple['R1']:
                            path = [(close_tu[1], x), (x, close_tu[0])]
                            results2wgt[tuple(path)] = tuple2weight[path[0]] + tuple2weight[path[1]] + tuple2weight[
                                close_tu]
                            results.append(path)

    else:

        for l_part in l_part_2weight:

            if l!= 3 and debug:
                assert len(l_part) == l-3
            tu_start = l_part[0]
            tu_end = l_part[-1]
            if tu_start not in tu2up_neis or tu_end not in tu2down_neis:
                # there is no cycles for this l_part.
                continue
            path_count = len(tu2up_neis[tu_start]) * len(tu2down_neis[tu_end])
            close_relation = rel2tuple['R' + str(l-1)]

            path_list = []
            if path_count < len(close_relation):
                # materialize the paths
                for up_nei in tu2up_neis[tu_start]:
                    for down_nei in tu2down_neis[tu_end]:
                        path = [up_nei] + list(l_part) + [down_nei]
                        path_list.append(path)
                        if (path[-1][1], path[0][0]) in tuple2weight:
                            results2wgt[tuple(path)] = tuple2weight[up_nei] + l_part_2weight[l_part] \
                                                   + tuple2weight[down_nei] + tuple2weight[(path[-1][1], path[0][0])]
                for path in path_list:
                    if (path[-1][1], path[0][0]) in close_relation:
                        results.append(path)
            else:
                # loop through each tuple tu_close in R(l-1)
                # check if the tuple made of this R1[0] and tu_close[1] is in R0,
                # and tuple made of  this R(l-2)[1] and tu_close[0] is in R(l-2)
                for close_tu in rel2tuple['R' + str(l-1)]:
                    if (close_tu[1], l_part[0][0]) in rel2tuple['R0'] and \
                            (l_part[-1][1], close_tu[0]) in rel2tuple['R'+str(l-2)]:
                        path = [(close_tu[1], l_part[0][0])] + list(l_part) + [(l_part[-1][1], close_tu[0])]
                        results2wgt[tuple(path)] = tuple2weight[(close_tu[1], l_part[0][0])] + l_part_2weight[l_part] \
                                                   + tuple2weight[(l_part[-1][1], close_tu[0])] + tuple2weight[close_tu]
                        results.append(path)
    values = []


    #fair comparison 
    
    PEIs = []
    for result in results:
        #print result
        assert len(result) == l-1
        #print  result[:l/2]
        #print result[l/2:] + [(result[-1][1], result[0][0])]
        PEI_instance = globalclass.PEI_lightcycle(result[0], 0, 0, l)
        PEI_instance.biginit(result[:l/2], 0, 0, l)
        PEI_instance.bigmerge(result[l/2:] + [(result[-1][1], result[0][0])], results2wgt[tuple(result)])
        PEIs.append(PEI_instance)

        values.append(results2wgt[tuple(result)])
    sorted_values = sorted(values)
    #sorted_values = values
    if debug:
        for i in range(min(len(sorted_values), k)):
            print sorted_values[i]

    sorted_PEIs = sorted(PEIs)
    if debug:
        for i in range(min(len(sorted_values), k)):
            print sorted_PEIs[i].wgt


    return results, sorted_values


def cycle_path_recursive(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, start, l):
    # NPRR recursive join on path as described. l-lenth path
    # will be used by cycle as a subroutine
    results = []

    results2wgt = dict()
    print "l-start=" + str(l-start)
    assert l >= 4
    # this resursive is an alternative implementation that got purged.
    # works correctly on 4+ cycles verified, Do not decide to update further
    if l-start == 1:
        for tu in rel2tuple['R' + str(start)]:
            result = [tu]
            results.append(result)
            results2wgt[tuple(result)] = tuple2weight[tu]
        return results2wgt

    if l-start == 2:
        for tu in rel2tuple['R'+str(start)]:
            if tu not in tu2down_neis:
                continue
            for neighbor in tu2down_neis[tu]:
                result = [tu, neighbor]
                results.append(result)
                results2wgt[tuple(result)] = tuple2weight[tu] + tuple2weight[neighbor]
        print results2wgt
        return results2wgt

    else:
        l_part_2weight = cycle_path_recursive(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, start, l-2)
        for l_part in l_part_2weight:
            assert len(l_part) == l-3
            tu_start = l_part[0]
            tu_end = l_part[-1]
            if tu_start not in tu2up_neis or tu_end not in tu2down_neis:
                # there is no cycles for this l_part.
                continue
            path_count = len(tu2down_neis[tu_end])
            close_relation = rel2tuple['R' + str(l-1)]

            path_list = []
            if path_count < len(close_relation):
                # materialize the paths

                for down_nei in tu2down_neis[tu_end]:
                    path = list(l_part) + [down_nei]
                    path_list.append(path)
                    results2wgt[tuple(path)] = l_part_2weight[l_part] + tuple2weight[down_nei]
                for path in path_list:
                    if path[-1] in close_relation:
                        results.append(path)
            else:
                for close_tu in rel2tuple['R' + str(l-1-start)]:
                    if (l_part[-1][1], close_tu[0]) in rel2tuple['R'+str(l-2-start)]:
                        path = list(l_part) + [(l_part[-1][1], close_tu[0])]
                        results2wgt[tuple(path)] = l_part_2weight[l_part] + tuple2weight[(l_part[-1][1], close_tu[0])]
                        results.append(path)
        ret = dict()
        for result in results:
            ret[tuple(result)] = results2wgt[tuple(result)]
        return ret
        # only return those that are in the result, throw away dangling ones.


'''
def l_cycle_naive(l, k):
    attr_card = [4, 2, 2, 4, 5]
    var2cand = semi_join_utils.build_data(l, attr_card)
    min_relations, tuple2weight = semi_join_utils.build_relation(l, var2cand, weightrange=10)
    tu2down_neis, tu2up_neis = cycle_SJ_reduce_l(min_relations, l)
    TOP_K_PQ = priority_search_l_cycle_naive(k, min_relations, tuple2weight, tu2down_neis, l)
    if l == 4:
        TOP_K_PQ2 = semi_join_utils.priority_search_4(k, min_relations, tuple2weight, tu2down_neis)
        assert TOP_K_PQ == TOP_K_PQ2
'''

def l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak, Lazy, PQmode, bound, debug):
    time_start = timeit.default_timer()

    partitions = l_cycle_database_partition(rel2tuple, l)
    small_PQ_list = []
    tuple2rem_list = []
    tu2down_neis_list = []
    tu2up_neis_list = []
    TOP_K = []
    time_for_each = []
    prev2sortedmap = None
    prev2heap = None
    bp2heap = None
    prev2sortedmaps = []
    prev2heaps = []



    for partition_index in range(l):
        # with a heavy case: call naive

        rotated_subdatabase = cycle_rotate(partitions[partition_index], partition_index, l)

        bp_set, bptu2down_neis, bptu2up_neis = cycle_SJ_reduce_l(rotated_subdatabase, l)
        tu2down_neis_list.append(bptu2down_neis)
        tu2up_neis_list.append(bptu2up_neis)

        if Deepak:
            prev2sortedmap, prev2heap, tuple2rem, PQ = priority_search_l_cycle_naive_init(rotated_subdatabase, tuple2weight, bp_set, bptu2down_neis, l, Deepak, Lazy, PQmode, bound)
            if debug:
                assert type(prev2sortedmap) == dict
            prev2sortedmaps.append(prev2sortedmap)
            prev2heaps.append(prev2heap)
        else:
            tuple2rem, PQ = priority_search_l_cycle_naive_init(rotated_subdatabase, tuple2weight, bp_set, bptu2down_neis, l, Deepak, Lazy, PQmode, bound)
        small_PQ_list.append(PQ)  # small_PQ_list[i] is i-th partition's local PQ.
        tuple2rem_list.append(tuple2rem)  # this is different for subdatabases, need to keep.

    # all light case
    tu2down_neis, tu2up_neis = cycle_SJ_reduce_l_light(partitions[l], l)
    if Deepak:
        bp2sortedmap, bp2heap, breakpoints2I2, I2_list2wgt, PQ = \
            priority_search_l_cycle_light_init(partitions[l], tuple2weight, tu2down_neis, l, Deepak, Lazy, PQmode, bound)
    else:
        bp2sortedmap, breakpoints2I2, I2_list2wgt, PQ = \
            priority_search_l_cycle_light_init(partitions[l], tuple2weight, tu2down_neis, l, Deepak, Lazy, PQmode, bound)
    small_PQ_list.append(PQ)

    # start global search
    head_values = []

    for i in range(len(small_PQ_list)):
        PQ = small_PQ_list[i]
        if PQ.size() == 0:
            head_values.append(99999999)  # mark that empty PQ as infinate large head value, since we look for lightest
        else:
            top_PEI = PQ.min_weight()  # peek at top result
            if debug:
                assert isinstance(top_PEI, globalclass.PEI_cycle)
            cur_value = top_PEI.wgt + top_PEI.hrtc
            head_values.append(cur_value)
    if debug:
        assert len(head_values) == l + 1
    min_value = min(head_values)
    top_pos = head_values.index(min_value)
    #if top_pos == l:
    #    print "top is a light!"

    while True:
        # popped instance from the top_pos PQ
        # get the next result from there.
        if head_values[top_pos] == 99999999:  # another way to tell all empty..
            break

        if top_pos != l :  # regular partition
            if Deepak:
                prev2sortedmap = prev2sortedmaps[top_pos]
                prev2heap = prev2heaps[top_pos]
            next_result = priority_search_l_cycle_naive_next \
                (tuple2weight, tu2down_neis_list[top_pos], l, small_PQ_list[top_pos], tuple2rem_list[top_pos],
                 prev2sortedmap, prev2heap, Deepak, Lazy)
            #if len(TOP_K)!= 0 and next_result.wgt == TOP_K[-1].wgt:
            #    print next_result.instance.R_list
            #    print TOP_K[-1].instance.R_list
            #debug usage only

        else:  # all light partition

            next_result = priority_search_l_cycle_light_next(breakpoints2I2, I2_list2wgt, small_PQ_list[l], bp2sortedmap, bp2heap, Deepak, Lazy)
            if not next_result:
                head_values[top_pos] = 99999999
            elif isinstance(next_result, globalclass.PEI_lightcycle) and (len(TOP_K)== 0 or len(TOP_K)!= 0):# and next_result.instance.R_list != TOP_K[-1].instance.R_list):  # when there is no next, maybe nontype.
                TOP_K.append(next_result)
                time_end = timeit.default_timer()
                time_for_each.append(time_end - time_start)
                time_start = time_end
            else:  # this PQ is done.
                head_values[top_pos] = 99999999
        
        ## Append to TOPK
        if not next_result:
            head_values[top_pos] = 99999999
        elif len(TOP_K)== 0 or next_result.instance.R_list != TOP_K[-1].instance.R_list:
            TOP_K.append(next_result)
            ## Decrease the size of all PQs
            for small_PQ in small_PQ_list:    
                small_PQ.decrease_max_size()    
 
            time_end = timeit.default_timer()
            time_for_each.append(time_end - time_start)
            time_start = time_end
        else:  # this PQ is done.
            head_values[top_pos] = 99999999

        # update the best value of this small PQ, if there is still some in there.
        if small_PQ_list[top_pos].size() != 0:
            new_top_PEI = small_PQ_list[top_pos].min_weight()   # peek
            cur_value = new_top_PEI.wgt + new_top_PEI.hrtc
            head_values[top_pos] = cur_value
        else:  # this PQ is done.
            head_values[top_pos] = 99999999

        # find the smallest head value and set that to top_position.
        min_value = min(head_values)
        top_pos = head_values.index(min_value)

        # terminate when all small PQs are empty
        all_empty = True
        for small_PQ in small_PQ_list:
            if small_PQ.size() != 0:
                all_empty = False
        if all_empty:
            break
        # terminate when TOP_K is full
        if len(TOP_K) == k:
            break

    return TOP_K, time_for_each


def l_cycle_split(l, k, test, PQmode, bound):
    attr_card = [2, 2, 2, 2, 2]
    var2cand = semi_join_utils.build_data(l, attr_card)
    rel2tuple, tuple2weight = semi_join_utils.build_relation(l, var2cand, weightrange=10)
    assert rel2tuple == cycle_rotate(rel2tuple, l, l)
    assert rel2tuple == cycle_rotate(rel2tuple, 0, l)

    if l == 4  and test:
        tu2down_neis4, tu2up_neis4 = semi_join_utils.full_SJ_reduce_4(rel2tuple)
        TOP_K_PQ2 = semi_join_utils.priority_search_4(k, rel2tuple, tuple2weight, tu2down_neis4)
        cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis4, tu2down_neis4, k, l, True, debug=True)
        cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis4, tu2down_neis4, k, l, False, debug=True)

    print "previous cycles"
    TOP_K_max, time_for_each_max = l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, False, PQmode, bound, debug=True)
    print "TOP K results are"
    for PEI in TOP_K_max:
        print PEI.wgt

    print "Deepak improved cycles"
    TOP_K_sort, time_for_each_sort = l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, True, PQmode, bound, debug=True)
    print "TOP K results are"
    for PEI in TOP_K_sort:
        print PEI.wgt

    if l == 4 and test:
        if len(TOP_K_max) != len(TOP_K_PQ2):
            print "missed instances from PQs"
        assert len(TOP_K_max) == len(TOP_K_PQ2)

    ## Verify results
    if len(TOP_K_max) != len(TOP_K_sort): print "== Error!!! Not the same length!"
    for i in range(len(TOP_K_max)):
        if not TOP_K_max[i].same_as(TOP_K_sort[i]):
            print "== Error!!! Different results!"

    return TOP_K_sort

def test_correctness():
    while True:
        l_cycle_split(5, 3, test=True)

def run_path_example(n, l, k, PQmode, bound):
    import DataGenerator

    rel2tuple, tuple2weight = DataGenerator.getDatabase("Path", n, l, "Full", "HardCase", 2)
    tu2down_neis, tu2up_neis = path_SJ_reduce_l(rel2tuple, l)
    print "PATH algo: any-k sort"
    TOP_K_sort, time_for_each_sort = priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak= True, Lazy= False, PQmode = PQmode, bound = bound, debug = True)
    print "PATH algo: any-k max"
    TOP_K_max, time_for_each_max = priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak= False, Lazy= False, PQmode = PQmode, bound = bound, debug = True)
    print "PATH algo: any-k lazy"
    TOP_K_max, time_for_each_max = priority_search_l_path(k, rel2tuple, tuple2weight, tu2down_neis, l, Deepak=True,
                                                          Lazy=True, PQmode=PQmode, bound=bound, debug=True)
    print "PATH algo: enumerate all"
    sorted_values = path_enumerate_all(rel2tuple, tuple2weight, tu2down_neis, k, l, debug = True)

    ## Verify results
    if len(TOP_K_max) != len(TOP_K_sort): 
        print "== Error (Path)!!! Not the same length!"
    for i in range(len(TOP_K_max)):
        if not TOP_K_max[i].same_as(TOP_K_sort[i]):
            print "== Error (Path)!!! Different results!"

    print len(sorted_values)
    if len(TOP_K_max) != min(k, len(sorted_values)):
        print "== Error (Path)!!! FE produces different amount of results!"
    for i in range(len(TOP_K_max)):
        if format(TOP_K_max[i].wgt, '.4f') != format(sorted_values[i], '.4f'):
            print "== Error (Path)!!! " + str(TOP_K_max[i].wgt) + " different than " + str(sorted_values[i])

def run_cycle_example(n, l, k, PQmode, bound):
    import DataGenerator

    rel2tuple, tuple2weight = DataGenerator.getDatabase("Cycle", n, l, "Full", "HardCase", 2)
    tu2down_neis, tu2up_neis = cycle_SJ_reduce_l_light(rel2tuple, l)
    print "Cycle algo: any-k sort"
    TOP_K_sort, time_for_each_sort = l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=True, Lazy=False,PQmode= PQmode, bound = bound, debug = True)
    for PEI in TOP_K_sort:
        print PEI.wgt
    print "Cycle algo: any-k max"
    TOP_K_max, time_for_each_max = l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=False, Lazy=False, PQmode=PQmode, bound=bound, debug=True)
    for PEI in TOP_K_max:
        print PEI.wgt
    print "Cycle algo: any-k lazy"
    TOP_K_lazy, time_for_each_lazy = l_cycle_split_prioritied_search(rel2tuple, tuple2weight, k, l, Deepak=True,
                                                                       Lazy=True, PQmode=PQmode, bound=bound,
                                                                       debug=True)
    for PEI in TOP_K_max:
        print PEI.wgt

    print "Cycle algo: enumerate all"
    results, sorted_values = cycle_enumerate_all(rel2tuple, tuple2weight, tu2up_neis, tu2down_neis, k, l, False, debug= True)
 
    ## Verify results
    if len(TOP_K_max) != len(TOP_K_sort): 
        print "== Error (Cycle)!!! Not the same length!"

    print len(TOP_K_sort)
    print len(TOP_K_lazy)
    assert len(TOP_K_lazy) == len(TOP_K_sort)
    assert len(time_for_each_lazy) == len(time_for_each_sort)

    for i in range(len(TOP_K_max)):
        print TOP_K_max[i].wgt
        print TOP_K_sort[i].wgt
        assert format(TOP_K_max[i].wgt, '.4f') == format(TOP_K_sort[i].wgt, '.4f')
        if not TOP_K_max[i].same_as(TOP_K_sort[i]):
            print "== Error (Cycle)!!! Sort and max different results!"

    if len(TOP_K_max) != min(k, len(sorted_values)):
        print "== Error (Cycle)!!! FE produces different amount of results!"

    for i in range(len(TOP_K_max)):
        assert format(TOP_K_max[i].wgt, '.4f') == format(sorted_values[i], '.4f')
        if format(TOP_K_max[i].wgt, '.4f') != format(sorted_values[i], '.4f'):
            print "== Error (Cycle)!!! " + str(TOP_K_max[i].wgt) + " different than " + str(sorted_values[i])

if __name__ == "__main__":
    l_path_sim(4, 5, PQmode="Heap", bound=5)
    #l_cycle_naive(5, 3)
    #l_cycle_split(3, 5, test=False, PQmode="Heap", bound=3)

    #test_correctness()
    while(True):
        for l in [5, 6, 7]:
            #run_path_example(n=100, l=l, k=100000, PQmode="Heap", bound=None)
            run_cycle_example(n=100, l=l, k=100000, PQmode="Heap", bound=None)



