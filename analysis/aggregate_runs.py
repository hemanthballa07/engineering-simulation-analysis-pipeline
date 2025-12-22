from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import csv


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object/dict: {path}")
    return data


def _safe_get(d: Dict[str, Any], key: str, default: Any = None) -> Any:
    return d.get(key, default)


def _to_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _to_int(v: Any) -> Optional[int]:
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def collect_runs(results_root: str | Path = "results/runs") -> List[Dict[str, Any]]:
    """
    Collect and flatten all runs under results_root.

    Expected structure:
      results/runs/<run_id>/
        - metadata.json
        - metrics.json
        - timeseries.csv (not needed here)
    """
    root = Path(results_root)
    if not root.exists():
        raise FileNotFoundError(f"Results root not found: {root}")

    rows: List[Dict[str, Any]] = []

    # root.iterdir() might pick up .DS_Store or files? Check is_dir()
    run_dirs = sorted([p for p in root.iterdir() if p.is_dir()])
    for run_dir in run_dirs:
        meta_path = run_dir / "metadata.json"
        metrics_path = run_dir / "metrics.json"

        # Skip incomplete runs (but keep behavior explicit)
        if not meta_path.exists() or not metrics_path.exists():
            continue

        meta = _read_json(meta_path)
        metrics = _read_json(metrics_path)

        row: Dict[str, Any] = {
            "run_id": _safe_get(meta, "run_id", run_dir.name),
            "created_at": _safe_get(meta, "created_at"),
            "git_commit_hash": _safe_get(meta, "git_commit_hash"),
            "python_version": _safe_get(meta, "python_version"),
            "platform": _safe_get(meta, "platform"),
            # Parameters (flattened)
            "L": _to_float(_safe_get(meta, "L")),
            "nx": _to_int(_safe_get(meta, "nx")),
            "alpha": _to_float(_safe_get(meta, "alpha")),
            "t_max": _to_float(_safe_get(meta, "t_max")),
            "actual_dt": _to_float(_safe_get(meta, "actual_dt")),
            "steps": _to_int(_safe_get(meta, "steps")),
            "save_interval": _to_int(_safe_get(meta, "save_interval")),
            # Metrics
            "max_temperature": _to_float(_safe_get(metrics, "max_temperature")),
            "min_temperature": _to_float(_safe_get(metrics, "min_temperature")),
            "mean_temperature": _to_float(_safe_get(metrics, "mean_temperature")),
            "energy_like_metric": _to_float(_safe_get(metrics, "energy_like_metric")),
            "stability_ratio": _to_float(_safe_get(metrics, "stability_ratio")),
            # File paths (nice for debugging)
            "run_dir": str(run_dir),
        }

        rows.append(row)

    return rows


def _format_md_table(headers: List[str], rows: List[List[Any]]) -> str:
    def fmt(v: Any) -> str:
        if v is None:
            return ""
        if isinstance(v, float):
            # Compact but readable
            if abs(v) < 1e-4 and v != 0.0:
                return f"{v:.3e}"
            return f"{v:.6f}".rstrip("0").rstrip(".")
        return str(v)

    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_lines = ["| " + " | ".join(fmt(v) for v in row) + " |" for row in rows]
    return "\n".join([header_line, sep_line] + body_lines)


def write_summary_artifacts(
    rows: List[Dict[str, Any]],
    artifacts_dir: str | Path = "artifacts",
    top_n: int = 5,
) -> Tuple[Path, Path, Path]:
    """
    Writes:
      - summary.csv
      - summary.md
      - top_runs.md
    Returns paths to written files.
    """
    out_dir = Path(artifacts_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Define stable column order (don’t rely on dict ordering)
    columns = [
        "run_id",
        "created_at",
        "nx",
        "alpha",
        "t_max",
        "actual_dt",
        "steps",
        "stability_ratio",
        "max_temperature",
        "mean_temperature",
        "energy_like_metric",
        "git_commit_hash",
        "python_version",
        "platform",
        "run_dir",
    ]

    # Write CSV (no pandas dependency)
    csv_path = out_dir / "summary.csv"
    with csv_path.open("w", encoding="utf-8") as f:
        f.write(",".join(columns) + "\n")
        for r in rows:
            values = []
            for c in columns:
                v = r.get(c)
                if v is None:
                    values.append("")
                else:
                    s = str(v)
                    # Escape commas and quotes
                    if "," in s or '"' in s:
                        s = '"' + s.replace('"', '""') + '"'
                    values.append(s)
            f.write(",".join(values) + "\n")

    # Write Markdown summary (subset)
    md_path = out_dir / "summary.md"
    md_headers = ["run_id", "nx", "alpha", "t_max", "stability_ratio", "max_temperature", "energy_like_metric"]
    md_rows = []
    for r in rows:
        md_rows.append([r.get(h) for h in md_headers])

    md_path.write_text(
        "# Run Summary\n\n"
        + _format_md_table(md_headers, md_rows)
        + "\n",
        encoding="utf-8",
    )

    # Rank runs: default objective = minimize energy_like_metric
    ranked = sorted(
        rows,
        key=lambda r: (r.get("energy_like_metric") is None, r.get("energy_like_metric", float("inf"))),
    )
    top = ranked[:top_n]

    top_md_path = out_dir / "top_runs.md"
    top_headers = ["run_id", "nx", "alpha", "t_max", "energy_like_metric", "stability_ratio", "max_temperature"]
    top_rows = [[r.get(h) for h in top_headers] for r in top]

    top_md_path.write_text(
        f"# Top {top_n} Runs (by lowest energy_like_metric)\n\n"
        + _format_md_table(top_headers, top_rows)
        + "\n\n"
        + "Note: This ranking is a simple, generic objective for demonstration.\n",
        encoding="utf-8",
    )

    return csv_path, md_path, top_md_path
