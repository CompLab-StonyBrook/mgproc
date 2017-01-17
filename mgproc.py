#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from pprint import pprint
from io_tree import *
from tree_values import *
from metrics import *
from comparisons import *


def raw_tokenize(string: str) -> list:
    # break string after [ and ]
    return re.split('([\[\]])', string)


def strip_comments(string: str, sep='%') -> str:
    # everything after first separator is removed
    return string.split(sep, 1)[0]


def tokenize(string: str) -> list:
    return [strip_comments(item)
            for item in map(str.strip, raw_tokenize(string))
            if strip_comments(item) != '']


def extract_properties(string: str, address: str) -> tuple:
    label = re.match(r'\s*([\w$\'\-\\{}\.]*)', string).group(1)
    empty = True if re.search(r',\s*empty\W*', string) else None
    content = True if re.search(r',\s*content\W*', string) else None

    name_match = re.search(r',\s*name\s*=\s*([\w\-\']*)', string)
    if name_match:
        name = name_match.group(1)
    else:
        name = None

    return {'address': address, 'label': label,
            'name': name, 'empty': empty, 'content': content}


def parse(string: str) -> list:
    """
    Convert forest tree to tuples for a GornTree.

    Takes a string that specifies a tree in the notation of the
    LaTeX forest package. It produces a list of tuples that each
    specify a GornNode.

    Examples
    --------
    >>> parse('[S\n [NP [John, name=subject]]\n
               [Aux, empty] [VP [slept, name=verb]]')
    [('', 'S'), ('1', 'NP), ('11', 'John', 'subject'),
     ('2', 'Aux', None, True), ('3', 'VP'), ('31', 'slept', 'verb')]
    """
    tree = []
    tokens = tokenize(string)
    for pos in range(len(tokens)):
        # root node
        if tokens[pos] == '[' and pos == 0:
            address = ''
        # descend into a subtree with left siblings
        elif tokens[pos] == '[' and tokens[pos-1] == ']':
            address = address[:-1] + str(int(address[-1]) + 1)
        # descend into a subtree without left siblings
        elif tokens[pos] == '[':
            address = address + '1'
        # descend out of rightmost sibling
        elif tokens[pos] == ']' and tokens[pos-1] == ']':
            address = address[:-1]
        # looking at a node
        elif tokens[pos] != ']':
            tree.append(extract_properties(tokens[pos], address))
    return tree


def file_accessible(filepath, mode) -> bool:
    """Check that file exists and is accessible."""
    try:
        f = open(filepath, mode)
        f.close()
    except IOError:
        return False
    return True


def linearization_from_file(inputfile) -> list:
    with open(inputfile, 'r') as linearization:
        leaf_order = [line.split(';')
                      for line in linearization.readlines()]
        linearization.close()
    return leaf_order


def move_from_file(inputfile) -> list:
    movement = []
    with open(inputfile, 'r') as movefile:
        for line in movefile.readlines():
            # match all (...) in line
            move = re.findall(r'\((.*?)\)', line)
            # feature as specified by move={f}
            feat = re.match(r'.*move\s*=\s*{([^}]*)}.*', line)
            # append first (...), last (...), and feature type
            movement.append((move[0], move[-1], feat.group(1)))
    movefile.close()
    return movement


def tree_from_file(inputfile: str=None,
                   extension: str='.tree.forest',
                   autolinearize: bool=False) -> 'MetricTree':
    # ask for input file if necessary
    if not inputfile:
        inputfile =\
            input("File to read in\
                  (without {0} extension):\n".format(extension))

    if inputfile.endswith(extension):
        inputfile = inputfile.replace(extension, '')
    basename = os.path.basename(inputfile)

    # read in specification file
    with open(inputfile + extension, 'r') as treefile:
        tree = treefile.read()
        treefile.close()

    # and set auxiliary files
    linear_file = inputfile + '.linear'
    move_file = inputfile + '.move.forest'

    # linearize automatically or...
    if autolinearize or not file_accessible(linear_file, 'r'):
        tree = MetricTree(*parse(tree), name=basename)
    # ... according to linearization file
    elif file_accessible(linear_file, 'r'):
        leaf_order = [int(address)
                      for label, address in
                      linearization_from_file(linear_file)]
        tree = MetricTree(*parse(tree), leaf_order=leaf_order, name=basename)

    # then read in Move information
    if file_accessible(move_file, 'r'):
        tree.add_movers(move_from_file(move_file))

    # and return fully built tree
    return tree


def trees_from_folder(directory: str=None,
                      extension: str='.tree.forest',
                      autolinearize: bool=False):
    if not directory:
        directory = input("Enter folder to be processed \
(relative to current working directory):\n")

    files = [tree_file.replace(extension, '')
             for tree_file in os.listdir(directory)
             if tree_file.endswith(extension)]

    return [tree_from_file(
        inputfile=basename, directory=directory,
        extension=extension, autolinearize=autolinearize)
        for basename in files]


def check_order(tree: IOTree, specification: 'linearization file') -> bool:
    for label, address in linearization_from_file(specification + '.linear'):
        # sanitize address (remove \n, whitespace)
        address = str(int(address))
        label_in_tree = tree.struct[address].label()
        if label != label_in_tree:
            print('Label mismatch: address {1} has label {2}, not {0}'.format(
                label, address, label_in_tree))
            return False
        return True


def io_process_folder(path: str=None, extension: str='.tree.forest'):
    if not path:
        path = input("Enter folder to be processed \
(relative to current working directory):\n")

    for tree_file in os.listdir(path):
        # only work on files that end in .tree.forest
        if tree_file.endswith(extension):
            basename = tree_file.replace(extension, '')
            current_file = os.path.join(path, basename)
            current_tree = tree_from_file(inputfile=current_file,
                                          autolinearize=False)
            current_tree.show()
            ioprint(current_tree, filename=basename, directory=path)
