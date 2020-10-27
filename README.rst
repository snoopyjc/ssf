===
ssf
===


.. image:: https://img.shields.io/pypi/v/ssf.svg
        :target: https://pypi.python.org/pypi/ssf

.. image:: https://img.shields.io/travis/snoopyjc/ssf.svg
        :target: https://travis-ci.com/snoopyjc/ssf

.. image:: https://readthedocs.org/projects/ssf/badge/?version=latest
        :target: https://ssf.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Spreadsheet Number Format processor - a Python port of SheetJS/ssf.js


* Free software: Apache Software License 2.0
* Documentation: https://ssf.readthedocs.io.


Features
--------

ssf (Spreadsheet Format) is a pure python library to format data using ECMA-376
spreadsheet format codes (used in popular spreadsheet software packages).  It is
derived from the JavaScript version available at https://github.com/SheetJS/ssf.
All listed issues in that package, up to #80, have been fixed in this version
and support for colors, widths, and localization including alternative
calendars have also been implemented.

Python Version and Required Libraries
-------------------------------------

A modern version of Python is required to use `ssf`: version 3.6 or better.
Also, these libraries are required by `ssf`: `Babel`, `python-dateutil`, `pytz`, `pyYAML`, `six`,
`ummalqura`, `convertdate`.

Example
-------

- `Basic Demo <http://www.snoopyjc.org/ssf/>`_

Credits
-------

This package is a Python port of the similarly named JavaScript library (https://github.com/SheetJS/ssf).

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
