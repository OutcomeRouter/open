from solution import *

assert transform('  a a bookkeeper a hello zzzz  ') == 'zz_hello_bookkeeper_a'
assert transform(' Data42 Data42 zzzz World Ok  ') == 'Ok_World_zz_Data42'
assert transform('hello 2026 io Queue  ') == 'Queue_io_2026_hello'
print('ok')
