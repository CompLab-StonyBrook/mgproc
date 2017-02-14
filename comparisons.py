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
        tree taht is prcoessed more slowly
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
                try:
                    self.tie.remove(metric)
                    self.failure.remove(metric)
                except:
                    pass
                finally:
                    self.success.add(metric)
            elif metric.viable == (False, True):
                try:
                    self.success.remove(metric)
                    self.failure.remove(metric)
                except:
                    pass
                finally:
                    self.tie.add(metric)
            else:
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
    def __init__(self, args: list, name: str='', metrics: set=set(),
                 success: set=set(), tie: set=set(), failure: set=set()):
        self.name = name
        self.metrics = metrics
        self.success = success
        self.tie = tie
        self.failure = failure
        self.comparisons = set()

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

    def add(self, comparison):
        self.comparisons.add(comparison)

    def compare(self, comparisons: set=None):
        if not comparisons:
            comparisons = self.comparisons

        for comparison in comparisons:
            comparison.compare(self.metrics)

        self.success = set.intersection(*[comparison.success
                                          for comparison in comparisons])
        self.tie = set.intersection(*[comparison.tie
                                      for comparison in comparisons])
        self.failure = set.union(*[comparison.failure
                                   for comparison in comparisons])

    def show(self):
        metric_dict = {}
        metric_dict['success'] = [metric.name for metric in self.success]
        metric_dict['tie'] = [metric.name for metric in self.tie]
        metric_dict['failure'] = [metric.name for metric in self.failure]
        pprint.pprint(metric_dict)


#########################################
#  Comparison Specifications from Text  #
#########################################


def comparison_from_line(comparison_line: str, metrics: set=set(),
                         inputfile: str=''):
    parameters = [field.strip() for field in comparison_line.split(';')]
    try:
        name, latex, winner_path, loser_path = parameters[:4]
    except:
        message = 'Error in file {0}:\n\
not enough parameters specified'
        raise Exception(message).format(inputfile)

    winner = tree_from_file(winner_path)
    loser = tree_from_file(loser_path)

    return {'name': name, 'latex': latex, 'metrics': metrics,
            'winner': winner, 'loser': loser}


def comparisons_from_file(inputfile: str=None,
                          extension: str='.compare',
                          metrics: set=set()):
    # ask for input file if necessary
    if not inputfile:
        inputfile =\
            input("File to read in (without .compare extension):\n")

    if inputfile.endswith(extension):
        inputfile = inputfile.replace(extension, '')
    basename = os.path.basename(inputfile)

    # read in specification file
    with open(inputfile + extension, 'r') as compfile:

        parameter_dicts = [comparison_from_line(line, metrics, inputfile)
                           for line in compfile.readlines()
                           if not re.match(r'\s*#.*', line)]
        compfile.close()

    return ComparisonSet(parameter_dicts, name=basename,
                         metrics=metrics)
