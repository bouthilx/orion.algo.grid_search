# -*- coding: utf-8 -*-
"""
:mod:`orion.algo.grid_search.gridsearch -- Grid Search
======================================================

.. module:: gridsearch
    :platform: Unix
    :synopsis: Grid Search Algorithm

TODO: Write long description
"""
import itertools

import numpy

from orion.algo.base import BaseAlgorithm
from orion.algo.space import Categorical, Integer


def _grid(dim, num, delta, nudge=None):

    if isinstance(dim, Categorical):
        if len(dim.categories) != num:
            raise ValueError(
                f'Categorical dimension {dim.name} must have {num} choices: {dim.categories}')
        if nudge is not None:
            raise ValueError(
                f'Categorical dimension not supported with NoisyGridSearch')
        return dim.categories
    elif isinstance(dim, Integer):
        raise TypeError('Grid search only supports Real space dimensions for now.')
    elif dim._prior_name == 'reciprocal':
        a, b = dim.interval()
        return _log_grid(a, b, num, delta, nudge)
    elif dim._prior_name == 'uniform':
        a, b = dim.interval()
        return _lin_grid(a, b, num, delta, nudge)
    else:
        raise TypeError(f'Grid Search only supports `loguniform`, `uniform` and `choices`: '
                         '{dim.get_prior_string}')

def _log_grid(a, b, num, delta, nudge):
    return numpy.exp(_lin_grid(numpy.log(a), numpy.log(b), num, delta, nudge))

def _lin_grid(a, b, num, delta, nudge):
    if delta is None:
        delta = (b - a) / (num - 1)
    if nudge is None:
        nudge = [0, 0]
    return numpy.linspace(
        a + delta * nudge[0],
        b + delta * nudge[1],
        num=num)


class GridSearch(BaseAlgorithm):
    """Grid Search algorithm
    
    Parameters
    ----------
    n_points: int or dict
        Number of points for each dimensions, or dictionary specifying number of points for each
        dimension independently (name, n_points).
    """

    def __init__(self, space, n_points=5, seed=None):
        if not isinstance(n_points, dict):
            n_points = {name: n_points for name in space.keys()}
        super(GridSearch, self).__init__(space, n_points=n_points, seed=seed)
        self.n = 0
        self.grid = self.build_grid(space, self.n_points)

    @staticmethod
    def build_grid(space, n_points, deltas=None, nudge=None):
        if deltas is None:
            deltas = {}
        if nudge is None:
            nudge = {}
        coordinates = []
        for name, dim in space.items():
            coordinates.append(list(_grid(dim, n_points[name], deltas.get(name), nudge.get(name))))

        return list(itertools.product(*coordinates))

    @property
    def state_dict(self):
        """Return a state dict that can be used to reset the state of the algorithm."""
        return {'n': self.n}

    def set_state(self, state_dict):
        """Reset the state of the algorithm based on the given state_dict

        :param state_dict: Dictionary representing state of an algorithm
        """
        self.n = state_dict['n']

    def suggest(self, num=1):
        """Suggest a `num`ber of new sets of parameters.

        Returns the (i+1)-th point on the grid after `i` calls to suggest().

        Parameters
        ----------
        num: int, optional
            Number of points to suggest. Defaults to 1.

        Returns
        -------
        list of points or None
            A list of lists representing points suggested by the algorithm. The algorithm may opt
            out if it cannot make a good suggestion at the moment (it may be waiting for other
            trials to complete), in which case it will return None.

        """
        points = self.grid[self.n:self.n + num]
        self.n += len(points)
        return points

    def observe(self, points, results):
        """Observe evaluation `results` corresponding to list of `points` in
        space.

        Grid search is dumb, it does not observe.
        """
        pass

    @property
    def is_done(self):
        """Return True when all grid has been covered."""
        return self.n >= len(self.grid)


class NoisyGridSearch(GridSearch):

    def __init__(self, space, n_points=5, deltas=None, seed=None):
        super(NoisyGridSearch, self).__init__(space, n_points=n_points, seed=seed)
        nudge = numpy.random.RandomState(seed).uniform(0, 1, size=(len(space), 2)) - 0.5
        nudge = dict((key, nudge[i]) for i, key in enumerate(space.keys()))
        self.grid = self.build_grid(space, self.n_points, deltas=deltas, nudge=nudge)
