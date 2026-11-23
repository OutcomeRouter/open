"""Demo agent that gets FizzBuzz right about half the time."""
import pathlib, random, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _solutions import CORRECT, WRONG
time.sleep(0.5)
ok = random.random() < 0.5
pathlib.Path("fizzbuzz.py").write_text(CORRECT if ok else WRONG)
print("flaky: wrote", "a correct" if ok else "a broken", "fizzbuzz.py")
