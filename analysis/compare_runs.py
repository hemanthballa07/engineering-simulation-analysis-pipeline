import os
import glob
import json
import pandas as pd
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

def load_run_data(run_dir):
    """Load metadata and metrics from a run directory."""
    try:
        meta_path = os.path.join(run_dir, 'metadata.json')
        metrics_path = os.path.join(run_dir, 'metrics.json')
        
        if not (os.path.exists(meta_path) and os.path.exists(metrics_path)):
            return None
            
        with open(meta_path, 'r') as f:
            meta = json.load(f)
            
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
            
        # Merge dicts
        data = {**meta, **metrics}
        return data
    except Exception as e:
        print(f"Error reading {run_dir}: {e}")
        return None

def main():
    results_dir = os.path.join(project_root, 'results')
    artifacts_dir = os.path.join(project_root, 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # Find all run directories
    # Assuming flat structure: results/run_*
    run_dirs = glob.glob(os.path.join(results_dir, 'run_*'))
    
    all_data = []
    print(f"Scanning {len(run_dirs)} runs in {results_dir}...")
    
    for r_dir in run_dirs:
        if os.path.isdir(r_dir):
            data = load_run_data(r_dir)
            if data:
                all_data.append(data)
    
    if not all_data:
        print("No valid run data found.")
        return
        
    df = pd.DataFrame(all_data)
    
    # Select and reorder columns for clarity
    # desired order: run_id, alpha, nx, L, max_temp_final, total_energy_final, ...
    cols = ['run_id', 'alpha', 'nx', 'L', 't_max', 'max_temp_final', 'avg_temp_final', 'total_energy_final', 'convergence_steps']
    # Filter to only existing columns
    cols = [c for c in cols if c in df.columns]
    # Add remaining columns at the end
    remaining = [c for c in df.columns if c not in cols]
    df = df[cols + remaining]
    
    # Sort
    if 'alpha' in df.columns and 'nx' in df.columns:
        df = df.sort_values(by=['alpha', 'nx'])
        
    # Save CSV
    csv_path = os.path.join(artifacts_dir, 'summary.csv')
    df.to_csv(csv_path, index=False)
    print(f"Summary CSV saved to {csv_path}")
    
    # Save Markdown Report
    md_path = os.path.join(artifacts_dir, 'summary.md')
    with open(md_path, 'w') as f:
        f.write("# Simulation Results Summary\n\n")
        f.write(f"**Total Runs:** {len(df)}\n")
        f.write(f"**Generated:** {pd.Timestamp.now()}\n\n")
        f.write("## Results Table\n\n")
        # Use pandas to_markdown if available (requires tabulate), else manual
        try:
            f.write(df.to_markdown(index=False))
        except ImportError:
            # Fallback simple table
            f.write(df.to_csv(sep='|', index=False))
            
    print(f"Summary Markdown saved to {md_path}")
    print("\nPreview:")
    print(df[cols].head())

if __name__ == "__main__":
    main()
