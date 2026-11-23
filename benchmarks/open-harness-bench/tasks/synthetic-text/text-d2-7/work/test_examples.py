from solution import *

assert transform('  rVqs ') == 'RVQS'
assert transform('Data42 hello hello Ok') == 'DATA42 HELLO HELLO OK'
assert transform('bookkeeper \n hello \n hello \n 2026 ') == 'BOOKKEEPER \n HELLO \n HELLO \n 2026'
print('ok')
