from solution import *

assert transform('  bookkeeper  a  IZ  io  2026  Data42  Queue') == '  Bkkpr    Z    2026  Dt42  Q'
assert transform(' hello \n zzzz \n Data42 \n io \n io \n hello \n Data42 \n io ') == ' hll \n Zzzz \n Dt42 \n  \n  \n hll \n Dt42 \n  '
assert transform(' World') == ' Wrld'
print('ok')
