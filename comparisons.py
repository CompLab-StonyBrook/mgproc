#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is called by mgproc.py
#
# It defines:
#
# - Comparison as a new base class with methods for
#    - computing the feasibility of all metrics wrt
#      a given psycholinguistic contrast
#    - reseting the results for all metrics
#
# - ComparisonSet as a new base class that collects multiple comparisons;
#   its methods are:
#   - .add for adding comparisons to the collection
#   - .compare for running every comparison in the set
#   - .show for printing the winners, ties, and losers among the metrics
#
# - Functions for definining Comparion(Set)s with text files

import os
import pprint
import re
import tabulate

from mgproc import tree_from_file

class Comparison:
    """
    Compare metrics with respect to a specific processing contrast.

    A processing contrast consists of two trees, one of which is parsed faster
    than the other. A Comparison collects two IOTrees, stores their empirical
    processing difficulty, and how well metrics predict this contrast.

    Picks two IOTrees as part of a processing contrast and records how well certain metrics
    captured this contrast.

    Public Methods
    --------------
    .name: str
        name of comparsion (e.g. Eng-SRC-ORC)
    .winner: IOTree
        tree that is processed faster
    .loser: IOTree
        tree that is processed more slowly
    .metrics: set
        set of metrics to be used in comparison
    .latex: str
        LaTeX command for name of comparison
    .success: set
        set of metrics that correctly pick the winner
    .tie: set
        set of metrics that predict a tie
    .failure: set
        set of metrics that incorrectly pick the loser
    .compare: list of metrics -> updated Comparison
        for each metric, compute the values it assigns to the two trees
        and update its viability accordingly
    .reset:
        wipe all comparison results calculated so far
    """
    def __init__(self, name: str='',
                 winner: 'IOTree'=None, loser: 'IOTree'=None,
                 metrics: set=set(), latex: str='',
                 success: set=set(), tie: set=set(), failure: set=set()):
        self.name = name
        self.winner = winner
        self.loser = loser
        self.metrics = metrics
        self.success = success
        self.tie = tie
        self.failure = failure

    def compare(self, metrics: set=set()):
        if not metrics:
            metrics = self.metrics

        for metric in metrics:
            # check how the metric does
            metric.compare(self.name, self.winner, self.loser)

            # and add it to the correct group (possibly removing it from others)
            if metric.viable == (True, True): 
                # predict first guy to win, second to lose
                try:
                    self.tie.remove(metric)
                    self.failure.remove(metric)
                except:
                    pass
                finally:
                    self.success.add(metric)
            elif metric.viable == (False, True):
                # predict a tie
                try:
                    self.success.remove(metric)
                    self.failure.remove(metric)
                except:
                    pass
                finally:
                    self.tie.add(metric)
            else:
                # predict first guy to lose, second to win
                try:
                    self.success.remove(metric)
                    self.tie.remove(metric)
                except:
                    pass
                finally:
                    self.failure.add(metric)

    def reset(self):
        self.metrics = []
        self.success = set()
        self.tie = set()
        self.failure = set()


class ComparisonSet:
    """
    Collection of Comparisons.

    Multiple comparisons can be collected into a single ComparisonSet. This
    makes it easy for the user to run multiple comparisons at once.

    Public Methods
    --------------
    .comparisons: list
        stores all Comparisons belonging to this ComparisonSet
    .add: Comparison -> updated ComparisonSet
        add a Comparison to .comparison
    .compare:
        call .compare for every member of the ComparisonSet
    .merge:
        merge another ComparisonSet into this one; to be implemented
    .show():
        print the overview of successful, tie-ing, and failing metrics
    .table():
        print tabular overview of comparison results per metric
    .trees():
        print list of trees used in comparison
    """
    def __init__(self, args: list, name: str='', metrics: set=set(),
                 success: set=set(), tie: set=set(), failure: set=set()):
        self.name = name
        self.metrics = metrics
        self.success = success
        self.tie = tie
        self.failure = failure
        self.comparisons = []
        self._winners = []
        self._losers = []
        self._trees = []

        for arg in args:
            try:
                if type(arg) == dict:
                    self.add(Comparison(**arg))
                elif type(arg) == tuple:
                    self.add(Comparison(*arg))
                else:
                    print('something is going wrong')
            except:
                print('Comparison specification of ' + arg + ' is illicit')

    def trees(self,split: bool=False, update: bool=False):
        if update or not self._losers:
            self._losers = [comp.loser for comp in self.comparisons]
        if update or not self._winners:
            self._winners = [comp.winner for comp in self.comparisons]
        if split and (update or not self._trees):
            self._trees = [self._winners, self._losers]
        elif update or not self._trees:
            self._trees = self._winners + self._losers
        return self._trees

    def add(self, comparison):
        self.comparisons.append(comparison)

    def compare(self, comparisons: set=None):
        # by default no Comparisons are passed;
        # in that case, use the full collection
        if not comparisons:
            comparisons = self.comparisons

        for comparison in comparisons:
            comparison.compare(self.metrics)

        # update our record of how the metrics did
        self.success = set.intersection(*[comparison.success
                                          for comparison in comparisons])
        self.failure = set.union(*[comparison.failure
                                   for comparison in comparisons])
        self.tie = set(self.metrics).difference(
                   self.success.union(self.failure))
        # self.tie = set.intersection(*[comparison.tie
                                      # for comparison in comparisons])

    def merge(self, compset: 'ComparisonSet') -> 'ComparisonSet':
        # fixme: to be implemented
        pass

    def _metric_id(self, metric: 'RankedMetric'):
        return '{0}_{1}'.format(metric._name(), metric._filters())

    def _metric_dict(self, function: 'function'=None):
        if not function:
            function = lambda x: x

        metric_dict = {}
        metric_dict['success'] = [function(metric)
                                  for metric in self.success]
        metric_dict['tie'] = [function(metric)
                              for metric in self.tie]
        metric_dict['failure'] = [function(metric)
                                  for metric in self.failure]
        return metric_dict

    def show(self,subtype=None):
        if subtype:
            pprint.pprint(self._metric_dict(function=self._metric_id)[subtype])
        else:
            pprint.pprint(self._metric_dict(function=self._metric_id))

    def _matrix(self, numerical: bool=False):
        metrics = self.metrics
        rows = []
        for metric in metrics:
            row = [metric.name, metric.filters]
            for comparison in self.comparisons:
                if numerical:
                    winner = str(
                        metric.profile[comparison.name]['desired winner'][2])
                    loser = str(
                        metric.profile[comparison.name]['desired loser'][2])
                    result = '{0}/{1}'.format(winner, loser)
                    row.append(result)
                else:
                    result = metric.profile[comparison.name]['captured']
                    row.append(_rewrite_tuple(result))
            rows.append(row)
        return rows

    def table(self, numerical: bool=False, filename: str=None):
        headers = ['Metric', 'Filters'] +\
                  [comp.name for comp in self.comparisons]
        table = tabulate.tabulate(sorted(self._matrix(numerical=numerical)),
                                  tablefmt='orgtbl', headers=headers)
        if filename:
            f = open(filename, 'w')
            f.write(table)
            f.close()
        else:
            print(table)


