from solution import *

assert transform(' ') == ''
assert transform('  World TWij') == 'twj Wrld'
assert transform('io io') == ''
print('ok')
