"""Smoke tests: every spec loads, and the eval passes a good agent and fails a lazy one."""
import glob, os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import orbench.core as orc
import orbench_eval as oe

class Specs(unittest.TestCase):
    def test_every_spec_loads(self):
        paths = sorted(glob.glob(str(ROOT / "examples/*/spec.toml")) + glob.glob(str(ROOT / "tasks/*/*/spec.toml")))
        self.assertTrue(paths)
        for p in paths:
            s = orc.load_spec(p)
            self.assertTrue(s.checks, p)
            self.assertTrue(all(c.level in orc.LEVELS for c in s.checks), p)

class Eval(unittest.TestCase):
    def run_eval(self, agent):
        home = tempfile.mkdtemp()
        env = dict(os.environ, ORBENCH_HOME=home)
        inspect = Path(sys.executable).with_name("inspect")
        subprocess.run([str(inspect), "eval", "orbench_eval.py@outcome", "-T", "spec=examples/fizzbuzz/spec.toml",
                        "-T", f"agent={agent}", "--model", "mockllm/model", "--log-dir", f"{home}/logs", "--display", "none"],
                       cwd=ROOT, env=env, check=True, capture_output=True)
        log = sorted(glob.glob(f"{home}/logs/*.eval"))[-1]
        from inspect_ai.log import read_eval_log
        result = read_eval_log(log)
        self.assertEqual(result.status, "success")
        return result.results.scores[0].metrics["accuracy"].value

    def test_good_agent_passes(self):
        self.assertEqual(self.run_eval("demo-good"), 1.0)

    def test_lazy_agent_fails(self):
        self.assertEqual(self.run_eval("demo-lazy"), 0.0)

class SandboxSelection(unittest.TestCase):
    """spec.sandbox must drive the Inspect Task, not be silently downgraded to local."""

    def _spec(self, sandbox):
        s = orc.load_spec(str(ROOT / "examples/fizzbuzz/spec.toml"))
        s.sandbox = sandbox
        return s

    def _agent(self):
        return next(a for a in orc.load_agents() if a.name == "demo-good")

    def test_docker_rejected_before_execution(self):
        with self.assertRaisesRegex(ValueError, "only the local sandbox"):
            oe.build_task(self._spec("docker"), self._agent())

    def test_suite_mixed_sandboxes_rejected(self):
        tmp = Path(tempfile.mkdtemp())
        for sandbox in ("local", "docker"):
            d = tmp / sandbox
            d.mkdir()
            spec_src = (ROOT / "examples/fizzbuzz/spec.toml").read_text()
            (d / "spec.toml").write_text(f'sandbox = "{sandbox}"\n' + spec_src)
            (d / "work").mkdir()
        with self.assertRaisesRegex(ValueError, "only the local sandbox"):
            oe.suite(str(tmp), "demo-good")

if __name__ == "__main__":
    unittest.main()
