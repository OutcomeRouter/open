#!/usr/bin/env python3
"""Generate synthetic tasks with a known difficulty, verified without any model calls.

    python3 tools/gen_tasks.py --family text --n 8 --seed 1 --out tasks/synthetic
    python3 tools/gen_tasks.py --family records --n 8 --seed 1 --out tasks/synthetic

Each task composes `difficulty` steps drawn from a family's step library into one function
the agent must write. The reference implementation composes the same steps, so the withheld
check is differential testing: 400 random inputs, the agent's answer against the reference.
Checking costs milliseconds and no tokens, so thousands of tasks cost nothing to verify, and
the difficulty is known exactly, which lets simulated agents be fitted to real outcomes
(used to fit difficulty).

Families:
  text     transform(s: str) -> str, a pipeline of string steps
  records  query(rows: list[dict]) -> list[dict], a pipeline of filter, sort, dedupe and project steps
  ledger   settle(events: list[dict]) -> dict, account rules that interact (up to 7)
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_inspect import Imported, validate, write_task  # noqa: E402

# ---------------------------------------------------------------- text family
# Each step: (description for the agent, Python source of one line transforming `s`)

TEXT_STEPS = [
    ("Strip leading and trailing whitespace.", "s = s.strip()"),
    ("Replace every run of whitespace with a single space.", "s = ' '.join(s.split()) if s.strip() else ''"),
    ("Convert to lowercase.", "s = s.lower()"),
    ("Convert to uppercase.", "s = s.upper()"),
    ("Replace every ASCII digit with '#'.", "s = ''.join('#' if c in '0123456789' else c for c in s)"),
    ("Remove every vowel (a, e, i, o, u, in either case).", "s = ''.join(c for c in s if c.lower() not in 'aeiou')"),
    ("Reverse the characters of each space-separated word, keeping the words in order. "
     "Words are separated by single spaces; keep empty words between consecutive spaces.",
     "s = ' '.join(w[::-1] for w in s.split(' '))"),
    ("Reverse the order of the space-separated words (split on single spaces, keep empty words).",
     "s = ' '.join(s.split(' ')[::-1])"),
    ("Remove repeated words: keep only the first occurrence of each space-separated word "
     "(split on single spaces; compare exactly; empty words count as words).",
     "s = ' '.join(dict.fromkeys(s.split(' ')))"),
    ("Capitalise the first letter of every space-separated word that is longer than 3 characters "
     "(only the first character changes; split on single spaces).",
     "s = ' '.join(w[:1].upper() + w[1:] if len(w) > 3 else w for w in s.split(' '))"),
    ("Sort the space-separated words by length, then alphabetically (split on single spaces, keep empty words).",
     "s = ' '.join(sorted(s.split(' '), key=lambda w: (len(w), w)))"),
    ("Collapse every run of the same character repeated three or more times to exactly two of it.",
     "import re\ns = re.sub(r'(.)\\1{2,}', r'\\1\\1', s)"),
    ("If the string is longer than 40 characters, keep the first 37 and add '...'.",
     "s = s[:37] + '...' if len(s) > 40 else s"),
    ("Replace each space with an underscore.", "s = s.replace(' ', '_')"),
]


def text_task(rng: random.Random, k: int) -> tuple[str, str, str]:
    steps = rng.sample(TEXT_STEPS, k)
    body = "\n".join("    " + line for _, src in steps for line in src.split("\n"))
    ref = f"def transform(s):\n{body}\n    return s\n"
    spec = "Write solution.py with transform(s: str) -> str that applies these steps, in this order:\n\n" + \
        "\n".join(f"{i}. {d}" for i, (d, _) in enumerate(steps, 1))
    gen = (
        "import random, string\n"
        "def gen(rng):\n"
        "    words = ['hello', 'World', 'a', 'Data42', 'zzzz', 'Queue', 'io', 'bookkeeper', '2026', 'Ok', 'hello']\n"
        "    parts = [rng.choice(words + [''.join(rng.choice(string.ascii_letters + string.digits) "
        "for _ in range(rng.randint(1, 8)))]) for _ in range(rng.randint(0, 9))]\n"
        "    sep = [' ', ' ', ' ', '  ', '\\t', ' \\n '][rng.randint(0, 5)]\n"
        "    return (' ' * rng.randint(0, 2)) + sep.join(parts) + (' ' * rng.randint(0, 2))\n"
    )
    return ref, spec, gen


# ---------------------------------------------------------------- records family

REC_STEPS = [
    ("Keep only rows whose `status` is \"active\".", "rows = [r for r in rows if r['status'] == 'active']"),
    ("Keep only rows whose `amount` is greater than 50.", "rows = [r for r in rows if r['amount'] > 50]"),
    ("Keep only rows whose `region` is \"eu\" or \"us\".", "rows = [r for r in rows if r['region'] in ('eu', 'us')]"),
    ("Sort by `amount`, largest first; rows with equal amounts keep their current order.",
     "rows = sorted(rows, key=lambda r: -r['amount'])"),
    ("Sort by `name` alphabetically, then by `id` ascending.", "rows = sorted(rows, key=lambda r: (r['name'], r['id']))"),
    ("Remove rows with a `name` already seen earlier in the list (keep the first).",
     "seen = set()\nrows = [r for r in rows if not (r['name'] in seen or seen.add(r['name']))]"),
    ("Add a field `tier`: \"gold\" if `amount` is at least 100, \"silver\" if at least 50, else \"bronze\".",
     "rows = [{**r, 'tier': 'gold' if r['amount'] >= 100 else 'silver' if r['amount'] >= 50 else 'bronze'} for r in rows]"),
    ("Round `amount` to the nearest multiple of 10 (halves round up: 15 becomes 20).",
     "rows = [{**r, 'amount': (r['amount'] + 5) // 10 * 10} for r in rows]"),
    ("Keep at most the first 5 rows.", "rows = rows[:5]"),
    ("Replace each row with only its `id`, `name` and `amount` fields, plus `tier` if the row has one.",
     "rows = [{k: r[k] for k in ('id', 'name', 'amount', 'tier') if k in r} for r in rows]"),
]


def records_task(rng: random.Random, k: int) -> tuple[str, str, str]:
    steps = rng.sample(REC_STEPS, k)
    steps.sort(key=lambda st: st is REC_STEPS[-1])  # projecting drops fields later steps need: it goes last
    body = "\n".join("    " + line for _, src in steps for line in src.split("\n"))
    ref = f"def query(rows):\n    rows = [dict(r) for r in rows]\n{body}\n    return rows\n"
    spec = ("Write solution.py with query(rows: list[dict]) -> list[dict]. Each row has `id` (int), `name` (str), "
            "`status` (str), `region` (str) and `amount` (int). Do not change the input list or its rows. "
            "Apply these steps, in this order:\n\n" + "\n".join(f"{i}. {d}" for i, (d, _) in enumerate(steps, 1)))
    gen = (
        "def gen(rng):\n"
        "    names = ['ana', 'bo', 'cy', 'dee', 'eli', 'fay']\n"
        "    return [{'id': i, 'name': rng.choice(names), 'status': rng.choice(['active', 'paused', 'closed']),\n"
        "             'region': rng.choice(['eu', 'us', 'apac']), 'amount': rng.randint(0, 160)}\n"
        "            for i in rng.sample(range(100), rng.randint(0, 12))]\n"
    )
    return ref, spec, gen


# ---------------------------------------------------------------- ledger family
# Rules interact (a fee changes what an overdraft check sees, ordering changes what counts as a duplicate),
# so difficulty grows faster than the rule count.

LEDGER_RULES = [
    ("sort", "Process events in order of `t`, breaking ties by `id` (otherwise, in list order)."),
    ("dedupe", "An event whose `id` appeared on an earlier event (in processing order, whatever happened to that "
               "earlier event) is skipped: neither applied nor rejected."),
    ("no_negative", "A withdrawal that would take the balance below zero (after its fee, if a fee rule applies) "
                    "is rejected."),
    ("fee", "Each applied withdrawal also takes a fee of 25 from the balance. A rejected withdrawal takes no fee."),
    ("cap", "A deposit of more than 100000 is rejected."),
    ("daily", "Withdrawals applied on the same day (day = t // 86400) may total at most 50000, fees not counted; "
              "a withdrawal over that is rejected."),
    ("interest", "An `interest` event adds 1% of the balance, rounded down, when the balance is positive; "
                 "it is applied either way."),
]

LEDGER_REF = """def settle(events):
    F = {flags!r}
    evs = list(events)
    if F['sort']:
        evs = sorted(evs, key=lambda e: (e['t'], e['id']))
    balance, applied, rejected, seen, day_total = 0, [], [], set(), {{}}
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
    return {{'balance': balance, 'applied': applied, 'rejected': rejected}}
