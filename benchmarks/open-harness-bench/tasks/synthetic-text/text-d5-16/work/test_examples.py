from solution import *

assert transform('  zzzz \n bookkeeper \n Ok \n 2026 ') == '#### \n k bkkpr zzzz'
assert transform('  hello \n Ok \n World \n a \n Queue') == 'Q \n  Wrld k hll'
assert transform('io \n zzzz \n zzzz \n zzzz \n World \n io \n hello \n Data42 \n bookkeeper ') == 'bkkpr \n Dt## hll  Wrld zzzz'
print('ok')
