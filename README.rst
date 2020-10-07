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
All listed issues in that package, up to #77, have been fixed in this version
and support for colors, widths, and localization have also been implemented.


Missing Feature
---------------

The only currenly missing feature is the support for alternative calendars, as described here: 
https://stackoverflow.com/questions/54134729/what-does-the-130000-in-excel-locale-code-130000-mean
Pull requests will be accepted.

Python Version and Required Libraries
-------------------------------------

A modern version of Python is required to use `ssf`: version 3.6 or better.
Also, these libraries are required by `ssf`: `Babel`, `python-dateutil`, `pytz`, `pyYAML`, `six`.

Credits
-------

This package is a Python port of the similarly named JavaScript library developed by
SheetJSDev (https://github.com/SheetJSDev).

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
