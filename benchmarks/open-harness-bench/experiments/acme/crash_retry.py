"""Crash real SQLite writers either side of COMMIT. No external resource is changed."""
import argparse
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

SCHEMA = """
CREATE TABLE grants(tenant TEXT PRIMARY KEY, revision INTEGER, cap INTEGER);
INSERT INTO grants VALUES ('A',1,200), ('B',1,300);
CREATE TABLE outbox(tenant TEXT, operation TEXT, cost INTEGER, revision INTEGER,
                    PRIMARY KEY(tenant, operation));
"""


def enqueue(db, tenant, operation, cost, revision, crash=None):
    with sqlite3.connect(db, timeout=15) as conn:
        conn.execute("BEGIN IMMEDIATE")
        # A retry after a lost acknowledgement returns the original receipt.
        prior = conn.execute("SELECT cost FROM outbox WHERE tenant=? AND operation=?",
                             (tenant, operation)).fetchone()
        if prior:
            return "replayed" if prior[0] == cost else "conflict"
        grant = conn.execute("SELECT revision, cap FROM grants WHERE tenant=?", (tenant,)).fetchone()
        if grant is None or grant[0] != revision or not 0 <= cost <= grant[1]:
            return "hold"
        conn.execute("INSERT INTO outbox VALUES (?,?,?,?)", (tenant, operation, cost, revision))
        if crash == "before":
            os._exit(73)
        conn.commit()
        if crash == "after":
            os._exit(73)
        return "queued"


def command(db, crash):
    return [sys.executable, str(Path(__file__).resolve()), "--child", str(db), crash]


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def exercise(db, point):
    with sqlite3.connect(db) as conn:
        conn.executescript(SCHEMA)
    child = subprocess.run(command(db, point))
    check(child.returncode == 73, "writer missed the crash point")
    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT count(*) FROM outbox").fetchone()[0]
        check(count == int(point == "after"), "partial transaction persisted")
        conn.execute("UPDATE grants SET revision=2, cap=100 WHERE tenant='A'")
    expected = "hold" if point == "before" else "replayed"
    check(enqueue(db, "A", "request", 150, 1) == expected, "incorrect retry after amendment")
    if point == "after":
        check(enqueue(db, "A", "request", 90, 2) == "conflict", "changed payload reused receipt")
    check(enqueue(db, "B", "request", 150, 1) == "queued", "foreign tenant's ID blocked request")
    children = [subprocess.Popen(command(db, "race"), stdout=subprocess.PIPE, text=True) for _ in range(8)]
    outputs = []
    for child in children:
        output, _ = child.communicate(timeout=30)
        check(child.returncode == 0, "retry process failed")
        outputs.append(output.strip())
    check(outputs.count("queued") == 1 and outputs.count("replayed") == 7, str(outputs))
    print(f"Crash {point} commit: persisted {count}, retry={expected}, competing writers=1 enqueue + 7 replays")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--child", nargs=2, metavar=("DB", "POINT"))
    args = parser.parse_args()
    if args.child:
        database, fault = args.child
        if fault == "race":
            print(enqueue(database, "A", "fresh", 90, 2))
        else:
            enqueue(database, "A", "request", 150, 1, fault)
    else:
        with tempfile.TemporaryDirectory() as temp:
            for point in ("before", "after"):
                exercise(Path(temp) / point, point)
