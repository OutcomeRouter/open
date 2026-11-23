"""Tests for tools/audit_corpus.py: no model calls, no network, no git operations.

Builds tiny synthetic and imported-style task fixtures on disk (via the real
tools/gen_tasks.py and tools/import_inspect.py helpers) in a temp directory, then
checks the audit script's parsing, counting and JSON report against them.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import audit_corpus as ac  # noqa: E402
import gen_tasks  # noqa: E402
from import_inspect import Imported, write_task  # noqa: E402


def make_synthetic_fixture(out: Path, family: str, idx: int, k: int, seed: int) -> Path:
    """Write one synthetic task exactly as `tools/gen_tasks.py --family ... --seed ...` would."""
    t, ref = gen_tasks.make(family, idx, k, seed)
    p = write_task(t, out)
    text = p.read_text().replace(
        f"# Imported from Inspect evals: synthetic/{family}",
        f"# Synthetic task (tools/gen_tasks.py --family {family} --seed {seed})", 1)
    p.write_text(text.replace("type = ", f'difficulty = {k}\nfamily = "{family}"\ntype = ', 1))
    return p


def make_imported_fixture(out: Path, name: str) -> Path:
    """A tiny HumanEval-style task: stub raises NotImplementedError, hidden check wants add()."""
    t = Imported(
        name=name, source=f"fixture/{name}", type="code",
        task="Implement add(a, b) in solution.py. Use only the Python standard library.",
        files={"solution.py": "def add(a, b):\n    raise NotImplementedError\n"},
        visible=("the module imports", "python3 -c 'import solution'"),
        hidden="from solution import add\nassert add(2, 3) == 5\n",
    )
    return write_task(t, out)


class SyntheticParams(unittest.TestCase):
    def test_parses_header_and_folder(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "tasks" / "synthetic-text"
            spec = make_synthetic_fixture(out, "text", idx=0, k=2, seed=7)
            params = ac.synthetic_params(spec)
            self.assertEqual(params, ("text", 2, 0, 7))

    def test_imported_task_has_no_synthetic_params(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "tasks" / "humaneval"
            spec = make_imported_fixture(out, "humaneval-0")
            self.assertIsNone(ac.synthetic_params(spec))


class AuditOne(unittest.TestCase):
    def test_valid_synthetic_task_passes_with_reference_checked(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "tasks" / "synthetic-text"
            spec = make_synthetic_fixture(out, "text", idx=0, k=2, seed=7)
            r = ac.audit_one(spec)
            self.assertTrue(r["ok"], r["reason"])
            self.assertTrue(r["reference_checked"])
            self.assertEqual(r["kind"], "synthetic")

    def test_valid_imported_task_passes_as_stub_only(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "tasks" / "humaneval"
            spec = make_imported_fixture(out, "humaneval-0")
            r = ac.audit_one(spec)
            self.assertTrue(r["ok"], r["reason"])
            self.assertFalse(r["reference_checked"])
            self.assertEqual(r["kind"], "imported")

    def test_stub_that_already_passes_is_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "tasks" / "humaneval"
            t = Imported(
                name="humaneval-ok", source="fixture/humaneval-ok", type="code",
                task="Implement add(a, b) in solution.py.",
                files={"solution.py": "def add(a, b):\n    return a + b\n"},
                visible=("the module imports", "python3 -c 'import solution'"),
                hidden="from solution import add\nassert add(2, 3) == 5\n",
            )
            spec = write_task(t, out)
            r = ac.audit_one(spec)
            self.assertFalse(r["ok"])
            self.assertIn("already pass", r["reason"])

    def test_gen_tasks_make_exception_is_reported_not_raised(self):
        """A corrupted difficulty (more steps than the family's step library) makes
        gen_tasks.make() raise; audit_one must report that as a failure, not crash."""
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "tasks" / "synthetic-text"
            spec = make_synthetic_fixture(out, "text", idx=0, k=1, seed=7)
            text = spec.read_text().replace("difficulty = 1", "difficulty = 999", 1)
            text = text.replace("text-d1-0", "text-d999-0")
            spec.write_text(text)
            moved = spec.parent.rename(spec.parent.with_name("text-d999-0"))
            spec = moved / "spec.toml"
            r = ac.audit_one(spec)
            self.assertFalse(r["ok"])
            self.assertIn("reason", r)

    def test_synthetic_task_with_tampered_difficulty_fails_reference_check(self):
        """A regenerated reference that no longer matches the on-disk checks must be reported, not raise."""
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "tasks" / "synthetic-text"
            spec = make_synthetic_fixture(out, "text", idx=0, k=2, seed=7)
            text = spec.read_text().replace("difficulty = 2", "difficulty = 3", 1)
            spec.write_text(text)
            r = ac.audit_one(spec)
            self.assertFalse(r["ok"])
            self.assertTrue(r["reference_checked"])


class BuildReport(unittest.TestCase):
    def _fixture_corpus(self, td: Path) -> Path:
        corpus = Path(td) / "tasks"
        make_synthetic_fixture(corpus / "synthetic-text", "text", idx=0, k=1, seed=1)
        make_synthetic_fixture(corpus / "synthetic-text", "text", idx=1, k=2, seed=1)
        make_imported_fixture(corpus / "humaneval", "humaneval-0")
        return corpus

    def test_counts_and_validity(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = self._fixture_corpus(Path(td))
            specs = ac.find_specs(corpus)
            self.assertEqual(len(specs), 3)
            report = ac.build_report(corpus, specs)
            self.assertTrue(report["all_valid"], report["failures"])
            self.assertEqual(report["total_tasks"], 3)
            self.assertEqual(set(report["collections"]), {"synthetic-text", "humaneval"})
            st = report["collections"]["synthetic-text"]
            self.assertEqual(st["total"], 2)
            self.assertEqual(st["reference_checked_tasks"], 2)
            self.assertEqual(st["reference_checked_ok"], 2)
            self.assertEqual(st["stub_only_tasks"], 0)
            he = report["collections"]["humaneval"]
            self.assertEqual(he["total"], 1)
            self.assertEqual(he["stub_only_tasks"], 1)
            self.assertEqual(he["stub_only_ok"], 1)
            self.assertEqual(report["failures"], [])

    def test_report_json_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = self._fixture_corpus(Path(td))
            specs = ac.find_specs(corpus)
            a = json.dumps(ac.build_report(corpus, specs), sort_keys=True)
            b = json.dumps(ac.build_report(corpus, specs), sort_keys=True)
            self.assertEqual(a, b)

    def test_failure_is_counted_and_listed(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = Path(td) / "tasks"
            make_imported_fixture(corpus / "humaneval", "humaneval-good")
            t = Imported(
                name="humaneval-bad", source="fixture/humaneval-bad", type="code",
                task="Implement add(a, b) in solution.py.",
                files={"solution.py": "def add(a, b):\n    return a + b\n"},  # stub already passes: invalid
                visible=("the module imports", "python3 -c 'import solution'"),
                hidden="from solution import add\nassert add(2, 3) == 5\n",
            )
            write_task(t, corpus / "humaneval")
            specs = ac.find_specs(corpus)
            report = ac.build_report(corpus, specs)
            self.assertFalse(report["all_valid"])
            self.assertEqual(report["collections"]["humaneval"]["failed"], 1)
            self.assertEqual(len(report["failures"]), 1)
            self.assertEqual(report["failures"][0]["name"], "humaneval-bad")


class MainCLI(unittest.TestCase):
    def test_exits_nonzero_on_invalid_task_and_writes_json(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = Path(td) / "tasks"
            t = Imported(
                name="humaneval-bad", source="fixture/humaneval-bad", type="code",
                task="Implement add(a, b) in solution.py.",
                files={"solution.py": "def add(a, b):\n    return a + b\n"},
                visible=("the module imports", "python3 -c 'import solution'"),
                hidden="from solution import add\nassert add(2, 3) == 5\n",
            )
            write_task(t, corpus / "humaneval")
            out_path = Path(td) / "report.json"
            rc = ac.main(["--corpus", str(corpus), "--out", str(out_path)])
            self.assertEqual(rc, 1)
            report = json.loads(out_path.read_text())
            self.assertFalse(report["all_valid"])

    def test_exits_zero_on_valid_corpus(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = Path(td) / "tasks"
            make_imported_fixture(corpus / "humaneval", "humaneval-0")
            out_path = Path(td) / "report.json"
            rc = ac.main(["--corpus", str(corpus), "--out", str(out_path)])
            self.assertEqual(rc, 0)
            report = json.loads(out_path.read_text())
            self.assertTrue(report["all_valid"])

    def test_missing_corpus_exits_with_usage_error(self):
        with tempfile.TemporaryDirectory() as td:
            rc = ac.main(["--corpus", str(Path(td) / "nope")])
            self.assertEqual(rc, 2)

    def test_empty_corpus_exits_with_usage_error(self):
        with tempfile.TemporaryDirectory() as td:
            empty = Path(td) / "tasks"
            empty.mkdir()
            rc = ac.main(["--corpus", str(empty)])
            self.assertEqual(rc, 2)


class RealCorpusSelection(unittest.TestCase):
    """The default --corpus must resolve to the real checked-in tasks/ folder."""

    def test_default_corpus_is_repo_tasks_dir(self):
        parser_default = Path(ac.TOOLS_DIR.parent / "tasks").resolve()
        self.assertEqual(parser_default, (ROOT / "tasks").resolve())


if __name__ == "__main__":
    unittest.main()
