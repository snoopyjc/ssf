To create new data files for ssf, run the appropriate create*.py which will
create xlsx files.  Open these with Excel 365, and use "Save As unicode text
(.txt)".  Use an editor or other program to convert the encoding from utf-16
to utf-8.  Rename the extension to ".tsv".  If the file needs to be compressed
then use "gzip FILE.tsv" in git bash.  Drop the files in the test or ssf
directories appropriately.  

Note that Excel will use "..." quoting sometimes, which doubles any " chars to "", so the appropriate decoding will have to be performed.

For lunarcal, use create_lunar.py, convert Excel to text, then run
create_lunar2.py to create the lunarcal.bin file.  Move it to the ssf
directory.  This calendar is currently good until the year 2173 (100,000 days).
