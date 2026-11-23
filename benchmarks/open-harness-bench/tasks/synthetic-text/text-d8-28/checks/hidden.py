import os, sys
sys.path.insert(0, os.getcwd())
import copy, json, random
from solution import transform as got

def want(s):
    s = s[:37] + '...' if len(s) > 40 else s
    s = ' '.join(w[:1].upper() + w[1:] if len(w) > 3 else w for w in s.split(' '))
    import re
    s = re.sub(r'(.)\1{2,}', r'\1\1', s)
    s = s.strip()
    s = ' '.join(s.split()) if s.strip() else ''
    s = s.lower()
    s = ' '.join(w[::-1] for w in s.split(' '))
    s = ' '.join(sorted(s.split(' '), key=lambda w: (len(w), w)))
    return s

import random, string
def gen(rng):
    words = ['hello', 'World', 'a', 'Data42', 'zzzz', 'Queue', 'io', 'bookkeeper', '2026', 'Ok', 'hello']
    parts = [rng.choice(words + [''.join(rng.choice(string.ascii_letters + string.digits) for _ in range(rng.randint(1, 8)))]) for _ in range(rng.randint(0, 9))]
    sep = [' ', ' ', ' ', '  ', '\t', ' \n '][rng.randint(0, 5)]
    return (' ' * rng.randint(0, 2)) + sep.join(parts) + (' ' * rng.randint(0, 2))

rng = random.Random(1028)
for _ in range(400):
    x = gen(rng)
    before = copy.deepcopy(x)
    w = want(copy.deepcopy(x))
    g = got(x)
    assert g == w, f'input {x!r}: expected {w!r}, got {g!r}'
    assert x == before, 'the input was changed'
print('ok')
