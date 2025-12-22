import os
import glob
import json
import matplotlib.pyplot as plt
import pandas as pd
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Set style (optional, for aesthetics)
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    pass # Fallback to default

def load_run_data(run_dir):
    """Load metadata, metrics, and timeseries from a run directory."""
    try:
        meta_path = os.path.join(run_dir, 'metadata.json')
        metrics_path = os.path.join(run_dir, 'metrics.json')
        ts_path = os.path.join(run_dir, 'timeseries.csv')
        
        if not (os.path.exists(meta_path) and os.path.exists(metrics_path) and os.path.exists(ts_path)):
            return None
            
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
            
        ts = pd.read_csv(ts_path)
        
        return {
            'meta': meta,
            'metrics': metrics,
            'ts': ts,
            'run_id': meta.get('run_id', os.path.basename(run_dir))
        }
    except Exception as e:
        print(f"Error reading {run_dir}: {e}")
        return None

def plot_temp_profiles(runs_data, output_dir):
    """Plot final temperature profiles for all runs."""
    plt.figure(figsize=(10, 6))
    
    for run in runs_data:
        # Get final state
        ts = run['ts']
        final_row = ts.iloc[-1]
        
        # Extract spatial points (columns p0, p1, ...)
        p_cols = [c for c in ts.columns if c.startswith('p')]
        # Sort just in case
        p_cols.sort(key=lambda x: int(x[1:]))
        
        u_final = final_row[p_cols].values
        
        # Reconstruct x (assuming L=1, evenly spaced)
        L = run['meta'].get('L', 1.0)
        nx = len(u_final)
        x = [i * L / (nx - 1) for i in range(nx)]
        
        # Label with key params
        alpha = run['meta'].get('alpha')
        nx_val = run['meta'].get('nx')
        label = f"alpha={alpha}, nx={nx_val}"
        
        plt.plot(x, u_final, label=label)
        
    plt.title("Final Temperature Profiles")
    plt.xlabel("x")
    plt.ylabel("Temperature")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "temp_profiles.png"))
    plt.close()
    print("Saved artifacts/temp_profiles.png")

def plot_metric_sweep(runs_data, output_dir):
    """Plot metrics comparison (e.g. Max Temp vs Alpha)."""
    # Extract data for plotting
    data = []
    for run in runs_data:
        item = {
            'alpha': run['meta'].get('alpha'),
            'nx': run['meta'].get('nx'),
            'max_temp': run['metrics'].get('max_temp_final'),
            'avg_temp': run['metrics'].get('avg_temp_final')
        }
        data.append(item)
    
    df = pd.DataFrame(data)
    
    if df.empty:
        return

    # Plot Max Temp vs Alpha, grouped by nx
    plt.figure(figsize=(10, 6))
    
    for nx, group in df.groupby('nx'):
        group = group.sort_values('alpha')
        plt.plot(group['alpha'], group['max_temp'], marker='o', label=f"nx={nx}")
        
    plt.title("Parameter Sweep: Max Final Temperature vs Alpha")
    plt.xlabel("Alpha (Thermal Diffusivity)")
    plt.ylabel("Max Final Temperature")
    plt.xscale('log') # Alpha varies by orders of magnitude often
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.savefig(os.path.join(output_dir, "metric_sweep.png"))
    plt.close()
    print("Saved artifacts/metric_sweep.png")

def main():
    results_dir = os.path.join(project_root, 'results')
    artifacts_dir = os.path.join(project_root, 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # Find all run directories
    run_dirs = glob.glob(os.path.join(results_dir, 'run_*'))
    
    runs_data = []
    print(f"Loading data from {len(run_dirs)} runs...")
    
    for r_dir in run_dirs:
        if os.path.isdir(r_dir):
            data = load_run_data(r_dir)
            if data:
                runs_data.append(data)
                
    if not runs_data:
        print("No valid data found.")
        return
        
    plot_temp_profiles(runs_data, artifacts_dir)
    plot_metric_sweep(runs_data, artifacts_dir)

if __name__ == "__main__":
    main()
