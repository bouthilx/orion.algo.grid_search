#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Perform integration tests for `orion.algo.skopt`."""
import os

import numpy
import pytest

from orion.algo.space import Integer, Real, Space
import orion.core.cli
from orion.client import create_experiment
from orion.core.utils.tests import OrionState
from orion.core.worker.primary_algo import PrimaryAlgo


algos = ['gridsearch', 'noisygridsearch']


@pytest.fixture(scope='session')
def database():
    """Return Mongo database object to test with example entries."""
    from pymongo import MongoClient
    client = MongoClient(username='user', password='pass', authSource='orion_test')
    database = client.orion_test
    yield database
    client.close()


@pytest.fixture()
def clean_db(database):
    """Clean insert example experiment entries to collections."""
    database.experiments.drop()
    database.trials.drop()
    database.workers.drop()
    database.resources.drop()


@pytest.fixture()
def space():
    """Return an optimization space"""
    space = Space()
    dim1 = Real('yolo1', 'uniform', -3, 6)
    space.register(dim1)
    dim2 = Real('yolo2', 'uniform', 0, 1)
    space.register(dim2)

    return space


@pytest.mark.parametrize('algo', algos)
def test_seeding(space, algo):
    """Verify that seeding after init have no effects"""
    optimizer = PrimaryAlgo(space, algo)

    optimizer.seed_rng(1)
    a = optimizer.suggest(1)[0]
    assert not numpy.allclose(a, optimizer.suggest(1)[0])

    optimizer.seed_rng(1)
    assert not numpy.allclose(a, optimizer.suggest(1)[0])


def test_seeding_noisy_grid_search(space):
    """Verify that seeding have effect at init"""
    optimizer = PrimaryAlgo(space, {'noisygridsearch': {'seed': 1}})
    a = optimizer.suggest(1)[0]
    assert not numpy.allclose(a, optimizer.suggest(1)[0])

    optimizer = PrimaryAlgo(space, {'noisygridsearch': {'seed': 1}})
    assert numpy.allclose(a, optimizer.suggest(1)[0])

    optimizer = PrimaryAlgo(space, {'noisygridsearch': {'seed': 2}})
    assert not numpy.allclose(a, optimizer.suggest(1)[0])


@pytest.mark.parametrize('algo', algos)
def test_set_state(space, algo):
    """Verify that resetting state makes sampling deterministic"""
    optimizer = PrimaryAlgo(space, algo)

    optimizer.seed_rng(1)
    state = optimizer.state_dict
    a = optimizer.suggest(1)[0]
    assert not numpy.allclose(a, optimizer.suggest(1)[0])

    optimizer.set_state(state)
    assert numpy.allclose(a, optimizer.suggest(1)[0])


@pytest.mark.parametrize('algo', algos)
def test_optimizer(monkeypatch, algo):
    """Check functionality of BayesianOptimizer wrapper for single shaped dimension."""
    monkeypatch.chdir(os.path.dirname(os.path.abspath(__file__)))

    with OrionState(experiments=[], trials=[]):

        orion.core.cli.main(["hunt", "--name", "exp", "--max-trials", "5", "--config",
                             "./benchmark/{algo}.yaml".format(algo=algo),
                             "./benchmark/rosenbrock.py",
                             "-x~uniform(-5, 5)"])


@pytest.mark.parametrize('algo', algos)
def test_int(monkeypatch, algo):
    """Check support of integer values."""
    monkeypatch.chdir(os.path.dirname(os.path.abspath(__file__)))

    with OrionState(experiments=[], trials=[]):

        with pytest.raises(TypeError) as exc:
            orion.core.cli.main(["hunt", "--name", "exp", "--max-trials", "5", "--config",
                                 "./benchmark/{algo}.yaml".format(algo=algo),
                                 "./benchmark/rosenbrock.py",
                                 "-x~uniform(-5, 5, discrete=True)"])
        assert 'Grid search only supports Real' in str(exc.value)


def test_categorical(monkeypatch):
    """Check support of categorical values."""
    monkeypatch.chdir(os.path.dirname(os.path.abspath(__file__)))

    with OrionState(experiments=[], trials=[]):

        orion.core.cli.main(["hunt", "--name", "exp", "--max-trials", "5", "--config",
                             "./benchmark/gridsearch.yaml",
                             "./benchmark/rosenbrock.py",
                             "-x~choices([-5, -2, 0, 2, 5])"])


def test_categorical_noisy_gridsearch(monkeypatch):
    """Check no support of categorical values."""
    monkeypatch.chdir(os.path.dirname(os.path.abspath(__file__)))

    with OrionState(experiments=[], trials=[]):

        with pytest.raises(ValueError) as exc:
            orion.core.cli.main(["hunt", "--name", "exp", "--max-trials", "5", "--config",
                                 "./benchmark/noisygridsearch.yaml",
                                 "./benchmark/rosenbrock.py",
                                 "-x~choices([-5, -2, 0, 2, 5])"])

        assert 'Categorical dimension not supported with NoisyGridSearch' in str(exc.value)


@pytest.mark.parametrize('algo', algos)
def test_optimizer_two_inputs(monkeypatch, algo):
    """Check functionality of BayesianOptimizer wrapper for 2 dimensions."""
    monkeypatch.chdir(os.path.dirname(os.path.abspath(__file__)))

    with OrionState(experiments=[], trials=[]):

        orion.core.cli.main(["hunt", "--name", "exp", "--max-trials", "5", "--config",
                             "./benchmark/{algo}.yaml".format(algo=algo),
                             "./benchmark/rosenbrock.py",
                             "-x~uniform(-5, 5)", "-y~uniform(-10, 10)"])


@pytest.mark.parametrize('algo', algos)
def test_optimizer_actually_optimize(monkeypatch, algo):
    """Check if Bayesian Optimizer has better optimization than random search."""
    monkeypatch.chdir(os.path.dirname(os.path.abspath(__file__)))
    best_random_search = 23.403275057472825

    with OrionState(experiments=[], trials=[]):

        orion.core.cli.main(["hunt", "--name", "exp", "--max-trials", "20", "--config",
                             "./benchmark/{algo}.yaml".format(algo=algo),
                             "./benchmark/rosenbrock.py",
                             "-x~uniform(-50, 50)"])

        with open("./benchmark/{algo}.yaml".format(algo=algo), "r") as f:
            exp = create_experiment(name='exp')

        objective = exp.stats['best_evaluation']

        assert best_random_search > objective
