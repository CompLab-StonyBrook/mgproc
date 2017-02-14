#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is called by mgproc.py
#
# It defines:
#
# - Metrics as a new base class, with methods for
#    - computing values over trees
#    - testing a metric on specific processing contrasts
#    - computing its overall viability
#
# - MetricTree as a subtype of IOTrees;
#   a MetricTRee is an IOTree that stores a dictionary of values
#   assigned to it by various metrics
#
# - Functions for building metrics from text files

import itertools
import os
import re

from io_tree import IOTree
from tree_values import memory_measure, safemax, safediv, avg


##################
# Metric Classes #
##################

class BaseMetric:
    """
    Class of base metrics for processing predictions.

    Parameters
    ----------
    name: str
        name of metric
    load_type: str
    operator: function
        operator to be used for computing metric value
    trivial: bool
        should trivial memory load values (e.g. tenure < 2) be included?
    filters: list
        list of node types that should be excluded from calculations
    latex: str
        LaTeX command for metric name
    function: function
        what basic function from tree_values should be used for calculations?

    Public Methods
    --------------
    .name: str
        name of metric
    .eval: IOTree -> val
        compute metric value for IOTree
    """
    def __init__(self, name: str='',
                 load_type: str='tenure', operator: 'function'=None,
                 trivial: bool=False, filters: list=[],
                 latex: str='', function=memory_measure):
        self.name = str(name)
        self.load_type = load_type
        self.operator = operator
        self.trivial = trivial
        self.filters = filters
        self.latex = latex
        self.function = function if function != '' else memory_measure

    def eval(self, tree: 'IOTree'):
        """Compute memory value of IOTree with respect to metric"""
        return self.function(tree,
                             operator=self.operator,
                             load_type=self.load_type,
                             filters=self.filters,
                             trivial=self.trivial)


class RankedMetric():
    """
    Class of ranked metrics for processing predictions.

    A ranked metric is a tuple <m_1, m_2, ..., m_k> of metrics, where 
    tree t_1 is preferred over t_2 iff there is some j such that all
    m_i with i < j produce a tie and m_j prefers t_1 over t_2.

    Public Methods
    --------------
    .metrics: tuple
        list of BaseMetrics from which RankedMetric is built
    .profile: dict
        stores how the metric fares for each processing contrast it has been
        tested on; each such contrast is itself a dictionary: 

        'name': name of contrast (e.g. Eng-SRC-ORC)
        'desired winner': (winning tree's object, name, and metric value)
        'desired loser ': (losing tree's object, name, and metric value)
        'captured': self.viable indicates whether the contrast was captured
    .viable: (bool, bool)
        (True, True) = correct prediction for all contrasts
        (False, True) = tie for at least one contrast, but no wrong predictions
        (False, False) = wrong prediction for at least one contrast
    .name: str
        name of metric
    .filters: str
        description of filters used by BaseMetrics;
        for instance, I>>PU means the first BaseMetric uses filter I, the second
        no filter at all, and the third the filters P and U
    .eval: IOTree -> val
        compute metric value for IOTree
    .get_or_set_value: MetricTree -> val
        compute value for MetricTree (if it doesn't exist yet) and return it
    .compare: IOTree, IOTree -> updated metric
        compares two IOTrees and updates the metric accordingly
    """
    def __init__(self, metrics: tuple):
        self.metrics = metrics
        self.profile = {}
        self.viable = (True, True)
        self.name = self._name()
        self.filters = self._filters()

    def _name(self):
        """Typest name as ranked version of BaseMetric names"""
        return ' > '.join([metric.name for metric in self.metrics])

    def _filters(self):
        """Typeset multiple filters in a nicer way"""
        filters = [metric.filters for metric in self.metrics]
        # replace tuples by strings;
        # e.g. ('I', 'U', 'P') -> 'IPU'
        for pos in range(len(filters)):
            filters[pos] = ''.join(sorted([char for char in filters[pos]]))
        # and join those strings
        return '>'.join(filters)

    def eval(self, tree: 'IOTree'):
        """Compute memory value of IOTree with respect to ranked metric"""
        return [metric.eval(tree)
                for metric in self.metrics]

    def get_or_set_value(self, tree: 'MetricTree'):
        """Retrieve or compute value of MetricTree with respect to metric"""
        assert(isinstance(tree, MetricTree))

        value = tree.profile.get(self.name, None)
        if not value:
            value = self.eval(tree)
            tree.add_metric(self, value)
        return value

    def _captures(self, value1: int, value2: int) -> (bool, bool):
        """Determine viability of metric based on computed values"""
        if value1 < value2:
            return (True, True)
        elif value1 == value2:
            return (False, True)
        else:
            return (False, False)

    def _pair_and(self, pair1: (bool, bool), pair2: (bool, bool)):
        """
        Compute metric viability from two (bool, bool) pairs.

        We have a three-valued generalization of the Boolean algebra 2,
        with (True, True) > (False, True) > (False, False). The
        component-wise meet is exactly the meet over this algebra.
        """
        return (pair1[0] and pair2[0], pair1[1] and pair2[1])

    def compare(self, name: str, tree1: 'IOTree', tree2: 'IOTree'):
        """Compare two IOTrees with respect to ranked metric"""

        tree1_value = self.get_or_set_value(tree1)
        tree2_value = self.get_or_set_value(tree2)
        viable = self._captures(tree1_value, tree2_value)

        contrast = {'name': name,
                    'desired winner': (tree1, tree1.name, tree1_value),
                    'desired loser': (tree2, tree2.name, tree2_value),
                    'captured': viable}
        self.profile[name] = contrast
        self.viable = self._pair_and(self.viable, viable)



