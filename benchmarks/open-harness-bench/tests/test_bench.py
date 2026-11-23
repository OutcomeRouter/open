"""Smoke tests: every spec loads, and the eval passes a good agent and fails a lazy one."""
import glob, json, os, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import orbench.core as orc

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
        inspect = ROOT / ".venv/bin/inspect"
        if not inspect.exists():
            self.skipTest("inspect not installed")
        subprocess.run([str(inspect), "eval", "orbench_eval.py@outcome", "-T", "spec=examples/fizzbuzz/spec.toml",
                        "-T", f"agent={agent}", "--model", "mockllm/model", "--log-dir", f"{home}/logs", "--display", "none"],
                       cwd=ROOT, env=env, check=True, capture_output=True)
        log = sorted(glob.glob(f"{home}/logs/*.eval"))[-1]
        h = json.loads(zipfile.ZipFile(log).read("header.json"))
        return h["results"]["scores"][0]["metrics"]["accuracy"]["value"]

    def test_good_agent_passes(self):
        self.assertEqual(self.run_eval("demo-good"), 1.0)

    def test_lazy_agent_fails(self):
        self.assertEqual(self.run_eval("demo-lazy"), 0.0)

if __name__ == "__main__":
    unittest.main()
