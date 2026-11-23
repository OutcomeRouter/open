from solution import *

assert transform('zzzz \n io \n World \n Ok \n bookkeeper \n hello  ') == 'Ok io zzzz World hello bookkeeper'
assert transform('bookkeeper \n Ok \n a \n a \n Data42 \n 2026 \n io \n io \n Data42  ') == 'a Ok io #### Data## bookkeeper'
assert transform('  Queue\tOk ') == 'Ok Queue'
print('ok')
