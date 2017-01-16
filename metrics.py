#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from io_tree import *
from tree_values import *
import itertools


class Metric:
    def __init__(self, name: str='',
                 load_type: str='tenure', operator: 'function'=None,
                 trivial: bool=False, filters: list=[],
                 latex: str='', function=memory_measure):
        self.name = str(name)
        self.load_type = load_type
        self.operator = operator
        self.trivial = trivial
        self.filters = filters
        self.profile = {}
        self.viable = True
        self.latex = latex
        self.function = function

    def eval(self, tree: 'IOTree'):
        """Compute memory value of tree with respect to metric"""
        return function(tree,
                        operator=self.operator,
                        load_type=self.load_type,
                        filters=self.filters,
                        trivial=self.trivial)

    def get_or_set_value(self, tree: 'MetricTree'):
        assert(isinstance(tree, MetricTree))

        value = tree.profile.get(self.name, None)
        if not value:
            value = self.eval(tree)
            tree.add_metric(self, value)
        return value

    def captures(self, value1: int, value2: int) -> (bool, bool):
        if value1 < value2:
            return (True, True)
        elif value1 == value2:
            return (False, True)
        else:
            return (False, False)

    def compare(self, name: str, tree1: 'IOTree', tree2: 'IOTree'):
        tree1_value = self.get_or_set_value(tree1)
        tree2_value = self.get_or_set_value(tree2)
        self.viable = self.captures(tree1_value, tree2_value)

        contrast = {'name': name,
                    'desired winner': (tree1, tree1.name, tree1_value),
                    'desired loser': (tree2, tree2.name, tree2_value),
                    'captured': self.viable}
        self.profile[name] = contrast


class MetricTree(IOTree):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = {}

    def add_metric(self, metric, value: int=None):
        self.profile[metric] = {'name': metric.name, 'value': None}
        self.profile[metric]['value'] = value if value else metric.eval(self)


######################
#  Building Metrics  #
######################


def construct_ranked_metric(metric_set: list=[], ranks: int=2) -> list:
    if ranks == 0:
        return []
    elif ranks < 2:
        return metric_set
    else:
        return list(itertools.product(*[metric_set for _ in range(ranks)]))


def construct_filtered_parameters(parameters: dict, filters: list=[]) -> list:
    def insert_filter(parameters: dict, filters: list=[]) -> list:
        filtered_metrics = []
        for a_filter in filters:
            new_filter = parameters.copy()
            new_filter['filters'] = a_filter
            filtered_metrics.append(new_filter)
        return filtered_metrics

    if not filters:
        return parameters

    if parameters['load_type'] == 'tenure':
        if '*' in filters:
            return insert_filter(parameters,
                                 powerset(['I', 'U', 'P', 'F', 'C']))
        else:
            return insert_filter(parameters, filters)


#####################################
#  Metric Specifications from Text  #
#####################################


def filter_eval(filters: str):
    def powerset(iterable):
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        s = list(iterable)
        return itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s)+1))

    # analyze filters
    filters = [a_filter.strip() for a_filter in filters.split(',')
               if a_filter.strip() != '']
    # and compile all combinations if * is present
    if '*' in filters:
        filters = powerset([a_filter
                            for a_filter in filters
                            if a_filter != '*'])
        return list(filters)
    else:
        return [tuple(filters)]


def construct_metrics_from_text(metric_text: list=[]):
    metric_props = ['name', 'latex', 'load_type', 'operator',
                    'trivial', 'filters', 'function']
    metric_dict = {}
    metrics = []

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
    for filter_variant in filter_eval(metric_dict['filters']):
        metric_variant = metric_dict.copy()
        metric_variant['filters'] = filter_variant
        metrics.append(metric_variant)

    return [Metric(**metric_dict) for metric_dict in metrics]


def metrics_from_file(inputfile: str=None,
                      directory: str=None,
                      extension: str='.metrics',
                      ranked: int=1):
    # ask for input file if necessary
    if not directory:
        directory =\
            input("Path to folder with the metrics file:\n")
    if directory[-1] != '/':
        directory += '/'
    if not inputfile:
        inputfile =\
            input("File to read in (without .metrics extension):\n")

    basename = directory + inputfile

    # read in specification file
    with open(basename + extension, 'r') as metricfile:
        metrics = [line.split(';')
                   for line in metricfile.readlines()
                   if not re.match(r'\s*#.*', line)]
        metricfile.close()

    return construct_ranked_metric(
        [metric_variant
         for metric in metrics
         for metric_variant in construct_metrics_from_text(metric)],
        ranked)
