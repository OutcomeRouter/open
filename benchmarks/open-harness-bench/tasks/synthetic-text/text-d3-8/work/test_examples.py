from solution import *

assert transform('  H Data42 hello ') == '__H_DATA42_HELLO_'
assert transform('vD  Data42  2026  ') == 'VD__DATA42__2026__'
assert transform('Ok World Ok 2026 World Data42 Queue ') == 'OK_WORLD_OK_2026_WORLD_DATA42_QUEUE_'
print('ok')
