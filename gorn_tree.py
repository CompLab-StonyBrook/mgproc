#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is called by metrics.py
#
# It defines the bases classes GornNode and GornTree from which all other
# classes inherit:
#
# GornNode --> IONode
# GornTree --> IOTree --> MetricTree
#
# Fixme: document this module very carefully (extended docstrings, examples)


import re
import pprint
from collections import OrderedDict
from helpers import int2str, ascii, named


class GornNode:
    """
    Construct nodes as objects with Gorn-style addresses
    """
    def __init__(self,
                 address='', label='', name=None,
                 empty: bool=None, leaf: bool=None,
                 content: bool=None,
                 movement: list=[]):
        self.address = str(address)
        self._label = str(label)
        if name:
            self._name = str(name)
        else:
            self._name = 't' + self.address
        self.movement = OrderedDict()
        for target, feature in movement:
            self.movement[target] = feature
        self.empty = empty
        self.leaf = leaf
        self.content = content

    def moves_to(self, address: str=None, feature: str=None):
        if address is not None:
            self.movement[address] = feature
        else:
            return self.movement

    def label(self, label: str=None):
        if label:
            self._label = label
        else:
            return self._label

    def name(self, name: str=None):
        if self._name:
            return self._name
        else:
            self._name = name

    def parts(self):
        return (('address', self.address),
                ('label', self._label),
                ('name', self._name),
                ('movement', self.movement),
                ('empty', self.empty),
                ('leaf', self.leaf),
                ('content', self.content))


