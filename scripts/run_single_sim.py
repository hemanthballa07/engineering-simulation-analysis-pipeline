import sys
import os
import csv
try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None
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
    
    # Prepare data rows
    data = []
    for t, u in results:
        row = {'time': t}
        for i, val in enumerate(u):
            row[f'p{i}'] = val # p0, p1, ... pn for spatial points
        data.append(row)
    
    csv_path = os.path.join(output_dir, "single_run.csv")
    
    if pd:
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
        print(f"Simulation saved to {csv_path} (using pandas)")
        print("Preview of first few rows:")
        print(df.head())
    else:
        # Fallback to csv module
        if not data:
            print("No data to save.")
            return

        fieldnames = list(data[0].keys())
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Simulation saved to {csv_path} (using csv module)")
        # Simple preview
        print("Preview of first data row:")
        print(data[0])

if __name__ == "__main__":
    main()
