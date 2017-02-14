#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is called by io_tree.py
#
# It defines several general purpose functions: 
#
# - a decorator that converts int to str;
#   Gorn addresses are more conveniently specified as int in the shell,
#   but many functions hinge on them being strings (e.g. for slicing);
#   the decorator abstracts away all the type-checking logic
#
# - various print functions for trees:
#   ascii: plain ascii labeled bracketing with indentation
#   named: ascii with tikz names for nodes
#   forest: forest output (with \Lab macro)
#   ioprint: writes index/outdex annotation as *.io.forest file

import os


def int2str(function) -> 'function':
    """Convert int-arguments of function to type str"""
    def wrapper(*args, **kwargs):
        # convert args from tuple to list for mutability
        args = list(args)
        # convert all int arguments to str
        for pos in range(len(args)):
            if type(args[pos]) == int:
                args[pos] = str(args[pos])
        # and now back from list to tuple
        args = tuple(args)
        # keyword arguments are next
        for kwarg in kwargs:
            if type(kwargs[kwarg]) == int:
                kwargs[kwarg] = str(kwargs[kwarg])
        return function(*args, **kwargs)
    return wrapper


@int2str
def ascii(tree: 'GornTree', address: str) -> str:
    """Prints label of tree node in plain ascii."""
    return tree.struct[address].label()


def named(tree: 'GornTree', address: str) -> str:
    """Prints label and name of tree node in plain ascii."""
    return tree.struct[address].label() +\
        ', name=' +\
        tree.struct[address].name()


@int2str
def forest(tree: 'IOTree', address: str) -> str:
    """Prints label of tree node in forest notation."""
    # make sure tree has been parsed; needed for index and outdex
    node = tree.struct[address]

    # get index and outdex
    index = node.index()
    outdex = node.outdex()

    # decide what LaTeX macro to use
    if outdex - index > 2 and not node.leaf:
        node_type = 'IBLab'
    elif outdex - index > 2:
        node_type = 'BLab'
    else:
        node_type = 'Lab'

    return (
        # start the LaTeX macro
        '\\' + node_type +
        # first macro argument: node label
        '{' + node.label() + '}' +
        # second macro argument: index
        '{' + str(node.index()) + '}' +
        # third macro argument: outdex
        '{' + str(node.outdex()) + '}' +
        # add name for movement arrows and other decorations
        ', name=' + node.name()
        )


@int2str
def ioprint(tree: 'IOTree', extension: str='.io.forest',
            filename: str=None, directory: str=None) -> str:
    """Prints index/outdex annotation as tikz nodes."""
    string = ''
    command_padding = 24
    label_padding = 8

    for node in tree.struct.values():
        node_name = node.name()
        node_index = node.index()
        node_outdex = node.outdex()

        # draw a tikz node for index
        index_string = '\\node[index]'.ljust(command_padding)
        index_node = ('{' + str(node_index) + '}').ljust(label_padding)
        index_string += '{1} at ({0});\n'.format(node_name, index_node)

        # draw a tikz node for outdex
        node_option = ', boxed]' if node_outdex - node_index > 2 else ']'
        outdex_string = ('\\node[outdex' + node_option).ljust(command_padding)
        outdex_node = ('{' + str(node_outdex) + '}').ljust(label_padding)
        outdex_string += '{1} at ({0});\n'.format(node_name, outdex_node)
        string += index_string + outdex_string + '%\n'

    # forest chokes on empty lines,
    # so add a % after the very last \n
    string += string + '%'

    if not filename:
        return string
    else:
        if not directory:
            directory = '.'
        filename += extension
        filename = os.path.join(directory, filename)
        with open(filename, "w") as text_file:
            print(string, file=text_file)
