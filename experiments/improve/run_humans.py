"""benchmark.py with the human-hearing prototype as --ablate humans."""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import benchmark
import humans

benchmark.ALGORITHMS["humans"] = humans.Humans

if __name__ == "__main__":
    benchmark.main()
