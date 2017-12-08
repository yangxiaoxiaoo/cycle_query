import functools

@functools.total_ordering
class PEI():
    # class of partially explored instance, instance can be any shape later, cycle_instance for now
    # maintaining a field of starting variable for join consistency check later
    def __init__(self, tu, wgt, hrtc):
        self.instance = cycle_instance(tu)
        self.wgt = wgt
        self.hrtc = hrtc
        self.breakpoint = tu[0]

    def __gt__(self, other):
        return (self.wgt + self.hrtc) > (other.wgt + other.hrtc)

    def __eq__(self, other):
        return (self.wgt + self.hrtc) == (other.wgt + other.hrtc)

    def merge(self, new_tuple, tuple2weight, rel2tuple, tuple2rem):
        # merge this partially explored tree with newly added relation
        self.instance.insert_relation(new_tuple)
        self.wgt += tuple2weight[new_tuple]
        self.hrtc = self.instance.max_wgt_rem(tuple2rem, self.breakpoint)

class PE_tree():
    # class of partially explored tree instance, for tree decomposition of cycle
    def __init__(self, Ix2, wgt, query_type, breakpair2maxweight):
        # if query_type == 1, I12(x0,x2,x3)
        self.query_type = query_type
        self.wgt = wgt
        self.completion = False
        if query_type == 1:
            self.x0, self.x2, self.x3 = Ix2
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
        if self.query_type == 1:
            self.x1 = Ix1[1]
        elif self.query_type == 2:
            self.x3 = Ix1[2]
        else:
            assert self.query_type == 3
            self.x0 = Ix1[0]
        self.wgt += wgt
        self.hrtc = 0
        self.completion = True


class cycle_instance():
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
