from solution import *

assert transform('  Ok\tio\tWorld\tOk\tio\tzzzz\tbookkeeper\tzzzz  ') == 'OK\tIO\tWORLD\tOK\tIO\tZZZZ\tBOOKKEEPER\tZZZZ'
assert transform('Queue Queue a hello uV3 hello zzzz  ') == 'HELLO QUEUE ZZZZ UV# A'
assert transform(' ') == ''
print('ok')
