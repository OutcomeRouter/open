"""Lose the sender's acknowledgment after a separate destination commits an effect."""
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile


def deliver(directory, deduplicate, crash=False):
    sender = directory / "sender.db"
    destination = directory / "destination.db"
    with sqlite3.connect(sender) as conn:
        pending = conn.execute("SELECT tenant, op, units FROM outbox WHERE ack=0").fetchall()
    for tenant, op, units in pending:
        with sqlite3.connect(destination) as conn:
            conn.execute("BEGIN IMMEDIATE")
            seen = conn.execute("SELECT units FROM receipt WHERE tenant=? AND op=?", (tenant, op)).fetchone()
            if deduplicate and seen:
                if seen != (units,):
                    raise ValueError("Same operation ID used for a different effect")
            else:
                conn.execute("UPDATE capacity SET units=units+? WHERE tenant=?", (units, tenant))
                if deduplicate:
                    conn.execute("INSERT INTO receipt VALUES(?,?,?)", (tenant, op, units))
        if crash:
            os._exit(74)  # destination has committed, sender has not acknowledged
        with sqlite3.connect(sender) as conn:
            conn.execute("UPDATE outbox SET ack=1 WHERE tenant=? AND op=?", (tenant, op))


def run(deduplicate):
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        with sqlite3.connect(directory / "sender.db") as conn:
            conn.executescript("""
                CREATE TABLE outbox(tenant TEXT, op TEXT, units INTEGER, ack INTEGER, PRIMARY KEY(tenant,op));
                INSERT INTO outbox VALUES('A','add-one',1,0);
            """)
        with sqlite3.connect(directory / "destination.db") as conn:
            conn.executescript("""
                CREATE TABLE capacity(tenant TEXT PRIMARY KEY, units INTEGER);
                CREATE TABLE receipt(tenant TEXT, op TEXT, units INTEGER, PRIMARY KEY(tenant,op));
                INSERT INTO capacity VALUES('A',0);
            """)
        child = subprocess.run([sys.executable, __file__, temp, str(int(deduplicate))])
        assert child.returncode == 74
        with sqlite3.connect(directory / "sender.db") as conn:
            assert conn.execute("SELECT ack FROM outbox").fetchone() == (0,)
        deliver(directory, deduplicate)
        deliver(directory, deduplicate)  # already acknowledged; should have no work
        with sqlite3.connect(directory / "destination.db") as conn:
            effects, = conn.execute("SELECT units FROM capacity").fetchone()
        with sqlite3.connect(directory / "sender.db") as conn:
            assert conn.execute("SELECT ack FROM outbox").fetchone() == (1,)
        assert effects == (1 if deduplicate else 2)
        print(f"Destination deduplication={deduplicate}: one outbox row, {effects} applied units")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        deliver(Path(sys.argv[1]), bool(int(sys.argv[2])), crash=True)
    else:
        run(False)
        run(True)
