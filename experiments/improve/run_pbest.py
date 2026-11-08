"""benchmark.py with the DE rule as --ablate pbest."""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import benchmark
import pbest

benchmark.ALGORITHMS["pbest"] = pbest.PBest

if __name__ == "__main__":
    benchmark.main()
