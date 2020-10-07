=====
Usage
=====

Simple Usage
------------

To use ssf in a project::

    >>> from ssf import SSF

    >>> ssf = SSF()
    >>> ssf.format('#,##0', 1000)
    '1,000'
    >>> ssf.format('Currency', 1000.98)
    '$1,000.98'
    >>> ssf.format('Currency', 1000.98, locale='de-DE')
    '1.000,98 €'
    >>> ssf.format('General', 100000, width=5)
    '1E+05'
    >>> ssf.format('?/?', 3.14159)
    '22/7'
    >>> ssf.format('Long Date', '1/1/2001', locale='fr-FR')
    'lundi 01 janvier 2001'
    >>> ssf.format('[DBNum1][$-804]General', 12.3456789)
    '一十二.三四五六七八九'

    >>> ssfc = SSF(color_pre='<span style="color:#{rgb}">', color_post='</span>')
    >>> ssfc.format('0;[Red]0;0;@', -2)
    '<span style="color:#FF0000">2</span>'

See the API reference for the options you can pass to `SSF()`.  Most options
can be also passed to the `ssf.format()` method, enabling you to create one instance of the
`SSF` object.

Manipulating the Internal Format Table
--------------------------------------

Binary spreadsheet formats store cell formats in a table and references them by index.  
This library uses a table implemented as a dict per object instance.  You can use 
`ssf.load(fmt)` to load additional entries into unused slots in the table - it returns 
the index it chooses.  You can also specify the index by using `ssf.load(fmt, ndx)`.
For compatibility with the XLS and XLSB file formats, custom indices should be in the valid ranges
`5-8`, `23-26`, `41-44`, `63-66`, `164-382` (see `[MS-XLSB] 2.4.655 BrtFmt`)

`ssf.get_table()` gets the internal table as a dict (number to format string mapping).

`ssf.load_table(table)` sets the internal table from a dict mapping ints to format strings.

Other Utilities
---------------

Static method `SSF.is_date(fmt)` returns `True` if `fmt` encodes a date format.

`ssf.get_format(type, ...)` returns a format appropriate for the type and locale.  The `type`
should be (`General`, `Number`, `Currency`, `Accounting`, `Date`, `Short Date`, `Long Date`, `Time`,
`Percentage`, `Fraction`, `Scientific`, or `Text`).  See the API reference for more information.

References
----------

- `MS-XLSB`: `Excel (.xlsb) Binary File Format <https://docs.microsoft.com/en-us/openspecs/office_file_formats/ms-xlsb/acc8aa92-1f02-4167-99f5-84f9f676b95a>`_
- `ECMA-376`: `Number Format Specification <https://c-rex.net/projects/samples/ooxml/e1/Part4/OOXML_P4_DOCX_numFmts_topic_ID0E6KK6.html>`_
