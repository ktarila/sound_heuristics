"""Our CEC 2022 functions against the organisers' C code, same points.

Points: uniform in the box, and near each best point (shift rows) at
several distances. Prints the largest relative difference per function.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = str(__import__("pathlib").Path(__file__).resolve().parents[2])
sys.path.insert(0, REPO)
from sound_heuristic import cec2022  # noqa: E402

DRIVER = Path(sys.argv[1])          # compiled driver
CDIR = Path(sys.argv[2])            # folder holding the C code's input_data/
WORK = Path(sys.argv[3])            # where point files go

rng = np.random.default_rng(12345)
worst_all = 0.0
for dim in (10, 20):
    for index in range(1, 13):
        shift = np.loadtxt(CDIR / "input_data" / f"shift_data_{index}.txt")
        rows = shift.reshape(-1, shift.shape[-1])[:, :dim]
        if index <= 8:
            rows = rows[:1]
        parts = [rng.uniform(-100, 100, (1500, dim))]
        for row in rows:
            parts.append(row[None])
            for scale in (1e-6, 1e-3, 0.1, 1.0, 10.0):
                parts.append(np.clip(row + scale * rng.standard_normal((60, dim)), -100, 100))
        points = np.vstack(parts)
        path = WORK / f"pts_{index}_{dim}.txt"
        with open(path, "w") as handle:
            handle.write(f"{len(points)}\n")
            np.savetxt(handle, points, fmt="%.17g")
        out = subprocess.run([str(DRIVER), str(index), str(dim), str(path)],
                             cwd=CDIR, capture_output=True, text=True, check=True)
        theirs = np.array([float(v) for v in out.stdout.split()])
        ours = cec2022.get_problem(index, dim).func(points)
        rel = np.abs(ours - theirs) / np.maximum(1.0, np.abs(theirs))
        worst = int(np.argmax(rel))
        worst_all = max(worst_all, rel[worst])
        at_best = theirs[1500]
        print(f"D{dim:<2} F{index:<2} points {len(points):5d}  max rel diff {rel[worst]:.2e}"
              f"  (ours {ours[worst]:.10g}, C {theirs[worst]:.10g})  C at best point {at_best:.10g}")
print(f"largest relative difference over all: {worst_all:.2e}")
