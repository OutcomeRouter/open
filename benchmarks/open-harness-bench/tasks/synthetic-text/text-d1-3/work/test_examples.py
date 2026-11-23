from solution import *

assert transform(' bookkeeper  bookkeeper  Queue  p8  io  zzzz  Ok  zzzz  bookkeeper') == ' bkkpr  bkkpr  Q  p8    zzzz  k  zzzz  bkkpr'
assert transform('Data42  bookkeeper  World  Queue  World  Data42  World  a  Queue') == 'Dt42  bkkpr  Wrld  Q  Wrld  Dt42  Wrld    Q'
assert transform('  Queue  Ok  bookkeeper  2026  io  Queue  io  hello') == '  Q  k  bkkpr  2026    Q    hll'
print('ok')
