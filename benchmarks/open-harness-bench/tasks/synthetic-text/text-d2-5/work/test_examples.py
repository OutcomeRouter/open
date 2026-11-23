from solution import *

assert transform('io\tbookkeeper\tOk\ta\tData42\tQueue\thello') == 'IO\tBOOKKEEPER\tOK\tA\tDATA42\tQUEUE\tHELLO'
assert transform(' 2026 \n 2026 \n io \n hello \n hello \n io') == 'IO \n HELLO \n HELLO \n IO \n 2026 \n 2026 '
assert transform('Ok\tio\thello\tData42  ') == '  OK\tIO\tHELLO\tDATA42'
print('ok')
