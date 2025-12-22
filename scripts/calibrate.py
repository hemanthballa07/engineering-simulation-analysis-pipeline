"""
Calibration Script: Design Optimization via Inverse Solving.

Goal: Find the thermal diffusivity (alpha) required to achieve 
      a specific peak temperature at t_max.

Method: Uses scipy.optimize.brentq (root finding) to solve:
        f(alpha) = simulate(alpha).max_temp - target_temp = 0
"""
import os
import sys
import numpy as np
from scipy.optimize import brentq
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulations.solver import HeatEquationSolver1D

def run_forward_model(alpha, target_temp):
    """
    Runs the simulation for a given alpha and returns (max_temp - target).
    """
    # Fixed parameters for the design problem
    L = 1.0
    nx = 50
    t_max = 0.5
    
    # Run Solver
    solver = HeatEquationSolver1D(L=L, nx=nx, alpha=alpha, t_max=t_max)
    
    # Consistent initial condition
    solver.set_initial_condition(lambda x: np.exp(-100 * (x - 0.5)**2))
    
    # Solve (we only need the final state)
    history = solver.solve(save_interval=999999) # Don't save intermediate steps
    final_u = history[-1][1]
    
    max_temp = np.max(final_u)
    return max_temp - target_temp

def calibrate_material(target_temp):
    print(f"--- Starting Calibration ---")
    print(f"Goal: Find 'alpha' such that Max Temp = {target_temp:.4f} at t=0.5s")
    
    # Define bounds for alpha search [0.001, 2.0]
    # We assume monotonic relationship: higher alpha -> faster diffusion -> lower peak temp
    # So f(alpha) is monotonic.
    
    start_time = time.time()
    
    # Solver
    try:
        optimal_alpha, result = brentq(
            run_forward_model, 
            0.001, 2.0,       # Bounds
            args=(target_temp,),
            xtol=1e-4,        # Precision of alpha
            full_output=True,
            disp=False
        )
    except ValueError as e:
        print(f"Optimization failed: {e}")
        print("Target temperature likely unreachable within alpha bounds [0.001, 2.0].")
        return

    duration = time.time() - start_time
    
    # Verification run
    error = run_forward_model(optimal_alpha, target_temp)
    print(f"\n--- Optimization Complete ({duration:.3f}s) ---")
    print(f"Converged!")
    print(f"optimal_alpha = {optimal_alpha:.6f}")
    print(f"Residual error = {error:.2e}")
    print(f"Iterations    = {result.iterations}")

if __name__ == "__main__":
    # Example Design Target: Ensure peak temp drops to 0.30 (from initial 1.0)
    calibrate_material(target_temp=0.30)
