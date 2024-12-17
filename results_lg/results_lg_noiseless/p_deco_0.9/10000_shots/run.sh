#!/bin/bash

# Deactivate any active virtual environment
deactivate 2>/dev/null || true

# Navigate to the project directory
cd /mnt/project_mnt/farm_fs/dmelegari/legget_garg || { echo 'Project directory not found'; exit 1; }

# Activate the Python virtual environment
source env/bin/activate

# Check that the virtual environment is active
echo "Python path: $(which python3)"
echo "Python version: $(python3 --version)"
echo "Pip path: $(which pip3)"
pip3 show qiskit

# Add the main project directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/mnt/project_mnt/farm_fs/dmelegari

# Print PYTHONPATH for debugging
echo "PYTHONPATH: $PYTHONPATH"

# Run the main Python script with the provided parameters
echo 'Running main script...'
python3 /mnt/project_mnt/farm_fs/dmelegari/legget_garg/src/main.py 1.5707963267948966 1.5707963267948966 0.9 10000 1000 /mnt/project_mnt/farm_fs/dmelegari/legget_garg/results_lg/results_lg_noiseless/p_deco_0.9/10000_shots True False 100
