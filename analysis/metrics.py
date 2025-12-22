import pandas as pd
import numpy as np
import json
import os

def load_timeseries(csv_path):
    """Load timeseries data from CSV."""
    return pd.read_csv(csv_path)

def compute_run_metrics(df, dx, dt, alpha):
    """
    Compute metrics from timeseries dataframe.
    
    Args:
        df (pd.DataFrame): Timeseries data.
        dx (float): Spatial step size.
        dt (float): Time step size.
        alpha (float): Thermal diffusivity.
        
    Returns:
        dict: Computed metrics.
    """
    # Get final timestep row
    final_row = df.iloc[-1]
    
    # Extract spatial columns (p0, p1, ...)
    p_cols = [c for c in df.columns if c.startswith('p')]
    # Sort numerically just in case
    p_cols.sort(key=lambda x: int(x[1:]))
    
    u_final = final_row[p_cols].values.astype(float)
    
    # 1. Basic Stats
    max_temp = float(np.max(u_final))
    min_temp = float(np.min(u_final))
    mean_temp = float(np.mean(u_final))
    
    # 2. Energy-like metric: sum(u^2 * dx)
    # Integral of u^2
    energy_like_metric = float(np.sum(u_final**2) * dx)
    
    # 3. Stability Ratio
    # r = alpha * dt / dx^2
    stability_ratio = float(alpha * dt / (dx**2))
    
    return {
        "max_temperature": max_temp,
        "min_temperature": min_temp,
        "mean_temperature": mean_temp,
        "energy_like_metric": energy_like_metric,
        "stability_ratio": stability_ratio
    }
