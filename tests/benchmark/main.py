#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Benchmark all algorithms on the rosenbrock function."""
import argparse
import glob
import os

import orion.core.cli
from orion.core.io.experiment_builder import ExperimentBuilder


database_config = {
    "type": 'EphemeralDB'}


def get_algorithm_configs():
    """Read the algorihm configuration from available files"""
    for file_name in glob.glob('*.yaml'):
        name, _ = os.path.splitext(file_name)
        yield name, file_name


def main(argv=None):
    """Execute the benchmark with cli"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-xserver', action='store_true',
                        help='Do not show results with matplotlib')

    options = parser.parse_args(argv)

    execute_simulations()

    plot(no_xserver=options.no_xserver)


def execute_simulations():
    """Execute the simulation for each available algorithm configuration"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    for algo_name, algo_config_file in get_algorithm_configs():
        print(" ==== ")
        print(" Executing {}".format(algo_name))
        print(" ==== ")
        # experiment name based on file name
        orion.core.cli.main(
            ["hunt", "--config", algo_config_file, '-n', algo_name,
                "--max-trials", "20", "--pool-size", "1",
             "./rosenbrock.py", "-x~uniform(-10, 10, shape=2)", "-y~uniform(-10, 10)"])


def plot(no_xserver=False):
    """Plot the evolution of the best objective for each algorithm"""
    if no_xserver:
        import matplotlib
        matplotlib.use('agg')

    import matplotlib.pyplot as plt
    for algo_name, _ in get_algorithm_configs():

        experiment = ExperimentBuilder().build_view_from(
            {"name": algo_name, "database": database_config})

        objectives = []
        sorted_trials = sorted(
            experiment.fetch_trials({'status': 'completed'}),
            key=lambda trial: trial.submit_time)

        for trial in sorted_trials:
            objectives.append(min([trial.objective.value] + objectives))

        plt.plot(range(len(objectives)), objectives, label=algo_name)

    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
