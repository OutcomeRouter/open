#!/usr/bin/env python3
"""Audit the checked-in task corpus against its own checks: no model calls, no network.

For every `<corpus>/<collection>/<task>/spec.toml` this:
  - regenerates the reference solution for synthetic tasks (family text/records/ledger,
    via tools/gen_tasks.make) and runs tools/import_inspect.validate() against the real
    on-disk work/ and checks/ for that task: the starting stub must fail at least one check and
    the regenerated reference must pass every check;
  - for imported tasks (class_eval, humaneval, mbpp), where no reference solution is
    checked in, runs the same validate() with files=None: only the starting stub's
    failure is checked ("stub coverage").

Usage:
    python3 tools/audit_corpus.py [--corpus PATH] [--out report.json]

Exits 0 if every task is valid (stub fails, reference -- when checked -- passes),
1 if any task fails, 2 on a usage/setup error. Prints a single deterministic JSON report
to stdout (or --out).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import gen_tasks  # noqa: E402
from import_inspect import validate as ii_validate  # noqa: E402

# The header gen_tasks.main() writes into a synthetic task's spec.toml, e.g.:
#   # Synthetic task (tools/gen_tasks.py --family text --seed 1)
SYNTHETIC_HEADER_RE = re.compile(r"--family\s+(?P<family>\S+)\s+--seed\s+(?P<seed>-?\d+)")
# The folder name gen_tasks.make() picks: f"{family}-d{k}-{idx}"
FOLDER_RE = re.compile(r"^(?P<family>[a-z]+)-d(?P<k>\d+)-(?P<idx>\d+)$")


def find_specs(corpus: Path) -> list[Path]:
    return sorted(corpus.glob("*/*/spec.toml"))


def synthetic_params(spec_path: Path) -> tuple[str, int, int, int] | None:
    """(family, k, idx, seed) if this spec was made by gen_tasks.py, else None."""
    text = spec_path.read_text()
    header = text.splitlines()[0] if text else ""
    m = SYNTHETIC_HEADER_RE.search(header)
    if not m:
        return None
    family, seed = m.group("family"), int(m.group("seed"))
    fm = FOLDER_RE.match(spec_path.parent.name)
    if not fm or fm.group("family") != family or family not in gen_tasks.FAMILIES:
        return None
    return family, int(fm.group("k")), int(fm.group("idx")), seed


def audit_one(spec_path: Path) -> dict:
    name = spec_path.parent.name
    collection = spec_path.parent.parent.name
    params = synthetic_params(spec_path)
    record = {
        "name": name,
        "collection": collection,
        "path": f"{collection}/{name}/spec.toml",
        "kind": "synthetic" if params else "imported",
        "reference_checked": params is not None,
    }
    try:
        definition = tomllib.loads(spec_path.read_text())
        for folder in ("work", "checks"):
            for source in (spec_path.parent / folder).rglob("*.py"):
                compile(source.read_bytes(), source.name, "exec")
        if collection.startswith("synthetic-") and params is None:
            raise ValueError("Synthetic task is missing a valid generator recipe")
        if params is not None:
            family, k, idx, seed = params
            if family != definition.get("family") or k != definition.get("difficulty"):
                raise ValueError("Task metadata differs from its generator recipe")
            _, ref = gen_tasks.make(family, idx, k, seed)
            ok, why = ii_validate(spec_path, {"solution.py": ref})
        else:
            ok, why = ii_validate(spec_path, None)
        record["ok"] = bool(ok)
        record["reason"] = why
    except Exception as exc:  # defensive: a broken task must show up as a failure, not a crash
        record["ok"] = False
        record["reason"] = f"{type(exc).__name__}: {exc}"
    return record


def build_report(corpus: Path, specs: list[Path]) -> dict:
    results = sorted((audit_one(p) for p in specs), key=lambda r: (r["collection"], r["name"]))

    collections: dict[str, dict] = {}
    for r in results:
        c = collections.setdefault(r["collection"], {
            "total": 0,
            "stub_only_tasks": 0, "stub_only_ok": 0,
            "reference_checked_tasks": 0, "reference_checked_ok": 0,
            "failed": 0,
        })
        c["total"] += 1
        if r["reference_checked"]:
            c["reference_checked_tasks"] += 1
            c["reference_checked_ok"] += int(r["ok"])
        else:
            c["stub_only_tasks"] += 1
            c["stub_only_ok"] += int(r["ok"])
        if not r["ok"]:
            c["failed"] += 1

    failures = [r for r in results if not r["ok"]]
    return {
        "corpus": corpus.name,
        "total_tasks": len(results),
        "collections": collections,
        "failures": failures,
        "all_valid": not failures,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default=str(TOOLS_DIR.parent / "tasks"),
                     help="root holding <collection>/<task>/spec.toml folders (default: tasks/ next to tools/)")
    ap.add_argument("--out", default=None, help="write the JSON report to this path instead of stdout")
    args = ap.parse_args(argv)

    corpus = Path(args.corpus).resolve()
    if not corpus.is_dir():
        print(f"no such corpus directory: {corpus}", file=sys.stderr)
        return 2

    specs = find_specs(corpus)
    if not specs:
        print(f"no spec.toml files found under {corpus}", file=sys.stderr)
        return 2

    report = build_report(corpus, specs)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text)
    else:
        sys.stdout.write(text)
    return 0 if report["all_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
