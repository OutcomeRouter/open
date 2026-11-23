import os, sys
sys.path.insert(0, os.getcwd())
import copy, json, random
from solution import settle as got

def want(events):
    F = {'sort': True, 'dedupe': False, 'no_negative': False, 'fee': False, 'cap': False, 'daily': True, 'interest': True}
    evs = list(events)
    if F['sort']:
        evs = sorted(evs, key=lambda e: (e['t'], e['id']))
    balance, applied, rejected, seen, day_total = 0, [], [], set(), {}
    for e in evs:
        if F['dedupe']:
            if e['id'] in seen:
                continue
            seen.add(e['id'])
        kind, amt = e['type'], e['amount']
        if kind == 'deposit':
            if F['cap'] and amt > 100000:
                rejected.append(e['id']); continue
            balance += amt; applied.append(e['id'])
        elif kind == 'withdraw':
            cost = amt + (25 if F['fee'] else 0)
            day = e['t'] // 86400
            if F['no_negative'] and balance - cost < 0:
                rejected.append(e['id']); continue
            if F['daily'] and day_total.get(day, 0) + amt > 50000:
                rejected.append(e['id']); continue
            balance -= cost; applied.append(e['id'])
            day_total[day] = day_total.get(day, 0) + amt
        elif kind == 'interest':
            if F['interest']:
                if balance > 0:
                    balance += balance // 100
                applied.append(e['id'])
        else:
            rejected.append(e['id'])
    return {'balance': balance, 'applied': applied, 'rejected': rejected}

def gen(rng):
    n = rng.randint(0, 14)
    ids = [rng.randint(1, 12) for _ in range(n)]
    return [{'id': i, 't': rng.choice([0, 3600, 86399, 86400, 90000, 172800]) + rng.randint(0, 2),
             'type': rng.choice(['deposit', 'deposit', 'withdraw', 'withdraw', 'interest', 'refund']),
             'amount': rng.choice([0, 25, 100, 4975, 25000, 30000, 100000, 100001])} for i in ids]

rng = random.Random(1011)
for _ in range(400):
    x = gen(rng)
    before = copy.deepcopy(x)
    w = want(copy.deepcopy(x))
    g = got(x)
    assert g == w, f'input {x!r}: expected {w!r}, got {g!r}'
    assert x == before, 'the input was changed'
print('ok')
