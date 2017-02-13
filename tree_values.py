#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is called by metrics.py
#
# It defines a general function memory_measure from which various the values
# for various memory-based metrics can be computed based on how its arguments
# are instantiated.
#
# Metric   | Operator        | Memory Type
# ---------|-----------------|----------------
# MaxT     | safemax         | tenure_extract
# SumT     | sum             | tenure_extract
# BoxT     | len             | tenure_extract
# AvgT     | avg             | tenure_extract
# MaxTR    | None/sorted     | tenure_extract
# --------------------------------------------
# MaxS     | safemax         | move_extract
# SumS     | sum             | move_extract
# Movers   | len             | move_extract
# AvgS     | avg             | move_extract
# MaxSR    | None/sorted     | move_extract
#
# While all the functions in this module are meant to be private,
# they are not prefixed with _ so that the user can easily reference them
# in text files to define various metrics.

from io_tree import *


####################
#  Math Operators  #
####################

def safemax(*args: 'list of ints') -> int:
    """max that returns 0 if there are no arguments"""
    try:
        return max(*args)
    except:
        return 0


def safediv(dividend: int, divisor: int) -> float:
    """safe division by 0"""
    if divisor != 0:
        return dividend / divisor
    else:
        return 0


def avg(int_list: list) -> float:
    """Compute the average of a list of integers."""
    return safediv(sum(int_list), len(int_list))


########################
#  Matching Functions  #
########################

def typedict(IONode) -> dict:
    """Compute dictionary of Bools encoding type of IONode.

    Possible node types are
    I: interior (= not a leaf node)
    U: unpronounced leaf (= empty head)
    P: pronounced leaf
    F: part of functional projection (e.g. T')
    C: part of content projection (e.g. V')

    The returned dictionary has exactly one of the three set to True.

    Examples
    --------
    >>> node = IONode(empty=True, leaf=True)
    >>> typedict(node)
    {'I': False, 'P': False, 'U': True}
    >>> node.leaf = False
    >>> typedict(node)
    {'I': True, 'P': False, 'U': False}
    >>> node.leaf = True
    >>> node.empty = False
    >>> typedict(node)
    {'I': False, 'P': True, 'U': False}
    """
    types = {'I': False, 'U': False, 'P': False, 'F': False, 'C': False}
    if IONode.leaf == False:
        types['I'] = True
    elif IONode.empty == True:
        types['U'] = True
    else:
        types['P'] = True

    if IONode.content == True:
        types['C'] = True
    else:
        types['F'] = True

    return types


def matches_types(IONode, node_types: list=None) -> bool:
    """Check whether IOnode matches at least one of the listed node types.

    The only standardized node types are
    I: interior (= not a leaf node)
    U: unpronounced leaf (= empty head)
    P: pronounced leaf
    F: part of functional projection
    C: part of content projection

    If node_types contains any other entries, they are treated as if
    their value were False.

    Examples
    --------
    >>> node = IONode(empty=True, leaf=True)
    >>> matches_types['I','U']
    True
    >>> matches_types['I','P']
    False
    >>> node.leaf = False
    >>> matches_types['I','P']
    True
    >>> matches_types['U']
    False
    """
    if node_types:
        return max([typedict(IONode).get(node_type, False)
                    for node_type in node_types])
    else:
        return False


##########################
#  Raw Value Extraction  #
##########################

def tenure_extract(IOTree, filters: list=[], trivial: bool=False) -> dict:
    """Compute dict of tenure values for all nodes in IOTree.

    The dictionary is of the form address: tenure.

    Parameters
    ----------
    IOTree : IOTree
        index/outdex annotated Gorn tree for which values are to be computed
    filters : list of str
        do not consider the values of nodes whose type is listed here
    trivial : bool
        whether to include nodes with trivial tenure (= tenure 1 or 2)

    Examples
    --------
    >>> tree = tree_from_file('./examples/ugly')
    >>> tenure_extract(tree)
    {'121': 12, '122111': 11, '1221223': 3, '122122': 3, '1222': 24, '11': 10,
     '1221122': 3, '122113': 13, '12212': 16}
    >>> tenure_extract(tree, trivial=True)
    {'': 1, '121': 12, '11': 10, '1211': 1, '1221122': 3, '122': 1,
     '122113': 13, '1221111': 1, '1221221': 1, '12211221': 1, '122111': 11,
     '1221': 1, '1221222': 2, '112': 2, '1': 1, '12211': 1, '12': 1, '111': 1,
     '12211211': 1, '1222': 24, '1221223': 3, '122112': 1, '1221211': 1,
     '1221121': 1, '12212': 16, '12221': 1, '1221131': 1, '122121': 1,
     '122122': 3}
    >>> tenure_extract(tree, filters=['P'], trivial=True)
    {'': 1, '121': 12, '11': 10, '122112': 1, '1221122': 3, '122': 1,
     '122113': 13, '1221121': 1, '12212': 16, '122111': 11, '1221': 1,
     '122121': 1, '1': 1, '12211': 1, '122122': 3, '12': 1, '1222': 24}
    >>> tenure_extract(tree, filters=['I', 'P'], trivial=True)
    {}
    """
    threshold = 2 if not trivial else 0
    return {node.address: node.tenure() for node in IOTree.struct.values()
            if not matches_types(node, filters) and node.tenure() > threshold}


