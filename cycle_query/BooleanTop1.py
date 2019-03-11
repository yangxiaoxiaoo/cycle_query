import CQ
import ranked_list
import globalclass
import copy
import timeit
import semi_join_utils
import sys
import DataGenerator


def l_cycle_split_bool(rel2tuple, tuple2weight, l):
    # split the cycle, run boolean on each, if there is any result in each, return True
    time_start = timeit.default_timer()
    res = False
    partitions = CQ.l_cycle_database_partition(rel2tuple, l)
    for partition_index in range(l):
        # with a heavy case: call naive

        rotated_subdatabase = CQ.cycle_rotate(partitions[partition_index], partition_index, l)
        bp_set, rel2tuplebp = semi_join_utils.explode_bp(rotated_subdatabase, l)

        for bp in bp_set:
            cur_bool = True
            for i in range(l-1):
                R_start = 'R'+str(i)
                R_end = 'R'+ str(i+1)
                semi_join_utils.semi_join_bp(R_start, R_end, rel2tuplebp, bp)
            for i in range(l-1, 0, -1):
                R_start = 'R' + str(i - 1)
                R_end = 'R' + str(i)
                semi_join_utils.semi_join_reverse_bp(R_start, R_end, rel2tuplebp, bp)
            for r in rel2tuplebp[bp]:
                if len(rel2tuplebp[bp][r]) == 0:
                    cur_bool = False
            res = cur_bool or res
            if res: # pre-exit
                time_end = timeit.default_timer()
                return res, time_end - time_start

            # if one bp is True, then total true. If one partition true, then total true.
        
    # TODO add all light one
        # all light
    light_bool = False
    bp2sortedmap, breakpoints2I2, I2_list2wgt, cur_PEI_cycle = Deepak_sort_alllight_top1(partitions[l], tuple2weight, l)
    if cur_PEI_cycle:
        light_bool = True
    res = res or light_bool

    time_end = timeit.default_timer()
    return res, time_end - time_start

def l_cycle_split_top1(rel2tuple, tuple2weight,l):
    # split the cycle, find the top 1 of each, then find the top 1 of all l + 1 partitions.
    time_start = timeit.default_timer()
    partitions = CQ.l_cycle_database_partition(rel2tuple, l)
    each_min = []
    for partition_index in range(l):

        rotated_subdatabase = CQ.cycle_rotate(partitions[partition_index], partition_index, l)
        bp_set, bptu2down_neis, bptu2up_neis = CQ.cycle_SJ_reduce_l(rotated_subdatabase, l)
        tuple2rem = CQ.heuristic_build_l_cycle(tuple2weight, rotated_subdatabase, bp_set, bptu2down_neis, l)
        prev2top = Deepak_sort_cycle_top1(tuple2rem, tuple2weight, rotated_subdatabase, l)
        cur_partition_min = None

        for k in prev2top:
            if k[0] == 0:

                tu = prev2top[k]['#']  # first
                if not cur_partition_min:

                    cur_partition_min = globalclass.PEI_cycle(tu, tuple2weight[tu], tuple2rem[(tu, tu[0])], l)

                else:
                    cur_partition_min = min(cur_partition_min, globalclass.PEI_cycle(tu, tuple2weight[tu], tuple2rem[(tu, tu[0])], l))
                assert cur_partition_min


        if cur_partition_min:
           # print "there are results"
           # print partition_index
            while not cur_partition_min.instance.completion:
                cur_partition_min.expand(prev2top, tuple2weight, tuple2rem)
            assert cur_partition_min.instance.completion
            each_min.append(cur_partition_min)
        #else:
            #print "no result in this partition"
            #print partition_index

    # all light
    bp2sortedmap, breakpoints2I2, I2_list2wgt, cur_PEI_cycle = Deepak_sort_alllight_top1(partitions[l], tuple2weight, l)
    if cur_PEI_cycle:
        cur_PEI_cycle.bigexpand(breakpoints2I2, I2_list2wgt, bp2sortedmap)
        assert cur_PEI_cycle.instance.completion
        each_min.append(cur_PEI_cycle)


    time_end = timeit.default_timer()
    #print "min comes from partition"
    #for PEI in each_min:
    #    print PEI.wgt
    #print each_min.index(min(each_min))
    return min(each_min), time_end - time_start





def l_path_bool(rel2tuple, l):
    # run 2-way semi-join reduction and see if there is empty relations.
    start_time = timeit.default_timer()
    res = True
    for i in range(l-1):
        R_start = 'R'+str(i)
        R_end = 'R'+ str(i+1)
        semi_join_utils.semi_join(R_start, R_end, rel2tuple)

    for i in range(l-1, 0, -1):
        R_start = 'R' + str(i-1)
        R_end = 'R' + str(i)
        semi_join_utils.semi_join_reverse(R_start, R_end, rel2tuple)

    for r in rel2tuple:
        if len(rel2tuple[r]) == 0:
            res = False
    end_time = timeit.default_timer()

    return res, end_time - start_time

