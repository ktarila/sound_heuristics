"""benchmark.py with the hearing prototype as --ablate hearing."""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import benchmark
import hearing

benchmark.ALGORITHMS["hearing"] = hearing.Hearing

if __name__ == "__main__":
    benchmark.main()
