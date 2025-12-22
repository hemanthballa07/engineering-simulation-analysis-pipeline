import numpy as np
from typing import List, Tuple, Optional, Callable

class HeatEquationSolver1D:
    """
    1D Heat Equation Solver using Explicit Finite Difference Method.
    Equation: dT/dt = alpha * d2T/dx^2
    """
    
    def __init__(self, L: float, nx: int, alpha: float, t_max: float, dt: float = None):
        """
        Initialize the solver.

        Args:
            L (float): Length of the domain.
            nx (int): Number of spatial points.
            alpha (float): Thermal diffusivity key parameter.
            t_max (float): Total simulation time.
            dt (float, optional): Time step size. If None, calculated for stability.
        """
        self.L = L
        self.nx = nx
        self.dx = L / (nx - 1)
        self.alpha = alpha
        self.t_max = t_max
        
        # Stability check: r = alpha * dt / dx^2 <= 0.5
        limit_dt = 0.5 * self.dx**2 / alpha
        
        if dt is None:
            # Use 90% of the limit for safety
            self.dt = 0.9 * limit_dt
        else:
            self.dt = dt
            if self.dt > limit_dt:
                raise ValueError(f"Stability check failed: dt={dt:.2e} > limit={limit_dt:.2e} (r > 0.5)")
        
        self.nt = int(t_max / self.dt)
        self.x = np.linspace(0, L, nx)
        self.u = np.zeros(nx)
        
    def set_initial_condition(self, func: Callable[[np.ndarray], np.ndarray]):
        """
        Set initial temperature profile u(x, 0) = func(x).
        
        Args:
            func: A function that takes x array and returns u array.
        """
        self.u = func(self.x)

    def solve(self, save_interval: int = 100) -> List[Tuple[float, np.ndarray]]:
        """
        Run the simulation.

        Args:
            save_interval (int): Number of steps between saving timepoints.

        Returns:
            history: List of tuples (time, temperature_array).
        """
        t = 0.0
        r = self.alpha * self.dt / (self.dx**2)
        
        # history storage
        history = [(t, self.u.copy())]
        
        u = self.u.copy()
        u_new = np.zeros_like(u)
        
        # Time-stepping
        for n in range(1, self.nt + 1):
            # Finite difference explicit scheme for interior points
            # u_i^{n+1} = u_i^n + r * (u_{i+1}^n - 2u_i^n + u_{i-1}^n)
            u_new[1:-1] = u[1:-1] + r * (u[2:] - 2*u[1:-1] + u[:-2])
            
            # Boundary conditions: Fixed Dirichlet (T=0 at ends)
            # In a more advanced version, this could be configurable-
            u_new[0] = 0.0
            u_new[-1] = 0.0
            
            # Update state
            u[:] = u_new[:]
            t += self.dt
            
            if n % save_interval == 0 or n == self.nt:
                history.append((t, u.copy()))
                
        return history
