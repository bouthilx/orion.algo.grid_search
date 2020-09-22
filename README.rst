======================
orion.algo.grid_search
======================


.. |pypi| image:: https://img.shields.io/pypi/v/orion.algo.grid_search
    :target: https://pypi.python.org/pypi/orion.algo.grid_search
    :alt: Current PyPi Version

.. |py_versions| image:: https://img.shields.io/pypi/pyversions/orion.algo.grid_search.svg
    :target: https://pypi.python.org/pypi/orion.algo.grid_search
    :alt: Supported Python Versions

.. |license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
    :target: https://opensource.org/licenses/BSD-3-Clause
    :alt: BSD 3-clause license

.. |rtfd| image:: https://readthedocs.org/projects/orion.algo.grid_search/badge/?version=latest
    :target: https://orion.algo-grid_search.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |codecov| image:: https://codecov.io/gh/bouthilx/orion.algo.grid_search/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/bouthilx/orion.algo.grid_search
    :alt: Codecov Report

.. |travis| image:: https://travis-ci.org/bouthilx/orion.algo.grid_search.svg?branch=master
    :target: https://travis-ci.org/bouthilx/orion.algo.grid_search
    :alt: Travis tests


Grid Search


----

This `orion.algo`_ plugin was generated with `Cookiecutter`_ along with `@Epistimio`_'s `cookiecutter-orion.algo`_ template.


Features
--------

* TODO


Requirements
------------

* TODO


Installation
------------

Install latest version of Oríon::

    $ pip install orion

You can then install "orion.algo.grid_search" via `pip`_ from `PyPI`_::

    $ pip install git+https://github.com/bouthilx/orion.algo.grid_search.git

Usage
-----

To use the Grid Search algorithm you need to create a configuration file for Oríon. For example:

.. code-block:: yaml

    experiment:
      name: 'grid_search_demo'
      algorithms:
        gridsearch:
          n_points: 5

    database: 
      type: 'pickleddb'
      host: 'db.pkl'

You can then call `orion` in commandline and pass the configuration file to use the algo.

orion hunt --config grid.yaml ./tests/functional/demo/black_box.py -x~'uniform(-50, 50)'

The file `./tests/functional/demo/black_box.py` can be found in source code of Oríon here: https://github.com/Epistimio/orion/blob/develop/tests/functional/demo/black_box.py.

You can also use it with the Python API

.. code-block:: python

    from orion.client import create_experiment


    def function(x):
        """Evaluate partial information of a quadratic."""
        z = x - 34.56789
        return [{'name': 'objective', 'type': 'objective', 'value': 4 * z**2 + 23.4}]


    experiment = create_experiment(
        name='grid_search_pyapi_demo',
        space={'x': 'uniform(-50, 50)'},
        algorithms={'gridsearch': {'n_points': 5}},
        storage={
            'database': {
                'type': 'pickleddb',
                'host': 'db.pkl'
            }
        })

    experiment.workon(function)

    print(experiment.stats)
    
See Oríon's documentation for more information on the python API: https://orion.readthedocs.io/en/stable/user/api.html#python-apis.

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the BSD-3-Clause license,
"orion.algo.grid_search" is free and open source software.


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@Epistimio`: https://github.com/Epistimio
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`cookiecutter-orion.algo`: https://github.com/Epistimio/cookiecutter-orion.algo
.. _`file an issue`: https://github.com/bouthilx/cookiecutter-orion.algo.grid_search/issues
.. _`orion`: https://github.com/Epistimio/orion