"""


def ledger_task(rng: random.Random, k: int) -> tuple[str, str, str]:
    on = set(name for name, _ in rng.sample(LEDGER_RULES, min(k, len(LEDGER_RULES))))
    flags = {name: name in on for name, _ in LEDGER_RULES}
    ref = LEDGER_REF.format(flags=flags)
    base = ("Write solution.py with settle(events: list[dict]) -> dict. Each event has `id` (int), `t` (int, seconds), "
            "`type` (str) and `amount` (int, cents). The balance starts at 0. A `deposit` adds its amount; a `withdraw` "
            "subtracts it. Events of any other type are rejected, except `interest` events, which are ignored "
            "(neither applied nor rejected) unless a rule below says otherwise. Return {\"balance\": int, "
            "\"applied\": [ids in the order applied], \"rejected\": [ids in the order rejected]}. "
            "Do not change the input.")
    rules = [d for name, d in LEDGER_RULES if name in on]
    spec = base + ("\n\nRules:\n\n" + "\n".join(f"{i}. {d}" for i, d in enumerate(rules, 1)) if rules else "")
    gen = (
        "def gen(rng):\n"
        "    n = rng.randint(0, 14)\n"
        "    ids = [rng.randint(1, 12) for _ in range(n)]\n"
        "    return [{'id': i, 't': rng.choice([0, 3600, 86399, 86400, 90000, 172800]) + rng.randint(0, 2),\n"
        "             'type': rng.choice(['deposit', 'deposit', 'withdraw', 'withdraw', 'interest', 'refund']),\n"
        "             'amount': rng.choice([0, 25, 100, 4975, 25000, 30000, 100000, 100001])} for i in ids]\n"
    )
    return ref, spec, gen


FAMILIES = {"text": ("transform", text_task, "synthetic-text"), "records": ("query", records_task, "synthetic-data"),
            "ledger": ("settle", ledger_task, "synthetic-ledger")}


def make(family: str, idx: int, k: int, seed: int) -> tuple[Imported, str]:
    fn, build, ttype = FAMILIES[family]
    rng = random.Random(f"{seed}-{family}-{idx}-{k}")
    ref, spec, gen = build(rng, k)
    ns: dict = {}
    exec(ref, ns)
    exec(gen, ns)
    examples = []
    erng = random.Random(seed * 7 + idx)
    for _ in range(3):
        x = ns["gen"](erng)
        examples.append(f"assert {fn}({x!r}) == {ns[fn](json.loads(json.dumps(x)))!r}")
    hidden = (
        f"import copy, json, random\nfrom solution import {fn} as got\n\n{ref.replace(f'def {fn}(', 'def want(')}\n{gen}\n"
        f"rng = random.Random({seed * 1000 + idx})\n"
        "for _ in range(400):\n"
        "    x = gen(rng)\n"
        "    before = copy.deepcopy(x)\n"
        "    w = want(copy.deepcopy(x))\n"
        "    g = got(x)\n"
        "    assert g == w, f'input {x!r}: expected {w!r}, got {g!r}'\n"
        "    assert x == before, 'the input was changed'\n"
    )
    t = Imported(
        name=f"{family}-d{k}-{idx}", source=f"synthetic/{family}", type=ttype,
        task=spec + "\n\nUse only the Python standard library.",
        files={"solution.py": f"def {fn}(*args):\n    raise NotImplementedError\n",
               "test_examples.py": "from solution import *\n\n" + "\n".join(examples) + "\nprint('ok')\n"},
        visible=("the examples pass", "python3 test_examples.py"), protect=("test_examples.py",),
        hidden=hidden, minutes=15,
    )
    return t, ref


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", choices=sorted(FAMILIES), required=True)
    ap.add_argument("--n", type=int, default=8, help="tasks to make, spread over difficulties")
    ap.add_argument("--min", type=int, default=1, help="fewest steps")
    ap.add_argument("--max", type=int, default=8, help="most steps")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="tasks/synthetic")
    a = ap.parse_args()
    out = Path(a.out)
    for i in range(a.n):
        k = a.min + (i * (a.max - a.min + 1)) // max(a.n, 1)
        t, ref = make(a.family, i, k, a.seed)
        p = write_task(t, out)
        text = p.read_text().replace(f"# Imported from Inspect evals: synthetic/{a.family}",
                                     f"# Synthetic task (tools/gen_tasks.py --family {a.family} --seed {a.seed})", 1)
        p.write_text(text.replace("type = ", f"difficulty = {k}\nfamily = \"{a.family}\"\ntype = ", 1))
        ok, why = validate(p, {"solution.py": ref})
        print(p if ok else f"INVALID {p.parent.name}: {why}")


if __name__ == "__main__":
    main()
