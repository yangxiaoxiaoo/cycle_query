import math
import random
import heapq
import globalclass
import copy
import time
import semi_join_utils

def path_SJ_reduce_l(rel2tuple, l):
    #path semi-join bottom-up, build dictionary to connected tuples.

    tu2down_neis, tu2up_neis = semi_join_utils.semi_join('R0', 'R1', rel2tuple)
    for relation_index in range(1, l-1):
        tu2down_neis1, tu2up_neis1 = semi_join_utils.semi_join('R'+str(relation_index), 'R'+str(relation_index + 1), rel2tuple)
        tu2up_neis.update(tu2up_neis1)
        tu2down_neis.update(tu2down_neis1)


    return tu2down_neis, tu2up_neis


def cycle_SJ_reduce_l(rel2tuple, l):
    #cycle SJ build dictionary to neighbors. Add closing one R(l-1) to R0

    tu2down_neis, tu2up_neis = semi_join_utils.semi_join('R0', 'R1', rel2tuple)
    for relation_index in range(1, l-1):
        tu2down_neis1, tu2up_neis1 = semi_join_utils.semi_join('R'+str(relation_index), 'R'+str(relation_index + 1), rel2tuple)
        tu2up_neis.update(tu2up_neis1)
        tu2down_neis.update(tu2down_neis1)

    tu2down_neis1, tu2up_neis1 = semi_join_utils.semi_join('R'+str(l-1), 'R0', rel2tuple)
    tu2up_neis.update(tu2up_neis1)
    tu2down_neis.update(tu2down_neis1)

    return tu2down_neis, tu2up_neis


def priority_search_l_cycle_naive(K, rel2tuple, tuple2weight, tu2down_neis, l):

    TOP_K = []
    PQ = []
    tuple2rem = heuristic_build_l_cycle(tuple2weight, rel2tuple, tu2down_neis, l)
    for tu in rel2tuple['R0']:
        if (tu, tu[0]) in tuple2rem:
            heapq.heappush(PQ, globalclass.PEI_cycle(tu, tuple2weight[tu], tuple2rem[(tu, tu[0])], l))

    while len(PQ) != 0:
        cur_PEI_cycle = heapq.heappop(PQ)
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
                    heapq.heappush(PQ, new_PEI)

        else:  # length == l, check breakpoint
            frontier = cur_PEI_cycle.instance.frontier()
            for neighbor in tu2down_neis[frontier]:
                if neighbor[1] == cur_PEI_cycle.breakpoint:
                    new_PEI = copy.deepcopy(cur_PEI_cycle)
                    new_PEI.merge(neighbor, tuple2weight, tuple2rem)
                    heapq.heappush(PQ, new_PEI)
    print "TOP K results are"
    for PEI_cycle in TOP_K:
        print PEI_cycle.wgt
    assert len(TOP_K) == K or len(PQ) == 0
    return TOP_K


def heuristic_build_l_cycle(tuple2weight, rel2tuple, tu2down_neis, l):
    # build a dictionary from tuple down to the remaining weight not including tuple
    # assumption: no tuple appear in different relations

    tuple2rem = dict()
    breakpoints = set()
    for tu in rel2tuple['R'+ str(l-1)]:
        breakpoints.add(tu[1])

    for tu in rel2tuple['R'+ str(l-2)]:
        for tu_down in tu2down_neis[tu]:
            new_val = tuple2weight[tu_down]
            if (tu, tu_down[1]) in tuple2rem:
                tuple2rem[(tu, tu_down[1])] = min(tuple2rem[(tu, tu_down[1])], new_val)
            else:
                tuple2rem[(tu, tu_down[1])] = new_val

    for which_relation in range(l-3, -1, -1): # when l = 4, which_relation will be 1, 0
        this_relation_name = 'R'+str(which_relation)
        for tu in rel2tuple[this_relation_name]:
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

    return tuple2rem


def heuristic_build_l_path(tuple2weight, rel2tuple, tu2down_neis, l):
    # build a dictionary from tuple down to the remaining weight not including tuple
    # assumption: no tuple appear in different relations

    tuple2rem = dict()

    for which_relation in range(l-2, -1, -1): # when l = 4, which_relation will be 2, 1, 0
        this_relation_name = 'R'+str(which_relation)
        for tu in rel2tuple[this_relation_name]:
            for tu_down in tu2down_neis[tu]:
                new_val = tuple2weight[tu_down]
                if tu in tuple2rem:
                    tuple2rem[tu] = min(tuple2rem[tu], new_val)
                else:
                    tuple2rem[tu] = new_val


    return tuple2rem


def priority_search_l_path(K, rel2tuple, tuple2weight, tu2down_neis, l):
    # push PEIs into a priority queue, pop k heaviest full items
    # [DESIGN CHOICE] pop the lightest element as consistent with heapq native! If paper is about heaviest, can modify later.
    TOP_K = []
    PQ = []
    tuple2rem = heuristic_build_l_path(tuple2weight, rel2tuple, tu2down_neis, l)
    for tu in rel2tuple['R0']:
        if tu in tuple2rem:
            heapq.heappush(PQ, globalclass.PEI_path(tu, tuple2weight[tu], tuple2rem[tu], l))

    while len(PQ) != 0:
        cur_PEI_path = heapq.heappop(PQ)
        if cur_PEI_path.instance.completion:
            TOP_K.append(cur_PEI_path)
            if len(TOP_K) == K:
                break
        elif cur_PEI_path.instance.length != l-1: # not completed, there is frontier, no need to check breakpoint
            frontier = cur_PEI_path.instance.frontier()
            for neighbor in tu2down_neis[frontier]:
                if cur_PEI_path.mergable(neighbor, tuple2rem):
                    new_PEI_path = copy.deepcopy(cur_PEI_path)
                    new_PEI_path.merge(neighbor, tuple2weight, tuple2rem)
                    heapq.heappush(PQ, new_PEI_path)

        else:  # length == l-1, last growth.
            frontier = cur_PEI_path.instance.frontier()
            for neighbor in tu2down_neis[frontier]:
                new_PEI_path = copy.deepcopy(cur_PEI_path)
                new_PEI_path.merge(neighbor, tuple2weight, tuple2rem)
                heapq.heappush(PQ, new_PEI_path)
    print "TOP K results are"
    for PEI_path in TOP_K:
        print PEI_path.wgt
    assert len(TOP_K) == K or len(PQ) == 0
    return TOP_K


def l_path_sim(l):
    degrees = [4, 2, 2, 4]
    var2cand = semi_join_utils.build_data(l, degrees)
    min_relations, tuple2weight = semi_join_utils.build_relation(l, var2cand, weightrange=10)
    tu2down_neis, tu2up_neis = path_SJ_reduce_l(min_relations, l)
    TOP_K_PQ = priority_search_l_path(5, min_relations, tuple2weight, tu2down_neis, l)

def l_cycle_sim(l):
    degrees = [4, 2, 2, 4]
    var2cand = semi_join_utils.build_data(l, degrees)
    min_relations, tuple2weight = semi_join_utils.build_relation(l, var2cand, weightrange=10)
    tu2down_neis, tu2up_neis = cycle_SJ_reduce_l(min_relations, l)
    TOP_K_PQ = priority_search_l_cycle_naive(5, min_relations, tuple2weight, tu2down_neis, l)
    TOP_K_PQ2 = semi_join_utils.priority_search_4(5, min_relations, tuple2weight, tu2down_neis)
    assert TOP_K_PQ == TOP_K_PQ2

if __name__ == "__main__":
    l_path_sim(4)
    l_cycle_sim(4)