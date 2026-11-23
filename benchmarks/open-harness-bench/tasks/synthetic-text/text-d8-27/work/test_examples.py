from solution import *

assert transform(' io Queue a Ok a Queue io zzzz ') == 'zzzz q k'
assert transform('a  Ok  zzzz  ') == 'zzzz k'
assert transform(' Queue\tbookkeeper\tzzzz\tOk ') == 'q\tbkkpr\tzzzz\tk'
print('ok')
