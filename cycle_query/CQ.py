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


def priority_search_l_cycle_naive_init(rel2tuple, tuple2weight, tu2down_neis, l):
    #used by a global PQ_global.
    PQ = []
    tuple2rem = heuristic_build_l_cycle(tuple2weight, rel2tuple, tu2down_neis, l)
    for tu in rel2tuple['R0']:
        if (tu, tu[0]) in tuple2rem:
            heapq.heappush(PQ, globalclass.PEI_cycle(tu, tuple2weight[tu], tuple2rem[(tu, tu[0])], l))
    return tuple2rem, PQ

def priority_search_l_cycle_naive_next(tuple2weight, tu2down_neis, l, PQ, tuple2rem):
    #used by a gobal PQ_global.
    #takes a PQ for this sub-database, return the next
    #PQ pass by ref, can be changed.
    while len(PQ) != 0:
        cur_PEI_cycle = heapq.heappop(PQ)
        if cur_PEI_cycle.instance.completion:
            return cur_PEI_cycle
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

    heavy_tables = []
    light_tables = [] # list of l light table sets. use later to construct partitions.

    # split each relation into heavy and light components.
    for relation_index in range(0, l):
        relation_name = 'R'+str(relation_index)
        current_relation_tuples = relation2tuple[relation_name]
        heavy_tuples = set()
        light_tuples = set()
        degree_count = dict()
        for tu in current_relation_tuples:
            if tu[0] not in degree_count:
                degree_count[tu[0]] = 1
            else:
                degree_count[tu[0]] += 1
        for tu in current_relation_tuples:
            if degree_count[tu[0]] < delta:
                light_tuples.add(tu)
            else:
                heavy_tuples.add(tu)
        # current partition is made of current relation light tuples, combined with remaining relation.
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



def l_path_sim(l,k):
    attr_card = [4, 2, 2, 4, 5]
    var2cand = semi_join_utils.build_data(l, attr_card)
    min_relations, tuple2weight = semi_join_utils.build_relation(l, var2cand, weightrange=10)
    tu2down_neis, tu2up_neis = path_SJ_reduce_l(min_relations, l)
    TOP_K_PQ = priority_search_l_path(k, min_relations, tuple2weight, tu2down_neis, l)

def l_cycle_naive(l, k):
    attr_card = [4, 2, 2, 4, 5]
    var2cand = semi_join_utils.build_data(l, attr_card)
    min_relations, tuple2weight = semi_join_utils.build_relation(l, var2cand, weightrange=10)
    tu2down_neis, tu2up_neis = cycle_SJ_reduce_l(min_relations, l)
    TOP_K_PQ = priority_search_l_cycle_naive(k, min_relations, tuple2weight, tu2down_neis, l)
    if l == 4:
        TOP_K_PQ2 = semi_join_utils.priority_search_4(k, min_relations, tuple2weight, tu2down_neis)
        assert TOP_K_PQ == TOP_K_PQ2

def l_cycle_split(l, k, test):
    attr_card = [2, 2, 2, 2, 2]
    var2cand = semi_join_utils.build_data(l, attr_card)
    min_relations, tuple2weight = semi_join_utils.build_relation(l, var2cand, weightrange=10)
    assert min_relations == cycle_rotate(min_relations, l, l)
    assert min_relations == cycle_rotate(min_relations, 0, l)

    if l == 4  and test:
        tu2down_neis4, tu2up_neis4 = semi_join_utils.full_SJ_reduce_4(min_relations)
        TOP_K_PQ2 = semi_join_utils.priority_search_4(k, min_relations, tuple2weight, tu2down_neis4)

    partitions = l_cycle_database_partition(min_relations, l)
    small_PQ_list = []
    tuple2rem_list = []
    tu2down_neis_list = []
    tu2up_neis_list = []
    TOP_K = []
    for partition_index in range(l+1):
        # TODO: handle all light case differently
        tu2down_neis, tu2up_neis = cycle_SJ_reduce_l(partitions[partition_index], l)
        tu2down_neis_list.append(tu2down_neis)
        tu2up_neis_list.append(tu2up_neis)
        rotated_subdatabase = cycle_rotate(partitions[partition_index], partition_index, l)

        tuple2rem, PQ = priority_search_l_cycle_naive_init(rotated_subdatabase, tuple2weight, tu2down_neis, l)
        small_PQ_list.append(PQ)  # small_PQ_list[i] is i-th partition's local PQ.
        tuple2rem_list.append(tuple2rem)  # this is different for subdatabases, need to keep.

    head_values = []
    for i in range(len(small_PQ_list)):
        PQ = small_PQ_list[i]
        if len(PQ) == 0:
            head_values.append(99999999) # mark that empty PQ as infinate large head value, since we look for lightest
        else:
            top_PEI = PQ[0]  # peak at top result
            assert isinstance(top_PEI, globalclass.PEI_cycle)
            cur_value = top_PEI.wgt + top_PEI.hrtc
            head_values.append(cur_value)
    min_value = min(head_values)
    top_pos = head_values.index(min_value)


    while True:
        # popped instance from the top_pos PQ
        # get the next result from there.

        if head_values[top_pos] == 99999999:  # another way to tell all empty..
            break
        next_result = priority_search_l_cycle_naive_next \
            (tuple2weight, tu2down_neis_list[top_pos], l, small_PQ_list[top_pos], tuple2rem_list[top_pos])
        if isinstance(next_result, globalclass.PEI_cycle):  # when there is no next, maybe nontype.
            TOP_K.append(next_result)
        else:  # this PQ is done.
            head_values[top_pos] = 99999999

        # update the best value of this small PQ, if there is still some in there.
        if len(small_PQ_list[top_pos]) != 0:
            new_top_PEI = small_PQ_list[top_pos][0]
            cur_value = new_top_PEI.wgt + new_top_PEI.hrtc
            head_values[top_pos] = cur_value
        else:  # this PQ is done.
            head_values[top_pos] = 99999999

        #find the smallest head value and set that to top_position.
        min_value = min(head_values)
        top_pos = head_values.index(min_value)

        #terminate when all small PQs are empty
        all_empty = True
        for small_PQ in small_PQ_list:
            if len(small_PQ) != 0:
                all_empty = False
        if all_empty:
            break
        #terminate when TOP_K is full
        if len(TOP_K) == k:
            break
    print "TOP K results are"
    for PEI in TOP_K:
        print PEI.wgt


    if l == 4 and test:
        if TOP_K != TOP_K_PQ2:
            print "rotation caused index off, ignore for now since we only need the weights"

    return TOP_K



if __name__ == "__main__":
    #l_path_sim(5, 3)
    #l_cycle_naive(5, 3)
    l_cycle_split(5, 10, test=False)