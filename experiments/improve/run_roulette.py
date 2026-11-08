"""benchmark.py with the noisy-perception prototype as --ablate roulette."""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import benchmark
import roulette

benchmark.ALGORITHMS["roulette"] = roulette.Roulette

if __name__ == "__main__":
    benchmark.main()
