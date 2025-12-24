-- Database Schema for Engineering Analytics Platform

-- 1. Runs Table: Central registry of all simulation executions
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    duration_ms REAL,
    git_commit_hash TEXT,
    platform TEXT,
    python_version TEXT
);

-- 2. Parameters Table: Normalizes input configuration (key-value pairs)
-- Allows querying: "SELECT run_id FROM parameters WHERE param_name='alpha' AND param_value > 0.5"
CREATE TABLE IF NOT EXISTS parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    param_name TEXT,
    param_value TEXT, -- Storing as text for flexibility, can cast in queries
    FOREIGN KEY(run_id) REFERENCES runs(run_id)
);

-- Index for fast parameter lookups
CREATE INDEX IF NOT EXISTS idx_params_run_id ON parameters(run_id);
CREATE INDEX IF NOT EXISTS idx_params_name ON parameters(param_name);

-- 3. Metrics Table: Stores computed scalar metrics for each run
-- Allows querying: "SELECT run_id, max_temperature FROM metrics WHERE stability_ratio < 0.5"
-- Note: We are flattening the metrics into specific columns for easier BI,
-- but a Key-Value approach (metric_name, metric_value) is also valid.
-- The spec requested: max_temperature, convergence stability, performance vs configuration
-- We will use a hybrid: Key columns for critical metrics, runs can have extra metrics joinable or in a JSON blob if needed.
-- However, for the specific request, we will match the implementation plan.

CREATE TABLE IF NOT EXISTS metrics (
    run_id TEXT PRIMARY KEY,
    max_temperature REAL,
    min_temperature REAL,
    mean_temperature REAL,
    energy_like_metric REAL,
    stability_ratio REAL,
    FOREIGN KEY(run_id) REFERENCES runs(run_id)
);
