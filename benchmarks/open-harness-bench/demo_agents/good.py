"""Demo agent that solves the FizzBuzz example correctly. Costs the most."""
import pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _solutions import CORRECT
time.sleep(1.0)
pathlib.Path("fizzbuzz.py").write_text(CORRECT)
print("good: wrote a correct fizzbuzz.py")
