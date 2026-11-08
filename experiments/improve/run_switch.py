"""benchmark.py with the switch prototype (leks.py, MODE=switch) as
--ablate switch. Set MODE=switch and SWITCH=<share> in the environment."""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "improve"))
import benchmark
import leks

benchmark.ALGORITHMS["switch"] = leks.Leks

if __name__ == "__main__":
    benchmark.main()
