import sys
import os
import itertools
import yaml
import csv
import hashlib
import json
import numpy as np

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None

from simulations.solver import HeatEquationSolver1D

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_stable_id(params):
    """Generate a stable ID based on parameter values."""
    # filtering out 'save_interval' from hash if it doesn't affect physics? 
    # But strictly speaking different interval = different output files.
    # Let's simple hash the whole sorted dictionary.
    
    # Ensure standard types for hashing
    clean_params = params.copy()
    # Normalize potential float representations if needed, but for now simple json dump
    param_str = json.dumps(clean_params, sort_keys=True)
    return hashlib.md5(param_str.encode('utf-8')).hexdigest()[:8]

def run_simulation(params, output_base_dir):
    """
    Run a single simulation with given params and save results.
    """
    run_id = f"run_{get_stable_id(params)}"
    print(f"Starting run {run_id} with params: {params}")
    
    L = params.get('L', 1.0)
    nx = int(params.get('nx', 50))
    alpha = params.get('alpha', 0.1)
    t_max = params.get('t_max', 0.5)
    dt = params.get('dt', None)
    save_interval = int(params.get('save_interval', 20))
    
    try:
        solver = HeatEquationSolver1D(L=L, nx=nx, alpha=alpha, t_max=t_max, dt=dt)
        
        # Consistent initial condition for fair comparison
        # Peak in center
        def initial_peak(x):
            return np.exp(-100 * (x - 0.5)**2)
        
        solver.set_initial_condition(initial_peak)
        
        results = solver.solve(save_interval=save_interval)
        
        # Save results
        run_dir = os.path.join(output_base_dir, run_id)
        os.makedirs(run_dir, exist_ok=True)
        
        # 1. Save results CSV
        data = []
        for t, u in results:
            row = {'time': t}
            for i, val in enumerate(u):
                row[f'p{i}'] = val
            data.append(row)
            
        csv_path = os.path.join(run_dir, "timeseries.csv")
        
        if pd:
            df = pd.DataFrame(data)
            df.to_csv(csv_path, index=False)
        else:
            if data:
                fieldnames = list(data[0].keys())
                with open(csv_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                    
        # 2. Save Config/Metadata used for this run
        # Merge calculated dt/nt into params for record keeping
        run_metadata = params.copy()
        run_metadata['actual_dt'] = solver.dt
        run_metadata['steps'] = solver.nt
        run_metadata['run_id'] = run_id
        
        with open(os.path.join(run_dir, "metadata.json"), 'w') as f:
            json.dump(run_metadata, f, indent=2)
            
        # 3. Compute and Save Metrics
        # Analysis of the FINAL state
        final_t, final_u = results[-1]
        
        # Global stats across history could also be useful, but let's stick to final or aggregation
        max_temp_all = max(np.max(u) for _, u in results)
        max_temp_final = np.max(final_u)
        avg_temp_final = np.mean(final_u)
        # Total energy ~ Integral(T dx) ~ sum(T)*dx
        total_energy_final = np.sum(final_u) * solver.dx
        
        metrics = {
            "max_temp_global": float(max_temp_all),
            "max_temp_final": float(max_temp_final),
            "avg_temp_final": float(avg_temp_final),
            "total_energy_final": float(total_energy_final),
            "convergence_steps": solver.nt,
            "final_time": float(final_t),
            "dx": float(solver.dx),
            "dt": float(solver.dt)
        }
        
        with open(os.path.join(run_dir, "metrics.json"), 'w') as f:
            json.dump(metrics, f, indent=2)
            
        print(f"  -> Run {run_id} completed. Saved to {run_dir}")
        return True
        
    except Exception as e:
        print(f"  -> Run {run_id} FAILED: {e}")
        return False

def main():
    base_config_path = os.path.join(project_root, 'configs', 'base.yaml')
    sweep_config_path = os.path.join(project_root, 'configs', 'sweep.yaml')
    
    base_config = load_config(base_config_path)
    sweep_config = load_config(sweep_config_path)
    
    base_params = base_config['simulation']
    sweep_params = sweep_config['sweep']
    
    # Generate Cartesian product of sweep parameters
    keys = list(sweep_params.keys())
    values = list(sweep_params.values())
    combinations = list(itertools.product(*values))
    
    print(f"Found {len(combinations)} parameter combinations to sweep.")
    
    results_dir = os.path.join(project_root, 'results')
    
    for combo in combinations:
        # Merge base params with sweep overrides
        current_params = base_params.copy()
        for i, key in enumerate(keys):
            current_params[key] = combo[i]
            
        # Run simulation (ID generation moved inside)
        run_simulation(current_params, results_dir)

if __name__ == "__main__":
    main()