class MetricTree(IOTree):
    """
    IOTree with values from each metric attached to it.
    
    Public Methods
    --------------
    .profile: dict
        stores a dictionary for each metric attached to the IOTree,
        consisting of

        'name': name of metric
        'value': value of tree according to metric
    .add_metric: metric, value -> updated MetricTree
        attach metric to tree by adding it to .profile;
        if value is not specified, it will be computed
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = {}

    def add_metric(self, metric, value: int=None):
        """Store self's value under metric in profile"""
        self.profile[metric] = {'name': metric.name, 'value': None}
        self.profile[metric]['value'] = value if value else metric.eval(self)


#####################################
#  Metric Specifications from Text  #
#####################################


def _construct_ranked_metric(metric_set: list=[], ranks: int=2) -> list:
    """
    Construct RankedMetrics from BaseMetrics.

    Given a set B of BaseMetrics, a RankedMetric of rank n is a member
    of B^n. RankedMetrics make it possible to resolve ties: if metric m1
    predicts a tie for trees t and t', we can expand it to a combined metric
    <m1, m2> such that m2 makes the correct prediction for t and t'.

    Parameters
    ----------
    metric_set: list
        list of BaseMetric objects
    ranks: int
        maximum number of BaseMetric objects a RankedMetric may consist of
    """
    if ranks == 0:
        return []
    else:
        return [RankedMetric(metric_tuple)
                for metric_tuple in
                itertools.product(*[metric_set for _ in range(ranks)])]

def _powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(len(s)+1))


def _filter_eval(filters: str) -> list:
    """
    Convert filter description to list of matching filter configurations.

    A *.metrics file may emply various filter specifications:

    - I: filter out interior nodes
    - U: filter out unpronoucned nodes
    - P: filter out pronounced nodes
    - *: construct every possible combination of zero or more listed filters 

    This function converts these strings into proper filter specifications,
    i.e. lists of the form [tuple1, tuple2, ...], where each tuple contains every
    possible filter at most once.

    Examples
    --------
    >>> _filter_eval("I, U, P")
    [('I', 'U', 'P')]
    >>> _filter_eval("I, U, *")
    [(), ('I',), ('U',), ('I,U')]
    """
    # extract individual filters from string
    filters = [a_filter.strip() for a_filter in filters.split(',')
               if a_filter.strip() != '']
    # and compile all combinations if * is present
    if '*' in filters:
        filters = _powerset([a_filter
                             for a_filter in filters
                             if a_filter != '*'])
        return list(filters)
    else:
        return [tuple(filters)]


def _construct_metrics_from_text(metric_text: list=[]):
    """
    Build metric from tokenized list based on *.metrics line.

    See the Metric class for a detailed description of all its methods.
    We assume that a *.metrics file follows the format

    name; LaTeX command; load_type; operator; trivial; filter; function

    so the metric_text list has the same order. Crucially, though, not all
    parameters may be specified in a *.metrics file, so metrics_text may be
    shorter than that.
    """
    # build a dictionary that can be fed into the Metric constructor
    metric_props = ['name', 'latex', 'load_type', 'operator',
                    'trivial', 'filters', 'function']
    metric_dict = {}

    for i in range(len(metric_props)):
        try:
            prop = metric_text[i].strip()
        except:
            prop = ''

        metric_dict[metric_props[i]] = prop

    # convert operator and function from string to
    # actual Python function to be called
    for key in ['function', 'operator']:
        if metric_dict[key]:
            metric_dict[key] = eval(metric_dict[key])

    # also construct filters correctly
    metrics = []
    for filter_variant in _filter_eval(metric_dict['filters']):
        metric_variant = metric_dict.copy()
        metric_variant['filters'] = filter_variant
        metrics.append(metric_variant)

    # now build all those lovely metrics
    return [BaseMetric(**metric_dict) for metric_dict in metrics]


def metrics_from_file(inputfile: str=None,
                      extension: str='.metrics',
                      ranks: int=1):
    """
    Batch construct metrics from text file.

    Metrics are defined in a *.metrics file with the format:
    name; LaTeX command; load_type; operator; trivial; filter; function
    
    Parameters
    ----------
    inputfile: str
        path to *.metrics file (extension can be omitted);
        if none is specified, we explicitly ask the user
    extension: str
        file extension for *.metrics files
    ranks: int
        build complex metrics that contain up to int base metrics

    Examples
    --------
    >>> test_metrics = metrics_from_file('./metrics/base', ranks=3)

    >>> test_metrics = metrics_from_file('./metrics/base.foo',
    >>> extension='.foo', ranks=2)
    """
    # ask for input file if necessary
    if not inputfile:
        inputfile =\
            input("File to read in (without .metrics extension):\n")

    if inputfile.endswith(extension):
        inputfile = inputfile.replace(extension, '')
    basename = os.path.basename(inputfile)

    # read in specification file
    with open(inputfile + extension, 'r') as metricfile:
        metrics = [line.split(';')
                   for line in metricfile.readlines()
                   # discard empty lines and comments
                   if not re.match(r'^\s*(#.*)?$', line)]
        metricfile.close()

    # use _construct_metrics_from_text to build a base set of metrics,
    # and expand that into the full set with construct_ranked_metric
    return _construct_ranked_metric(
        ranks=ranks,
        metric_set=[metric_variant
                    for metric in metrics
                    for metric_variant in _construct_metrics_from_text(metric)])
