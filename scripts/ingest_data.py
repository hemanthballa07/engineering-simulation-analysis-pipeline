import sqlite3
import json
import os
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

DB_PATH = os.path.join(project_root, 'results', 'analytics.db')
SCHEMA_PATH = os.path.join(project_root, 'sql', 'db_schema.sql')

def init_db(db_path=DB_PATH):
    """Initialize the database with the schema."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
    conn.executescript(schema)
    conn.close()
    print(f"Database initialized at {db_path}")

def ingest_run(run_dir, db_path=DB_PATH):
    """Ingest a single run directory into the database."""
    run_path = Path(run_dir)
    
    # Check for required files
    metadata_path = run_path / "metadata.json"
    metrics_path = run_path / "metrics.json"
    
    if not metadata_path.exists() or not metrics_path.exists():
        print(f"Skipping {run_dir}: Missing metadata.json or metrics.json")
        return False
        
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        run_id = metadata.get('run_id', run_path.name)
        
        # 1. Upsert Run
        cursor.execute('''
            INSERT OR REPLACE INTO runs (run_id, timestamp, status, duration_ms, git_commit_hash, platform, python_version)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            run_id,
            metadata.get('created_at'),
            'SUCCESS', # Assuming success if artifacts exist
            0.0, # Duration not currently captured explicitly in ms in example, defaulting
            metadata.get('git_commit_hash'),
            metadata.get('platform'),
            metadata.get('python_version')
        ))
        
        # 2. Insert Parameters (simpler to delete old and re-insert for updates)
        cursor.execute('DELETE FROM parameters WHERE run_id = ?', (run_id,))
        
        # Filter out non-parameter metadata keys if possible, or just dump everything not "system"
        # For this logic, we will dump keys that were in the original config
        # We know some "system" keys we added in sweep.py
        system_keys = {'actual_dt', 'steps', 'run_id', 'git_commit_hash', 'python_version', 'platform', 'created_at'}
        
        for k, v in metadata.items():
            if k not in system_keys:
                cursor.execute('INSERT INTO parameters (run_id, param_name, param_value) VALUES (?, ?, ?)',
                               (run_id, k, str(v)))
                               
        # 3. Upsert Metrics
        cursor.execute('''
            INSERT OR REPLACE INTO metrics (run_id, max_temperature, min_temperature, mean_temperature, energy_like_metric, stability_ratio)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            run_id,
            metrics.get('max_temperature'),
            metrics.get('min_temperature'),
            metrics.get('mean_temperature'),
            metrics.get('energy_like_metric'),
            metrics.get('stability_ratio')
        ))
        
        conn.commit()
        conn.close()
        print(f"Ingested run: {run_id}")
        return True
        
    except Exception as e:
        print(f"Failed to ingest {run_dir}: {e}")
        return False

def ingest_all(results_dir, db_path=DB_PATH):
    """Ingest all runs in a results directory."""
    init_db(db_path)
    
    count = 0
    results_path = Path(results_dir)
    if not results_path.exists():
        print(f"Results directory not found: {results_dir}")
        return
        
    for run_dir in results_path.iterdir():
        if run_dir.is_dir() and (run_dir / "metadata.json").exists():
            if ingest_run(run_dir, db_path):
                count += 1
                
    print(f"Total runs ingested: {count}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest simulation results into SQL database.')
    parser.add_argument('--results', type=str, help='Path to results folder', default=None)
    
    args = parser.parse_args()
    
    if args.results:
        results_dir = args.results
    else:
        results_dir = os.path.join(project_root, 'results', 'runs')
        
    ingest_all(results_dir)
