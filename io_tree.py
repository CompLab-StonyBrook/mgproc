#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gorn_tree import *
from helpers import *


class IONode(GornNode):
    """
    Construct nodes as objects with Gorn-style addresses
    """
    def __init__(self,
                 address='', label='', name=None,
                 empty: bool=None, leaf: bool=None,
                 movement: dict={},
                 index: int=None, outdex: int=None):
        super().__init__(address=address,
                         label=label,
                         name=name,
                         empty=empty,
                         leaf=leaf,
                         movement=movement)
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
        if self.outdex and self.index:
            return self.outdex - self.index

    def parts(self):
        return super(IONode, self).parts() +\
            (('index', self._index),
             ('outdex', self._outdex))


class IOTree(GornTree):
    def __init__(self, *args: tuple, leaf_order: list=None, movers: list=None):
        super().__init__()

        # fill up self.struct with arguments, if specified
        for arg in args:
                try:
                    if type(arg) == tuple:
                        self.add(IONode(*arg))
                    elif type(arg) == dict:
                        self.add(IONode(**arg))
                except:
                    print('Node specification of ' + arg + ' is illicit')

        if leaf_order:
            self.sentence(*leaf_order)
        elif '' in self.addresses():
            self.sentence(*self.leaves())

        if self.is_consistent():
            self.parse()

        if movers:
            self.add_movers(movers)


    ################
    #  Annotation  #
    ################

    def annotate(self) -> 'IOTree':
        """Add index/outdex annotation to index-dictionary of flat tree."""
        # check that linear order of leafs is known
        if not self._linear:
            raise Exception("""self._linear is empty;\
specify a linearly ordered list of leaf addresses!

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

    def set_status(self) -> 'IOTree':
        for address in self.struct:
            if self.has_daughters(address):
                self.struct[address].leaf = False
                self.struct[address].empty = False
            else:
                self.struct[address].leaf = True

    def parse(self) -> 'IOTree':
        self.annotate()
        self.set_status()

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
