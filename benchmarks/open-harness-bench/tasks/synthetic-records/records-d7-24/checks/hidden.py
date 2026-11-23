import os, sys
sys.path.insert(0, os.getcwd())
import copy, json, random
from solution import query as got

def want(rows):
    rows = [dict(r) for r in rows]
    rows = [{**r, 'tier': 'gold' if r['amount'] >= 100 else 'silver' if r['amount'] >= 50 else 'bronze'} for r in rows]
    rows = sorted(rows, key=lambda r: -r['amount'])
    rows = rows[:5]
    rows = [r for r in rows if r['amount'] > 50]
    rows = [r for r in rows if r['region'] in ('eu', 'us')]
    rows = [{**r, 'amount': (r['amount'] + 5) // 10 * 10} for r in rows]
    rows = [r for r in rows if r['status'] == 'active']
    return rows

def gen(rng):
    names = ['ana', 'bo', 'cy', 'dee', 'eli', 'fay']
    return [{'id': i, 'name': rng.choice(names), 'status': rng.choice(['active', 'paused', 'closed']),
             'region': rng.choice(['eu', 'us', 'apac']), 'amount': rng.randint(0, 160)}
            for i in rng.sample(range(100), rng.randint(0, 12))]

rng = random.Random(1024)
for _ in range(400):
    x = gen(rng)
    before = copy.deepcopy(x)
    w = want(copy.deepcopy(x))
    g = got(x)
    assert g == w, f'input {x!r}: expected {w!r}, got {g!r}'
    assert x == before, 'the input was changed'
print('ok')