def move_length(IOTree, IONode, filters: list=[], trivial: bool=False) -> dict:
    """Compute dict of size values for given IONode in IOTree.

    The dictionary is of the form triple: value, where triple has the form 
    (address of mover, address of target, movement feature). Note that the
    dictionary is flat rather than nested to make it behave just like the
    dictionary produced by tenure_extract --- the unwieldy keys are the price
    we pay for this design.

    Parameters
    ----------
    IOTree : IOTree
        index/outdex annotated Gorn tree within which values are to be computed
    IONode: IONode
        node in IOTree whose move length is to be evaluated
    filters: list of str
        do not consider move steps that were triggered by one of these features
    trivial : bool
        whether to consider intermediate movement steps

    Examples
    --------
    >>> tree = tree_from_file('./examples/ugly')
    >>> node = tree.struct['122112']
    >>> move_length(tree, node)
    {('122112', '', 'top'): 6}
    >>> move_length(tree, node, trivial=True)
    {('122112', '122', 'acc'): 3, ('122112', '', 'top'): 6
    >>> move_length(tree, node, filters=['nom', 'top'], trivial=True)
    {('122112', '122', 'acc'): 3}
    >>> move_length(tree, node, filters=['nom', 'acc', 'top'], trivial=True)
    {}
    """
    # only keep non-final movers if intermediate is set to True
    try:
        final_target = [next(reversed(IONode.movement))]
    except:
        final_target = []
    move_targets = IONode.movement if trivial else final_target

    return {(IONode.address, target, IONode.movement[target]):
            abs(IONode.index() - IOTree.struct[target].index())
            for target in move_targets
            if IONode.movement[target] not in filters}


def move_extract(IOTree, filters: list=[], trivial: bool=False) -> dict:
    """Compute dict of size values for all nodes in IOTree.

    See move_length for details about the format of the dictionary.

    Parameters
    ----------
    IOTree : IOTree
        index/outdex annotated Gorn tree whose size values are to be computed
    filters: list of str
        do not consider move steps that were triggered by one of these features
    trivial : bool
        whether to consider intermediate movement steps

    Examples
    --------
    >>> tree = tree_from_file('./examples/right_embedding')
    >>> move_extract(tree)
    {('212112121211212121', '212112121211212', 'nom'): 3,
     ('212112121211', '21211212', 'nom'): 4, ('21211', '2', 'nom'): 5,
     ('21211212121121', '2121121212', 'extra'): 13,
     ('21211212121121212222', '2121121212112', 'hn'): 15,
     ('2121121', '212', 'extra'): 5, ('21211212121222', '212112', 'hn'): 9}
    >>> move_extract(tree, filters=['nom', 'hn'])
    {('21211212121121', '2121121212', 'extra'): 13,
     ('2121121', '212', 'extra'): 5}
    >>> move_extract(tree, filters=['nom', 'hn', 'extra'], trivial=True)
    {}
    """
    movers = {}
    for node in IOTree.struct.values():
        new = move_length(IOTree, node, filters=filters, trivial=trivial)
        movers.update(new)
    return movers


###################
#  Main Function  #
###################

def memory_measure(IOTree,
                   operator: 'function'=None, load_type: str='tenure',
                   filters: list=[], trivial: bool=False) -> 'int/list':
    """A general method for computing processing complexity values of IOTrees.

    With the right choice of operator and memory type, this function computes
    a variety of memory-load values for an index/outdex annotated tree.

    Metric   | Operator        | Memory Type
    ---------|-----------------|----------------
    MaxT     | safemax         | tenure_extract
    SumT     | sum             | tenure_extract
    BoxT     | len             | tenure_extract
    AvgT     | avg             | tenure_extract
    MaxTR    | None/sorted     | tenure_extract
    --------------------------------------------
    MaxS     | safemax         | move_extract
    SumS     | sum             | move_extract
    Movers   | len             | move_extract
    AvgS     | avg             | move_extract
    MaxSR    | None/sorted     | move_extract
 
    Parameters
    ----------
    IOTree : IOTree
        index/outdex annotated Gorn tree for which values are to be computed
    operator : function
        what function to apply to the list of tenure values;
    load_type : str
        whether to compute tenure or size-based values with tenure_extract
        or move_extract, respectively; either one returns a dictionary
    filters : list of str
        do not consider the values created by objects of a specific type;
        with load_type = tenure:
            interior (I), lexical (L), pronounced (P), unpronounced (U),
            functional (F), or content (C)
        with load_type = movement:
            names of features to ignore
    trivial : bool
        whether to include trivial instances of memory load
        with load_type = tenure:
            consider nodes with trivial tenure (= tenure 1 or 2)
        with load_type = size:
            consider instances of intermediate movement

    Examples
    --------
    >>> tree = tree_from_file('./examples/ugly')
    >>> memory_measure(ugly)
    [24, 16, 13, 12, 11, 10, 3, 3, 3]
    >>> memory_measure(ugly, load_type='tenure')
    [24, 16, 13, 12, 11, 10, 3, 3, 3]
    >>> memory_measure(ugly, load_type='size')
    [6]
    >>> memory_measure(ugly, trivial=True)
    [24, 16, 13, 12, 11, 10, 3, 3, 3, 2, 2,
     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    >>> memory_measure(ugly, operator=safemax)
    24
    >>> memory_measure(ugly, operator=sum)
    95
    >>> memory_measure(ugly, operator=sum, trivial=True)
    117
    """
    # for recursive metrics, lists should be ordered from largest to smallest
    if not operator or operator == sorted:
        operator = lambda x: sorted(x, reverse=True)

    if load_type == 'tenure':
        load_type = tenure_extract
    elif load_type == 'size':
        load_type = move_extract

    return operator(load_type(IOTree,
                              filters=filters,
                              trivial=trivial).values())

# fixme: incorporate divergence and mtrack
