#/* vim: set ts=2: */
#/*jshint loopfunc:true, mocha:true, node:true */
#var SSF = require('../');
from ssf import SSF
import json
from datetime import date
ssf = SSF()
#var fs = require('fs'), assert = require('assert');
#var data = JSON.parse(fs.readFileSync('./test/general.json','utf8'));
with open('tests/general.json', 'r', encoding='utf-8') as d:
    data = json.load(d)

#var skip = [];
#describe('General format', function() {
def test_general():
#  data.forEach(function(d) {
    for d in data:
#    it(d[1]+" for "+d[0], skip.indexOf(d[1]) > -1 ? null : function(){
#      assert.equal(SSF.format(d[1], d[0], {}), d[2]);
        assert ssf.format(d[1], d[0]) == d[2]
#    });
#  });
#  it('should handle special values', function() {
def test_general_special_values():
#    assert.equal(SSF.format("General", true), "TRUE");
    assert ssf.format("General", True) == "TRUE"
#    assert.equal(SSF.format("General", undefined), "");
    # Python doesn't have "undefined"
#    assert.equal(SSF.format("General", null), "");
    assert ssf.format("General", None) == ""
#  });
#  it('should handle dates', function() {
def test_general_dates():
#    assert.equal(SSF.format("General", new Date(2017, 1, 19)), "2/19/17");
    assert ssf.format("General", date(2017, 2, 19)) == "2/19/2017"      # https://github.com/SheetJS/ssf/issues/55
#    assert.equal(SSF.format("General", new Date(2017, 1, 19), {date1904:true}), "2/19/17");
    ssf1904 = SSF(date1904=True)
    assert ssf1904.format("General", date(2017, 2, 19)) == "2/19/2017"      # https://github.com/SheetJS/ssf/issues/55
#    assert.equal(SSF.format("General", new Date(1901, 0, 1)), "1/1/01");
    assert ssf.format("General", date(1901, 1, 1)) == "1/1/1901"
#    if(SSF.format("General", new Date(1901, 0, 1), {date1904:true}) == "1/1/01") throw new Error("date1904 invalid date");
    assert ssf1904.format("General", date(1901, 1, 1)) == '##########'
#    assert.equal(SSF.format("General", new Date(1904, 0, 1)), "1/1/04");
    assert ssf.format("General", date(1904, 1, 1)) == "1/1/1904"
#    assert.equal(SSF.format("General", new Date(1904, 0, 1), {date1904:true}), "1/1/04");
    assert ssf1904.format("General", date(1904, 1, 1)) == "1/1/1904"
#  });
#});
