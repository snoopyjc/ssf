#/* vim: set ts=2: */
#/*jshint loopfunc:true, mocha:true, node:true */
#/*eslint-env mocha, node */
#var SSF = require('../');
from ssf import SSF
ssf = SSF()
#var assert = require('assert');
#describe('dateNF override', function() {
def test_dateNF():
#  it('should override format code 14', function() {
#    assert.equal(SSF.format(14, 43880), "2/19/20");
    assert ssf.format(14, 43880) == "2/19/2020"     # Note format 14 now uses a 4-digit year
#    assert.equal(SSF.format(14, 43880, {dateNF:"yyyy-mm-dd"}), "2020-02-19");
    ssfNF = SSF(dateNF="yyyy-mm-dd")
    assert ssfNF.format(14, 43880) == "2020-02-19"
#    assert.equal(SSF.format(14, 43880, {dateNF:"dd/mm/yyyy"}), "19/02/2020");
    ssfNF = SSF(dateNF="dd/mm/yyyy")
    assert ssfNF.format(14, 43880) == "19/02/2020"
#  });
#  it('should override format "m/d/yy"', function() {
def test_should_override():
#    assert.equal(SSF.format('m/d/yy', 43880), "2/19/20");
    assert ssf.format('m/d/yyyy', 43880) == "2/19/2020"
#    assert.equal(SSF.format('m/d/yy', 43880, {dateNF:"yyyy-mm-dd"}), "2020-02-19");
    ssfNF = SSF(dateNF="yyyy-mm-dd")
    assert ssfNF.format('m/d/yyyy', 43880) == "2020-02-19"
#    assert.equal(SSF.format('m/d/yy', 43880, {dateNF:"dd/mm/yyyy"}), "19/02/2020");
    ssfNF = SSF(dateNF="dd/mm/yyyy")
    assert ssfNF.format('m/d/yyyy', 43880) == "19/02/2020"
#  });
#});
#describe('asian formats', function() {
def test_asian_formats():
#    it('上午/下午 (AM/PM)', function() {
#        assert.equal(SSF.format('上午/下午', 0),    '上午');
    assert ssf.format('上午/下午', 0) == '上午'     # AM
#        assert.equal(SSF.format('上午/下午', 0.25), '上午');
    assert ssf.format('上午/下午', 0.25) == '上午'     # AM
#        assert.equal(SSF.format('上午/下午', 0.49), '上午');
    assert ssf.format('上午/下午', 0.49) == '上午'     # AM
#        assert.equal(SSF.format('上午/下午', 0.5),  '下午');
    assert ssf.format('上午/下午', 0.5) == '下午'   # PM
#        assert.equal(SSF.format('上午/下午', 0.51), '下午');
    assert ssf.format('上午/下午', 0.51) == '下午'   # PM
#        assert.equal(SSF.format('上午/下午', 0.99), '下午');
    assert ssf.format('上午/下午', 0.99) == '下午'   # PM
#        assert.equal(SSF.format('上午/下午', 1),    '上午');
    assert ssf.format('上午/下午', 1) == '上午'     # AM
#    });
#    it('bb (buddhist)', function() {
#        [
#            [12345,
#                [ 'yyyy',   '1933'],
#                [ 'eeee',   '1933'],
#                [ 'bbbb',   '2476'],
#                //[ 'ปปปป',   '๒๔๗๖'],
#                [ 'b2yyyy', '1352'],
#                [ 'b2eeee', '1352'],
#                [ 'b2bbbb', '1895'],
#                //[ 'b2ปปปป', '๑๘๙๕']
#            ]
#        ].forEach(function(row) {
    for row in [
            [12345,
                [ 'yyyy',   '1933'],
                [ 'eeee',   '1933'],
                [ 'bbbb',   '2476'],
                #[ 'ปปปป',   '๒๔๗๖'],
                [ 'b2yyyy', '1352'],
                [ 'b2eeee', '1352'],
                [ 'b2bbbb', '1895'],
                #[ 'b2ปปปป', '๑๘๙๕']
            ]
        ]:
#            row.slice(1).forEach(function(fmt) {
        for fmt in row[1:]:
#                assert.equal(SSF.format(fmt[0], row[0]), fmt[1]);
            assert ssf.format(fmt[0], row[0]) == fmt[1]
#            });
#        });
#    });
#    it.skip('thai fields', function() {
#        SSF.format('\u0E27/\u0E14/\u0E1B\u0E1B\u0E1B\u0E1B \u0E0A\u0E0A:\u0E19\u0E19:\u0E17\u0E17', 12345.67);
#        assert.equal(SSF.format('\u0E27/\u0E14/\u0E1B\u0E1B\u0E1B\u0E1B \u0E0A\u0E0A:\u0E19\u0E19:\u0E17\u0E17', 12345.67), "๑๘/๑๐/๒๔๗๖ ๑๖:๐๔:๔๘");
#    });
#});
