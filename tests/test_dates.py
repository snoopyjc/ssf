#/* vim: set ts=2: */
#/*jshint -W041 */
#/*jshint loopfunc:true, mocha:true, node:true, evil:true */
#var SSF = require('../');
from ssf import SSF
ssf = SSF()
ssf1904 = SSF(date1904=True)
#var fs = require('fs'), assert = require('assert');
#var data = JSON.parse(fs.readFileSync('./test/date.json','utf8'));
import json
import re
from datetime import date
with open('tests/date.json', 'r', encoding='utf-8') as d:
    data = json.load(d)
#
#describe('date values', function() {
def test_data_values():
#	it('should roundtrip dates', function() { data.forEach(function(d) {
    for d in data:
#		assert.equal(SSF.format("yyyy-mm-dd HH:MM:SS", eval(d[0]), {date1904:!!d[2]}), d[1]);
        formatter = ssf1904 if d[2] else ssf
        m = re.match(r'new Date\((\d+),(\d+),(\d+)\)', d[0])
        assert m
        dt = date(int(m.group(1)), int(m.group(2))+1, int(m.group(3)))
        assert formatter.format("yyyy-mm-dd HH:MM:SS", dt) == d[1]
#	}); });
#});
