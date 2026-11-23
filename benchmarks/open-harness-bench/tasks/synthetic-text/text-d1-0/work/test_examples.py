from solution import *

assert transform('  World \n hello \n World \n Ok \n hello') == '  World \n Hello \n World \n Ok \n Hello'
assert transform('io  zzzz  hello  World  Data42  bookkeeper  Data42  2026  2026 ') == 'io  Zzzz  Hello  World  Data42  Bookkeeper  Data42  2026  2026 '
assert transform('Queue bookkeeper ') == 'Queue Bookkeeper '
print('ok')
