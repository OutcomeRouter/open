from solution import *

assert transform('  ') == '  '
assert transform('World World World  ') == '  dlroW dlroW dlroW'
assert transform(' World  2026  io  World  hello  bookkeeper  2026 ') == '        oi 6202 6202 olleH dlroW dlroW repeekkooB'
print('ok')
