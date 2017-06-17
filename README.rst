gmalt HGT file parser
=====================

.. image:: https://travis-ci.org/gmalt/hgtparser.svg?branch=master
    :target: https://travis-ci.org/gmalt/hgtparser

Introduction
------------

This package provides a class to parse and iterate over HGT file. 
It should support SRTM1 and SRTM3 formats but I must confess having only worked with SRTM3 for now.

Installation
------------

.. code:: shell

    pip install gmalthgtparser

This is compatible python 2.7, 3.4, 3.5 and 3.6.

Usage
-----

Import the parser :

.. code:: python

    >>> from gmalthgtparser import HgtParser

Get the elevation of a coordinate inside a file

.. code:: python

    >>> with HgtParser('/tmp/N00E010.hgt') as parser:
    ...    alt = parser.get_elevation((1.0001, 10.0001))  # (alt, lng)
    ...    # return a tuple (line index from the top, column index from the left, elevation in meters)
    ...    print(alt)
    ...
    (0, 0, 57)

Iterate over all the elevation values inside a file.

.. code:: python

    >>> with HgtParser('/tmp/N00E010.hgt') as parser:
    ...    for elev_value in parser.get_value_iterator():
    ...        # each value is a tuple (zero based line number, zero based column number, zero based index, square corners of the elevation value, elevation value)
    ...        print(elev_value)
    ...        break
    ...
    (0, 0, 0, ((0.9995833333333334, 9.999583333333334), (1.0004166666666667, 9.999583333333334), (1.0004166666666667, 10.000416666666666), (0.9995833333333334, 10.000416666666666)), 57)

Iterate over square of elevation values inside a file.

.. code:: python

    >>> with HgtParser('/tmp/N00E010.hgt') as parser:
    ...    for elev_value in parser.get_sample_iterator(50, 50):  # (width, height)
    ...        # each value is a tuple (zero based line number of top left corner, zero based column number of top left corner, zero based index of top left corner, square corners position, list of all elevation values in square line per line)
    ...        print(elev_value[:-1])
    ...        # print number of lines in elevation values list and number of column in each line and the first elevation value
    ...        print(len(elev_value[4]), len(elev_value[4][0]), elev_value[4][0][0])
    ...        break
    ...
    (0, 0, 0, (0.95875, 9.999583333333334), (1.0004166666666667, 9.999583333333334), (1.0004166666666667, 10.04125), (0.95875, 10.04125))
    (50, 50, 57)

Release
-------

Just for me to remember

.. code:: shell

    # Increase version number and tag repository
    rm -rf gmalthgtparser.egg-info/
    python setup.py register -r pypitest
    python setup.py sdist bdist_egg bdist_wheel upload -r pypitest
    # check installation in a custom venv
    mkdir tmp
    cd tmp
    virtualenv venv
    . venv/bin/activate
    pip install -i https://testpypi.python.org/pypi gmalthgtparser
    python
    from gmalthgtparser import HgtParser
    # Then push to production
    python setup.py register -r pypi
    python setup.py sdist bdist_egg bdist_wheel upload -r pypi
