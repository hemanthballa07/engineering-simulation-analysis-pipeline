import pytest
import numpy as np
import os
import sys

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulations.solver import HeatEquationSolver1D

def test_solver_stability():
    """
    Verify solver prevents unstable configuration.
    r = alpha * dt / dx^2 must be <= 0.5
    """
    L = 1.0
    nx = 11      # dx = 0.1
    alpha = 1.0
    # Stability limit: dt_limit = 0.5 * 0.1^2 / 1.0 = 0.005
    
    # CASE 1: Explicit safe dt -> Success
    solver = HeatEquationSolver1D(L=L, nx=nx, alpha=alpha, t_max=0.01, dt=0.004)
    r = alpha * solver.dt / (solver.dx**2)
    assert r <= 0.5
    
    # CASE 2: Explicit unsafe dt -> ValueError
    with pytest.raises(ValueError, match="Stability check failed"):
        HeatEquationSolver1D(L=L, nx=nx, alpha=alpha, t_max=0.01, dt=0.006)
        
    # CASE 3: Auto-calculated dt -> Success and stable
    solver_auto = HeatEquationSolver1D(L=L, nx=nx, alpha=alpha, t_max=0.01, dt=None)
    r_auto = alpha * solver_auto.dt / (solver_auto.dx**2)
    assert r_auto <= 0.5
    assert r_auto > 0.0  # Should be positive

def test_solver_physics():
    """
    Verify basic physics properties:
    - Temperature decays (max decreases) for diffusion with T=0 boundaries.
    - Non-negative if initial condition is non-negative.
    """
    L = 1.0
    nx = 21
    alpha = 0.1
    t_max = 0.1
    
    solver = HeatEquationSolver1D(L=L, nx=nx, alpha=alpha, t_max=t_max)
    
    # Initial condition: Peak in center (positive)
    solver.set_initial_condition(lambda x: np.exp(-100 * (x - 0.5)**2))
    
    initial_u = solver.u.copy()
    initial_max = np.max(initial_u)
    
    # Run simulation
    history = solver.solve(save_interval=10)
    final_t, final_u = history[-1]
    
    final_max = np.max(final_u)
    
    # Check 1: Decay
    assert final_max < initial_max, "Max temperature should decrease due to diffusion/BCs"
    
    # Check 2: Positivity (explicit method preserves positivity if stable)
    assert np.min(final_u) >= 0.0, "Temperature should remain non-negative"

def test_solver_determinism():
    """
    Verify solver produces identical outputs for identical inputs.
    """
    params = dict(L=1.0, nx=20, alpha=0.1, t_max=0.05)
    
    # Run 1
    s1 = HeatEquationSolver1D(**params)
    s1.set_initial_condition(lambda x: np.sin(np.pi * x))
    res1 = s1.solve()
    
    # Run 2
    s2 = HeatEquationSolver1D(**params)
    s2.set_initial_condition(lambda x: np.sin(np.pi * x))
    res2 = s2.solve()
    
    # Compare Final State
    t1, u1 = res1[-1]
    t2, u2 = res2[-1]
    
    # Floating point comparison
    np.testing.assert_allclose(u1, u2, err_msg="Solver output differs between identical runs")
    assert t1 == t2
