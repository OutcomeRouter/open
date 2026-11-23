from solution import *

assert transform(' bookkeeper hello  ') == 'BOOKKEEPER_HELLO'
assert transform(' Data42 io Queue j hello hello') == 'DATA42_IO_QUEUE_J_HELLO_HELLO'
assert transform('  hello') == 'HELLO'
print('ok')
