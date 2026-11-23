from solution import *

assert transform(' a hello Data42 Ok') == 'Ok Data42 hello a '
assert transform(' a') == 'a '
assert transform(' World bookkeeper bookkeeper 2026 io Data42 a  ') == 'a Data42 io 2026 bookkeeper World '
print('ok')
