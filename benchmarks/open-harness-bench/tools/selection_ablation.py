"""Isolate the selector in a two-proposal harness using the synthetic task corpus."""
import argparse
import ast
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

from audit_corpus import synthetic_params
from gen_tasks import FAMILIES, make


def example_lookup(source, function):
    """Build a deliberately narrow candidate using only the published example pairs."""
    table = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assert):
            test = node.test
            call = test.left
            if call.func.id != function or len(call.args) != 1 or not isinstance(test.ops[0], ast.Eq):
                raise ValueError("Expected a single-input equality example")
            table[repr(ast.literal_eval(call.args[0]))] = ast.literal_eval(test.comparators[0])
    if not table:
        raise ValueError("Task needs visible examples")
    return f"def {function}(value):\n    return {table!r}.get(repr(value))\n"


def passes(code, script):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "solution.py").write_text(code)
        (root / "check.py").write_text(script)
        result = subprocess.run([sys.executable, "check.py"], cwd=root, capture_output=True, timeout=30)
        return result.returncode == 0


def evaluate(path):
    family, steps, index, seed = synthetic_params(path)
    function, factory, _ = FAMILIES[family]
    _, reference = make(family, index, steps, seed)
    visible = (path.parent / "work/test_examples.py").read_text()
    hidden = (path.parent / "checks/hidden.py").read_text()
    candidates = {"example_lookup": example_lookup(visible, function), "reference": reference}
    order = list(candidates)
    task = path.parent.name
    random.Random("candidate-order/" + task).shuffle(order)
    # A separate seed fixes one development probe. The selector never reads the final check.
    _, _, generator = factory(random.Random(f"{seed}-{family}-{index}-{steps}"), steps)
    helpers = {}
    exec(generator, helpers)
    probe_input = helpers["gen"](random.Random("development/" + task))
    oracle = {}
    exec(reference, oracle)
    expected = oracle[function](probe_input)
    probe = f"from solution import {function}\nassert {function}({probe_input!r}) == {expected!r}\n"
    if not all(passes(code, visible) for code in candidates.values()):
        raise RuntimeError(f"{task}: control candidate failed the visible examples")
    first = order[0]
    second = next(name for name in order if passes(candidates[name], probe))
    final = {name: passes(code, hidden) for name, code in candidates.items()}
    if not final["reference"]:
        raise RuntimeError(f"{task}: reference failed the final check")
    return {"task": task, "family": family, "candidate_order": order,
            "visible_only": first, "with_probe": second,
            "visible_only_pass": final[first], "with_probe_pass": final[second]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    corpus = Path(__file__).resolve().parents[1] / "tasks"
    tasks = [evaluate(p) for p in sorted(corpus.glob("synthetic-*/*/spec.toml"))]
    if not tasks:
        raise ValueError("No synthetic tasks found")
    counts = {"pairs": len(tasks), "visible_only_passes": sum(t["visible_only_pass"] for t in tasks),
              "with_probe_passes": sum(t["with_probe_pass"] for t in tasks),
              "gains": sum(t["with_probe_pass"] and not t["visible_only_pass"] for t in tasks),
              "losses": sum(t["visible_only_pass"] and not t["with_probe_pass"] for t in tasks)}
    report = {"experiment": "synthetic-selector-v1", "counts": counts, "tasks": tasks}
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
