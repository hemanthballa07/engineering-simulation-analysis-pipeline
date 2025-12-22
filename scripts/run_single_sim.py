import sys
import os
import pandas as pd
import numpy as np

# Add project root to path to ensure we can import simulation module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from simulations.solver import HeatEquationSolver1D

def main():
    print("Running single simulation test...")
    
    # Parameters
    L = 1.0
    nx = 50
    alpha = 0.1
    t_max = 0.5
    
    # Instantiate solver
    solver = HeatEquationSolver1D(L=L, nx=nx, alpha=alpha, t_max=t_max)
    
    # Initial Condition: Peak in center e^(-100(x-0.5)^2)
    def initial_peak(x):
        return np.exp(-100 * (x - 0.5)**2)
    
    solver.set_initial_condition(initial_peak)
    
    print(f"Configuration: L={L}, nx={nx}, alpha={alpha}, t_max={t_max}")
    print(f"Computed dt: {solver.dt:.6f}, Steps: {solver.nt}")
    
    # Solve
    results = solver.solve(save_interval=20)
    
    # Save output
    output_dir = os.path.join(project_root, "results")
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert simulation history to flat DataFrame
    # Format: time, x, temp (long format) or time, x0, x1... (wide format)
    # Requirement asked for timeseries.parquet/csv. Wide format is usually easier for simple arrays.
    
    data = []
    for t, u in results:
        row = {'time': t}
        for i, val in enumerate(u):
            row[f'p{i}'] = val # p0, p1, ... pn for spatial points
        data.append(row)
    
    df = pd.DataFrame(data)
    csv_path = os.path.join(output_dir, "single_run.csv")
    df.to_csv(csv_path, index=False)
    
    print(f"Simulation saved to {csv_path}")
    print("Preview of first few rows:")
    print(df.head())

if __name__ == "__main__":
    main()
