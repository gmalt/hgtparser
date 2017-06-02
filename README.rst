GmAlt HGT file parser
=====================

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

Get the elevation of a coordinate inside a file

.. code:: python

    with HgtParser('myhgtfile.hgt') as parser:
        parser.get_elevation((lat, lng))

Iterate over all the elevation values inside a file.

.. code:: python

    with HgtParser('myhgtfile.hgt') as parser:
        for elev_value in parser.get_value_iterator():
            print(elev_value)
            # each value is a tuple (line number, column number, zero based index, square corners of the elevation value, elevation value)

Iterate over square of elevation values inside a file.

.. code:: python

    with HgtParser('myhgtfile.hgt') as parser:
        for elev_value in parser.get_sample_iterator(width, height):
            print(elev_value)
            # each value is a tuple line number of top left corner, column number of top left corner, zero based index of top left corner, square corners position, list of all elevation values in square line per line)

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
