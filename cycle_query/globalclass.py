import functools

@functools.total_ordering
class PEI():
    #class of partially explored instance
    #maintaining a field of starting variable for join consistency check later
    def __init__(self):
        self.instance = None
        self.wgt = 0
    def __gt__(self, other):
        return self.wgt > other.wgt
    def __eq__(self, other):
        return self.wgt == other.wgt
    def merge(self, relation): #merge all partially explored trees