import pytest
import numpy as np
import os
import sys

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulations.solver import HeatEquationSolver1D

def test_stability_check():
    """Test that solver raises ValueError if dt is too large."""
    # Stability: r = alpha * dt / dx^2 <= 0.5
    # Limit dt = 0.5 * dx^2 / alpha
    L = 1.0
    nx = 11 # dx = 0.1
    alpha = 1.0
    # dx = 0.1, dx^2 = 0.01
    # limit_dt = 0.5 * 0.01 / 1.0 = 0.005
    
    # Init with safe dt
    solver = HeatEquationSolver1D(L, nx, alpha, t_max=0.1, dt=0.004)
    assert solver.dt == 0.004
    
    # Init with unsafe dt
    with pytest.raises(ValueError, match="Stability check failed"):
        HeatEquationSolver1D(L, nx, alpha, t_max=0.1, dt=0.006)

def test_determinism():
    """Test that solver produces identical results for identical inputs."""
    params = dict(L=1.0, nx=20, alpha=0.1, t_max=0.1)
    
    solver1 = HeatEquationSolver1D(**params)
    solver1.set_initial_condition(lambda x: np.sin(np.pi * x / params['L']))
    res1 = solver1.solve(save_interval=100)
    
    solver2 = HeatEquationSolver1D(**params)
    solver2.set_initial_condition(lambda x: np.sin(np.pi * x / params['L']))
    res2 = solver2.solve(save_interval=100)
    
    # Check final state match
    t1, u1 = res1[-1]
    t2, u2 = res2[-1]
    
    assert t1 == t2
    np.testing.assert_array_equal(u1, u2)

def test_conservation_or_decay():
    """Test basic physics: with Dirichlet BCs=0, energy should decrease or stay 0."""
    L = 1.0
    nx = 20
    alpha = 0.1
    
    solver = HeatEquationSolver1D(L=L, nx=nx, alpha=alpha, t_max=0.1)
    # Positive initial condition
    solver.set_initial_condition(lambda x: np.sin(np.pi * x / L))
    
    results = solver.solve(save_interval=100)
    
    initial_energy = np.sum(results[0][1])
    final_energy = np.sum(results[-1][1])
    
    # With T=0 at boundaries and T>0 inside, heat flows out -> energy decreases
    assert final_energy < initial_energy
    assert final_energy > 0
