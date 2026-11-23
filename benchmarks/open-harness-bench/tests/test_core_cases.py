"""Core semantic cases, one class per harness layer. Each test names the case the README lists."""
import glob, json, os, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import orbench.core as orc

SPEC = ROOT / "examples/fizzbuzz/spec.toml"
AGENTS = """
[[agents]]
name = "demo-good"
cmd = "python3 {demo}/good.py {prompt_file}"
price_usd = 0.40
[[agents]]
name = "demo-lazy"
cmd = "python3 {demo}/lazy.py {prompt_file}"
price_usd = 0.05
[[agents]]
name = "demo-cheat"
cmd = "python3 {demo}/cheat.py {prompt_file}"
price_usd = 0.05
[[agents]]
name = "demo-noop"
cmd = "true"
price_usd = 0.01
"""

def run(agent, spec=SPEC):
    inspect = ROOT / ".venv/bin/inspect"
    if not inspect.exists():
        raise unittest.SkipTest("inspect not installed")
    home = Path(tempfile.mkdtemp())
    (home / "agents.toml").write_text(AGENTS)
    subprocess.run([str(inspect), "eval", "orbench_eval.py@outcome", "-T", f"spec={spec}", "-T", f"agent={agent}",
                    "--model", "mockllm/model", "--log-dir", str(home / "logs"), "--display", "none"],
                   cwd=ROOT, env=dict(os.environ, ORBENCH_HOME=str(home)), check=True, capture_output=True)
    z = zipfile.ZipFile(sorted(glob.glob(str(home / "logs/*.eval")))[-1])
    sample = json.loads(z.read([n for n in z.namelist() if n.startswith("samples/")][0]))
    return next(iter(sample["scores"].values()))["metadata"]

class Task(unittest.TestCase):
    def test_starting_files_fail(self):
        """Task: the starting files alone never pass."""
        self.assertEqual(run("demo-noop")["verdict"], "fail")

    def test_digest_changes_with_the_spec(self):
        """Task: editing the spec changes its digest."""
        d = Path(tempfile.mkdtemp())
        p = d / "spec.toml"
        p.write_text(SPEC.read_text().replace('workdir = "work"', f'workdir = "{SPEC.parent / "work"}"'))
        a = orc.load_spec(str(p)).digest
        p.write_text(p.read_text() + "\n# edited\n")
        self.assertNotEqual(a, orc.load_spec(str(p)).digest)

class Checks(unittest.TestCase):
    def test_withheld_check_counts(self):
        """Checks: passing every visible check is not enough; the withheld check decides."""
        m = run("demo-lazy")
        visible = [c for c in m["checks"] if not c["withheld"]]
        self.assertTrue(visible and all(c["passed"] for c in visible))
        self.assertEqual(m["verdict"], "fail")

    def test_failed_check_stops_the_attempt(self):
        """Checks: the first failed check stops the run; later checks are not run."""
        m = run("demo-noop")
        self.assertFalse(m["checks"][-1]["passed"])
        self.assertLess(len(m["checks"]), len(orc.load_spec(str(SPEC)).checks))

class Sandbox(unittest.TestCase):
    def test_protected_files_are_restored(self):
        """Sandbox: a worker that rewrites the tests still fails, because protected files are restored."""
        self.assertEqual(run("demo-cheat")["verdict"], "fail")

class Worker(unittest.TestCase):
    def test_prompt_hides_withheld_checks(self):
        """Worker: the prompt shows visible checks and never a withheld one."""
        s = orc.load_spec(str(SPEC))
        prompt = orc.prompt_for(s)
        for c in s.checks:
            (self.assertNotIn if c.withheld else self.assertIn)(c.name, prompt)

class Verdict(unittest.TestCase):
    def test_pass_needs_every_check(self):
        """Verdict: pass only when every check passes, with each check's output kept."""
        m = run("demo-good")
        self.assertEqual(m["verdict"], "pass")
        self.assertEqual(len(m["checks"]), len(orc.load_spec(str(SPEC)).checks))
        self.assertTrue(all("output" in c for c in m["checks"]))

if __name__ == "__main__":
    unittest.main(verbosity=2)
