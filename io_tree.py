#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is called by metrics.py
#
# It defines:
#
# - IONode as a subtype of GornNode, with new methods for
#   working with indices and outdices
#
# - IOTree as a subtype of GornTree where each GornNode is an IONode.
#   They also provide new methods for annotating/parsing these trees
#   and fprint for pretty-printing them to the Python shell.
#
# IOTrees are expanded into MetricTrees by metrics.py. A MetricTree
# is an IOTree that also stores information about the values it receives
# from various metrics.

from gorn_tree import GornNode, GornTree
from helpers import forest


class IONode(GornNode):
    """
    Subclass of GornNode with index/outdex annotation.

    Public Methods
    --------------
    .index: int
        set index value of node to int;
        if int is None, return current value
    .outdex: int
        set outdex value of node to int;
        if int is None, return current value
    .tenure: int
        return tenure (= outdex - index) of node
    .parts:
        extends eponymous GornNode method to also include information
        about index, outdex, and tenure
    """
    # all arguments except index and outdex are initialized with the
    # init function defined for GornNode
    def __init__(self,
                 address='', label='', name=None,
                 empty: bool=None, leaf: bool=None,
                 content: bool=None,
                 movement: dict={},
                 index: int=None, outdex: int=None):
        super().__init__(address=address,
                         label=label,
                         name=name,
                         empty=empty,
                         leaf=leaf,
                         movement=movement,
                         content=content)
        self._index = index
        self._outdex = outdex

    def index(self, index: int=None):
        if index:
            self._index = index
        else:
            return self._index

    def outdex(self, outdex: int=None):
        if outdex:
            self._outdex = outdex
        else:
            return self._outdex

    def tenure(self):
        if self.outdex() and self.index():
            return self.outdex() - self.index()

    def parts(self):
        return super(IONode, self).parts() +\
            (('index', self.index()),
             ('outdex', self.outdex()),
             ('tenure', self.tenure()))


class IOTree(GornTree):
    """
    Subclass of GornTree such that all GornNodes are IONodes.

    Public Methods
    --------------
    .parse:
        add index/outdex annotation and set leaf/empty status for all nodes
    .fprint:
        print forest code for tree (with \Lab macros)
    """
    # we initialize almost everything ourselves and only pass name to
    # the GornTree init function
    def __init__(self, *args: tuple,
                 leaf_order: list=None, movement: list=None, name: str=''):
        super().__init__(name=name)

        # fill up self.struct with arguments, if specified
        for arg in args:
                try:
                    if type(arg) == dict:
                        self.add(IONode(**arg))
                    elif type(arg) == tuple:
                        self.add(IONode(*arg))
                except:
                    print('Node specification of ' + arg + ' is illicit')

        if leaf_order:
            self.sentence(*leaf_order)
        elif '' in self.addresses():
            self.sentence(*self.leaves())

        if self.is_consistent():
            self.parse()

        if movement:
            self.add_movers(movement)


    ################
    #  Annotation  #
    ################

    def _annotate(self) -> 'IOTree':
        """
        Add index/outdex annotation to index-dictionary of flat tree.

        This algorithm traverses the tree in a peculiar fashion that combines
        top-down and bottom-up. The idea is to first move top-down from the
        root towards the linearly first leaf node while adding indices and
        outdices. Once the leaf has been found, we move to the next leaf and
        move bottom-up until we find a node with an index, and pass the
        outdices down from there along the pather to the second leaf. Rinse
        and repeat until all nodes have indices and outdices.
        
        The basic idea behind the algorithm was first articulated and implemented
        by Chong Zhang.
        """
        # check that linear order of leafs is known
        if not self._linear: raise Exception("""self._linear is empty;\ specify
        a linearly ordered list of leaf addresses!

Example: tree.sentence(231, 232, 11, 12, 21, 221)
""")

        # now start with the root for the base case
        self.struct[''].index(1)
        current_outdex = 1

        # all the code below borrows heavily from Chong Zhang's algorithm
        # for annotating MG derivation trees
        for leaf in self._linear:
            # bottom-up list of dominating nodes
            ancestors = self.ancestors(leaf)
            for interior in ancestors:
                # stop at the lowest node with an index
                if self.struct[interior].index():
                    # give the node an outdex if it doesn't have one yet
                    if not self.struct[interior].outdex():
                        current_outdex += 1
                        self.struct[interior].outdex(current_outdex)
                    # we now need to percolate indices/outdices down from
                    # interior towards the leaf;
                    # note that index here is the Python built-in
                    # method for list search
                    for pos in reversed(range(ancestors.index(interior))):
                        current_key = ancestors[pos]
                        previous_key = ancestors[pos+1]
                        # current index = mother's outdex
                        self.struct[current_key].index(
                            self.struct[previous_key].outdex())
                        # current outdex = current index + 1
                        current_outdex += 1
                        self.struct[current_key].outdex(
                            current_outdex)
                    break  # do not continue for loop
                           # after first item with index value
            # we finally add the indices and outdices for the leaf
            self.struct[leaf].index(self.struct[self.mother(leaf)].outdex())
            current_outdex += 1
            self.struct[leaf].outdex(current_outdex)

    def _set_status(self) -> 'IOTree':
        """Set the flags "leaf" and "empty' for each node"""
        for address in self.struct:
            if self.has_daughters(address):
                self.struct[address].leaf = False
                self.struct[address].empty = False
            else:
                self.struct[address].leaf = True

    def parse(self) -> 'IOTree':
        self._annotate()
        self._set_status()

    def fprint(self, annotation: 'labeling'=forest, address: str='',
              indent: int=0, tabwidth: int=4, whitespace: str=' ') -> str:
        print(self.print(annotation, address, indent, tabwidth, whitespace))


#############
#  Example  #
#############

if __name__ == '__main__':
    tuple_tree = IOTree(
        ('', 'S', 'root'),
        (1, 'NP', None, None, None, [('', 'nom')]),
        (2, 'VP'),
        (11, 'the', 'Det', True, True),
        (12, 'man'),
        (21, 'gave'),
        (22, 'NP'),
        (221, 'Bill'),
        (23, 'NP'),
        (231, 'a'),
        (232, 'book'),
        leaf_order=[231, 232, 11, 12, 21, 221]
    )

    dict_tree = IOTree(
        {'address': '', 'label': 'S', 'name': 'root'},
        {'address': 1, 'label': 'NP', 'movement': [('', 'nom')]},
        {'address': 2, 'label': 'VP'},
        {'address': 11, 'label': 'the', 'name': 'Det', 'empty': True, 'leaf': True},
        {'address': 12, 'label': 'man'},
        {'address': 21, 'label': 'gave'},
        {'address': 22, 'label': 'NP'},
        {'address': 221, 'label': 'Bill'},
        {'address': 23, 'label': 'NP'},
        {'address': 231, 'label': 'a'},
        {'address': 232, 'label': 'book'},
        leaf_order=[231, 232, 11, 12, 21, 221]
    )
