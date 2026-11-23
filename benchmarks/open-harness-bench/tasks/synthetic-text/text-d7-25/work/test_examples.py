from solution import *

assert transform('Data42  ') == 'data42'
assert transform('   ') == ''
assert transform('  H hello Data42 bookkeeper hello ') == 'hello bookkeeper data42 hello h'
print('ok')
