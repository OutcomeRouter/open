#!/usr/bin/env python3
"""Turn Inspect eval samples into OutcomeRouter task specs.

    .venv/bin/python tools/import_inspect.py humaneval --ids 0 32 75 129 145 --out tasks/humaneval
    .venv/bin/python tools/import_inspect.py mbpp --sample 10 --seed 1 --out tasks/mbpp
    .venv/bin/python tools/import_inspect.py class_eval --ids 0 5 --out tasks/class_eval

For each sample it writes
  <out>/<name>/work/...            what the agent starts from (never a reference solution)
  <out>/<name>/checks/hidden.py    the eval's own tests, kept outside the agent's folder
  <out>/<name>/spec.toml           a visible check the agent can run, and the eval's tests as a withheld check

Specs refer to their hidden tests through {spec_dir}, so a task folder can be moved,
exported or mounted into a container.
"""
from __future__ import annotations

import argparse
import ast
import json
import random
from dataclasses import dataclass
from pathlib import Path

HIDDEN_HEADER = "import os, sys\nsys.path.insert(0, os.getcwd())\n"


@dataclass
class Imported:
    name: str          # folder name
    source: str        # the eval sample id
    type: str          # task type, for track records
    task: str          # what the agent is asked to do
    files: dict        # starting files, relative to work/
    visible: tuple     # (name, cmd) of the check the agent sees
    hidden: str        # Python source of the withheld check (runs in the result folder)
    minutes: int = 15
    protect: tuple = ()  # starting files restored before checks, so an agent cannot edit its way to a pass


def write_task(t: Imported, out: Path) -> Path:
    d = out / t.name
    (d / "work").mkdir(parents=True, exist_ok=True)
    (d / "checks").mkdir(exist_ok=True)
    for rel, text in t.files.items():
        (d / "work" / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / "work" / rel).write_text(text)
    (d / "checks" / "hidden.py").write_text(HIDDEN_HEADER + t.hidden.rstrip() + "\nprint('ok')\n")
    q = json.dumps
    (d / "spec.toml").write_text(
        f"# Imported from Inspect evals: {t.source}\n"
        f"type = {q(t.type)}\ntask = {q(t.task)}\nworkdir = \"work\"\n"
        f"deadline_minutes = {t.minutes}\nmax_attempts = 3\nattempt_timeout_minutes = {max(5, t.minutes // 2)}\n"
        + (f"protect = {q(list(t.protect))}\n" if t.protect else "") + "\n"
        f"[[checks]]\nname = {q(t.visible[0])}\nlevel = \"tested\"\ncmd = {q(t.visible[1])}\n\n"
        f"[[checks]]\nname = {q(t.source + ' hidden tests')}\nlevel = \"tested\"\nwithheld = true\n"
        'cmd = "python3 {spec_dir}/checks/hidden.py"\n'
    )
    return d / "spec.toml"


# ---------------------------------------------------------------- per eval


def examples_check(source: str) -> tuple[dict, tuple, tuple]:
    """Docstring examples as a separate doctest file the agent cannot edit (it is protected).
    Running doctest on solution.py itself would let an agent pass by deleting the examples."""
    import doctest

    ex = []
    try:  # examples come from the docstrings only, never the surrounding code
        tree = ast.parse(source + "\n    pass\n" if source.rstrip().endswith('"""') else source)
    except SyntaxError:
        tree = None
    for node in ast.walk(tree) if tree else []:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            doc = ast.get_docstring(node)
            try:
                ex += doctest.DocTestParser().get_examples(doc or "")
            except ValueError:  # malformed examples in this docstring
                pass
    if not ex:
        return {}, ("the module imports", "python3 -c 'import solution'"), ()
    body = [">>> from solution import *"]
    for e in ex:
        src = e.source.rstrip("\n").split("\n")
        body += [f">>> {src[0]}"] + [f"... {l}" for l in src[1:]]
        body += e.want.rstrip("\n").split("\n") if e.want else []
    return ({"examples.txt": "\n".join(body) + "\n"},
            ("docstring examples pass", "python3 -m doctest examples.txt"), ("examples.txt",))


def from_humaneval(s) -> Imported:
    md = s.metadata
    files, visible, protect = examples_check(md["prompt"])
    return Imported(
        name=f"humaneval-{str(s.id).split('/')[-1]}", source=str(s.id), type="code",
        task=(f"Implement `{md['entry_point']}` in solution.py so it does what its docstring says. "
              "Keep the signature. Use only the Python standard library."),
        files={"solution.py": md["prompt"].rstrip() + "\n    raise NotImplementedError\n", **files},
        visible=visible, protect=protect,
        # tests may use helpers defined in the stub
        hidden=f"from solution import *\n\n{md['test']}\n\ncheck({md['entry_point']})",
    )


def _list(v) -> list:
    return v if isinstance(v, list) else ast.literal_eval(v)


def from_mbpp(s) -> Imported:
    md = s.metadata
    tests = _list(md["test_list"])
    imports = _list(md.get("test_imports") or "[]")
    first = tests[0]
    return Imported(
        name=f"mbpp-{md['task_id']}", source=f"MBPP/{md['task_id']}", type="code",
        task=(f"{md['prompt'].strip()}\n\nWrite it in solution.py. The function name and argument order "
              f"must match this example: `{first}`. Use only the Python standard library."),
        files={"solution.py": "# Write your solution here.\n", "test_example.py":
               "\n".join(imports + ["from solution import *", "", first, "print('ok')"]) + "\n"},
        visible=("the example passes", "python3 test_example.py"), protect=("test_example.py",),
        hidden="\n".join(imports + ["from solution import *", ""] + tests),
    )


