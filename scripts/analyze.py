import os
import sys
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from analysis.aggregate_runs import collect_runs, write_summary_artifacts


def main():
    results_root = Path(project_root) / "results" / "runs"
    artifacts_dir = Path(project_root) / "artifacts"

    rows = collect_runs(results_root)
    if not rows:
        print(f"No complete runs found under: {results_root}")
        print("Expected each run folder to contain metadata.json and metrics.json.")
        return

    csv_path, md_path, top_md_path = write_summary_artifacts(rows, artifacts_dir, top_n=5)

    print("Wrote artifacts:")
    print(f"- {csv_path}")
    print(f"- {md_path}")
    print(f"- {top_md_path}")


if __name__ == "__main__":
    main()
