import os, sys
sys.path.insert(0, os.getcwd())
import copy, json, random
from solution import transform as got

def want(s):
    s = s.upper()
    s = ''.join(c for c in s if c.lower() not in 'aeiou')
    s = ' '.join(dict.fromkeys(s.split(' ')))
    s = ''.join('#' if c in '0123456789' else c for c in s)
    s = s.strip()
    s = ' '.join(sorted(s.split(' '), key=lambda w: (len(w), w)))
    s = s.lower()
    s = ' '.join(s.split(' ')[::-1])
    return s

import random, string
def gen(rng):
    words = ['hello', 'World', 'a', 'Data42', 'zzzz', 'Queue', 'io', 'bookkeeper', '2026', 'Ok', 'hello']
    parts = [rng.choice(words + [''.join(rng.choice(string.ascii_letters + string.digits) for _ in range(rng.randint(1, 8)))]) for _ in range(rng.randint(0, 9))]
    sep = [' ', ' ', ' ', '  ', '\t', ' \n '][rng.randint(0, 5)]
    return (' ' * rng.randint(0, 2)) + sep.join(parts) + (' ' * rng.randint(0, 2))

rng = random.Random(1027)
for _ in range(400):
    x = gen(rng)
    before = copy.deepcopy(x)
    w = want(copy.deepcopy(x))
    g = got(x)
    assert g == w, f'input {x!r}: expected {w!r}, got {g!r}'
    assert x == before, 'the input was changed'
print('ok')
