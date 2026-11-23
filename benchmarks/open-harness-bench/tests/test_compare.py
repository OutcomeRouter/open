import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as Row

from tools.compare import compare
from orbench.provenance import task_identity


def arm(agent, verdict):
    metadata = dict(fixture_sha256="fixture", runner_sha256="runner", sandbox="local",
                    agent=agent, worker_layers={"coordination": agent}, command_sha256=agent,
                    inspect_version="1", tier="standard", timeout_minutes=1)
    score = Row(metadata={"verdict": verdict})
    return Row(status="success", samples=[Row(id="example", epoch=1, error=None,
               metadata=metadata, scores={"checks": score})])


class Comparison(unittest.TestCase):
    def test_task_level_gain_and_loss(self):
        left, right = arm("solo", "fail"), arm("pair", "pass")
        report = compare(left, right)
        self.assertEqual(report["right_only"], 1)
        self.assertEqual(report["changed_verdicts"][0]["task"], "example")
        self.assertEqual(compare(right, left)["left_only"], 1)

    def test_rejects_unmatched_runs(self):
        left = arm("solo", "fail")
        for field in ("runner_sha256", "fixture_sha256", "timeout_minutes"):
            right = copy.deepcopy(left)
            right.samples[0].metadata[field] = "different"
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, field):
                compare(left, right)
        right = copy.deepcopy(left)
        right.samples[0].epoch = 2
        with self.assertRaisesRegex(ValueError, "epochs"):
            compare(left, right)

    def test_incomplete_run_is_not_a_failed_attempt(self):
        right = arm("pair", "fail")
        right.status = "error"
        with self.assertRaisesRegex(ValueError, "completed log"):
            compare(arm("solo", "pass"), right)

    def test_fixture_hash_covers_work_and_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec = Row(path=root / "spec.toml", workdir=root / "work")
            spec.path.write_text("# task")
            spec.workdir.mkdir()
            (root / "checks").mkdir()
            hashes = [task_identity(spec)]
            for path in (spec.workdir / "a", root / "checks" / "b"):
                path.write_text("fixture")
                hashes.append(task_identity(spec))
            self.assertEqual(len(set(hashes)), 3)