class GornTree:
    """
    Constructs trees as flat dictionaries with Gorn-style addresses
    as key (of type str) to each node.
    """
    def __init__(self, *args: tuple,
                 name: str='', leaf_order: list=None, movement: dict={}):
        # name of tree
        self.name = name
        # tree structure as flat dictionary
        self.struct = {}
    
        # dictionary of nodes by name for quick lookup
        self.names = {}

        self.movement = {}

        # fill up self.struct with arguments, if specified
        for arg in args:
            try:
                self.add(GornNode(*arg))
            except:
                print('Node specification of ' + arg + ' is illicit')

        # combine the two dictionaries into one on demand;
        # this code only works on Python 3.5 and higher
        # self.full = {**self.struct, **self.names}

        # the variable self._linear stores the linearly ordered string of
        # terminal nodes in the sentence, which may differ from order of
        # nodes in tree. We use self.sentence to set self._linear in case
        # we change from lists to tuples in the future.
        if leaf_order:
            self.sentence(*leaf_order)
        elif '' in self.addresses():
            self.sentence(*self.leaves())
        else:
            self._linear = []


    ###########################
    #  Adding/Removing Nodes  #
    ###########################

    @int2str
    def add(self, gorn_node,
            after: str=None) -> 'GornTree':
        """Add node to tree. 

        Optionally, the new node can be linearly ordered
        with respect to other leaf nodes by updating self._linear.
        
        Parameters
        ----------
        address : str
            Gorn address of node
        label : str
            node label
        after: str
            address of preceding leaf node;
            use any non-existant address when inserting a leftmost node

        Returns
        -------
        GornTree
            GornTree with new node added
        """
        self.struct[gorn_node.address] = gorn_node
        self.names[gorn_node._name] = gorn_node

        # fixme: what is this good for? adding nodes in between others?
        if after:
            try:
                pos = self._linear.index(after)
            except:
                pos = 0
            self._linear.insert(pos + 1, address)

    @int2str
    def pop(self, address: str) -> dict:
        """Remove node from tree.

        Pops a node at address from tree structure.
        We also update self._linear by deleting the node,
        or replacing the node by its mother if it has no siblings.
        Note that careless popping will make the tree domain inconsistent.

        Parameters
        ----------
        address : str
            Gorn address of node
        """
        # update self._linear for leaf nodes
        try:
            pos = self._linear.index(address)
        except ValueError:
            pos = None
        if pos:
            if not self.has_siblings(address):
                self._linear[pos] = self.mother(address)
            else:
                self._linear.pop(pos)

        # remove node from tree structure
        self.struct.pop(address, {})

    @int2str
    def sentence(self, *args) -> list:
        """Set or retrieve value of self._linear.

        Examples
        --------
        >>> tree.sentence(231, 232, 11, 12, 21, 221)
        >>> tree._linear
        ['231', '232', '11', '12', '21', '221']
        >>> tree.sentence()
        ['231', '232', '11', '12', '21', '221']
        """
        if args:
            self._linear = list(args)
        else:
            return self._linear

    @int2str
    def add_mover(self, source: str, target: str, feature: str,
                  update_tree: bool=True):
        """Add movement information to a node"""
        # convert name to address if necessary
        source = self.produce_address(source)
        target = self.produce_address(target)

        self.struct[source].moves_to(target, feature)
        if update_tree:
            self.update_movers

    def update_movers(self):
        for node in self.struct.values():
            if node.movement:
                self.movement[node.address] = node.movement

    def add_movers(self, movement: list):
        for source, target, feature in movement:
            self.add_mover(source, target, feature, update_tree=False)
        self.update_movers()


    ###################
    #  Getting Nodes  #
    ###################

    def produce_address(self, name: 'str'):
        match = re.match(r'[0-9]*', str(name))
        if match.group(0):
            return name
        else:
            return self.names[name].address

    def addresses(self) -> list:
        """Print sorted list of all tree addresses."""
        return sorted([key for key in self.struct])

    @int2str
    def ancestors(self, address: str, safe: bool=False) -> list:
        """Return bottom-up list of all properly dominating nodes.

        Note that by default we do not check that the ancestors actually exist
        because this is always the case for a well-formed tree.

        Parameters
        ----------
        address : str
            Gorn address of node
        safe : bool
            should we check that the ancestors exist?

        Examples
        --------
        >>> tree.ancestors('13147')
        ['1314', '131', '13', '1', '']
        """
        # safety check the node address
        if address not in self.addresses():
            raise Exception('Node does not exist')

        # non-safe: ancestors are all address prefixes
        ancestors = [address[:-(i+1)] for i in range(len(address))]
        # safe: throw away non-existant ancestors
        if safe:
            ancestors = [ancestor for ancestor in ancestors
                         if ancestor in self.addresses()]
        return ancestors

    @int2str
    def subtree(self, address: str) -> list:
        """Return addresses of all reflexively dominated nodes."""
        return [node for node in self.addresses()
                if node.startswith(address)] 

    @int2str
    def pdom(self, address: str) -> list:
        """Return addresses of all properly dominated nodes."""
        return [node for node in self.addresses()
                if node.startswith(address) and
                node != address]

    @int2str
    def daughters(self, address: str) -> list:
        """Return addresses of all immediately dominated nodes."""
        return [node for node in self.addresses()
                if node.startswith(address) and
                len(node) == len(address) + 1]

    @int2str
    def leaves(self, address: str='') -> list:
        """Return addresses of all reflexively dominated leaf nodes."""
        if self.is_leaf(address):
            return [address]
        else:
            return [node for node in self.pdom(address)
                    if self.is_leaf(node)]

    @int2str
    def left_siblings(self, address: str) -> list:
        """Return addresses of all right siblings."""
        if address == '':
            return []
        else:
            return [node for node in self.daughters(self.mother(address))
                    if node[-1] < address[-1]]

    @int2str
    def right_siblings(self, address: str) -> list:
        """Return addresses of all right siblings."""
        if address == '':
            return []
        else:
            return [node for node in self.daughters(self.mother(address))
                    if node[-1] > address[-1]]

    @int2str
    def mother(self, address: str) -> str:
        """Return address of mother."""
        return address[:-1] if address != '' else None

    @int2str
    def precede_list(self, address: str) -> list:
        """Return all addresses preceded by node at Gorn address"""
        return [follower for follower in self.addresses()
                if self.precedes(address, follower)]


    #########################
    #  Node Geometry Tests  #
    #########################

    @int2str
    def has_daughters(self, address: str) -> bool:
        """Check if the node has any daughters."""
        return True if len(self.daughters(address)) != 0 else False

    @int2str
    def is_leaf(self, address: str) -> bool:
        """Check if the node is a leaf node."""
        return not self.has_daughters(address)

    @int2str
    def has_left_siblings(self, address: str) -> bool:
        """Check if the node has right siblings."""
        return True if len(self.left_siblings(address)) != 0 else False

    @int2str
    def has_right_siblings(self, address: str) -> bool:
        """Check if the node has right siblings."""
        return True if len(self.right_siblings(address)) != 0 else False

    @int2str
    def has_siblings(self, address: str) -> bool:
        """Check if the node has right siblings."""
        return self.has_right_siblings(address) and\
            self.has_left_siblings(address)

    @int2str
    def precedes(self, node1: str, node2: str) -> bool:
        """Check if node1 surface precedes node2.

        Surface precedence is determined by the linear order
        of leaves in the sentence, not the tree structure.
        So a right sibling R may precede its left sibling L
        if R contains a node that's linearized to the left
        of all leaves dominated by L.

        This presupposes that self._linear has been set.

        Parameters
        ----------
        node1 : str
            address of node1
        node2 : str
            address of node2

        Returns
        -------
        bool
            True if node1 s-precedes node2, False otherwise

        Raises
        ------
        Exception
            if neither node dominates any leafs,
            which indicates a faulty GornTree
        """
        # precedence cannot hold between nodes related by reflexive dominance
        if node1 in self.pdom(node2) or\
           node2 in self.pdom(node1) or\
           node1 == node2:
            return False

        # check leaf nodes in sentence from left to right
        for node in self._linear:
            # if we first find a node that is dominated by node1, 
            # then node1 surface precedes node2
            if node in self.leaves(node1):
                return True
            # and if we first find one  dominated by node2,
            # then node2 surface precedes node1
            elif node in self.leaves(node2):
                return False
        # something went wrong, so raise an exception to be safe
        raise Exception('Neither node dominates any leafs')


    ##############
    #  Printing  #
    ##############

    def parts(self, by_name: bool=False, leaves_only: bool=False):
        if by_name:
            all_parts = self.names
        else:
            all_parts = self.struct

        if leaves_only:
            return {key: val.parts() for key, val in all_parts.items()
                    if self.is_leaf(all_parts[key].address)}
        else:
            return {key: val.parts() for key, val in all_parts.items()}

    def show(self, by_name: bool=False, leaves_only: bool=False):
        """Pretty print tree structure (of type dict)."""
        node_parts = self.parts(by_name, leaves_only)
        all_parts = [node_parts, self._linear, self.movement]
        pprint.pprint(all_parts)

    def leaf_parts(self, listing: bool=True):
        leaves = sorted(
            [(leaf[1][1], leaf[0][1])  # address and label of leaf nodes
             for leaf in self.parts(leaves_only=True).values()],
            key=lambda x: x[1])

        if not listing:
            return leaves
        else:
            string = ''
            for leaf in leaves:
                string += leaf[0] + '; ' + leaf[1] + '\n'
            return string

    def show_leaves(self, listing: bool=True):
        print(self.leaf_parts(listing))

    def print(self, annotation: 'labeling'=ascii, address: str='',
              indent: int=0, tabwidth: int=4, whitespace: str=' ') -> str:
        """
        Print (sub)tree to shell or for use with LaTeX.

        Parameters
        ----------
        address : str
            Gorn address of (sub)tree's root
        indent : int
            depth of current node in (sub)tree
        tabwidth : int
            how much indentation to add per tree level
        whitespace: str
            what whitespace character to use for indentation
        annotation : function
            function for typesetting node labels
        """
        # compute label of current node
        label = annotation(self, address)
        # set appropriate offset per indentation level
        offset = whitespace * (tabwidth * indent)

        # the rest of the function uses recursion;
        # first the base case: current node is a leaf
        if self.is_leaf(address):
            return offset + '[' + label + ']'
        # and now the recursion:
        # center embed strings computed for the daughters
        else:
            start = offset + '[' + label + '\n'
            end = '\n' + offset + ']'
            middle = [self.print(annotation, daughter,
                                 indent+1, tabwidth, whitespace)
                      for daughter in self.daughters(address)]
            return start + '\n'.join(middle) + end

    def pprint(self, annotation: 'labeling'=ascii, address: str='',
              indent: int=0, tabwidth: int=4, whitespace: str=' ') -> str:
        print(self.print(annotation, address, indent, tabwidth, whitespace))



    ###################
    #  Safety Checks  #
    ###################

    def is_mother_closed(self) -> bool:
        """Ensure Gorn domain is prefix/mother-of closed."""
        for node in self.addresses():
            # check everything but the root
            if len(node) >= 1 and\
               node[:-1] not in self.addresses():
                return False
        return True

    def is_left_sibling_closed(self) -> bool:
        """Ensure Gorn domain is left-sibling closed."""
        for node in self.addresses():
            if node != '':
                for branch in range(1, int(node[-1])):
                    if node[:-1] + str(branch) not in self.addresses():
                        return False
        return True

    def is_consistent(self) -> bool:
        """Run all consistency checks."""
        inconsistent = False
        if not self.is_mother_closed():
            print('mother closure not satisfied')
            inconsistent = True
        if not self.is_left_sibling_closed():
            print('left sibling closure not satisfied')
            inconsistent = True
        if inconsistent:
            return False
        return True


#############
#  Example  #
#############

if __name__ == '__main__':
    tree = GornTree(
        ('', 'S'),
        (1, 'NP'),
        (2, 'VP'),
        (11, 'the'),
        (12, 'man'),
        (21, 'gave'),
        (22, 'NP'),
        (221, 'Bill'),
        (23, 'NP'),
        (231, 'a'),
        (232, 'book'),
        leaf_order=[231, 232, 11, 12, 21, 221]
    )
