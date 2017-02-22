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
def forest(tree: 'IOTree', address: str, macros: bool=False) -> str:
    """Prints label of tree node in forest notation."""
    # make sure tree has been parsed; needed for index and outdex
    node = tree.struct[address]

    # get index and outdex
    index = node.index()
    outdex = node.outdex()

    empty = ', empty' if node.empty else ''

    # decide what LaTeX macro to use
    if macros:
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
            ', name=' + node.name() +
            # add property empty if necessary
            empty
            )
    else:
        return (
            # node label
            node.label() +
            # add name for movement arrows and other decorations
            ', name=' + node.name() +
            # add property empty if necessary
            empty
            )


def ioprint(tree: 'IOTree', extension: str='.io.forest',
            filename: str=None, directory: str=None) -> str:
    """Prints index/outdex annotation as tikz nodes."""
    string = ''
    command_padding = 24
    label_padding = 24
    node_padding = 5

    for node in tree.struct.values():
        node_name = ('(' + node.name() + ')').ljust(label_padding)
        node_index = ('{' + str(node.index()) + '}').rjust(node_padding)
        node_outdex = ('{' + str(node.outdex()) + '}').rjust(node_padding)

        # draw a tikz node for index
        index_string = '\\node[index]'.ljust(command_padding)
        index_string += 'at {0} {1};\n'.format(node_name, node_index)

        # draw a tikz node for outdex
        node_option = ', boxed]' if node.outdex() - node.index() > 2 else ']'
        outdex_string = ('\\node[outdex' + node_option).ljust(command_padding)
        outdex_string += 'at {0} {1};\n'.format(node_name, node_outdex)

        # put them together
        string += index_string + outdex_string + '%\n'

    # forest chokes on empty lines,
    # so add a % after the very last \n
    string += '%'

    if not filename:
        return string
    else:
        if not directory:
            directory = '.'
        filename += extension
        filename = os.path.join(directory, filename)
        with open(filename, 'w') as text_file:
            print(string, file=text_file)


def texprint(tree: 'IOTree', extension: str='.mgproc.forest',
             filename: str=None, directory: str=None,
             tree_directory: str=None,
             io: bool=True) -> str:
    """
    Prints forest output of tree.
    
    This function outputs a complete forest environment describing the full
    structure of the tree, all the move arcs, and (if desired) the index/
    outdex annotation.

    Parameters
    ----------
    tree: IOTree
        IOTree to be converted to forest code
    extension: str
        standard extension for produced file
    filename: str
        name of file to be produced
    directory: str
        directory in which to save the file
    tree_directory: str
        directory in which tree files are saved
    io: bool
        add code for index/outdex annotation?
    """
    string = '\\begin{forest}'
    tree_header = '\n%\n' + '%' * 8 + '\n% Tree %\n' + '%' * 8
    string += tree_header + '\n%\n' + tree.print(annotation=forest)

    # add move specification
    move = os.path.join(tree_directory, tree.name) if tree_directory else tree.name
    move_header = '%' * 10 + '\n% Movers %\n' + '%' * 10
    try:
        with open(move + '.move.forest', 'r') as move_file:
            string += '\n%\n' + move_header + '\n%\n' + move_file.read() + '%'
            move_file.close()
    except:
        pass
        # fixme: construct move code directly from IOTree

    # add index/outdex annotation if requested
    if io:
        io_header = '%' * 15 + '\n% Annotations %\n' + '%' * 15
        string += '\n' + io_header + '\n%\n' + ioprint(tree)

    # and close the forest environment
    string += '\n\\end{forest}'

    if not filename:
        return string
    else:
        if io:
            filename += '.io'
        filename += extension
        if not directory:
            directory = '.'
        filename = os.path.join(directory, filename)
        with open(filename, "w") as text_file:
            print(string, file=text_file)
