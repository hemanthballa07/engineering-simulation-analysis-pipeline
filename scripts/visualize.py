import os
import sys
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from visualization.plot_metric_sweep import plot_energy_vs_alpha
from visualization.plot_temp_profiles import plot_final_profiles


def _extract_run_ids_from_top_runs(top_runs_md: Path, max_n: int = 5):
    """
    Extract run_ids from the markdown table in artifacts/top_runs.md.
    Assumes first column header is 'run_id'.
    """
    if not top_runs_md.exists():
        raise FileNotFoundError(f"Missing file: {top_runs_md}")

    run_ids = []
    for line in top_runs_md.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("|") and "run_" in line and "run_id" not in line and "---" not in line:
            # markdown row like: | run_xxx | ...
            parts = [p.strip() for p in line.strip("|").split("|")]
            if parts:
                run_ids.append(parts[0])
        if len(run_ids) >= max_n:
            break
    return run_ids


def main():
    results_root = Path(project_root) / "results" / "runs"
    artifacts = Path(project_root) / "artifacts"

    summary_csv = artifacts / "summary.csv"
    top_runs_md = artifacts / "top_runs.md"

    # Plot metric sweep
    plot_energy_vs_alpha(summary_csv, artifacts / "metric_sweep.png")

    # Plot final profiles for top runs
    run_ids = _extract_run_ids_from_top_runs(top_runs_md, max_n=5)
    run_dirs = [results_root / rid for rid in run_ids]
    plot_final_profiles(run_dirs, artifacts / "temp_profiles.png")

    print("Wrote plots:")
    print(f"- {artifacts / 'metric_sweep.png'}")
    print(f"- {artifacts / 'temp_profiles.png'}")


if __name__ == "__main__":
    main()
