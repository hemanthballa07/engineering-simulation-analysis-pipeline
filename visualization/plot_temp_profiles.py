from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt


def _read_csv_timeseries(path: Path) -> Tuple[List[float], List[List[float]]]:
    """
    Returns (times, snapshots)
    snapshots is a list of u vectors (each list[float]) corresponding to each saved time row.
    """
    times: List[float] = []
    snapshots: List[List[float]] = []

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header in {path}")

        p_cols = [c for c in reader.fieldnames if c.startswith("p")]
        if not p_cols:
            raise ValueError(f"No spatial columns found in {path} (expected p0..pN)")

        # Ensure stable ordering p0, p1, ...
        p_cols.sort(key=lambda s: int(s[1:]))

        for row in reader:
            t = float(row["time"])
            u = [float(row[c]) for c in p_cols]
            times.append(t)
            snapshots.append(u)

    return times, snapshots


def plot_final_profiles(
    run_dirs: List[Path],
    out_path: Path,
    title: str = "Final temperature profiles (top runs)",
) -> None:
    plt.figure()
    for run_dir in run_dirs:
        ts_path = run_dir / "timeseries.csv"
        times, snapshots = _read_csv_timeseries(ts_path)
        u_final = snapshots[-1]
        x = list(range(len(u_final)))
        plt.plot(x, u_final, label=run_dir.name)

    plt.title(title)
    plt.xlabel("Spatial index")
    plt.ylabel("Temperature")
    plt.legend(fontsize=7)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()
