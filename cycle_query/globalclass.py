import functools

@functools.total_ordering
class PEI():
    # earlier hard-coded 4-cycle
    # class of partially explored instance, instance can be any shape later, cycle_instance for now
    # maintaining a field of starting variable for join consistency check later
    def __init__(self, tu, wgt, hrtc):
        self.instance = cycle4_instance(tu)
        self.wgt = wgt
        self.hrtc = hrtc
        self.breakpoint = tu[0]

    def __gt__(self, other):
        return (self.wgt + self.hrtc) > (other.wgt + other.hrtc)

    def __eq__(self, other):
        return (self.wgt + self.hrtc) == (other.wgt + other.hrtc)

    def merge(self, new_tuple, tuple2weight, tuple2rem):
        # merge this partially explored tree with newly added relation
        self.instance.insert_relation(new_tuple)
        self.wgt += tuple2weight[new_tuple]
        self.hrtc = self.instance.max_wgt_rem(tuple2rem, self.breakpoint)

    def mergable(self, new_tuple, tuple2rem):
        # check if this new relation can be added
        # if adding the relation, it's guaranteed that a cycle won't form
        # then return False, else return true.
        return (new_tuple, self.breakpoint) in tuple2rem

@functools.total_ordering
class PEI_path():
    # class of partially explored instance of paths.
    # ALREADY l-general length!
    def __init__(self, tu, wgt, hrtc, l):
        self.instance = path_instance(tu, l)
        self.wgt = wgt
        self.hrtc = hrtc
        self.goal_length = l

    def __gt__(self, other):
        return (self.wgt + self.hrtc) > (other.wgt + other.hrtc)

    def __eq__(self, other):
        return (self.wgt + self.hrtc) == (other.wgt + other.hrtc)

    def merge(self, new_tuple, tuple2weight, tuple2rem):
        # merge this partially explored tree with newly added relation
        self.instance.insert_relation(new_tuple)
        self.wgt += tuple2weight[new_tuple]
        self.hrtc = self.instance.max_wgt_rem(tuple2rem)

    def mergable(self, new_tuple, tuple2rem):
        # check if this new relation can be added
        # if adding the relation, it's guaranteed that a path won't form
        # then return False, else return true.
        return new_tuple in tuple2rem

    def successor(self, sortedmap, tuple2weight, tuple2rem):
        # return a successor of current instance if there exist one, return None if not.
        # input: sorted-map comes from subtree-weight tuple2rem.
        # TODO: write in CQ.py a builder that sort and construct the map to next.
        cur_frontier = self.instance.popfront()

        if cur_frontier == None: # empty path cannot be popped.
            print "empty path considered? Please double check..."
            return None
        if cur_frontier in sortedmap:
            successor_frontier = sortedmap[cur_frontier]  # there is a successor
            assert self.mergable(successor_frontier, tuple2rem)
            self.instance.insert_relation(successor_frontier)
            self.wgt += (tuple2weight[successor_frontier] - tuple2weight[cur_frontier])
            self.hrtc = self.instance.max_wgt_rem(tuple2rem)
        else:
            return None

    def expand(self, sortedmap):
        # TODO: make sure that sortedmap[('#', l , prev)] gives the top result in Rl whose attribute hashes from prev




@functools.total_ordering
class PEI_cycle():
    # any-length cycle
    def __init__(self, tu, wgt, hrtc, l):
        self.instance = cycle_instance(tu, l)
        self.wgt = wgt
        self.hrtc = hrtc
        self.breakpoint = tu[0]
        self.goal_length = l

    def __gt__(self, other):
        return (self.wgt + self.hrtc) > (other.wgt + other.hrtc)

    def __eq__(self, other):
        return (self.wgt + self.hrtc) == (other.wgt + other.hrtc)

    def merge(self, new_tuple, tuple2weight, tuple2rem):
        # merge this partially explored tree with newly added relation
        self.instance.insert_relation(new_tuple)
        self.wgt += tuple2weight[new_tuple]
        self.hrtc = self.instance.max_wgt_rem(tuple2rem, self.breakpoint)

    def mergable(self, new_tuple, tuple2rem):
        # check if this new relation can be added
        # if adding the relation, it's guaranteed that a cycle won't form
        # then return False, else return true.
        return (new_tuple, self.breakpoint) in tuple2rem



@functools.total_ordering
class PEI_lightcycle(PEI_cycle):
    # the right way to call __init__:
    # PEI_lightcycle(I1_list[0], 0, 0, l)
    # leave hrtc to the call of biginit.

    #hrtc is the best I2's weight to this I1_list (a list of all tuples in this I1 instance).
    def biginit(self, I1_list, I1_wgt, hrtc, l):
        for tuple in I1_list[1:]:
            self.instance.insert_relation(tuple)
        self.wgt = I1_wgt
        self.hrtc = hrtc
        self.goal_length = l
        self.breakpointpair = (I1_list[0][0], I1_list[-1][1])

    def bigmerge(self, I2_list, I2_wgt):
        for tuple in I2_list:
            self.instance.insert_relation(tuple)
        self.wgt += I2_wgt
        self.hrtc = 0
        assert self.instance.completion


