"""benchmark.py with the masking prototype as --ablate masking."""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import benchmark
import masking

benchmark.ALGORITHMS["masking"] = masking.Masking

if __name__ == "__main__":
    benchmark.main()
