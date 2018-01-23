# demo of tree algorithm KARPET. The prioritized search should be kept the same, only changing the building of prophet.
import globalclass
import functools
import heapq




class PET():
    # class that implement a partially explored tree
    # used in the PQ, comparable
    # template is a binary tree
    def __init__(self, node, hrtc):
        self.wgt = 0
        self.hrtc = hrtc
        self.instance = binary_tree_node(node)
        self.map2parent = dict()
        self.map2left = dict()
        self.map2right = dict()
        # above are all mapping from value to a tree_node

    def left_insert(self, node, newnode, edge2weight):
        self.wgt += edge2weight[(node.val, newnode.val)]
        # update the heuristic value
        self.hrtc = self.hrtc - node.left_hrtc + (newnode.left_hrtc + newnode.right_hrtc)



class binary_tree_node():

    def __init__(self, node):
        self.val = node
        self.left = None
        self.right = None
        #TODO: add left and right heuristic value

    def left_insert(self, node):
        # insert a new node to this current node's left child position
        self.left = binary_tree_node(node)


    def right_insert(self, node):
        self.left = binary_tree_node(node)


    def pre_order(self):
        # return a list of values (ids) of nodes

    def getsize(self):
        if self.left and self.right:
            return self.left.getsize() + self.right.getsize() + 1
        elif not self.left and self.right:
            return self.right.getsize() + 1
        elif not self.right and self.left:
            return self.left.getsize() + 1
        else:
            return 1


class query():

    def __init__(self, template):
        self.template = template
        self.template_pre_order = template.pre_order()
        self.PQ = []

    def grow(self, cur_PET):
        # compare the current PET shape with the template,
        # and grow it in pre-order
        # observation: the pre-order of cur_PET is always a prefix of template!

        PET_node = cur_PET.instance
        # the pointers were both initiated at the root
        size = PET_node.getsize()
        diff_node = self.template_pre_order[size]
        parent_node = cur_PET.map2parent[diff_node]




