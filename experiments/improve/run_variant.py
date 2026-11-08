"""benchmark.py with prototype variants added as --ablate choices."""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import benchmark
import hyper3
import hyper4
import shrink

benchmark.ALGORITHMS["episode"] = hyper3.EpisodeHyper  # top level: children inherit this
benchmark.ALGORITHMS["agent"] = hyper4.AgentHyper
benchmark.ALGORITHMS["shrink"] = shrink.Shrink

if __name__ == "__main__":
    benchmark.main()
