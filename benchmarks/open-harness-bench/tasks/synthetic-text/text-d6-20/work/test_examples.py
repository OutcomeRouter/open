from solution import *

assert transform('zzzz \n Data42 \n hello \n io \n hello \n qiN8vNPo \n zzzz  ') == '_ZZZZ _24ATAD_ _OLLEH_ _OI_ _OLLEH_ ..._'
assert transform(' kD  a  a  bookkeeper  Queue  Data42  bookkeeper  hello  ') == '..._24ATAD__EUEUQ__REPEEKKOOB__A__A__DK_'
assert transform(' World ') == '_DLROW_'
print('ok')
