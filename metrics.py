#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from io_tree import *
from tree_values import *


class Metric:
    def __init__(self, name: str='',
                 load_type: str='tenure', operator: 'function'=None,
                 trivial: bool=False, filters: list=[]):
        self.name = str(name)
        self.load_type = load_type
        self.operator = operator
        self.trivial = trivial
        self.filters = filters
        self.profile = {}
        self.viable = True

    def eval(self, tree: 'IOTree'):
        """Compute memory value of tree with respect to metric"""
        return memory_measure(tree,
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
