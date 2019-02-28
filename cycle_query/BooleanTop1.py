import CQ
import ranked_list
import globalclass
import copy
import timeit
import semi_join_utils
import sys

#def l_cycle_split_bool(rel2tuple, tuple2weight, k, l, Deepak, RLmode, bound, debug):
    # split the cycle, run boolean on each, if there is any result in each, return True

#def l_cycle_split_top1(rel2tuple, tuple2weight, k, l, Deepak, RLmode, bound, debug):
    # split the cycle, find the top 1 of each, then find the top 1 of all l + 1 partitions.

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
        if len(r) == 0:
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



if __name__ == "__main__":
    # test top-1
    import DataGenerator

    n = 10
    l = 4
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
        assert  format(TOP_K_sort[0].wgt, '.4f') == format(Top1.wgt, '.4f')