class path_instance():

    def __init__(self, tu, l):
        # initialize the tuples to dummy values
        #self.R0 = tu
        self.R_list = [tu]
        for i in range(1, l):
            self.R_list.append((0, 0))

        self.length = 1
        self.completion = False
        self.goal_length = l

    def frontier(self):
        assert self.length < self.goal_length
        return self.R_list[self.length - 1]

    def popfront(self):
        if self.completion:
            self.completion = False
        if self.length == 0:
            # no front to pop
            return None
        else:
            front = self.R_list[self.length - 1]
            self.R_list[self.length - 1] = (0, 0)
            self.length -= 1
            return front


    def insert_relation(self, newtuple):
        # take tuple, insert into instance
        assert self.length <= self.goal_length
        assert self.completion == False
        if self.length == 0:
            self.R_list[0] = newtuple
            self.length = 1
        elif self.length == self.goal_length - 1:
            assert self.R_list[self.length - 1][1] == newtuple[0]
            self.R_list[self.length] = newtuple
            self.length += 1
            self.completion = True
        else:
            assert self.R_list[self.length - 1][1] == newtuple[0]
            self.R_list[self.length] = newtuple
            self.length += 1

    def max_wgt_rem(self, tuple2rem):
        # return the min wgt for the remaining part -- lightest weight, lower bound H value
        if self.length == self.goal_length:
            return 0.0
        else:
            return tuple2rem[self.R_list[self.length-1]]


class cycle_instance():

    def __init__(self, tu, l):

        self.R_list = [tu]
        for i in range(1, l):
            self.R_list.append((0, 0))

        self.length = 1
        self.completion = False
        self.goal_length = l

    def frontier(self):
        assert self.length < self.goal_length
        return self.R_list[self.length - 1]

    def insert_relation(self, newtuple):
        # take tuple, insert into instance
        assert self.length <= self.goal_length
        assert self.completion == False
        if self.length == 0:
            self.R_list[0] = newtuple
            self.length = 1
        elif self.length == self.goal_length - 1:
            assert self.R_list[self.length - 1][1] == newtuple[0]
            assert self.R_list[0][0] == newtuple[1]
            self.R_list[self.length] = newtuple
            self.length += 1
            self.completion = True
        else:
            assert self.R_list[self.length - 1][1] == newtuple[0]
            self.R_list[self.length] = newtuple
            self.length += 1


    def max_wgt_rem(self, tuple2rem, a):
        if self.length == self.goal_length:
            return 0.0
        else:
            return tuple2rem[self.R_list[self.length-1], a]



class cycle4_instance():
    # will need to extend later to support generic tree case,
    # should make sure that they are consistent
    def __init__(self, tu):
        # initialize the tuples to dummy values
        self.R0 = tu
        self.R1 = (0, 0)
        self.R2 = (0, 0)
        self.R3 = (0, 0)
        self.length = 1
        self.completion = False

    def frontier(self):
        assert self.length in {1, 2, 3}
        if self.length == 1:
            return self.R0
        elif self.length == 2:
            return self.R1
        elif self.length == 3:
            return self.R2

    def insert_relation(self, newtuple):
        # take tuple, insert into instance
        assert self.length in {1, 2, 3, 4}
        assert self.completion == False
        if self.length == 0:
            self.R0 = newtuple
            self.length = 1
        elif self.length == 1:
            assert self.R0[1] == newtuple[0]
            self.R1 = newtuple
            self.length = 2
        elif self.length == 2:
            assert self.R1[1] == newtuple[0]
            self.R2 = newtuple
            self.length = 3
        elif self.length == 3:
            assert self.R2[1] == newtuple[0]
            assert self.R0[0] == newtuple[1]
            self.R3 = newtuple
            self.length = 4
            self.completion = True


    def max_wgt_rem(self, tuple2rem, a):
        # return the min wgt for the remaining part -- lightest weight, lower bound H value
        if self.length == 4:
            return 0.0
        if self.length == 3:
            return tuple2rem[(self.R2, a)]
        if self.length == 2:
            return tuple2rem[(self.R1, a)]
        if self.length == 1:
            return tuple2rem[(self.R0, a)]


@functools.total_ordering
class PE_tree():
    # class of partially explored tree instance, for tree decomposition of cycle
    def __init__(self, Ix2, wgt, query_type, breakpair2maxweight):
        # if query_type == 1, I12(x0,x2,x3)
        self.query_type = query_type
        self.wgt = wgt
        self.completion = False
        if query_type == 1:
            self.x2, self.x3, self.x0 = Ix2
            # print breakpair2maxweight
            self.hrtc = breakpair2maxweight[(self.x2, self.x0)]
        elif query_type == 2:
            self.x0, self.x1, self.x2 = Ix2
            self.hrtc = breakpair2maxweight[(self.x0, self.x2)]
            # [DESIGN CHOICE]reversed order to distinguish type 1 and type 2. clockwise.
        else:
            assert query_type == 3
            self.x1, self.x2, self.x3 = Ix2
            self.hrtc = breakpair2maxweight[(self.x1, self.x3)]

    def __gt__(self, other):
        return (self.wgt + self.hrtc) > (other.wgt + other.hrtc)

    def __eq__(self, other):
        return (self.wgt + self.hrtc) == (other.wgt + other.hrtc)

    def merge(self, Ix1, wgt):
        # take an Ix1 tuple and its weight and merge to current Ix2, update total weight
        if self.query_type == 1:  # checked consistence with I11
            self.x1 = Ix1[1]
        elif self.query_type == 2:
            self.x3 = Ix1[1]  # checked consistence with I21
        else:
            assert self.query_type == 3
            self.x0 = Ix1[1]  # checked consistence with I31
        self.wgt += wgt
        self.hrtc = 0
        self.completion = True
