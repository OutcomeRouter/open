"""Run the bounded TLC model and verify that each missing guard has a counterexample."""
import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = [(None, None), ("CheckScope", "ScopeAtCommit"),
         ("CheckRevision", "RevisionAtCommit"), ("CheckOnce", "AtMostOnce")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jar", type=Path)
    parser.add_argument("--java", default="java")
    args = parser.parse_args()
    for guard, invariant in CASES:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            shutil.copy(ROOT / "Clarification.tla", work)
            config = (ROOT / "Clarification.cfg").read_text()
            if guard:
                config = config.replace(f"{guard} = TRUE", f"{guard} = FALSE")
            (work / "Clarification.cfg").write_text(config)
            result = subprocess.run([args.java, "-XX:+UseParallelGC", "-cp", str(args.jar.resolve()),
                                     "tlc2.TLC", "-workers", "1", "-deadlock", "Clarification"],
                                    cwd=work, capture_output=True, text=True, timeout=120)
            log = result.stdout + result.stderr
            if guard:
                ok = result.returncode != 0 and f"Invariant {invariant} is violated" in log
            else:
                ok = result.returncode == 0 and "No error has been found" in log
            if not ok:
                raise SystemExit(log)
            states = re.search(r"(\d+) distinct states found", log)
            print(f"{guard or 'All guards'}: {invariant or 'all invariants hold'}; "
                  f"{states[1] if states else '?'} distinct states visited")


if __name__ == "__main__":
    main()
