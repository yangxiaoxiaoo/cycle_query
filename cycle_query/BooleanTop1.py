import CQ
import ranked_list
import globalclass
import copy
import timeit
import semi_join_utils
import sys

def l_cycle_split_prioritied_bool(rel2tuple, tuple2weight, k, l, Deepak, RLmode, bound, debug):
    # split the cycle, run boolean on each, if there is any result in each, return True

def l_cycle_split_prioritied_top1(rel2tuple, tuple2weight, k, l, Deepak, RLmode, bound, debug):
    # split the cycle, find the top 1 of each, then find the top 1 of all l + 1 partitions.

def priority_search_l_path_bool(K, rel2tuple, tuple2weight, tu2down_neis, l, Deepak, RLmode, bound, debug):
    # run 2-way semi-join reduction and see if there is empty relations.


def priority_search_l_path_top1(K, rel2tuple, tuple2weight, tu2down_neis, l, Deepak, RLmode, bound, debug):
    # semi-join up, compute top-1 mappings, then construct the result following this mapping.