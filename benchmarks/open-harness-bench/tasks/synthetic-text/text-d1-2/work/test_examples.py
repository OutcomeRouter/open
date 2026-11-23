from solution import *

assert transform('Queue hello a a io Data42 World ') == 'QUEUE HELLO A A IO DATA42 WORLD '
assert transform('io io Ok Ok ') == 'IO IO OK OK '
assert transform('  ') == '  '
print('ok')
