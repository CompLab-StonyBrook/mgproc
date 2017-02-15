#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is the main file for mgproc
#
# Besides loading all helper modules, it only defines some functions
# for working with tree text files.
#
# The overall structure of the package is as follows:
#
# mgproc
#   metrics
#       io_tree
#           gorn_tree
#           helpers
#       tree_values
#   comparisons

import re
import os

from metrics import MetricTree
from helpers import ioprint


def _raw_tokenize(string: str) -> list:
    """Convert string to list of tokens, breaking after [ and ]"""
    return re.split('([\[\]])', string)


def _strip_comments(string: str, sep='%') -> str:
    """Delete string suffix after first comment marker"""
    return string.split(sep, 1)[0]


def _tokenize(string: str) -> list:
    """Tokenizer for forest files"""
    return [_strip_comments(item)
            for item in map(str.strip, _raw_tokenize(string))
            if _strip_comments(item) != '']


def _extract_properties(string: str, address: str) -> tuple:
    """
    Convert forest string to Gorn node specification.

    Parameters
    ----------
    string: str
        line from forest file to be processed
    address: str
        Gorn address of Gorn node to be constructed

    Output
    ------
    Dictionary of the form

    {'address': str, Gorn address
     'label': str, label of node
     'name': str, tikz name of node
     'empty': bool, (un)pronounced node
     'content': bool, (non)content node
    }

    Examples
    --------
    >>> extract_properties('[Aux, empty, name=embedded', '201')
    {'address': '201', 'label': Aux, 'name': 'embedded',
     'empty': True, 'content': }
    """
    # label is string of word characters, including -, \, {, }, and .
    label = re.match(r'\s*([\w$\'\-\\{}\.]*)', string).group(1)
    # do we have "empty" after a comma somewhere in the string?
    empty = True if re.search(r',\s*empty\W*', string) else None
    # do we have "content" after a comma somewhere in the string?
    content = True if re.search(r',\s*content\W*', string) else None
    # do we have a string immedidately preceded by "name = "?
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
    tokens = _tokenize(string)
    # infer Gorn address of node in token from bracketing
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
            tree.append(_extract_properties(tokens[pos], address))
    return tree


def _file_accessible(filepath, mode) -> bool:
    """Check that file exists and is accessible."""
    try:
        f = open(filepath, mode)
        f.close()
    except IOError:
        return False
    return True


def _linearization_from_file(inputfile) -> list:
    """Convert *.linear file to linearization specification"""
    with open(inputfile, 'r') as linearization:
        leaf_order = [line.split(';')
                      for line in linearization.readlines()]
        linearization.close()
    return leaf_order


def _move_from_file(inputfile) -> list:
    """Convert *.move.forest file to movevement specification"""
    movement = []
    with open(inputfile, 'r') as movefile:
        for line in movefile.readlines():
            # match all (...) in line
            # fixme: ignore stuff after last . so that we can use anchors like .south
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
    """
    Construct MetricTree from forest & linearization files.

    This function presupposes that a tree *foo* has already been specified via
    three files:

    - foo.tree.forest: forest file for foo, without any movement
    - foo.move.forest: move arcs for foo as tikz draw commands
    - foo.linear: linearly ordered list of leaf nodes;
                  one line per "node; Gorn address" pair

    Parameters
    ----------
    inputfile: str
        path to foo.tree.forest (file extension can be omitted);
        if none is specified, we explicitly ask the user
    extension: str
        default file extension for forest files
    autolinearize: str
        should the linearization of leaf nodes be computed automatically?
        if false, make sure a linearization file exists
    """
    # ask for input file if necessary
    if not inputfile:
        inputfile =\
            input("File to read in\
                  (without {0} extension):\n".format(extension))

    # remove extension if user included it in path
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
    if autolinearize or not _file_accessible(linear_file, 'r'):
        tree = MetricTree(*parse(tree), name=basename)
    # ... according to linearization file
    elif _file_accessible(linear_file, 'r'):
        leaf_order = [int(address)
                      for label, address in
                      _linearization_from_file(linear_file)]
        tree = MetricTree(*parse(tree), leaf_order=leaf_order, name=basename)

    # then read in Move information
    if _file_accessible(move_file, 'r'):
        tree.add_movers(_move_from_file(move_file))

    # and return fully built tree
    return tree


def trees_from_folder(directory: str=None,
                      extension: str='.tree.forest',
                      autolinearize: bool=False):
    """
    Batch create trees from files in a folder.

    Given a path to a directory, run tree_from_file for each tree specified in
    the folder.  As in tree_from_file, we presuppose that a tree *foo* has
    already been specified via three files:

    - foo.tree.forest: forest file for foo, without any movement
    - foo.move.forest: move arcs for foo as tikz draw commands
    - foo.linear: linearly ordered list of leaf nodes;
                  one line per "node; Gorn address" pair

    Parameters
    ----------
    inputfile: str
        path to folder containing the .tree.forest-files; 
        if none is specified, we explicitly ask the user
    extension: str
        default file extension for forest files
    autolinearize: str
        should the linearization of leaf nodes be computed automatically?
        if false, make sure a linearization file exists for each tree
    """
    if not directory:
        directory = input("Enter folder to be processed \
(relative to current working directory):\n")

    # list of trees (= list of *.tree.forest with extension stripped)
    files = [tree_file.replace(extension, '')
             for tree_file in os.listdir(directory)
             if tree_file.endswith(extension)]

    return [tree_from_file(
        inputfile=basename, extension=extension,
        autolinearize=autolinearize)
        for basename in files]


def check_order(tree: 'IOTree', specification: 'linearization file') -> bool:
    """
    Check *.linear files for consistency with *.tree.forest

    Since *.linear files are created semi-automatically, there is a risk of
    user error. This function checks for each address in *.linear that it
    has the same label in the tree as specified in *.linear.

    Parameters
    ----------
    tree: IOTree
        IOTree which we should compare the *.linear file against
    specification: str
        path to *.linear file
    """
    for label, address in _linearization_from_file(specification + '.linear'):
        # sanitize address (remove \n, whitespace);
        # fails for address '', but root should never be leaf anyways
        address = str(int(address))
        label_in_tree = tree.struct[address].label()
        if label != label_in_tree:
            print('Label mismatch: address {1} has label {2}, not {0}'.format(
                label, address, label_in_tree))
            return False
        return True


def process_folder(path: str=None, extension: str='.tree.forest'):
    """
    Batch create trees from files in a folder and print their forest specification.

    This function allows you to i/o-annotate every tree in a folder and print
    all the information about each tree to the Python shell.
    """
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