def from_class_eval(s) -> Imported:
    md = s.metadata
    cls = md["class_name"]
    test_classes = _list(md["test_classes"])
    files, visible, protect = examples_check(md["skeleton"])
    runner = ("\nimport unittest as _ut\n_s = _ut.TestSuite()\n"
              + "".join(f"_s.addTests(_ut.defaultTestLoader.loadTestsFromTestCase({t}))\n" for t in test_classes)
              + "_r = _ut.TextTestRunner(verbosity=1).run(_s)\nsys.exit(0 if _r.wasSuccessful() else 1)")
    return Imported(
        name=f"classeval-{md['task_id'].split('_')[-1]}", source=md["task_id"], type="code-class",
        task=(f"Implement every method of `{cls}` in solution.py so it does what its docstrings say. "
              "Keep the class name, method names and signatures. Use only the Python standard library "
              "and the imports already in the file."),
        files={"solution.py": md["skeleton"].rstrip() + "\n", **files},
        visible=visible, protect=protect,
        hidden=f"from solution import *\n\n{md['test']}\n{runner}",
        minutes=30,
    )


# Reference solutions, used only to validate an imported task (never written to the task).
REFERENCE = {
    "humaneval": lambda s: {"solution.py": s.metadata["prompt"] + str(s.target)},
    "mbpp": lambda s: {"solution.py": s.metadata["code"]},
    "class_eval": lambda s: {"solution.py": s.metadata["solution_code"]},
}


def without_examples(t: Imported) -> Imported:
    """Fallback when a docstring's examples are wrong (the reference fails them): the visible
    check becomes "the module imports", and the eval's own tests still decide the pass."""
    files = {k: v for k, v in t.files.items() if k != "examples.txt"}
    return Imported(**{**t.__dict__, "files": files, "protect": (),
                       "visible": ("the module imports", "python3 -c 'import solution'")})


def validate(spec_path: Path, files: dict | None) -> tuple[bool, str]:
    """Run the task's checks on its starting files (must fail) and on the reference (must pass).
    A task whose reference fails, or whose stub already passes, is broken and should not be used."""
    import shutil
    import subprocess
    import tempfile

    spec_dir = spec_path.resolve().parent
    cmds = []
    import tomllib
    for c in tomllib.loads(spec_path.read_text())["checks"]:
        cmds.append(c["cmd"].replace("{spec_dir}", str(spec_dir)))

    def all_pass(overlay: dict | None) -> bool:
        with tempfile.TemporaryDirectory() as t:
            w = Path(t) / "work"
            shutil.copytree(spec_dir / "work", w)
            for rel, text in (overlay or {}).items():
                (w / rel).write_text(text)
            return all(subprocess.run(["bash", "-c", c], cwd=w, capture_output=True, timeout=120).returncode == 0
                       for c in cmds)

    if all_pass(None):
        return False, "the starting files already pass every check"
    if files is not None and not all_pass(files):
        return False, "the reference solution fails the checks"
    return True, "ok"


EVALS = {
    "humaneval": ("inspect_evals.humaneval", "humaneval", from_humaneval, lambda s: str(s.id).split("/")[-1]),
    "mbpp": ("inspect_evals.mbpp", "mbpp", from_mbpp, lambda s: str(s.metadata["task_id"])),
    "class_eval": ("inspect_evals.class_eval", "class_eval", from_class_eval,
                   lambda s: s.metadata["task_id"].split("_")[-1]),
}


def load(eval_name: str):
    import importlib

    mod, fn, conv, key = EVALS[eval_name]
    return list(getattr(importlib.import_module(mod), fn)().dataset), conv, key


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("eval", choices=sorted(EVALS))
    pick = ap.add_mutually_exclusive_group(required=True)
    pick.add_argument("--ids", nargs="+", help="sample ids (HumanEval/MBPP/ClassEval numbers)")
    pick.add_argument("--sample", type=int, help="pick this many samples at random")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="tasks")
    ap.add_argument("--no-validate", action="store_true", help="skip the reference-solution check")
    a = ap.parse_args()
    samples, conv, key = load(a.eval)
    by_id = {key(s): s for s in samples}
    if a.ids:
        missing = [i for i in a.ids if i not in by_id]
        if missing:
            raise SystemExit(f"unknown ids: {' '.join(missing)}")
        chosen = [by_id[i] for i in a.ids]
    else:
        chosen = random.Random(a.seed).sample(samples, min(a.sample, len(samples)))
    import shutil
    for s in chosen:
        t = conv(s)
        p = write_task(t, Path(a.out))
        if a.no_validate:
            print(p)
            continue
        ref = REFERENCE[a.eval](s)
        ok, why = validate(p, ref)
        if not ok and "examples.txt" in t.files:
            shutil.rmtree(p.parent)
            p = write_task(without_examples(t), Path(a.out))
            ok, why = validate(p, ref)
            why += " (also without the docstring examples)"
            if ok:
                print(f"note {p.parent.name}: docstring examples disagree with the reference; visible check is import only")
        if ok:
            print(p)
        else:
            shutil.rmtree(p.parent)
            print(f"skipped {p.parent.name}: {why}")


if __name__ == "__main__":
    main()
