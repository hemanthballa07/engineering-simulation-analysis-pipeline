import pytest
import os
import sys
import shutil
import tempfile
from unittest.mock import patch

# Add project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import simulations.sweep as sweep_module

def test_end_to_end_sweep():
    """Run a small sweep using the actual sweep function and verify output files."""
    
    # Create temp directory for results
    with tempfile.TemporaryDirectory() as tmp_dir:
        
        # Define small test params
        test_params = {
            'L': 1.0,
            'nx': 20,
            'alpha': 0.1,
            't_max': 0.05,
            'dt': None,
            'save_interval': 5
        }
        
        # Manually trigger the simulation function
        # Note: We need to bypass the 'main' / config loading part to test quickly
        # or we could construct a dummy combinations check.
        # Let's test `run_simulation` directly.
        
        success = sweep_module.run_simulation(test_params, tmp_dir)
        assert success
        
        # Check files
        run_id = f"run_{sweep_module.get_stable_id(test_params)}"
        run_dir = os.path.join(tmp_dir, run_id)
        
        assert os.path.exists(run_dir)
        assert os.path.exists(os.path.join(run_dir, "timeseries.csv"))
        assert os.path.exists(os.path.join(run_dir, "metadata.json"))
        assert os.path.exists(os.path.join(run_dir, "metrics.json"))
