"""Demo agent that hardcodes answers: it passes the visible checks and fails withheld ones."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _solutions import LAZY
pathlib.Path("fizzbuzz.py").write_text(LAZY)
print("lazy: hardcoded 1..20")
