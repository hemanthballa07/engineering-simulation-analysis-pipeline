#!/bin/bash
set -e

# Define colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Starting Local Engineering Pipeline ===${NC}"

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# 1. Setup / Check Environment
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Warning: .venv not found. Assuming dependencies are installed globally or in current env."
fi

# 2. Run Tests
echo -e "\n${GREEN}[Step 1/4] Running Tests...${NC}"
pytest tests/

# 3. Run Sweep
echo -e "\n${GREEN}[Step 2/4] Running Parameter Sweep...${NC}"
# Optional: clean old results?
# rm -rf results/*
python simulations/sweep.py

# 4. Run Analysis
echo -e "\n${GREEN}[Step 3/4] Running Analysis...${NC}"
python analysis/compare_runs.py

# 5. Run Visualization
echo -e "\n${GREEN}[Step 4/4] Generating Visualizations...${NC}"
python visualization/plot_simulations.py

echo -e "\n${GREEN}=== Pipeline Completed Successfully ===${NC}"
echo "Artifacts are available in artifacts/"
