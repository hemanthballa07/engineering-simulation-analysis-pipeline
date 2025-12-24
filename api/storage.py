import os
import json
import sys
from pathlib import Path

# Add project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Import validation logic
from scripts.validate_metrics import validate_run_metrics, load_schema as load_metrics_schema
import jsonschema

RESULTS_DIR = Path(project_root) / "results" / "runs"
INSIGHTS_DIR = Path(project_root) / "results" / "runs" # Assuming insights are inside run dir or separate?
# The generation script puts insights inside run_dir/insights/
# generate_ai_insights.py: out_path = run_path / "insights"

def get_run_metrics(run_id: str):
    """
    Retrieves and VALIDATES the canonical metrics.json for a run.
    Returns: (payload, error_message)
    """

    # Try finding the run directory
    # Run ID is folder name in results/runs/ usually, but let's search or assume standard structure
    # Robust Lookup: Check main runs, then smoke runs, then ci runs
    candidate_roots = [
        RESULTS_DIR,
        Path(project_root) / "results" / "runs_smoke",
        Path(project_root) / "results" / "runs_ci"
    ]
    
    run_dir = None
    for root in candidate_roots:
        candidate = root / run_id
        if candidate.exists():
            run_dir = candidate
            break
            
    # Check if run exists
    if not run_dir or not run_dir.exists():
        return None, "Run directory not found in known results paths."

    metrics_path = run_dir / "metrics.json" # Wait, Day 3 script (extract_metrics) puts it somewhere?
    # extract_metrics.py prints to stdout or file. 
    # Standard practice here: The pipeline should have persisted "metrics.json" to the run folder.
    # Day 3 extract_metrics can output anywhere. 
    # Let's assume for the API that we expect a 'canonical_metrics.json' or 'metrics.json' in the run dir.
    # We will look for 'metrics.json' first (raw) or 'canonical_metrics.json'.
    # Actually, Day 3 extract_metrics is a tool. We need to ensure it was RUN.
    # For this Day 5 implementation, we will try to load 'canonical_metrics.json' if it exists,
    # or generate it on fly using extract_run_metrics logic (but read-only means we shouldn't write).
    # Let's import the extractor to be safe and generated in-memory if file missing but raw artifacts exist.
    
    from scripts.extract_metrics import extract_run_metrics
    
    try:
        # Generate fresh from artifacts (guarantees up to date)
        payload = extract_run_metrics(str(run_dir))
        
        # Validate
        is_valid, errors = validate_run_metrics(payload)
        if not is_valid:
            return None, f"Validation Failed: {errors}"
            
        return payload, None
        
    except FileNotFoundError:
        return None, "Raw artifacts (metadata/metrics) missing."
    except Exception as e:
        return None, str(e)

def get_run_insights(run_id: str):
    """
    Retrieves and VALIDATES the insights.json for a run.
    Returns: (json_payload, md_content, error_message)
    """
    run_dir = RESULTS_DIR / run_id
    insights_dir = run_dir / "insights"
    json_path = insights_dir / f"{run_id}.insights.json"
    md_path = insights_dir / f"{run_id}.insights.md"
    
    if not json_path.exists():
        return None, None, "Insights not found. Run 'scripts/generate_ai_insights.py' first."
        
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        # Validate Schema
        # We need to import the schema loading from somewhere or just load strictly
        schema_path = Path(project_root) / "ai" / "insights_schema.json"
        with open(schema_path, 'r') as f:
            schema = json.load(f)
            
        jsonschema.validate(instance=data, schema=schema)
        
        md_content = ""
        if md_path.exists():
            with open(md_path, 'r') as f:
                md_content = f.read()
                
        return data, md_content, None
        
    except jsonschema.ValidationError as e:
        return None, None, f"Invalid Insights Schema: {e.message}"
    except Exception as e:
        return None, None, f"Error reading insights: {e}"
