#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Comparison:
    def __init__(self, name: str='',
                 winner: 'IOTree', loser: 'IOTree',
                 metrics: set=set(), latex: str='',
                 success: set=set(), tie: set=set(), falsified: set=set()):
        self.name = name
        self.winner = winner
        self.loser = loser
        self.metrics = metrics
        self.success = success
        self.tie = tie
        self.falsified = falsified

    def compare(self, metrics: list=[]):
        if not metrics:
            metrics = self.metrics

        for metric in metrics:
            metric.compare(self.name, winner, loser)

            if metric.viable == (True, True): 
                self.success.add(metric)
                try:
                    self.tie.remove(metric)
                    self.falsified.remove(metric)
            elif metric.viable == (False, True):
                self.tie.add(metric)
                try:
                    self.success.remove(metric)
                    self.falsified.remove(metric)
            else:
                self.falsified.add(metric)
                try:
                    self.success.remove(metric)
                    self.tie.remove(metric)

    def reset(self):
        self.metrics = []
        self.viable = set()
        self.falsified = set()


class ComparisonSet:
    def __init__(self, *args: tuple, name: str='', metrics: set=set(),
                 success: set=set(), tie: set=set(), falsified: set=set()):
        self.metrics = metrics
        self.success = success
        self.tie = tie
        self.falsified = falsified
        self.comparisons = set()

        for arg in args:
            try:
                if type(arg) == dict:
                    self.add(Comparison(**arg))
                elif type(arg) == tuple:
                    self.add(Comparison(*arg))
            except:
                print('Comparison specification of ' + arg + ' is illicit')

    def add(self, comparison):
        self.comparisons.add(comparison)

    def compare(self, comparisons: set=self.comparisons):
        for comparison in comparisons:
            comparison.compare(self.metrics)
        self.success = set.intersection(*[comparison.success
                                          for comparison in comparisons])
        self.tie = set.intersection(*[comparison.success
                                      for comparison in comparisons])
        self.falsified = set.intersection(*[comparison.falsified
                                            for comparison in comparisons])