def l_path_top1(rel2tuple, tuple2weight, tu2down_neis, l):
    # semi-join up, compute top-1 mappings, then construct the result following this mapping.
    start_time = timeit.default_timer()
    tuple2rem = CQ.heuristic_build_l_path(tuple2weight, rel2tuple, tu2down_neis, l)
    prev2top = Deepak_sort_path_top1(tuple2rem, tuple2weight, rel2tuple, l)
    res = None
    for k in prev2top:
        if k[0] == 0:
            tu = prev2top[k]['#']  # first
            if not res:
                res = globalclass.PEI_path(tu, tuple2weight[tu], tuple2rem[tu], l)
            else:
                res = min(res, globalclass.PEI_path(tu, tuple2weight[tu], tuple2rem[tu], l))

    while not res.instance.completion:
        res.expand(prev2top, tuple2weight, tuple2rem)

    assert res.instance.completion
    end_time = timeit.default_timer()

    return res, end_time - start_time



def Deepak_sort_path_top1(tuple2rem, tuple2weight, rel2tuple, l):
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
        top1 = min(list)
        if len(list)!= 0:
            localdict['#'] = top1[1]
        res[k] = localdict
    return res


def Deepak_sort_cycle_top1(tuple2rem, tuple2weight, rel2tuple, l):
    # l is the goal length, build sorted subtree weights for R0, R1...Rl-1
    key2list = dict() # first map all keys in the output dictionary into a list of (subtree-weight, tuple)
    breakpoints = set()

    for i in range(l-1, -1, -1):
        relation = 'R' + str(i)
        if i == l-1:
            for t in rel2tuple[relation]:
                breakpoints.add(t[1])
                if (i, t[0], t[1]) in key2list:
                    key2list[i, t[0], t[1]].append((tuple2weight[t], t))
                else:
                    key2list[i, t[0], t[1]] = [(tuple2weight[t], t)]
        else:
            for t in rel2tuple[relation]:
                for bp in breakpoints:
                    if (t, bp) in tuple2rem:
                        if (i, t[0], bp) in key2list:
                            key2list[i, t[0], bp].append((tuple2weight[t] + tuple2rem[t, bp], t))
                        else:
                            key2list[i, t[0], bp] = [(tuple2weight[t] + tuple2rem[t, bp], t)]
    res = dict()
    for k in key2list:
        localdict = dict()
        list = key2list[k]
        top_1 = min(list)
        # print list
        if len(list)!= 0:
            localdict['#'] = top_1[1]
        res[k] = localdict
    return res



def Deepak_sort_alllight_top1(db, tuple2weight, l):
    minPEI = None
    tu2down_neis, tu2up_neis = CQ.cycle_SJ_reduce_l_light(db, l)
    I1_list2wgt = CQ.simple_join(db, tuple2weight, tu2down_neis, 0, int(l / 2))
    I2_list2wgt = CQ.simple_join(db, tuple2weight, tu2down_neis, int(l / 2), l)
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
            if not minPEI:
                minPEI = curPEI
            else:
                minPEI = min(minPEI, curPEI)
    key2list = dict()
    bp2sortedmap = dict()
    for bp in breakpoints2I2:
        key2list[bp] = []
        for i2 in breakpoints2I2[bp]:
            key2list[bp].append((I2_list2wgt[i2], i2))
    for k in key2list:
        localdict = dict()
        list = key2list[k]
        top_1 = min(list)
        if len(list) != 0:
            localdict['#'] = top_1[1]
        # keep only a dictionary to top-1
        bp2sortedmap[k] = localdict

    return bp2sortedmap, breakpoints2I2, I2_list2wgt, minPEI





def test_path(n, l):
    rel2tuple, tuple2weight = DataGenerator.getDatabase("Path", n, l, "Full", "HardCase", 2)
    tu2down_neis, tu2up_neis = CQ.path_SJ_reduce_l(rel2tuple, l)
    print "PATH algo: any-k sort"
    TOP_K_sort, time_for_each_sort = CQ.priority_search_l_path(3, rel2tuple, tuple2weight, tu2down_neis, l,
                                                               Deepak=True, RLmode='PQ', bound=None, debug=True)
    exist, time1 = l_path_bool(rel2tuple, l)
    print exist
    if exist:
        assert len(TOP_K_sort) > 0
        print TOP_K_sort[0].wgt

        Top1, time2 = l_path_top1(rel2tuple, tuple2weight, tu2down_neis, l)
        print Top1.wgt
        assert format(TOP_K_sort[0].wgt, '.4f') == format(Top1.wgt, '.4f')


def test_cycle(n, l):

    rel2tuple, tuple2weight = DataGenerator.getDatabase("Cycle", n, l, "Full", "HardCase", 2)
    tu2down_neis, tu2up_neis = CQ.path_SJ_reduce_l(rel2tuple, l)
    print "Cycle algo: any-k sort"
    TOP_K_sort, time_for_each_sort = CQ.l_cycle_split_prioritied_search(rel2tuple, tuple2weight, 3, l, Deepak=True, RLmode= 'PQ', bound = None, debug = True)

    exist, time1 = l_cycle_split_bool(rel2tuple, tuple2weight, l)
    print exist
    if exist:
        assert len(TOP_K_sort) > 0
        print TOP_K_sort[0].wgt

        Top1, time2 = l_cycle_split_top1(rel2tuple, tuple2weight, l)
        print Top1.wgt
        assert format(TOP_K_sort[0].wgt, '.4f') == format(Top1.wgt, '.4f')

if __name__ == "__main__":
    # test top-1


    n = 100
    l = 4
    test_path(n, l)
    test_cycle(n, l)
