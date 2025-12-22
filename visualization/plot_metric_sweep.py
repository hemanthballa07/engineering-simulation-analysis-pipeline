from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd


def plot_energy_vs_alpha(summary_csv: Path, out_path: Path) -> None:
    df = pd.read_csv(summary_csv)

    # Drop incomplete rows
    df = df.dropna(subset=["alpha", "energy_like_metric", "nx"])

    plt.figure()
    # Group by nx to give separate markers
    for nx_val, g in df.groupby("nx"):
        plt.scatter(g["alpha"], g["energy_like_metric"], label=f"nx={nx_val}")

    plt.title("Energy-like metric vs alpha")
    plt.xlabel("alpha")
    plt.ylabel("energy_like_metric")
    plt.legend()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()