def _rewrite_tuple(tuplepair: (bool, bool)) -> str:
    """Rewrite (bool, bool) pair as human-friendly string"""
    rewrite = {(True, True): 'Yes',
               (False, True): 'Tie',
               (False, False): 'No'}
    return rewrite.get(tuplepair, 'Error')


#########################################
#  Comparison Specifications from Text  #
#########################################


def _comparison_from_line(comparison_line: str, metrics: set=set(),
                          inputfile: str='', directory: str=None) -> dict:
    """
    Construct Comparison from line in *.compare file.

    The lines of a *.compare file are of the form
    name; LaTeX command; winner; loser

    name: Python-internal name of comparison
    LaTeX: LaTeX command for the comparison name
    winner: path to .tree.forest for more quickly processed tree
    loser: path to .tree.forest for more slowly processed tree

    Parameters
    ----------
    comparison_line: str
        line from *.compare file that is to be processed
    metrics: set
        set of metrics to be used in comparison
    inputfile: str
        path to *.compare file
    directory: str
        if specified, this will be prepended to the paths for winner and loser
    """
    # split line at every ; and keep first four values
    parameters = [field.strip() for field in comparison_line.split(';')]
    try:
        name, latex, winner_path, loser_path = parameters[:4]
    except:
        message = 'Error in file {0}:\n\
not enough parameters specified'
        raise Exception(message).format(inputfile)

    # construct IOTrees for winner and loser
    if directory:
        winner_path = os.path.join(directory, winner_path)
        loser_path = os.path.join(directory, loser_path)
    winner = tree_from_file(winner_path)
    loser = tree_from_file(loser_path)

    # return dictionary from which the Comparison will be built
    return {'name': name, 'latex': latex, 'metrics': metrics,
            'winner': winner, 'loser': loser}


def comparisons_from_file(inputfile: str=None,
                          directory: str=None,
                          extension: str='.compare',
                          metrics: set=set()) -> 'ComparisonSet':
    """
    Build collection of Comparisons from *.compare file.

    Users can define a ComparisonSet with a *.compare file,
    where each line is of the form
    name; LaTeX command; winner; loser

    name: Python-internal name of comparison
    LaTeX: LaTeX command for the comparison name
    winner: path to .tree.forest for more quickly processed tree
    loser: path to .tree.forest for more slowly processed tree

    Parameters
    ----------
    inputfile: str
        path to *.compare file
    directory: str
        if specified, this will be prepended to the paths for winner and loser
    extension: str
        overwrite default file extension for *.compare files
    metrics: set
    """
    # ask for input file if necessary
    if not inputfile:
        inputfile =\
            input("File to read in (without .compare extension):\n")

    # remove extension if specified
    if inputfile.endswith(extension):
        inputfile = inputfile.replace(extension, '')

    # set baseneame
    basename = os.path.basename(inputfile)

    # read in specification file
    with open(inputfile + extension, 'r') as compfile:

        # create list of dictionary, each one of defines a Comparison
        parameter_dicts = [_comparison_from_line(line, metrics, inputfile, directory)
                           for line in compfile.readlines()
                           if not (re.match(r'^\s*$', line) or
                                   re.match(r'\s*#.*', line))]
        compfile.close()

    comp = ComparisonSet(parameter_dicts, name=basename,
                         metrics=metrics)
    comp.compare()
    return comp
